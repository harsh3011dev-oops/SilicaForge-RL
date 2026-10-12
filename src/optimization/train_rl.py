import os
import sys
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import EvalCallback, CheckpointCallback, BaseCallback

class CurriculumCostCallback(BaseCallback):
    """Synchronizes curriculum episode count and logs metrics to TensorBoard."""
    def __init__(self, verbose=0):
        super().__init__(verbose)
        self.episodes_completed = 0

    def _on_step(self) -> bool:
        dones = self.locals.get("dones")
        if dones is not None and any(dones):
            self.episodes_completed += sum(dones)
            env = self.training_env.envs[0].unwrapped
            env.current_episode = self.episodes_completed
            
            infos = self.locals.get("infos")
            if infos and len(infos) > 0 and "liquid_silicon_yield" in infos[0]:
                self.logger.record("metallurgy/silicon_yield", infos[0]["liquid_silicon_yield"])
                self.logger.record("metallurgy/temperature_c", infos[0]["temperature_c"])
                self.logger.record("curriculum/lambda_cost", infos[0]["lambda_cost_current"])
                self.logger.record("curriculum/action_delta", infos[0]["action_delta"])
        return True

# Add required paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'env'))
from silicon_env import SiliconEnv

def train_agent():
    print("Initializing the PBRS Silicon RL Environment...")
    env = make_vec_env(lambda: SiliconEnv(), n_envs=1)
    eval_env = make_vec_env(lambda: SiliconEnv(), n_envs=1)
    
    # Setup directories for checkpoints and logging
    log_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Auto-Resume Logic: Check if a previous model exists
    best_model_path = os.path.join(os.path.dirname(__file__), '..', '..', 'best_model.zip')
    if os.path.exists(best_model_path):
        print(f"🔄 Found existing model at {best_model_path}!")
        print("RESUMING training from where it left off (You can safely stop and start anytime)...")
        model = PPO.load(best_model_path, env=env, tensorboard_log=log_dir)
    else:
        print("Setting up a NEW PPO Agent with high Curiosity...")
        model = PPO(
            "MlpPolicy", 
            env, 
            verbose=1,
            learning_rate=0.0003,
            n_steps=2048,
            batch_size=64,
            n_epochs=10,
            gamma=0.99,
            ent_coef=0.01, # Increased exploration (Curiosity)
            tensorboard_log=log_dir
        )
    
    # Save a checkpoint every 5000 steps
    checkpoint_callback = CheckpointCallback(
        save_freq=5000,
        save_path=log_dir,
        name_prefix="ppo_silicon_milestone"
    )
    
    # Evaluate the model every 5000 steps and strictly save the absolute best one
    eval_callback = EvalCallback(
        eval_env, 
        best_model_save_path=os.path.join(os.path.dirname(__file__), '..', '..'),
        log_path=log_dir, 
        eval_freq=5000,
        deterministic=True, 
        render=False
    )
    
    # Curriculum callback
    curriculum_callback = CurriculumCostCallback()
    
    # The user wants 1 Crore STEPS (not episodes) which is about 1,04,166 episodes.
    total_steps = 10_000_000 # 1 Crore Steps
    target_episodes = total_steps // 96
    
    print(f"Starting God-Mode Training for {target_episodes:,} EPISODES ({total_steps:,} steps). This will take about 2.5 hours...")
    try:
        model.learn(total_timesteps=total_steps, callback=[checkpoint_callback, eval_callback, curriculum_callback], reset_num_timesteps=False)
        print("Training Complete! Best model saved automatically as best_model.zip")
    except KeyboardInterrupt:
        print("\n⚠️ Training stopped by user (Ctrl+C). Saving current progress...")
        model.save(os.path.join(os.path.dirname(__file__), '..', '..', 'best_model.zip'))
        print("✅ Progress safely saved! You can resume from this exact point on Monday.")

if __name__ == "__main__":
    train_agent()
