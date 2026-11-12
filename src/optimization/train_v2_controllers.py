#!/usr/bin/env python3
"""
SilicaForge-RL v2.0 Controller Training Pipeline:
Supports PPO and SAC (Soft Actor-Critic) on the 18-D Multi-Zone Physical Simulator
with Economic Cost-per-kg Optimization and Safety-Shielded Actuator Interlocks.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import torch
from stable_baselines3 import PPO, SAC
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from stable_baselines3.common.env_util import make_vec_env


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "env"))

from silicon_env import SiliconEnv


def build_env(seed: int, domain_randomization: bool = True, multizone: bool = True):
    return make_vec_env(
        lambda: SiliconEnv(
            enhanced_observations=True,
            multizone_observations=multizone,
            domain_randomization=domain_randomization,
            safety_shield=True,
            reward_mode="economic",
        ),
        n_envs=1,
        seed=seed,
    )


def train(
    algo: str = "ppo",
    timesteps: int = 200_000,
    seed: int = 42,
    device: str = "auto",
    multizone: bool = True,
):
    print("=" * 90)
    print(f"SILICAFORGE-RL v2.0: Training {algo.upper()} Controller on Multi-Zone SAF Simulator")
    print(f"Algorithm: {algo.upper()} | Observation: {'18-D Multi-Zone' if multizone else '12-D'} | Steps: {timesteps:,}")
    print(f"Reward Mode: Economic Production Cost ($/kg Saleable Si) | Safety Shield: ACTIVE")
    print("=" * 90)

    model_dir = PROJECT_ROOT / "models"
    log_dir = PROJECT_ROOT / "logs" / f"v2_{algo.lower()}"
    model_dir.mkdir(exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    training_env = build_env(seed=seed, domain_randomization=True, multizone=multizone)
    eval_env = build_env(seed=seed + 999, domain_randomization=False, multizone=multizone)

    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=str(model_dir / f"best_{algo.lower()}"),
        log_path=str(log_dir),
        eval_freq=max(5_000, timesteps // 20),
        n_eval_episodes=5,
        deterministic=True,
        render=False,
    )

    checkpoint_callback = CheckpointCallback(
        save_freq=max(10_000, timesteps // 5),
        save_path=str(model_dir / f"checkpoints_{algo.lower()}"),
        name_prefix=f"{algo.lower()}_v2_checkpoint",
    )

    if algo.lower() == "sac":
        # SAC configuration optimized for continuous industrial process control
        model = SAC(
            "MlpPolicy",
            training_env,
            learning_rate=3e-4,
            buffer_size=100_000,
            learning_starts=1_000,
            batch_size=256,
            tau=0.01,
            gamma=0.99,
            train_freq=1,
            gradient_steps=1,
            ent_coef="auto",
            seed=seed,
            device=device,
            verbose=1,
            tensorboard_log=str(log_dir),
        )
    elif algo.lower() == "ppo":
        # PPO configuration for bounded industrial control
        model = PPO(
            "MlpPolicy",
            training_env,
            learning_rate=3e-4,
            n_steps=2048,
            batch_size=64,
            n_epochs=10,
            gamma=0.99,
            gae_lambda=0.95,
            clip_range=0.2,
            ent_coef=0.005,
            seed=seed,
            device=device,
            verbose=1,
            tensorboard_log=str(log_dir),
        )
    else:
        raise ValueError(f"Unknown algorithm '{algo}'. Supported: 'ppo', 'sac'.")

    model.learn(
        total_timesteps=timesteps,
        callback=[checkpoint_callback, eval_callback],
        progress_bar=False,
    )

    final_model_path = model_dir / f"{algo.lower()}_v2_final.zip"
    model.save(str(final_model_path))
    print(f"\n[DONE] Training complete. Final model saved to: {final_model_path}")
    return final_model_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SilicaForge-RL v2 Controller Training.")
    parser.add_argument("--algo", type=str, choices=["ppo", "sac"], default="ppo", help="Algorithm: ppo or sac")
    parser.add_argument("--timesteps", type=int, default=100_000, help="Total training timesteps (default: 100,000)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument("--device", type=str, default="auto", help="Compute device: auto, cpu, cuda")
    parser.add_argument("--legacy-obs", action="store_true", help="Use legacy observation instead of 18-D multi-zone")

    args = parser.parse_args()
    train(
        algo=args.algo,
        timesteps=args.timesteps,
        seed=args.seed,
        device=args.device,
        multizone=not args.legacy_obs,
    )
