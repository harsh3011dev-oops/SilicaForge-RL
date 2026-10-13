import os
import sys
from stable_baselines3 import PPO

# Add required paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'env'))
from silicon_env import SiliconEnv

def evaluate_agent():
    model_path = os.path.join(os.path.dirname(__file__), '..', '..', 'best_model.zip')
    if not os.path.exists(model_path):
        print("Model not found! Train it first.")
        return

    print("Loading Trained AI Agent...")
    model = PPO.load(model_path)
    env = SiliconEnv()
    
    print("\n--- Starting Evaluation Episode ---")
    state, _ = env.reset()
    
    # Run for a full episode (96 steps / 24 hours)
    for step in range(env.max_steps_per_episode):
        # AI decides the best action
        action, _states = model.predict(state, deterministic=True)
        
        # Take the action in the environment
        state, reward, terminated, truncated, info = env.step(action)
        
        # Action breakdown
        power_mw = (float(action[0]) * 0.5 + 0.5) * env.MAX_POWER_MW
        electrode_delta = float(action[1])
        c_si_ratio = float(action[2]) * 0.2 + 2.0
        
        # Physical observation results from info dict
        temp_c = float(info['temperature_c'])
        si_yield = float(info['liquid_silicon_yield']) * 100.0
        sio_loss = float(info['sio_loss_fraction']) * 100.0
        cost_usd = float(info['electricity_cost_per_hr'])
        
        print(f"Step {step+1:02d} [Hour {(step+1)*0.25:4.2f}]: Power={power_mw:5.2f} MW | ElecDelta={electrode_delta:+5.2f} | C/Si={c_si_ratio:.3f}")
        print(f"         Response   -> Temp={temp_c:6.1f}°C | Yield={si_yield:5.2f}% | SiO Loss={sio_loss:4.2f}% | Cost=${cost_usd:7.2f}/hr | Reward={reward:+6.2f}")
        print("-" * 88)
        
        if terminated or truncated:
            print(f"\nEpisode Finished after {step+1} steps! Final Temp: {temp_c:.1f}°C | Final Yield: {si_yield:.2f}%")
            break

if __name__ == "__main__":
    evaluate_agent()
