#!/usr/bin/env python3
"""Reproducible controller comparison for the SilicaForge-RL simulator.

This script evaluates PPO against fixed, PID, and seeded-random policies under
identical initial furnace states. Its results describe simulator performance,
not real-furnace performance.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from collections import defaultdict
from pathlib import Path
from typing import Callable

import matplotlib.pyplot as plt
import numpy as np
from stable_baselines3 import PPO


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "env"))

from silicon_env import SiliconEnv


Controller = Callable[[np.ndarray, dict, int], np.ndarray]

SCENARIOS = {
    "nominal": {},
    "high_heat_loss": {"heat_loss_multiplier": 1.25},
    "power_derate": {"power_derate": 0.12},
    "low_reactivity_feed": {"yield_multiplier": 0.92},
    "sensor_noise": {"sensor_noise_std_c": 10.0},
}


def action_from_power(power_mw: float, electrode_delta: float = 0.0, c_si_ratio: float = 1.996) -> np.ndarray:
    """Convert physical controller commands to the environment action space."""
    normalized_power = (power_mw / 30.0) * 2.0 - 1.0
    normalized_ratio = (c_si_ratio - 2.0) / 0.2
    return np.array([normalized_power, electrode_delta, normalized_ratio], dtype=np.float32).clip(-1.0, 1.0)


def fixed_controller(_observation: np.ndarray, _info: dict, _step: int) -> np.ndarray:
    """A constant commercial-scale operating point used as a simple baseline."""
    return action_from_power(27.57)


def build_pid_controller(target_temp_c: float = 1865.0, normalized_observation: bool = False) -> Controller:
    """Return a temperature-only PID-style controller with safe power limits."""
    previous_error = 0.0

    def controller(observation: np.ndarray, _info: dict, _step: int) -> np.ndarray:
        nonlocal previous_error
        measured_temp_c = float(observation[0]) * 2500.0 if normalized_observation else float(observation[0])
        error = target_temp_c - measured_temp_c
        derivative = error - previous_error
        previous_error = error
        power_mw = float(np.clip(27.57 + 0.010 * error + 0.001 * derivative, 0.0, 30.0))
        return action_from_power(power_mw)

    return controller


def build_random_controller(seed: int) -> Controller:
    """Return a seeded random policy so every result can be reproduced."""
    generator = np.random.default_rng(seed)

    def controller(_observation: np.ndarray, _info: dict, _step: int) -> np.ndarray:
        return generator.uniform(-1.0, 1.0, size=3).astype(np.float32)

    return controller


def build_ppo_controller(model: PPO) -> Controller:
    def controller(observation: np.ndarray, _info: dict, _step: int) -> np.ndarray:
        action, _ = model.predict(observation, deterministic=True)
        return np.asarray(action, dtype=np.float32)

    return controller


def silicon_tons_produced(power_mw: float, yield_fraction: float) -> float:
    """Use the project's existing 15-minute production scaling convention."""
    nominal_rate_tons_per_hour = (power_mw / 28.5) * 2.72 * yield_fraction
    return nominal_rate_tons_per_hour * 0.25


def run_rollout(
    controller_name: str,
    controller: Controller,
    scenario_name: str,
    scenario_config: dict,
    enhanced_observations: bool,
    seed: int,
    steps: int,
    multizone_observations: bool = False,
) -> tuple[dict, list[dict]]:
    """Run one seeded episode and return aggregate metrics plus raw telemetry."""
    random.seed(seed)
    np.random.seed(seed)
    environment = SiliconEnv(
        **scenario_config,
        enhanced_observations=enhanced_observations,
        multizone_observations=multizone_observations,
        safety_shield=(enhanced_observations or multizone_observations),
    )
    observation, _ = environment.reset(seed=seed)

    traces: list[dict] = []
    total_energy_mwh = 0.0
    total_silicon_tons = 0.0
    total_reward = 0.0
    terminated = False

    for step in range(steps):
        action = controller(observation, {}, step)
        observation, reward, ended, truncated, info = environment.step(action)
        applied_action = np.asarray(info["applied_action"], dtype=np.float32)
        power_mw = float(info["actual_power_mw"])
        step_energy_mwh = power_mw * 0.25
        step_silicon_tons = silicon_tons_produced(power_mw, float(info["liquid_silicon_yield"]))
        total_energy_mwh += step_energy_mwh
        total_silicon_tons += step_silicon_tons
        total_reward += float(reward)

        traces.append(
            {
                "controller": controller_name,
                "scenario": scenario_name,
                "seed": seed,
                "step": step + 1,
                "hour": round((step + 1) * 0.25, 2),
                "temperature_c": float(info["temperature_c"]),
                "power_mw": power_mw,
                "c_si_ratio": float(applied_action[2]) * 0.2 + 2.0,
                "yield_pct": float(info["liquid_silicon_yield"]) * 100.0,
                "sio_loss_pct": float(info["sio_loss_fraction"]) * 100.0,
                "reward": float(reward),
                "terminated": ended,
            }
        )
        terminated = terminated or ended
        if ended or truncated:
            break

    temperatures = [row["temperature_c"] for row in traces]
    yields = [row["yield_pct"] for row in traces]
    sio_losses = [row["sio_loss_pct"] for row in traces]
    return (
        {
            "controller": controller_name,
            "scenario": scenario_name,
            "seed": seed,
            "steps_completed": len(traces),
            "mean_yield_pct": float(np.mean(yields)),
            "mean_sio_loss_pct": float(np.mean(sio_losses)),
            "mean_temperature_c": float(np.mean(temperatures)),
            "temperature_std_dev_c": float(np.std(temperatures)),
            "max_temperature_c": float(max(temperatures)),
            "total_energy_mwh": total_energy_mwh,
            "total_silicon_tons": total_silicon_tons,
            "sec_kwh_per_kg": total_energy_mwh / max(total_silicon_tons, 1e-9),
            "total_reward": total_reward,
            "safety_violation": terminated,
        },
        traces,
    )


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def summarize(run_metrics: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for metric in run_metrics:
        grouped[(metric["scenario"], metric["controller"])].append(metric)

    summary = []
    for (scenario_name, controller_name), metrics in grouped.items():
        row = {"scenario": scenario_name, "controller": controller_name, "runs": len(metrics)}
        for key in (
            "mean_yield_pct",
            "mean_sio_loss_pct",
            "mean_temperature_c",
            "temperature_std_dev_c",
            "max_temperature_c",
            "sec_kwh_per_kg",
            "total_reward",
        ):
            values = np.array([metric[key] for metric in metrics], dtype=float)
            row[f"{key}_mean"] = float(np.mean(values))
            row[f"{key}_std"] = float(np.std(values, ddof=1)) if len(values) > 1 else 0.0
        row["safety_violations"] = int(sum(metric["safety_violation"] for metric in metrics))
        summary.append(row)
    return sorted(summary, key=lambda row: (row["scenario"], row["controller"]))


def write_chart(path: Path, summary: list[dict]) -> None:
    names = [f"{row['scenario']}\n{row['controller']}" for row in summary]
    yields = [row["mean_yield_pct_mean"] for row in summary]
    yield_errors = [row["mean_yield_pct_std"] for row in summary]
    secs = [row["sec_kwh_per_kg_mean"] for row in summary]
    sec_errors = [row["sec_kwh_per_kg_std"] for row in summary]

    figure, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].bar(names, yields, yerr=yield_errors, capsize=3, color="#d97706")
    axes[0].set_title("Mean silicon yield")
    axes[0].set_ylabel("Yield (%)")
    axes[1].bar(names, secs, yerr=sec_errors, capsize=3, color="#0f766e")
    axes[1].set_title("Specific energy consumption")
    axes[1].set_ylabel("SEC (kWh/kg)")
    axes[1].set_yscale("log")
    figure.suptitle("SilicaForge-RL simulator controller comparison")
    for axis in axes:
        axis.tick_params(axis="x", labelrotation=90, labelsize=7)
    figure.tight_layout()
    figure.savefig(path, dpi=160)
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate PPO against reproducible simulator baselines.")
    parser.add_argument("--runs", type=int, default=30, help="Seeded rollouts per controller (default: 30).")
    parser.add_argument("--steps", type=int, default=96, help="Maximum 15-minute steps per rollout (default: 96).")
    parser.add_argument("--seed", type=int, default=2026, help="First random seed (default: 2026).")
    parser.add_argument(
        "--model-path",
        default="best_model.zip",
        help="PPO model path relative to the project root (default: best_model.zip).",
    )
    parser.add_argument(
        "--scenarios",
        default="all",
        help="Comma-separated scenario names, or 'all' (default: all).",
    )
    parser.add_argument(
        "--output-dir",
        default="data/validation/disturbance",
        help="Directory for generated reports, relative to the project root by default.",
    )
    arguments = parser.parse_args()

    if arguments.runs < 1 or arguments.steps < 1:
        parser.error("--runs and --steps must both be positive integers.")

    scenario_names = list(SCENARIOS) if arguments.scenarios == "all" else arguments.scenarios.split(",")
    unknown_scenarios = sorted(set(scenario_names) - set(SCENARIOS))
    if unknown_scenarios:
        parser.error(f"Unknown scenarios: {', '.join(unknown_scenarios)}. Available: {', '.join(SCENARIOS)}")

    model_path = Path(arguments.model_path)
    if not model_path.is_absolute():
        model_path = PROJECT_ROOT / model_path
    if not model_path.exists():
        raise FileNotFoundError(f"PPO model not found: {model_path}")

    output_dir = Path(arguments.output_dir)
    if not output_dir.is_absolute():
        output_dir = PROJECT_ROOT / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    ppo_model = PPO.load(str(model_path))
    observation_size = int(ppo_model.observation_space.shape[0])
    if observation_size not in (7, 12, 18):
        raise ValueError(f"Unsupported PPO observation size: {observation_size}. Expected 7, 12, or 18.")
    enhanced_observations = observation_size == 12
    multizone_observations = observation_size == 18

    run_metrics: list[dict] = []
    traces: list[dict] = []
    for scenario_name in scenario_names:
        for run_index in range(arguments.runs):
            seed = arguments.seed + run_index
            controllers = {
                "fixed_power": fixed_controller,
                "pid_temperature": build_pid_controller(normalized_observation=(enhanced_observations or multizone_observations)),
                "ppo": build_ppo_controller(ppo_model),
                "seeded_random": build_random_controller(seed),
            }
            for controller_name, controller in controllers.items():
                metrics, rollout_traces = run_rollout(
                    controller_name,
                    controller,
                    scenario_name,
                    SCENARIOS[scenario_name],
                    enhanced_observations,
                    seed,
                    arguments.steps,
                    multizone_observations=multizone_observations,
                )
                run_metrics.append(metrics)
                traces.extend(rollout_traces)
                print(
                    f"{scenario_name:>19} | Run {run_index + 1:02d}/{arguments.runs:02d} | {controller_name:>15} | "
                    f"yield={metrics['mean_yield_pct']:.2f}% | SEC={metrics['sec_kwh_per_kg']:.2f} kWh/kg | "
                    f"max temp={metrics['max_temperature_c']:.1f}°C | safety violation={metrics['safety_violation']}",
                    flush=True,
                )

    summary = summarize(run_metrics)
    write_csv(output_dir / "per_run_metrics.csv", run_metrics)
    write_csv(output_dir / "telemetry.csv", traces)
    with (output_dir / "summary.json").open("w", encoding="utf-8") as file_handle:
        json.dump(
            {
                "scope": "Simulation-only controller comparison; not evidence of real-furnace performance.",
                "runs_per_controller": arguments.runs,
                "steps_per_rollout": arguments.steps,
                "seed_start": arguments.seed,
                "model_path": str(model_path),
                "enhanced_observations": enhanced_observations,
                "scenarios": {name: SCENARIOS[name] for name in scenario_names},
                "controllers": summary,
            },
            file_handle,
            indent=2,
        )
    write_chart(output_dir / "comparison.png", summary)

    print("Validation complete.")
    for row in summary:
        print(
            f"{row['scenario']:>19} | {row['controller']:>15}: yield={row['mean_yield_pct_mean']:.2f} ± {row['mean_yield_pct_std']:.2f}% | "
            f"SEC={row['sec_kwh_per_kg_mean']:.2f} ± {row['sec_kwh_per_kg_std']:.2f} kWh/kg | "
            f"safety violations={row['safety_violations']}"
        )
    print(f"Results saved to: {output_dir}")


if __name__ == "__main__":
    main()
