"""
Carbothermic Reduction PPO Agent (PyTorch Gymnasium Environment)
Simulates SiO2 + 2C -> Si + 2CO furnace optimization.
"""
import numpy as np

class SilicaFurnaceEnv:
    def __init__(self):
        # Action space: [Target Temp (1000-2200), Pressure (0.1-10.0), Argon Flow (0.0-5.0)]
        self.state = np.array([1400.0, 1.0, 1.0])
        
    def step(self, action):
        temp, press, ar_flow = action
        # Kinetic yield calculation
        raw_yield = max(0.0, min(1.0, (temp - 1500) / 360)) if temp <= 1860 else max(0.1, 1.0 - (temp - 1860) / 300)
        gas_loss = ((temp / 2000) ** 3) * (1.0 / (press ** 0.5)) * (0.8 + ar_flow / 5.0) if temp > 1650 else 0.0
        cost_rate = 50 + 220 * ((temp / 1800) ** 3.8) + (press * 8) + (ar_flow * 4)
        
        # Reward formulation for PPO
        reward = (raw_yield * 1.6) - (gas_loss * 1.3) - ((cost_rate / 8000) * 0.9)
        return self.state, reward, False, {}
