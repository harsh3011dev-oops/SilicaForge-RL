import numpy as np
import gymnasium as gym
from gymnasium import spaces

class SilicaSmeltingEnv(gym.Env):
    """
    Submerged Electric Arc Furnace (SAF) Environment for Carbothermic Silica Reduction:
    SiO2(s, l) + 2C(s) -> Si(l) + 2CO(g)
    
    Includes multi-zone intermediate thermodynamics, Dynamic Curriculum Annealing,
    Thermal Inertia, and a Non-Linear Cubic Reward Surface.
    """
    metadata = {"render_modes": ["human"]}

    def __init__(self):
        super().__init__()
        
        # State: [Temperature (°C), SiO2 burden (kg), C burden (kg), 
        #         Liquid Si Yield, SiO Loss, Prev Power Action, Energy MWh]
        self.observation_space = spaces.Box(
            low=np.array([25.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], dtype=np.float32),
            high=np.array([2500.0, 50000.0, 30000.0, 1.0, 1.0, 1.0, 500.0], dtype=np.float32)
        )
        
        # Action: [Normalized Power (0 to 1 -> 0 to 30 MW), Electrode Delta (-1 to 1), C/Si Ratio (1.8 to 2.2)]
        self.action_space = spaces.Box(
            low=np.array([-1.0, -1.0, -1.0], dtype=np.float32), # Use [-1, 1] for stable-baselines3 compatibility
            high=np.array([1.0, 1.0, 1.0], dtype=np.float32)
        )
        
        # Physical & Economic Constants
        self.MAX_POWER_MW = 30.0
        self.ELECTRICITY_PRICE_PER_MWH = 65.0  # USD/MWh
        self.OPTIMAL_TEMP_C = 1865.0
        self.TARGET_YIELD = 0.95
        self.SIO_LOSS_THRESHOLD = 0.02
        self.THERMAL_CAPACITY_GJ_PER_C = 24.5  # Heavy furnace lining thermal inertia
        self.DT_SECONDS = 900.0                # 15 minutes per control step
        
        # Curriculum Hyperparameters
        self.current_episode = 0
        self.warmup_episodes = 500  # Give it 50,000 steps of pure yield focus before cost penalty hits!
        self.annealing_episodes = 1500
        self.lambda_cost_max = 0.045
        self.lambda_cost_min = 0.0005
        self.action_smoothness_weight = 0.12   # beta penalty on (a_t - a_{t-1})^2
        self.yield_exponent = 3.0              # Cubic steepening
        self.gamma = 0.99                      # PBRS discount factor
        
        # Internal state
        self.temperature = 1000.0
        self.prev_action_power = 0.5
        self.prev_potential = 0.0
        self.step_count = 0
        self.max_steps_per_episode = 96        # 24 hours (96 * 15 min)

    def _clausius_clapeyron_sio_pressure(self, temp_c):
        """Equilibrium SiO vapor pressure: log10(P_SiO [atm]) = 8.52 - 18400 / T_K"""
        temp_k = temp_c + 273.15
        if temp_k < 1200:
            return 0.0001
        log10_p = 8.52 - (18400.0 / temp_k)
        return max(1e-4, 10.0 ** log10_p)

    def _compute_thermodynamic_yield_and_loss(self, temp_c, c_si_ratio):
        """Multi-zone thermodynamic equilibrium for Liquid Silicon yield & SiO loss."""
        if temp_c < 1414.0:
            return 0.0, 0.001
        
        ratio_eff = np.exp(-((c_si_ratio - 2.0) ** 2) / 0.08)
        p_sio = self._clausius_clapeyron_sio_pressure(temp_c)
        
        # 1. Liquid Silicon Yield
        if temp_c <= 1700.0:
            norm_t = (temp_c - 1414.0) / (1700.0 - 1414.0)
            yield_val = 0.17 * (norm_t ** 1.8) * ratio_eff
        elif temp_c <= 1865.0:
            norm_t = (temp_c - 1700.0) / (1865.0 - 1700.0)
            sigmoid_climb = 1.0 / (1.0 + np.exp(-6.5 * (norm_t - 0.55)))
            yield_val = (0.17 + (0.94 - 0.17) * sigmoid_climb) * ratio_eff
        elif temp_c <= 1940.0:
            over_t = (temp_c - 1865.0) / (1940.0 - 1865.0)
            yield_val = (0.94 + 0.015 * np.sin(over_t * np.pi) - 0.03 * over_t) * ratio_eff
        else:
            excess = temp_c - 1940.0
            yield_val = (0.91 * np.exp(-excess / 95.0)) * ratio_eff
            
        yield_fraction = float(np.clip(yield_val, 0.0, 0.955))
        
        # 2. SiO Offgas Loss Fraction
        if temp_c < 1650.0:
            sio_loss = 0.002
        else:
            sio_loss = 0.002 + 0.022 * ((p_sio / 0.85) ** 2.4)
        sio_loss = float(np.clip(sio_loss, 0.001, 1.0))
        
        return yield_fraction, sio_loss

    def _calculate_potential_phi(self, temp_c, yield_fraction, sio_loss):
        """PBRS Potential Function Phi(s) strictly preserving optimal policy invariance."""
        yield_term = 15.0 * (yield_fraction ** 2.0)
        sio_loss_term = -25.0 * ((sio_loss / self.SIO_LOSS_THRESHOLD) ** 2.0)
        temp_deviation = (temp_c - self.OPTIMAL_TEMP_C) / 100.0
        temp_term = -3.0 * (temp_deviation ** 2.0)
        return float(yield_term + sio_loss_term + temp_term)

    def _get_dynamic_cost_weight(self):
        """Curriculum Annealing: Cosine schedule from lambda_min to lambda_max."""
        if self.current_episode <= self.warmup_episodes:
            return self.lambda_cost_min
        
        progress = min(1.0, (self.current_episode - self.warmup_episodes) / float(max(1, self.annealing_episodes)))
        cosine_factor = 0.5 * (1.0 - np.cos(np.pi * progress))
        lambda_t = self.lambda_cost_min + (self.lambda_cost_max - self.lambda_cost_min) * cosine_factor
        return float(lambda_t)

    def step(self, action):
        """
        Executes one step with Thermal Inertia, Non-Linear Composite Reward,
        Action Slew Damping, and Curriculum Cost Annealing.
        """
        self.step_count += 1
        
        # Unpack normalized continuous action [-1, 1] and scale to physics bounds
        action = np.clip(action, -1.0, 1.0)
        target_power_norm = float(action[0]) * 0.5 + 0.5  # [-1, 1] -> [0.0, 1.0]
        electrode_delta = float(action[1])                # [-1, 1] -> [-1.0, 1.0]
        c_si_ratio = float(action[2]) * 0.2 + 2.0         # [-1, 1] -> [1.8, 2.2]
        
        power_mw = target_power_norm * self.MAX_POWER_MW
        
        # 1. Thermal Inertia Integration (1st-Order ODE)
        delta_t = self.temperature - 25.0
        # Reduced radiation coefficient by 100x because a Submerged Arc Furnace is insulated by the burden
        q_loss_mw = 3.2 + 0.0078 * delta_t + 2.8e-14 * ((self.temperature + 273.15) ** 4.0)
        current_yield, _ = self._compute_thermodynamic_yield_and_loss(self.temperature, c_si_ratio)
        q_reaction_mw = 6.5 * current_yield if current_yield > 0.1 else 1.2
        
        net_thermal_mw = (power_mw * 0.88) - q_loss_mw - q_reaction_mw
        rate_deg_per_sec = net_thermal_mw / self.THERMAL_CAPACITY_GJ_PER_C
        
        prev_temp = self.temperature
        self.temperature = float(np.clip(prev_temp + rate_deg_per_sec * self.DT_SECONDS, 25.0, 2300.0))
        
        # 2. Thermodynamic Evaluation
        next_yield, sio_loss = self._compute_thermodynamic_yield_and_loss(self.temperature, c_si_ratio)
        
        # 3. COMPOSITE NON-LINEAR REWARD CALCULATION
        # (A) Cubic Yield Pull:
        yield_ratio = next_yield / self.TARGET_YIELD
        r_yield = 20.0 * (yield_ratio ** self.yield_exponent)
        
        # (B) SiO Offgas Barrier Penalty:
        r_sio_loss = 0.0
        if sio_loss > self.SIO_LOSS_THRESHOLD:
            excess = (sio_loss - self.SIO_LOSS_THRESHOLD) / 0.05
            r_sio_loss = -15.0 * (excess ** 2.0)
            
        # (C) Dynamic Curriculum Cost Penalty with Sigmoid Yield Gating:
        lambda_cost = self._get_dynamic_cost_weight()
        cost_usd_hr = power_mw * self.ELECTRICITY_PRICE_PER_MWH
        normalized_cost = cost_usd_hr / 1000.0
        yield_gate = 1.0 / (1.0 + np.exp(-12.0 * (next_yield - 0.22)))
        r_cost = -lambda_cost * normalized_cost * yield_gate * 10.0
        
        # (D) Action Smoothing / Residual Slew-Rate Penalty:
        action_delta = abs(target_power_norm - self.prev_action_power)
        r_smooth = -self.action_smoothness_weight * (action_delta ** 2.0)
        self.prev_action_power = target_power_norm
        
        # (E) Potential-Based Reward Shaping (PBRS):
        current_potential = self._calculate_potential_phi(self.temperature, next_yield, sio_loss)
        r_pbrs = (self.gamma * current_potential) - self.prev_potential
        self.prev_potential = current_potential
        
        composite_reward = float(r_yield + r_sio_loss + r_cost + r_smooth + r_pbrs)
        
        terminated = bool(self.temperature > 2250.0)  # Refractory failure
        truncated = bool(self.step_count >= self.max_steps_per_episode)
        
        # Massive penalty for melting the furnace (Arson prevention)
        if terminated:
            composite_reward -= 5000.0
        
        obs = np.array([
            self.temperature,
            35000.0 * (1.0 - next_yield),
            14000.0 * (1.0 - next_yield),
            next_yield,
            sio_loss,
            target_power_norm,
            power_mw * 0.25 * self.step_count
        ], dtype=np.float32)
        
        info = {
            "temperature_c": self.temperature,
            "liquid_silicon_yield": next_yield,
            "sio_loss_fraction": sio_loss,
            "electricity_cost_per_hr": cost_usd_hr,
            "lambda_cost_current": lambda_cost,
            "action_delta": action_delta,
            "yield": next_yield,
            "cost": cost_usd_hr,
            "sio_lost": sio_loss,
            "temperature": self.temperature,
            "pressure": 1.0,
            "argon": 1.0,
            "reward": composite_reward
        }
        
        return obs, composite_reward, terminated, truncated, info

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.temperature = float(np.random.uniform(950.0, 1050.0))
        self.prev_action_power = 0.5
        self.step_count = 0
        init_yield, init_sio = self._compute_thermodynamic_yield_and_loss(self.temperature, 2.0)
        self.prev_potential = self._calculate_potential_phi(self.temperature, init_yield, init_sio)
        
        obs = np.array([
            self.temperature, 35000.0, 14000.0, init_yield, init_sio, self.prev_action_power, 0.0
        ], dtype=np.float32)
        return obs, {}

# Keep the old class name as an alias so existing imports don't break
SiliconEnv = SilicaSmeltingEnv
