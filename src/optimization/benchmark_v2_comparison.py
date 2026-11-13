#!/usr/bin/env python3
"""Comprehensive Benchmark & Comparison: PPO vs SAC vs PID vs Fixed Baseline.

Evaluates trained agents on the recalibrated 18-D Multi-Zone Submerged Arc Furnace (SAF) simulator
across nominal and disturbed operational scenarios, computing realistic industrial KPIs:
- Yield (%)
- Specific Energy Consumption (kWh/kg Si)
- Cost per kg saleable Silicon ($/kg)
- Crater, Bath, and Burden Temperatures (°C)
- SiO Offgas Loss (%)
- Electrical Power Factor (cos phi)
"""

import sys
import os
import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from stable_baselines3 import PPO, SAC

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "env"))
from silicon_env import SiliconEnv

EVAL_SEEDS = [101, 202, 303, 404, 505]
STEPS_PER_RUN = 96  # 24-hour simulation at 15-minute DT

SCENARIOS = {
    "Nominal_Steady": {},
    "Heat_Loss_Disturbance": {"heat_loss_multiplier": 1.25},
    "Grid_Power_Derate": {"power_derate": 0.15},
    "Low_Reactivity_Feed": {"yield_multiplier": 0.90},
    "Sensor_Noise_Thermal": {"sensor_noise_std_c": 15.0},
}

def run_controller_evaluation(controller_fn, scenario_params, multizone=True):
    results = []
    
    for seed in EVAL_SEEDS:
        env = SiliconEnv(
            multizone_observations=multizone,
            reward_mode="economic",
            safety_shield=True,
            domain_randomization=False,
            **scenario_params
        )
        obs, info = env.reset(seed=seed)
        
        episode_reward = 0.0
        yields, sio_losses, crater_temps, bath_temps, burden_temps = [], [], [], [], []
        costs_per_kg, sec_vals, cos_phis = [], [], []
        total_si_tapped_kg = 0.0
        total_energy_mwh = 0.0
        total_cost_usd = 0.0
        safety_trips = 0
        
        for step in range(STEPS_PER_RUN):
            action = controller_fn(obs)
            obs, r, term, trunc, info = env.step(action)
            episode_reward += r
            
            yields.append(info.get("yield_fraction", info.get("liquid_silicon_yield", 0.0)) * 100.0)
            sio_losses.append(info.get("sio_loss_fraction", 0.0) * 100.0)
            crater_temps.append(info.get("temperature_crater_c", info.get("temperature_c", 0.0)))
            bath_temps.append(info.get("temperature_bath_c", 1600.0))
            burden_temps.append(info.get("temperature_burden_c", 1180.0))
            
            cos_phis.append(info.get("power_factor", 0.84))
            
            # Step mass, total saleable production & energy
            si_produced = info.get("saleable_silicon_kg", info.get("mass_si_tapped_kg", 0.0))
            total_si_tapped_kg += si_produced
            
            power_mw = info.get("actual_power_mw", info.get("power_mw", 28.0))
            step_mwh = power_mw * (15.0 / 60.0)
            total_energy_mwh += step_mwh
            
            # Step accounting from env physical cost breakdown
            step_cost = info.get("total_step_cost_usd", (step_mwh * 65.0) + (si_produced * 0.55))
            total_cost_usd += step_cost
            
            if term:
                safety_trips += 1
                break
                
        # Metrics summary for this seed
        overall_yield = np.mean(yields)
        mean_sec = (total_energy_mwh * 1000.0) / max(1.0, total_si_tapped_kg)
        cost_per_kg = total_cost_usd / max(1.0, total_si_tapped_kg)
        
        results.append({
            "seed": seed,
            "total_reward": episode_reward,
            "mean_yield_pct": overall_yield,
            "mean_sio_loss_pct": np.mean(sio_losses),
            "mean_crater_temp_c": np.mean(crater_temps),
            "std_crater_temp_c": np.std(crater_temps),
            "mean_bath_temp_c": np.mean(bath_temps),
            "mean_burden_temp_c": np.mean(burden_temps),
            "sec_kwh_per_kg": mean_sec,
            "cost_per_kg_si_usd": cost_per_kg,
            "mean_cos_phi": np.mean(cos_phis),
            "total_si_tapped_kg": total_si_tapped_kg,
            "safety_trips": safety_trips
        })
        
    return results

def main():
    print("=" * 80)
    print("SILICAFORGE-RL v2.0: MULTI-CONTROLLER INDUSTRIAL BENCHMARK (PPO vs SAC vs PID vs Fixed)")
    print("=" * 80)
    
    # 1. Load trained models
    ppo_path = PROJECT_ROOT / "models" / "best_ppo" / "best_model.zip"
    sac_path = PROJECT_ROOT / "models" / "best_sac" / "best_model.zip"
    
    if not ppo_path.exists():
        ppo_path = PROJECT_ROOT / "models" / "ppo_v2_final.zip"
    if not sac_path.exists():
        sac_path = PROJECT_ROOT / "models" / "sac_v2_final.zip"
        
    print(f"Loading PPO: {ppo_path}")
    ppo_model = PPO.load(str(ppo_path), device="cpu")
    print(f"Loading SAC: {sac_path}")
    sac_model = SAC.load(str(sac_path), device="cpu")
    
    controllers = {
        "PPO_v2": lambda o: ppo_model.predict(o, deterministic=True)[0],
        "SAC_v2": lambda o: sac_model.predict(o, deterministic=True)[0],
        "Industrial_PID": lambda o: np.array([
            float(np.clip((1880.0 - (o[1] * 2500.0 if len(o) == 18 else o[0] * 2500.0)) * 0.05, -1.0, 1.0)),
            0.0,
            0.0
        ], dtype=np.float32),
        "Fixed_Baseline": lambda o: np.array([(28.5 / 30.0) * 2.0 - 1.0, 0.0, 0.0], dtype=np.float32),
    }
    
    full_report = {}
    
    for scen_name, scen_params in SCENARIOS.items():
        print(f"\n---> Evaluating Scenario: {scen_name} across 5 seeds...")
        full_report[scen_name] = {}
        
        for c_name, c_fn in controllers.items():
            res = run_controller_evaluation(c_fn, scen_params)
            
            # Aggregate over 5 seeds
            agg = {
                "reward_mean": float(np.mean([r["total_reward"] for r in res])),
                "reward_std": float(np.std([r["total_reward"] for r in res])),
                "yield_pct_mean": float(np.mean([r["mean_yield_pct"] for r in res])),
                "yield_pct_std": float(np.std([r["mean_yield_pct"] for r in res])),
                "sio_loss_pct_mean": float(np.mean([r["mean_sio_loss_pct"] for r in res])),
                "sec_kwh_per_kg_mean": float(np.mean([r["sec_kwh_per_kg"] for r in res])),
                "cost_per_kg_usd_mean": float(np.mean([r["cost_per_kg_si_usd"] for r in res])),
                "crater_temp_mean": float(np.mean([r["mean_crater_temp_c"] for r in res])),
                "crater_temp_std": float(np.mean([r["std_crater_temp_c"] for r in res])),
                "cos_phi_mean": float(np.mean([r["mean_cos_phi"] for r in res])),
                "total_si_tapped_kg_mean": float(np.mean([r["total_si_tapped_kg"] for r in res])),
                "safety_trips_total": int(np.sum([r["safety_trips"] for r in res]))
            }
            full_report[scen_name][c_name] = agg
            print(f"  {c_name:<16} | Reward: {agg['reward_mean']:>8.1f} | Yield: {agg['yield_pct_mean']:>5.2f}% | SEC: {agg['sec_kwh_per_kg_mean']:>5.2f} kWh/kg | Cost: ${agg['cost_per_kg_usd_mean']:>5.2f}/kg")

    # Save JSON report
    report_path = PROJECT_ROOT / "data" / "validation" / "ppo_vs_sac_benchmark_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(full_report, f, indent=2)
    print(f"\n[DONE] Saved benchmark JSON to: {report_path}")
    
    # Generate Comparison Plot
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    scenarios = list(SCENARIOS.keys())
    ctrl_names = list(controllers.keys())
    colors = ["#2563eb", "#10b981", "#f59e0b", "#6b7280"]
    x = np.arange(len(scenarios))
    width = 0.2
    
    # 1. Silicon Yield
    ax1 = axes[0, 0]
    for i, c_name in enumerate(ctrl_names):
        vals = [full_report[s][c_name]["yield_pct_mean"] for s in scenarios]
        errs = [full_report[s][c_name]["yield_pct_std"] for s in scenarios]
        ax1.bar(x + i*width - 1.5*width, vals, width, yerr=errs, capsize=3, label=c_name, color=colors[i])
    ax1.set_title("Silicon Recovery Yield (%) - Higher is Better")
    ax1.set_ylabel("Yield (%)")
    ax1.set_xticks(x)
    ax1.set_xticklabels([s.replace("_", "\n") for s in scenarios], fontsize=8)
    ax1.set_ylim(70, 95)
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.legend(loc="lower left", fontsize=8)

    # 2. Production Cost ($/kg Si)
    ax2 = axes[0, 1]
    for i, c_name in enumerate(ctrl_names):
        vals = [full_report[s][c_name]["cost_per_kg_usd_mean"] for s in scenarios]
        ax2.bar(x + i*width - 1.5*width, vals, width, label=c_name, color=colors[i])
    ax2.set_title("Production Cost ($/kg Si) - Lower is Better")
    ax2.set_ylabel("USD / kg")
    ax2.set_xticks(x)
    ax2.set_xticklabels([s.replace("_", "\n") for s in scenarios], fontsize=8)
    ax2.set_ylim(1.0, 3.5)
    ax2.grid(True, linestyle="--", alpha=0.5)

    # 3. Specific Energy Consumption (SEC, kWh/kg)
    ax3 = axes[1, 0]
    for i, c_name in enumerate(ctrl_names):
        vals = [full_report[s][c_name]["sec_kwh_per_kg_mean"] for s in scenarios]
        ax3.bar(x + i*width - 1.5*width, vals, width, label=c_name, color=colors[i])
    ax3.set_title("Specific Energy Consumption (kWh/kg Si) - Lower is Better")
    ax3.set_ylabel("kWh / kg")
    ax3.set_xticks(x)
    ax3.set_xticklabels([s.replace("_", "\n") for s in scenarios], fontsize=8)
    ax3.grid(True, linestyle="--", alpha=0.5)

    # 4. Total Episode Reward
    ax4 = axes[1, 1]
    for i, c_name in enumerate(ctrl_names):
        vals = [full_report[s][c_name]["reward_mean"] for s in scenarios]
        ax4.bar(x + i*width - 1.5*width, vals, width, label=c_name, color=colors[i])
    ax4.set_title("Cumulative Multi-Objective Reward")
    ax4.set_ylabel("Episode Reward")
    ax4.set_xticks(x)
    ax4.set_xticklabels([s.replace("_", "\n") for s in scenarios], fontsize=8)
    ax4.grid(True, linestyle="--", alpha=0.5)

    plt.suptitle("SilicaForge-RL v2.0: Industrial Controller Comparison (PPO vs SAC vs Baselines)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    
    chart_path = PROJECT_ROOT / "data" / "validation" / "ppo_vs_sac_comparison.png"
    plt.savefig(chart_path, dpi=200)
    plt.close()
    print(f"[DONE] Saved comparison chart to: {chart_path}")

if __name__ == "__main__":
    main()
