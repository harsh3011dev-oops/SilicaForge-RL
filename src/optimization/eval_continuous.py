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
            writer.writerow(['Episode', 'Step', 'Temperature_C', 'Power_MW', 'C_Si_Ratio', 'Electrode_Delta', 'Yield_Pct', 'SiO_Loss_Pct', 'Cost_USD_hr', 'Reward'])

    print(f"\n--- Starting Continuous Evaluation ---")
    print(f"Logging 'Good Discoveries' (Yield > 88% or High Reward) to {csv_file}\n")
    
    episode = 1
    best_reward_ever = -99999.0
    
    while True:
        state, _ = env.reset()
        print(f"--- Starting Episode {episode} ---")
        
        for step in range(env.max_steps_per_episode):
            # Inject some exploratory actions 5% of the time
            import random
            if random.random() < 0.05:
                action = env.action_space.sample()
            else:
                action, _states = model.predict(state, deterministic=False)
            
            state, reward, terminated, truncated, info = env.step(action)
            
            # Extract real physical furnace parameters
            temp_c = float(info['temperature_c'])
            power_mw = (float(action[0]) * 0.5 + 0.5) * env.MAX_POWER_MW
            electrode_delta = float(action[1])
            c_si_ratio = float(action[2]) * 0.2 + 2.0
            yield_pct = float(info['liquid_silicon_yield']) * 100.0
            sio_loss_pct = float(info['sio_loss_fraction']) * 100.0
            cost_usd = float(info['electricity_cost_per_hr'])
            
            # THE "GOOD DISCOVERY" LOGIC:
            if yield_pct > 88.0 or reward > best_reward_ever:
                if reward > best_reward_ever:
                    best_reward_ever = reward
                    
                print(f"\n🌟 BREAKTHROUGH! Ep {episode} Step {step+1}: Temp={temp_c:.1f}°C | Power={power_mw:.1f}MW | C/Si={c_si_ratio:.3f} | Yield={yield_pct:.2f}% | Reward={reward:.2f}")
                
                # Save to CSV
                with open(csv_file, mode='a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([episode, step+1, round(temp_c, 2), round(power_mw, 2), round(c_si_ratio, 3), round(electrode_delta, 2), round(yield_pct, 2), round(sio_loss_pct, 2), round(cost_usd, 2), round(reward, 2)])
            
            # Print a small dot to show it's running
            print(".", end="", flush=True)
            time.sleep(0.005)
            
            if terminated or truncated:
                print(f" (Done! Final Temp: {temp_c:.1f}°C | Yield: {yield_pct:.2f}% | Reward: {reward:.2f})")
                break
                
        episode += 1

if __name__ == "__main__":
    try:
        run_continuous_evaluation()
    except KeyboardInterrupt:
        print("\nStopped by user.")
