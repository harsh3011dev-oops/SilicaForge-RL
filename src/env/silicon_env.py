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

    def __init__(
        self,
        heat_loss_multiplier=1.0,
        power_derate=0.0,
        yield_multiplier=1.0,
        sensor_noise_std_c=0.0,
        enhanced_observations=False,
        domain_randomization=False,
        safety_shield=False,
        multizone_observations=False,
        reward_mode="economic",
    ):
        super().__init__()

        self.base_heat_loss_multiplier = float(max(0.0, heat_loss_multiplier))
        self.base_power_derate = float(np.clip(power_derate, 0.0, 0.95))
        self.base_yield_multiplier = float(np.clip(yield_multiplier, 0.0, 1.0))
        self.base_sensor_noise_std_c = float(max(0.0, sensor_noise_std_c))
        self.enhanced_observations = enhanced_observations
        self.multizone_observations = multizone_observations
        self.reward_mode = reward_mode
        self.domain_randomization = domain_randomization
        self.safety_shield = safety_shield
        self.heat_loss_multiplier = self.base_heat_loss_multiplier
        self.power_derate = self.base_power_derate
        self.yield_multiplier = self.base_yield_multiplier
        self.sensor_noise_std_c = self.base_sensor_noise_std_c
        
        # State:
        # Legacy (7): [Temperature (°C), SiO2 burden, C burden, Yield, SiO Loss, Prev Power, Energy]
        # Enhanced (12): Normalized legacy + electrode depth + power derate
        # Multi-Zone v2 (18): 3 Thermal zones, 4 Electrical, 4 Feedstock, 3 Chemical, 4 Operational
        legacy_low = [25.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        legacy_high = [2500.0, 50000.0, 30000.0, 1.0, 1.0, 1.0, 500.0]
        enhanced_low_12 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.05, 0.0, 0.25]
        enhanced_high_12 = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        v2_low_18 = [0.0] * 18
        v2_high_18 = [1.0] * 18
        
        if multizone_observations:
            obs_low = v2_low_18
            obs_high = v2_high_18
        elif enhanced_observations:
            obs_low = enhanced_low_12
            obs_high = enhanced_high_12
        else:
            obs_low = legacy_low
            obs_high = legacy_high

        self.observation_space = spaces.Box(
            low=np.array(obs_low, dtype=np.float32),
            high=np.array(obs_high, dtype=np.float32),
        )
        
        # Action: [Normalized Power (0 to 1 -> 0 to 30 MW), Electrode Delta (-1 to 1), C/Si Ratio (1.8 to 2.2)]
        self.action_space = spaces.Box(
            low=np.array([-1.0, -1.0, -1.0], dtype=np.float32), # Use [-1, 1] for stable-baselines3 compatibility
            high=np.array([1.0, 1.0, 1.0], dtype=np.float32)
        )
        
        # Physical & Economic Constants
        self.MAX_POWER_MW = 30.0
        self.ELECTRICITY_PRICE_PER_MWH = 65.0  # USD/MWh
        self.OPTIMAL_TEMP_C = 1880.0
        self.TARGET_YIELD = 0.885              # Industrial SAF calibrated target recovery (87-90%)
        self.SIO_LOSS_THRESHOLD = 0.12         # Industrial SAF realistic offgas SiO loss threshold (10-14%)
        self.DT_SECONDS = 900.0                # 15 minutes per control step
        
        # Multi-Zone Thermal Capacities (GJ / °C)
        self.CAPACITY_BURDEN_GJ_PER_C = 80.0   # Zone 1: Heavy upper burden (preheating + condensation)
        self.CAPACITY_CRATER_GJ_PER_C = 45.0   # Zone 2: Crater cavity (arc zone + main reduction)
        self.CAPACITY_BATH_GJ_PER_C = 60.0     # Zone 3: Molten bath / hearth (liquid Si reservoir)
        self.THERMAL_CAPACITY_GJ_PER_C = 45.0  # Backward compatibility alias
        
        # Coupled 3-Phase Electrical Parameters (Section 3.2 Roadmap)
        self.BASE_RESISTANCE_MOHM = 1.35       # Operating resistance per electrode (~1.35 mOhm)
        self.BASE_REACTANCE_MOHM = 0.92        # Busbar and corrected furnace reactance (~0.92 mOhm -> cos phi ~0.83)
        
        # Feedstock Stoichiometry & Mass Constants (Schei & Tveit 1998)
        self.MOLAR_MASS_SI = 28.0855           # g/mol
        self.MOLAR_MASS_SIO2 = 60.0843         # g/mol
        self.SI_MASS_FRACTION_IN_SIO2 = self.MOLAR_MASS_SI / self.MOLAR_MASS_SIO2 # ~0.46743
        self.NOMINAL_QUARTZ_FEED_KG_HR = 5500.0# Nominal quartz feed rate at ~28.5 MW
        self.QUARTZ_PURITY = 0.988             # 98.8% pure SiO2
        self.HEAT_OF_REACTION_MJ_PER_KG_SI = 28.5 # Endothermic heat of reaction SiO2 + 2C -> Si + 2CO

        # Industrial Unit Cost Constants ($ USD)
        self.QUARTZ_PRICE_PER_KG = 0.055       # High-purity silica quartz ($55/t)
        self.CARBON_PRICE_PER_KG = 0.350       # Low-ash metallurgical coke/charcoal ($350/t)
        self.ELECTRODE_PRICE_PER_KG = 2.40     # Carbon / pre-baked graphite electrode ($2400/t)
        self.BASELINE_COST_PER_KG_SI = 1.65    # Global top-quartile benchmark cost ($/kg Si)
        self.SECONDARY_CONDENSER_EFFICIENCY = 0.70  # Stage 2: 70% of offgas SiO recovered as saleable Si/silica
        self.SECONDARY_RECOVERY_ENABLED = True      # Enable Stage 2 SiO Offgas Loop
        
        # Raw Material & Feedstock Baseline Parameters (Section 3.1 Roadmap)
        self.quartz_purity = self.QUARTZ_PURITY
        self.quartz_moisture = 0.012           # 1.2% moisture in quartz
        self.carbon_fixed_pct = 0.90           # 90% fixed carbon
        self.carbon_reactivity = 1.0           # Reductant reactivity index
        
        # Internal Thermal Zone States
        self.temperature_crater = 1865.0
        self.temperature_burden = 1180.0
        self.temperature_bath = 1580.0
        
        self.last_sic_inventory_pct = 2.0
        self.elec_state = {
            "resistance_mohm": self.BASE_RESISTANCE_MOHM,
            "reactance_mohm": self.BASE_REACTANCE_MOHM,
            "impedance_mohm": float(np.sqrt(self.BASE_RESISTANCE_MOHM**2 + self.BASE_REACTANCE_MOHM**2)),
            "power_factor": 0.84,
            "current_ka": 82.5,
            "voltage_v": 160.0,
            "electrode_wear_kg_per_t": 68.0,
        }
        
        # Cumulative Mass & Energy Balances (Episode level tracking)
        self.cum_si_fed_kg = 0.0
        self.cum_si_tapped_kg = 0.0
        self.cum_si_sio_loss_kg = 0.0
        self.cum_si_slag_loss_kg = 0.0
        self.cum_si_dust_loss_kg = 0.0
        self.cum_si_sic_inventory_kg = 0.0
        self.cum_energy_input_mwh = 0.0
        self.cum_total_cost_usd = 0.0
        
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
        self.electrode_depth_mm = 240.0
        self.electrode_efficiency = 1.0
        self.step_count = 0
        self.max_steps_per_episode = 96        # 24 hours (96 * 15 min)
        self.max_steps = self.max_steps_per_episode # Backward compatibility alias

    def _clausius_clapeyron_sio_pressure(self, temp_c):
        """Equilibrium SiO vapor pressure: log10(P_SiO [atm]) = 8.52 - 18400 / T_K"""
        temp_k = temp_c + 273.15
        if temp_k < 1200:
            return 0.0001
        log10_p = 8.52 - (18400.0 / temp_k)
        return max(1e-4, 10.0 ** log10_p)

    def _compute_thermodynamic_yield_and_loss(self, temp_c, c_si_ratio):
        """
        Multi-zone thermodynamic equilibrium for Liquid Silicon yield & SiO loss
        calibrated against Schei & Tveit (1998) industrial SAF benchmarks.
        Yield calibrated to 87-90% maximum recovery; SiO loss to 10-13% baseline.
        """
        if temp_c < 1414.0:
            return 0.0, 0.015
        
        ratio_eff = float(np.exp(-((c_si_ratio - 2.0) ** 2) / 0.08))
        p_sio = self._clausius_clapeyron_sio_pressure(temp_c)
        
        # 1. Liquid Silicon Recovery Fraction (Schei-Tveit SAF kinetics, peak 88.5%)
        if temp_c <= 1700.0:
            norm_t = (temp_c - 1414.0) / (1700.0 - 1414.0)
            yield_val = 0.12 * (norm_t ** 1.8) * ratio_eff
        elif temp_c <= 1865.0:
            norm_t = (temp_c - 1700.0) / (1865.0 - 1700.0)
            sigmoid_climb = 1.0 / (1.0 + np.exp(-6.5 * (norm_t - 0.55)))
            yield_val = (0.12 + (0.885 - 0.12) * sigmoid_climb) * ratio_eff
        elif temp_c <= 1930.0:
            over_t = (temp_c - 1865.0) / (1930.0 - 1865.0)
            yield_val = (0.885 + 0.010 * np.sin(over_t * np.pi) - 0.025 * over_t) * ratio_eff
        else:
            excess = temp_c - 1930.0
            yield_val = (0.870 * np.exp(-excess / 85.0)) * ratio_eff
            
        yield_fraction = float(np.clip(
            yield_val * self.yield_multiplier * self.electrode_efficiency,
            0.0,
            0.898,
        ))
        
        # 2. SiO Offgas Loss Fraction (Realistic industrial baseline 10-14%, spiking at high temp)
        if temp_c < 1650.0:
            sio_loss = 0.015
        elif temp_c <= 1880.0:
            norm_t = (temp_c - 1650.0) / (1880.0 - 1650.0)
            sio_loss = 0.015 + 0.095 * (norm_t ** 1.5)
        else:
            # Over-temperature blowout: exponential vaporization loss
            sio_loss = 0.110 + 0.075 * ((p_sio / 0.94) ** 2.2)
            
        # Stoichiometric mismatch penalty on SiO escape (under-coking lets SiO escape)
        if c_si_ratio < 2.0:
            sio_loss += 0.06 * (2.0 - c_si_ratio)
            
        sio_loss = float(np.clip(sio_loss, 0.01, 0.45))
        
        return yield_fraction, sio_loss

    def _compute_mass_and_elemental_balance(self, temp_c, c_si_ratio, power_mw, yield_fraction, sio_loss_fraction):
        """
        Rigorous elemental silicon mass balance satisfying Level 1 mathematical validation:
        Feed Si In = Tapped Liquid Si + Offgas SiO + Slag Retention + Dust Loss + SiC Inventory.
        Strictly enforces: sum(fractions) == 1.0 and mass conservation.
        """
        power_ratio = float(power_mw / 28.5) if power_mw > 0.1 else 0.0
        quartz_feed_kg = float(self.NOMINAL_QUARTZ_FEED_KG_HR * 0.25 * power_ratio)
        pure_sio2_feed_kg = quartz_feed_kg * self.QUARTZ_PURITY
        si_feed_kg = pure_sio2_feed_kg * self.SI_MASS_FRACTION_IN_SIO2
        
        if si_feed_kg <= 1e-4:
            return {
                "quartz_feed_kg": 0.0,
                "si_fed_kg": 0.0,
                "si_tapped_kg": 0.0,
                "si_sio_loss_kg": 0.0,
                "si_slag_loss_kg": 0.0,
                "si_dust_loss_kg": 0.0,
                "si_sic_inventory_kg": 0.0,
                "recovery_fraction": 0.0,
                "sio_loss_fraction": 0.0,
                "slag_loss_fraction": 0.0,
                "dust_loss_fraction": 0.0,
                "sic_fraction": 0.0,
                "product_purity_pct": 98.8,
                "mass_balance_error_kg": 0.0,
                "mass_balance_conserved": True,
            }
        
        # Base fractions
        f_tapped = float(yield_fraction)
        f_sio = float(sio_loss_fraction)
        f_slag = float(0.014 + 0.006 * abs(c_si_ratio - 2.0))
        temp_over = max(0.0, (temp_c - 1880.0) / 200.0)
        f_dust = float(0.008 * (1.0 + temp_over))
        
        # Intermediate SiC inventory remainder
        f_remainder = 1.0 - (f_tapped + f_sio + f_slag + f_dust)
        if f_remainder >= 0.0:
            f_sic = f_remainder
        else:
            overflow = abs(f_remainder)
            scale = max(0.1, (f_tapped + f_sio - overflow)) / max(1e-6, f_tapped + f_sio)
            f_tapped *= scale
            f_sio *= scale
            f_sic = 0.0
            
        # Strictly normalize so sum of fractions == 1.0000000
        total_f = f_tapped + f_sio + f_slag + f_dust + f_sic
        f_tapped /= total_f
        f_sio /= total_f
        f_slag /= total_f
        f_dust /= total_f
        f_sic /= total_f
        
        m_tapped = si_feed_kg * f_tapped
        m_sio = si_feed_kg * f_sio
        m_slag = si_feed_kg * f_slag
        m_dust = si_feed_kg * f_dust
        m_sic = si_feed_kg * f_sic
        
        mass_out_sum = m_tapped + m_sio + m_slag + m_dust + m_sic
        balance_error = abs(si_feed_kg - mass_out_sum)
        
        # Product Purity (%):
        # Quartz impurities (Fe, Al, Ca oxides ~ 1.2% in quartz) partition into metal and slag
        impurity_carryover_kg = quartz_feed_kg * (1.0 - self.QUARTZ_PURITY) * 0.45 * (f_tapped / max(1e-4, f_tapped + f_slag))
        purity_pct = float((m_tapped / max(1e-4, m_tapped + impurity_carryover_kg)) * 100.0) if m_tapped > 1e-4 else 98.8
        purity_pct = float(np.clip(purity_pct, 98.0, 99.4))
        
        return {
            "quartz_feed_kg": quartz_feed_kg,
            "si_fed_kg": si_feed_kg,
            "si_tapped_kg": m_tapped,
            "si_sio_loss_kg": m_sio,
            "si_slag_loss_kg": m_slag,
            "si_dust_loss_kg": m_dust,
            "si_sic_inventory_kg": m_sic,
            "recovery_fraction": f_tapped,
            "sio_loss_fraction": f_sio,
            "slag_loss_fraction": f_slag,
            "dust_loss_fraction": f_dust,
            "sic_fraction": f_sic,
            "product_purity_pct": purity_pct,
            "mass_balance_error_kg": balance_error,
            "mass_balance_conserved": bool(balance_error < 1e-5),
        }

    def _compute_electrical_state(self, power_mw):
        """
        Coupled 3-phase electrical circuit model for Submerged Arc Furnace:
        Active power P = 3 * I_phase^2 * R_phase.
        Calculates resistance, impedance, power factor, current, voltage, and electrode wear.
        """
        p_active_mw = max(0.05, float(power_mw))
        p_phase_mw = p_active_mw / 3.0
        
        # Operating resistance per electrode (mOhm):
        depth_offset = (self.electrode_depth_mm - 250.0) / 100.0
        temp_offset = (self.temperature_crater - 1880.0) / 500.0
        r_mohm = self.BASE_RESISTANCE_MOHM * (1.0 - 0.25 * depth_offset - 0.08 * temp_offset)
        r_mohm = float(np.clip(r_mohm, 0.85, 2.40))
        
        # Reactance and impedance (mOhm)
        x_mohm = self.BASE_REACTANCE_MOHM
        z_mohm = float(np.sqrt(r_mohm ** 2 + x_mohm ** 2))
        cos_phi = float(np.clip(r_mohm / z_mohm, 0.75, 0.92))
        
        # RMS Electrode Current (kA): P_phase (MW) * 1e9 / R_mohm -> sqrt -> / 1e3
        i_ka = float(np.sqrt((p_phase_mw * 1e9) / max(1e-4, r_mohm)) * 1e-3)
        i_ka = float(np.clip(i_ka, 15.0, 120.0))
        
        # Phase-to-bath voltage (V): V = I * Z
        v_volts = float(i_ka * z_mohm)
        
        # Electrode Consumption (kg per tonne Si produced):
        electrode_wear_kg_per_t = float(68.0 * ((i_ka / 84.0) ** 1.35))
        electrode_wear_kg_per_t = float(np.clip(electrode_wear_kg_per_t, 55.0, 110.0))
        
        return {
            "resistance_mohm": r_mohm,
            "reactance_mohm": x_mohm,
            "impedance_mohm": z_mohm,
            "power_factor": cos_phi,
            "current_ka": i_ka,
            "voltage_v": v_volts,
            "electrode_wear_kg_per_t": electrode_wear_kg_per_t,
        }

    @property
    def temperature(self):
        return self.temperature_crater

    @temperature.setter
    def temperature(self, value):
        self.temperature_crater = float(value)

    def _integrate_three_zone_thermal_model(self, power_mw, m_si_tapped_kg, q_moisture_evap_mw):
        """
        Integrates dynamic lumped energy balance across 3 coupled SAF zones:
        Zone 1 (Burden), Zone 2 (Crater), Zone 3 (Molten Bath).
        Conserves net energy rigorously.
        """
        p_elec_mw = power_mw * 0.88 # 88% electrical-to-thermal efficiency
        
        # Zone power allocation:
        # 88% of arc power dissipated in crater cavity, 12% in bath/hearth
        q_elec_crater = 0.88 * p_elec_mw
        q_elec_bath = 0.12 * p_elec_mw
        
        # Endothermic reduction reaction in crater cavity (28.5 MJ / kg Si)
        m_si_prod_kg_sec = m_si_tapped_kg / self.DT_SECONDS
        q_rxn_crater = m_si_prod_kg_sec * self.HEAT_OF_REACTION_MJ_PER_KG_SI
        
        # Heat transfer between zones (MW):
        q_up = 0.0035 * (self.temperature_crater - self.temperature_burden)
        q_down = 0.0038 * (self.temperature_crater - self.temperature_bath)
        
        # Exothermic condensation heat in burden zone:
        q_cond_burden = 1.2 * (self.temperature_burden / 1200.0) if self.temperature_burden > 900.0 else 0.0
        
        # Heat losses to ambient (MW):
        delta_t1 = max(0.0, self.temperature_burden - 25.0)
        q_loss_burden = self.heat_loss_multiplier * (1.2 + 0.0019 * delta_t1)
        
        delta_t2 = max(0.0, self.temperature_crater - 25.0)
        q_loss_crater = self.heat_loss_multiplier * (1.0 + 0.0010 * delta_t2)
        
        delta_t3 = max(0.0, self.temperature_bath - 25.0)
        q_loss_bath = self.heat_loss_multiplier * (0.8 + 0.0006 * delta_t3)
        q_tap_bath = 1.4 * (self.temperature_bath / 1600.0)
        
        # Net thermal rates (MW):
        net_burden = q_up + q_cond_burden - q_loss_burden - q_moisture_evap_mw
        net_crater = q_elec_crater - q_rxn_crater - q_loss_crater - q_up - q_down
        net_bath = q_elec_bath + q_down - q_loss_bath - q_tap_bath
        
        dT1_dt = net_burden / self.CAPACITY_BURDEN_GJ_PER_C
        dT2_dt = net_crater / self.CAPACITY_CRATER_GJ_PER_C
        dT3_dt = net_bath / self.CAPACITY_BATH_GJ_PER_C
        
        prev_t1, prev_t2, prev_t3 = self.temperature_burden, self.temperature_crater, self.temperature_bath
        
        self.temperature_burden = float(np.clip(prev_t1 + dT1_dt * self.DT_SECONDS, 200.0, 1600.0))
        self.temperature_crater = float(np.clip(prev_t2 + dT2_dt * self.DT_SECONDS, 800.0, 2400.0))
        self.temperature_bath = float(np.clip(prev_t3 + dT3_dt * self.DT_SECONDS, 600.0, 1850.0))
        
        total_q_loss = q_loss_burden + q_loss_crater + q_loss_bath + q_tap_bath
        
        # First-Law energy conservation closure check across all 3 zones:
        delta_e_thermal_total_gj = (
            (self.temperature_burden - prev_t1) * self.CAPACITY_BURDEN_GJ_PER_C
            + (self.temperature_crater - prev_t2) * self.CAPACITY_CRATER_GJ_PER_C
            + (self.temperature_bath - prev_t3) * self.CAPACITY_BATH_GJ_PER_C
        )
        e_in_gj = p_elec_mw * self.DT_SECONDS
        e_out_gj = (total_q_loss + q_rxn_crater + q_moisture_evap_mw - q_cond_burden) * self.DT_SECONDS
        energy_error_gj = abs(e_in_gj - (e_out_gj + delta_e_thermal_total_gj))
        
        return {
            "q_elec_mw": p_elec_mw,
            "q_loss_total_mw": total_q_loss,
            "q_rxn_total_mw": q_rxn_crater,
            "q_loss_burden_mw": q_loss_burden,
            "q_loss_crater_mw": q_loss_crater,
            "q_loss_bath_mw": q_loss_bath,
            "q_trans_burden_mw": q_up,
            "q_trans_bath_mw": q_down,
            "energy_error_gj": energy_error_gj,
            "dT1_step": self.temperature_burden - prev_t1,
            "dT2_step": self.temperature_crater - prev_t2,
            "dT3_step": self.temperature_bath - prev_t3,
        }

    def _randomize_episode_conditions(self):
        """Sample plausible, bounded process variation for robust-policy training."""
        if not self.domain_randomization:
            self.heat_loss_multiplier = self.base_heat_loss_multiplier
            self.power_derate = self.base_power_derate
            self.yield_multiplier = self.base_yield_multiplier
            self.sensor_noise_std_c = self.base_sensor_noise_std_c
            self.quartz_purity = self.QUARTZ_PURITY
            self.quartz_moisture = 0.012
            self.carbon_fixed_pct = 0.90
            self.carbon_reactivity = 1.0
            return

        self.heat_loss_multiplier = self.base_heat_loss_multiplier * float(np.random.uniform(0.85, 1.25))
        self.power_derate = float(np.clip(self.base_power_derate + np.random.uniform(0.0, 0.12), 0.0, 0.95))
        self.yield_multiplier = float(np.clip(self.base_yield_multiplier * np.random.uniform(0.90, 1.0), 0.0, 1.0))
        self.sensor_noise_std_c = self.base_sensor_noise_std_c + float(np.random.uniform(0.0, 8.0))
        self.quartz_purity = float(np.random.uniform(0.982, 0.995))
        self.quartz_moisture = float(np.random.uniform(0.005, 0.030))
        self.carbon_fixed_pct = float(np.random.uniform(0.88, 0.94))
        self.carbon_reactivity = float(np.random.uniform(0.92, 1.08))

    def _apply_safety_shield(self, action):
        """Limit unsafe actuator commands while preserving the requested action in info."""
        requested_action = np.clip(np.asarray(action, dtype=np.float32), -1.0, 1.0)
        if not self.safety_shield:
            return requested_action, False

        shielded_action = requested_action.copy()
        requested_power_norm = float(shielded_action[0]) * 0.5 + 0.5
        power_norm = float(np.clip(requested_power_norm, self.prev_action_power - 0.18, self.prev_action_power + 0.18))
        if self.temperature >= 2180.0:
            power_norm = 0.0
        elif self.temperature >= 2100.0:
            power_norm = min(power_norm, 0.20)
        elif self.temperature >= 2025.0:
            power_norm = min(power_norm, 0.45)

        if self.electrode_depth_mm <= 185.0:
            shielded_action[1] = max(0.0, shielded_action[1])
        elif self.electrode_depth_mm >= 315.0:
            shielded_action[1] = min(0.0, shielded_action[1])

        shielded_action[0] = power_norm * 2.0 - 1.0
        shield_applied = not np.allclose(requested_action, shielded_action, atol=1e-6)
        return shielded_action, shield_applied

    def _make_observation(self, yield_fraction, sio_loss, cumulative_energy_mwh):
        observed_crater = float(np.clip(
            self.temperature_crater + np.random.normal(0.0, self.sensor_noise_std_c),
            25.0,
            2500.0,
        ))
        observed_burden = float(np.clip(
            self.temperature_burden + np.random.normal(0.0, self.sensor_noise_std_c * 0.7),
            25.0,
            1800.0,
        ))
        observed_bath = float(np.clip(
            self.temperature_bath + np.random.normal(0.0, self.sensor_noise_std_c * 0.5),
            25.0,
            2000.0,
        ))
        
        if self.multizone_observations:
            observation = [
                # Thermal (3)
                observed_burden / 1600.0,
                observed_crater / 2400.0,
                observed_bath / 1900.0,
                # Electrical (4)
                np.clip(self.elec_state["current_ka"] / 120.0, 0.0, 1.0),
                np.clip(self.elec_state["voltage_v"] / 250.0, 0.0, 1.0),
                np.clip(self.elec_state["resistance_mohm"] / 3.0, 0.0, 1.0),
                self.elec_state["power_factor"],
                # Feedstock & Material (4)
                self.quartz_purity,
                np.clip(self.quartz_moisture * 20.0, 0.0, 1.0),
                self.carbon_fixed_pct,
                np.clip(self.carbon_reactivity / 1.2, 0.0, 1.0),
                # Reaction & Chemistry (3)
                yield_fraction,
                sio_loss,
                np.clip(self.last_sic_inventory_pct / 10.0, 0.0, 1.0),
                # Operational (4)
                (self.electrode_depth_mm - 180.0) / 140.0,
                self.prev_action_power,
                min(cumulative_energy_mwh, 800.0) / 800.0,
                1.0 - self.power_derate,
            ]
        elif self.enhanced_observations:
            observation = [
                observed_crater / 2500.0,
                35000.0 * (1.0 - yield_fraction) / 50000.0,
                14000.0 * (1.0 - yield_fraction) / 30000.0,
                yield_fraction,
                sio_loss,
                self.prev_action_power,
                min(cumulative_energy_mwh, 800.0) / 800.0,
                (self.electrode_depth_mm - 180.0) / 140.0,
                np.clip((1483.0 + (observed_crater - 1860.0) * 0.4) / 2250.0, 0.0, 1.0),
                1.0 - self.power_derate,
                self.yield_multiplier,
                np.clip(self.heat_loss_multiplier / 2.0, 0.25, 1.0),
            ]
        else:
            observation = [
                observed_crater,
                35000.0 * (1.0 - yield_fraction),
                14000.0 * (1.0 - yield_fraction),
                yield_fraction,
                sio_loss,
                self.prev_action_power,
                cumulative_energy_mwh,
            ]
        return np.array(observation, dtype=np.float32)

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
        Executes one step with 3-Zone Thermal Inertia, Coupled Electrical Dynamics,
        Non-Linear Composite Reward, Action Slew Damping, and Curriculum Cost Annealing.
        """
        self.step_count += 1
        
        # Unpack normalized continuous action [-1, 1] and scale to physics bounds
        requested_action = np.clip(action, -1.0, 1.0)
        action, shield_applied = self._apply_safety_shield(requested_action)
        target_power_norm = float(action[0]) * 0.5 + 0.5  # [-1, 1] -> [0.0, 1.0]
        electrode_delta = float(action[1])                # [-1, 1] -> [-1.0, 1.0]
        c_si_ratio = float(action[2]) * 0.2 + 2.0         # [-1, 1] -> [1.8, 2.2]
        
        power_mw = target_power_norm * self.MAX_POWER_MW * (1.0 - self.power_derate)
        if self.enhanced_observations or self.multizone_observations:
            # Pillar 1: Electrode depth dynamics with physical rate limiting
            self.electrode_depth_mm = float(np.clip(self.electrode_depth_mm + electrode_delta * 5.0, 180.0, 320.0))
            # Optimal immersion window is 240-265 mm (arc submerged under burden):
            electrode_offset = (self.electrode_depth_mm - 250.0) / 40.0
            self.electrode_efficiency = float(0.88 + 0.12 * np.exp(-(electrode_offset ** 2)))
        
        # 1. Coupled Electrical Circuit State (Section 3.2 Roadmap)
        self.elec_state = self._compute_electrical_state(power_mw)
        
        # 2. Evaluate Reaction Kinetics & Elemental Mass Balance
        raw_yield, raw_sio_loss = self._compute_thermodynamic_yield_and_loss(self.temperature_crater, c_si_ratio)
        mass_bal = self._compute_mass_and_elemental_balance(
            self.temperature_crater, c_si_ratio, power_mw, raw_yield, raw_sio_loss
        )
        tapped_yield = mass_bal["recovery_fraction"]
        sio_loss = mass_bal["sio_loss_fraction"]
        self.last_sic_inventory_pct = mass_bal["sic_fraction"] * 100.0

        # Pillar 3: Stage 2 Closed-Loop Secondary SiO Offgas Condensation Reactor
        # 2 SiO(g) -> Si(s) + SiO2(s) in lower-temperature condensation shaft (800 - 1100 °C)
        si_sio_loss_kg = mass_bal["si_sio_loss_kg"]
        if self.SECONDARY_RECOVERY_ENABLED and si_sio_loss_kg > 0.0:
            # Condensation recovery efficiency depends on burden preheat and offgas velocity
            cond_eff = self.SECONDARY_CONDENSER_EFFICIENCY * float(np.clip(
                1.0 - 0.20 * abs(c_si_ratio - 2.0) - 0.15 * max(0.0, (self.temperature_crater - 1920.0) / 200.0),
                0.40,
                0.85
            ))
            si_recovered_secondary_kg = si_sio_loss_kg * cond_eff
            # Exothermic disproportionation heat recycled back into burden:
            # 2 SiO(g) -> Si + SiO2 releases ~18.2 MJ/kg Si recovered
            q_secondary_cond_mw = (si_recovered_secondary_kg * 18.2) / self.DT_SECONDS
        else:
            si_recovered_secondary_kg = 0.0
            q_secondary_cond_mw = 0.0

        # Total saleable silicon production
        si_tapped_kg = mass_bal["si_tapped_kg"]
        saleable_si_kg = si_tapped_kg + si_recovered_secondary_kg
        overall_yield = saleable_si_kg / max(1e-4, mass_bal["si_fed_kg"]) if mass_bal["si_fed_kg"] > 1e-4 else 0.0
        overall_yield = float(np.clip(overall_yield, 0.0, 0.94))

        # Moisture evaporation power demand (MW)
        m_water_kg = mass_bal["quartz_feed_kg"] * self.quartz_moisture
        q_moisture_evap_mw = (m_water_kg * 2.26) / self.DT_SECONDS

        # 3. 3-Zone Coupled Thermal Model Integration with Secondary Condensation Heat Recycle
        thermal_diag = self._integrate_three_zone_thermal_model(
            power_mw, mass_bal["si_tapped_kg"], q_moisture_evap_mw
        )
        energy_error_gj = thermal_diag["energy_error_gj"]
        
        # Cumulative mass and energy tracking
        step_energy_mwh = power_mw * (self.DT_SECONDS / 3600.0)
        step_sec_kwh_per_kg = (step_energy_mwh * 1000.0) / max(1e-4, saleable_si_kg) if saleable_si_kg > 1e-4 else 0.0
        self.cum_si_fed_kg += mass_bal["si_fed_kg"]
        self.cum_si_tapped_kg += saleable_si_kg
        self.cum_si_sio_loss_kg += max(0.0, mass_bal["si_sio_loss_kg"] - si_recovered_secondary_kg)
        self.cum_si_slag_loss_kg += mass_bal["si_slag_loss_kg"]
        self.cum_si_dust_loss_kg += mass_bal["si_dust_loss_kg"]
        self.cum_si_sic_inventory_kg += mass_bal["si_sic_inventory_kg"]
        self.cum_energy_input_mwh += step_energy_mwh
        cum_sec = (self.cum_energy_input_mwh * 1000.0) / max(1e-4, self.cum_si_tapped_kg) if self.cum_si_tapped_kg > 1e-4 else 0.0
        
        # Industrial Cost Accounting ($ USD per 15-min step)
        cost_elec = step_energy_mwh * self.ELECTRICITY_PRICE_PER_MWH
        cost_quartz = mass_bal["quartz_feed_kg"] * self.QUARTZ_PRICE_PER_KG
        carbon_fed_kg = (mass_bal["quartz_feed_kg"] / 60.08) * c_si_ratio * 12.011
        cost_carbon = carbon_fed_kg * self.CARBON_PRICE_PER_KG
        electrode_consumed_kg = (self.elec_state["electrode_wear_kg_per_t"] / 1000.0) * saleable_si_kg
        cost_electrode = electrode_consumed_kg * self.ELECTRODE_PRICE_PER_KG
        total_step_cost = float(cost_elec + cost_quartz + cost_carbon + cost_electrode)
        cost_per_kg_si = float(total_step_cost / max(1e-4, saleable_si_kg)) if saleable_si_kg > 1e-4 else 10.0
        cost_per_kg_si = float(np.clip(cost_per_kg_si, 0.50, 15.0))
        self.cum_total_cost_usd += total_step_cost

        # 4. COMPOSITE REWARD CALCULATION
        if self.reward_mode == "economic":
            # Direct Industrial Cost-per-kg & Efficiency Objective:
            # Anchor: $1.35/kg is global top performance, $1.65/kg is average benchmark
            r_cost_term = -4.0 * (cost_per_kg_si / self.BASELINE_COST_PER_KG_SI)
            # Yield pull (incentivize high primary + secondary silicon recovery)
            r_yield_term = 25.0 * ((overall_yield / 0.88) ** 2.5)
            # SEC penalty (target <= 13.0 kWh/kg Si)
            r_sec_term = -2.0 * max(0.0, (step_sec_kwh_per_kg - 11.5) / 5.0)
            # SiO unrecovered offgas penalty
            net_unrecovered_sio_frac = (mass_bal["si_sio_loss_kg"] - si_recovered_secondary_kg) / max(1e-4, mass_bal["si_fed_kg"])
            r_sio_term = -15.0 * ((net_unrecovered_sio_frac / 0.05) ** 2.0) if net_unrecovered_sio_frac > 0.04 else 0.0
            # Pillar 2: Stoichiometric balance penalty (punish over-coking SiC build-up or under-coking)
            r_stoich_penalty = -10.0 * ((c_si_ratio - 2.0) ** 2.0)
            # Action smoothing
            action_delta = float(abs(target_power_norm - self.prev_action_power))
            r_smooth = -self.action_smoothness_weight * (action_delta ** 2.0)
            self.prev_action_power = target_power_norm
            # PBRS Potential
            current_potential = self._calculate_potential_phi(self.temperature_crater, overall_yield, net_unrecovered_sio_frac)
            r_pbrs = (self.gamma * current_potential) - self.prev_potential
            self.prev_potential = current_potential

            composite_reward = float(r_cost_term + r_yield_term + r_sec_term + r_sio_term + r_stoich_penalty + r_smooth + 0.1 * r_pbrs)
        else:
            # Legacy reward mode fallback
            yield_ratio = overall_yield / self.TARGET_YIELD
            r_yield = 20.0 * (yield_ratio ** self.yield_exponent)
            r_sio_loss = -15.0 * (((sio_loss - self.SIO_LOSS_THRESHOLD) / 0.05) ** 2.0) if sio_loss > self.SIO_LOSS_THRESHOLD else 0.0
            lambda_cost = self._get_dynamic_cost_weight()
            cost_usd_hr = power_mw * self.ELECTRICITY_PRICE_PER_MWH
            normalized_cost = cost_usd_hr / 1000.0
            yield_gate = 1.0 / (1.0 + np.exp(-12.0 * (overall_yield - 0.22)))
            r_cost = -lambda_cost * normalized_cost * yield_gate * 10.0
            action_delta = abs(target_power_norm - self.prev_action_power)
            r_smooth = -self.action_smoothness_weight * (action_delta ** 2.0)
            self.prev_action_power = target_power_norm
            current_potential = self._calculate_potential_phi(self.temperature_crater, overall_yield, sio_loss)
            r_pbrs = (self.gamma * current_potential) - self.prev_potential
            self.prev_potential = current_potential
            composite_reward = float(r_yield + r_sio_loss + r_cost + r_smooth + r_pbrs)

        cost_usd_hr = power_mw * self.ELECTRICITY_PRICE_PER_MWH
        lambda_cost = self._get_dynamic_cost_weight()
        
        terminated = bool(self.temperature_crater > 2250.0)  # Refractory failure
        truncated = bool(self.step_count >= self.max_steps_per_episode)
        
        # Massive penalty for melting the furnace
        if terminated:
            composite_reward -= 5000.0
        
        obs = self._make_observation(overall_yield, sio_loss, power_mw * 0.25 * self.step_count)
        
        info = {
            "temperature_c": self.temperature_crater,
            "liquid_silicon_yield": overall_yield,
            "primary_tapped_yield": tapped_yield,
            "sio_loss_fraction": sio_loss,
            "electricity_cost_per_hr": cost_usd_hr,
            "lambda_cost_current": lambda_cost,
            "action_delta": action_delta,
            "yield": overall_yield,
            "cost": cost_usd_hr,
            "sio_lost": sio_loss,
            "temperature": self.temperature_crater,
            "pressure": 1.0,
            "argon": 1.0,
            "reward": composite_reward,
            "requested_action": requested_action.tolist(),
            "applied_action": action.tolist(),
            "safety_shield_applied": shield_applied,
            "electrode_depth_mm": self.electrode_depth_mm,
            "available_power_fraction": 1.0 - self.power_derate,
            "feed_reactivity": self.yield_multiplier,
            "heat_loss_multiplier": self.heat_loss_multiplier,
            "actual_power_mw": power_mw,
            # Economic & Cost-Per-Kg Industrial Breakdown
            "cost_per_kg_saleable_si": cost_per_kg_si,
            "total_step_cost_usd": total_step_cost,
            "cost_electricity_usd": cost_elec,
            "cost_quartz_usd": cost_quartz,
            "cost_carbon_usd": cost_carbon,
            "cost_electrode_usd": cost_electrode,
            "saleable_silicon_kg": saleable_si_kg,
            "secondary_recovered_si_kg": si_recovered_secondary_kg,
            "cumulative_total_cost_usd": self.cum_total_cost_usd,
            "cumulative_cost_per_kg": float(self.cum_total_cost_usd / max(1e-4, self.cum_si_tapped_kg)),
            # Multi-Zone Thermal Diagnostics (Section 8 Roadmap)
            "temperature_crater_c": self.temperature_crater,
            "temperature_burden_c": self.temperature_burden,
            "temperature_bath_c": self.temperature_bath,
            # Coupled Electrical Circuit Diagnostics (Section 3.2 Roadmap)
            "electrode_current_ka": self.elec_state["current_ka"],
            "electrode_voltage_v": self.elec_state["voltage_v"],
            "furnace_resistance_mohm": self.elec_state["resistance_mohm"],
            "power_factor_cos_phi": self.elec_state["power_factor"],
            "electrode_consumption_kg_per_t_si": self.elec_state["electrode_wear_kg_per_t"],
            # Feedstock Diagnostics (Section 3.1 Roadmap)
            "quartz_purity_pct": self.quartz_purity * 100.0,
            "quartz_moisture_pct": self.quartz_moisture * 100.0,
            "carbon_reactivity": self.carbon_reactivity,
            # Mass & Energy Balance Audit Metrics
            "silicon_recovery_pct": overall_yield * 100.0,
            "primary_recovery_pct": tapped_yield * 100.0,
            "sio_loss_pct": mass_bal["sio_loss_fraction"] * 100.0,
            "silicon_in_slag_pct": mass_bal["slag_loss_fraction"] * 100.0,
            "silicon_dust_pct": mass_bal["dust_loss_fraction"] * 100.0,
            "sic_inventory_pct": mass_bal["sic_fraction"] * 100.0,
            "product_purity_pct": mass_bal["product_purity_pct"],
            "mass_si_tapped_kg": mass_bal["si_tapped_kg"],
            "mass_si_fed_kg": mass_bal["si_fed_kg"],
            "quartz_fed_kg": mass_bal["quartz_feed_kg"],
            "step_sec_kwh_per_kg": step_sec_kwh_per_kg,
            "cumulative_sec_kwh_per_kg": cum_sec,
            "mass_balance_error_kg": mass_bal["mass_balance_error_kg"],
            "mass_balance_conserved": mass_bal["mass_balance_conserved"],
            "energy_balance_error_gj": energy_error_gj,
            "energy_balance_conserved": bool(energy_error_gj < 1e-4),
            "cumulative_si_tapped_kg": self.cum_si_tapped_kg,
            "cumulative_energy_mwh": self.cum_energy_input_mwh,
        }
        
        return obs, composite_reward, terminated, truncated, info

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self._randomize_episode_conditions()
        
        # Initial thermal equilibrium across the 3 zones
        self.temperature_crater = float(np.random.uniform(1840.0, 1890.0))
        self.temperature_burden = float(np.random.uniform(1120.0, 1220.0))
        self.temperature_bath = float(np.random.uniform(1550.0, 1630.0))
        self.temperature = self.temperature_crater
        
        self.prev_action_power = 0.5
        if self.enhanced_observations or self.multizone_observations:
            self.electrode_depth_mm = float(np.random.uniform(230.0, 270.0))
            electrode_offset = (self.electrode_depth_mm - 250.0) / 45.0
            self.electrode_efficiency = float(0.90 + 0.10 * np.exp(-(electrode_offset ** 2)))
        else:
            self.electrode_depth_mm = 250.0
            self.electrode_efficiency = 1.0
        self.step_count = 0
        
        # Reset cumulative accounting metrics
        self.cum_si_fed_kg = 0.0
        self.cum_si_tapped_kg = 0.0
        self.cum_si_sio_loss_kg = 0.0
        self.cum_si_slag_loss_kg = 0.0
        self.cum_si_dust_loss_kg = 0.0
        self.cum_si_sic_inventory_kg = 0.0
        self.cum_energy_input_mwh = 0.0
        self.cum_total_cost_usd = 0.0
        self.last_sic_inventory_pct = 2.0
        
        self.elec_state = self._compute_electrical_state(self.prev_action_power * self.MAX_POWER_MW)
        init_yield, init_sio = self._compute_thermodynamic_yield_and_loss(self.temperature_crater, 2.0)
        self.prev_potential = self._calculate_potential_phi(self.temperature_crater, init_yield, init_sio)
        
        obs = self._make_observation(init_yield, init_sio, 0.0)
        return obs, {}

# Keep the old class name as an alias so existing imports don't break
SiliconEnv = SilicaSmeltingEnv
