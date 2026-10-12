import os
import sys
import csv
import time
from stable_baselines3 import PPO

# Add required paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'env'))
from silicon_env import SiliconEnv

def run_continuous_evaluation():
    model_path = os.path.join(os.path.dirname(__file__), '..', '..', 'best_model.zip')
    if not os.path.exists(model_path):
        print("Model not found! Train it first.")
        return

    print("Loading AI Agent for Continuous Operation...")
    model = PPO.load(model_path)
    env = SiliconEnv()
    
    csv_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'best_discoveries.csv')
    
    # Create CSV file with headers if it doesn't exist
    file_exists = os.path.exists(csv_file)
    with open(csv_file, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Episode', 'Step', 'Temperature_C', 'Pressure_atm', 'Argon_Flow', 'Si_Yield_moles', 'Cost_INR', 'Reward'])

    print(f"\n--- Starting Infinite Evaluation ---")
    print(f"Logging 'Good Discoveries' (High Yield or Reward) to {csv_file}\n")
    
    episode = 1
    best_reward_ever = -99999.0
    
    while True:
        state, _ = env.reset()
        print(f"--- Starting Episode {episode} ---")
        
        for step in range(env.max_steps):
            # Inject some completely random actions 10% of the time to force it to discover high temperatures
            import random
            if random.random() < 0.10:
                action = env.action_space.sample()
            else:
                action, _states = model.predict(state, deterministic=False)
            
            state, reward, terminated, truncated, info = env.step(action)
            
            real_temp = (state[0] * 1200.0) + 1000.0
            real_press = (state[1] * 9.9) + 0.1
            real_argon = state[2] * 5.0
            si_yield = state[3]
            cost = info['cost']
            
            # THE "GOOD CHANGE" LOGIC:
            if si_yield > 0.05 or reward > best_reward_ever:
                if reward > best_reward_ever:
                    best_reward_ever = reward
                    
                print(f"\n🌟 BREAKTHROUGH! Ep {episode} Step {step+1}: Temp={real_temp:.0f}C | Yield={si_yield:.4f} | Reward={reward:.2f}")
                
                # Save to CSV
                with open(csv_file, mode='a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([episode, step+1, round(real_temp, 2), round(real_press, 2), round(real_argon, 2), round(si_yield, 4), round(cost, 2), round(reward, 2)])
            
            # Print a small dot to show it's running
            print(".", end="", flush=True)
            time.sleep(0.01) # Speed it up slightly
            
            if terminated or truncated:
                print(f" (Done! Final Temp: {real_temp:.0f}C | Yield: {si_yield:.4f} | Reward: {reward:.2f})")
                break
                
        episode += 1

if __name__ == "__main__":
    try:
        run_continuous_evaluation()
    except KeyboardInterrupt:
        print("\nStopped by user.")
