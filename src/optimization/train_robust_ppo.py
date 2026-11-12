#!/usr/bin/env python3
"""Train a safety-shielded PPO policy under randomized furnace disturbances."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from stable_baselines3.common.env_util import make_vec_env


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "env"))

from silicon_env import SiliconEnv


def build_training_env(seed: int):
    return make_vec_env(
        lambda: SiliconEnv(
            enhanced_observations=True,
            domain_randomization=True,
            safety_shield=True,
        ),
        n_envs=1,
        seed=seed,
    )


def build_evaluation_env(seed: int):
    return make_vec_env(
        lambda: SiliconEnv(
            enhanced_observations=True,
            safety_shield=True,
        ),
        n_envs=1,
        seed=seed,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Train robust, safety-shielded PPO for SilicaForge-RL.")
    parser.add_argument("--timesteps", type=int, default=500_000, help="Training transitions (default: 500000).")
    parser.add_argument("--seed", type=int, default=2026, help="Training seed (default: 2026).")
    arguments = parser.parse_args()
    if arguments.timesteps < 1:
        parser.error("--timesteps must be positive.")

    model_dir = PROJECT_ROOT / "models"
    log_dir = PROJECT_ROOT / "logs" / "robust_ppo"
    model_dir.mkdir(exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    training_env = build_training_env(arguments.seed)
    evaluation_env = build_evaluation_env(arguments.seed + 10_000)

    checkpoint_callback = CheckpointCallback(
        save_freq=25_000,
        save_path=str(log_dir),
        name_prefix="robust_ppo_checkpoint",
    )
    evaluation_callback = EvalCallback(
        evaluation_env,
        best_model_save_path=str(model_dir),
        log_path=str(log_dir),
        eval_freq=25_000,
        n_eval_episodes=10,
        deterministic=True,
    )

    model = PPO(
        "MlpPolicy",
        training_env,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=128,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        ent_coef=0.01,
        verbose=1,
        tensorboard_log=str(log_dir),
        seed=arguments.seed,
        device="cpu",
    )
    print(f"Training robust PPO for {arguments.timesteps:,} timesteps.")
    model.learn(total_timesteps=arguments.timesteps, callback=[checkpoint_callback, evaluation_callback])
    model.save(str(model_dir / "robust_ppo_model"))
    training_env.close()
    evaluation_env.close()
    print(f"Saved model: {model_dir / 'robust_ppo_model.zip'}")


if __name__ == "__main__":
    main()
