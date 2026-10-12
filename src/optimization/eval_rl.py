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
    
    # Run for a full episode (50 steps)
    for step in range(50):
        # AI decides the best action
        action, _states = model.predict(state, deterministic=True)
        
        # Take the action in the environment
        state, reward, terminated, truncated, info = env.step(action)
        
        # We need to un-normalize the state just for printing
        real_temp = (state[0] * 1200.0) + 1000.0
        real_press = (state[1] * 9.9) + 0.1
        real_argon = state[2] * 5.0
        si_yield = state[3]
        cost = info['cost'] # Info contains the raw cost
        
        print(f"Step {step+1}: Action Taken -> Temp={real_temp:.0f}°C | Press={real_press:.2f}atm | Ar={real_argon:.2f}L/m")
        print(f"         Result -> Yield: {si_yield:.4f} moles | Cost: ₹{cost:.2f} | Reward: {reward:.2f}")
        print("-" * 60)
        
        if terminated or truncated:
            print("Episode Finished!")
            break

if __name__ == "__main__":
    evaluate_agent()
