import os
import sys
import numpy as np
from stable_baselines3 import PPO

# Add required paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'env'))
from silicon_env import SiliconEnv

def evaluate_model():
    env = SiliconEnv()
    model_path = os.path.join(os.path.dirname(__file__), '..', '..', 'best_model.zip')
    
    if not os.path.exists(model_path):
        print(f"Error: Could not find {model_path}")
        return
        
    print(f"Loading model from {model_path}...")
    model = PPO.load(model_path)
    
    obs, _ = env.reset()
    
    total_reward = 0
    total_yield = 0
    total_sio_lost = 0
    total_cost = 0
    steps = 100
    
    print("\n--- Running Evaluation Episode ---")
    for step in range(steps):
        action, _states = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        
        total_reward += reward
        total_yield += info['yield']
        total_sio_lost += info['sio_lost']
        total_cost += info['cost']
        
        # We know action is either scaled physically or -1 to +1. Let's see what the environment scaled it to.
        # Actually, let's just print every 20 steps
        if step % 20 == 0 or step == steps - 1:
            print(f"Step {step}: Reward: {reward:.2f}, Yield: {info['yield']*100:.2f}%, Cost: ${info['cost']:.2f}")
            
        if terminated or truncated:
            break
            
    print("\n--- Final Results ---")
    print(f"Average Reward per step: {total_reward/steps:.2f}")
    print(f"Average Yield: {(total_yield/steps)*100:.2f}%")
    print(f"Average SiO Gas Lost: {(total_sio_lost/steps)*100:.2f}%")
    print(f"Average Operating Cost: ${total_cost/steps:.2f}")
    
    if (total_yield/steps)*100 > 50.0:
        print("\nCONCLUSION: EXCELLENT MODEL! The agent found the optimal sweet spot!")
    elif (total_yield/steps)*100 == 0.0:
        print("\nCONCLUSION: BAD MODEL! The agent is still 'lazy' and shutting down the furnace.")
    else:
        print("\nCONCLUSION: OKAY MODEL. The agent is producing some Silicon, but not optimal.")

if __name__ == "__main__":
    evaluate_model()
