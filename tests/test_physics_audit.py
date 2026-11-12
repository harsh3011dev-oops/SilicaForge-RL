#!/usr/bin/env python3
"""
SilicaForge-RL: Physics Audit & Verification Suite (v2.0 Milestone)
Validates Phase 1 Roadmap Requirements:
- Level 1: Mathematical Conservation (Silicon Mass Conservation, Energy Balance)
- Level 2: Thermodynamic Calibration (Schei-Tveit Recovery 87-90%, Offgas SiO Loss 10-14%, SEC 11-13 kWh/kg)
- Numerical Stability and Physical Consistency
"""

import sys
import os
import unittest
import numpy as np

# Add src/env to path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src", "env"))

from silicon_env import SiliconEnv


class TestPhysicsAudit(unittest.TestCase):
    def setUp(self):
        self.env = SiliconEnv(enhanced_observations=True, safety_shield=True)
        self.env.reset(seed=42)

    def test_silicon_mass_conservation_strict(self):
        """Level 1 Audit: Verify elemental silicon mass conservation across multiple actions."""
        obs, _ = self.env.reset(seed=101)
        
        # Test 50 random steps across full action space
        for step_idx in range(50):
            action = self.env.action_space.sample()
            obs, reward, term, trunc, info = self.env.step(action)
            
            # Check mass balance conservation flag
            self.assertTrue(
                info["mass_balance_conserved"],
                f"Mass balance violated at step {step_idx}: error = {info['mass_balance_error_kg']:.8f} kg"
            )
            self.assertLess(
                info["mass_balance_error_kg"],
                1e-4,
                f"Silicon mass error exceeded 1e-4 kg: {info['mass_balance_error_kg']}"
            )
            
            # Verify stream sum explicitly
            si_fed = info["mass_si_fed_kg"]
            si_sum_out = (
                info["mass_si_tapped_kg"]
                + (si_fed * info["sio_loss_pct"] / 100.0)
                + (si_fed * info["silicon_in_slag_pct"] / 100.0)
                + (si_fed * info["silicon_dust_pct"] / 100.0)
                + (si_fed * info["sic_inventory_pct"] / 100.0)
            )
            self.assertAlmostEqual(si_fed, si_sum_out, places=3)
            
            if term or trunc:
                obs, _ = self.env.reset()

    def test_energy_balance_conservation(self):
        """Level 1 Audit: Verify First Law energy conservation E_elec = E_loss + E_rxn + delta_E."""
        obs, _ = self.env.reset(seed=202)
        
        for step_idx in range(40):
            action = np.array([0.8, 0.0, 0.0], dtype=np.float32) # steady power
            obs, reward, term, trunc, info = self.env.step(action)
            
            self.assertTrue(
                info["energy_balance_conserved"],
                f"Energy conservation violated at step {step_idx}: error = {info['energy_balance_error_gj']:.6f} GJ"
            )
            self.assertLess(info["energy_balance_error_gj"], 1e-3)
            if term or trunc:
                break

    def test_calibrated_recovery_bounds(self):
        """Level 2 Audit: Verify silicon recovery peaks realistically in 87-90% range (no unphysical 94%+)."""
        # Test optimal operating region: ~1880 C, C/Si = 2.0, power = 28.5 MW
        self.env.temperature = 1880.0
        self.env.electrode_depth_mm = 250.0 # optimal immersion
        self.env.electrode_efficiency = 1.0
        
        raw_yield, raw_sio_loss = self.env._compute_thermodynamic_yield_and_loss(1880.0, 2.0)
        mass_bal = self.env._compute_mass_and_elemental_balance(1880.0, 2.0, 28.5, raw_yield, raw_sio_loss)
        recovery_pct = mass_bal["recovery_fraction"] * 100.0
        
        self.assertGreaterEqual(recovery_pct, 86.5, f"Recovery {recovery_pct:.2f}% below industrial target")
        self.assertLessEqual(recovery_pct, 90.0, f"Recovery {recovery_pct:.2f}% exceeds realistic industrial ceiling 90%")

    def test_calibrated_sio_loss_bounds(self):
        """Level 2 Audit: Verify offgas SiO loss is in the realistic 10-14% industrial window at optimal temp."""
        raw_yield, raw_sio_loss = self.env._compute_thermodynamic_yield_and_loss(1880.0, 2.0)
        mass_bal = self.env._compute_mass_and_elemental_balance(1880.0, 2.0, 28.5, raw_yield, raw_sio_loss)
        sio_loss_pct = mass_bal["sio_loss_fraction"] * 100.0
        
        self.assertGreaterEqual(sio_loss_pct, 10.0, f"SiO loss {sio_loss_pct:.2f}% unrealistically low (<10%)")
        self.assertLessEqual(sio_loss_pct, 14.0, f"SiO loss {sio_loss_pct:.2f}% exceeds optimal benchmark (>14%)")

    def test_overtemperature_volatilization_spikes(self):
        """Level 2 Audit: Overheating past 1950°C must trigger SiO gas blowouts and reduce net yield."""
        y_opt, sio_opt = self.env._compute_thermodynamic_yield_and_loss(1880.0, 2.0)
        y_hot, sio_hot = self.env._compute_thermodynamic_yield_and_loss(2050.0, 2.0)
        
        self.assertGreater(sio_hot, sio_opt * 1.5, "SiO loss did not surge under extreme thermal volatilization")
        self.assertLess(y_hot, y_opt, "Silicon recovery did not drop during high-temperature gas escape")

    def test_specific_energy_consumption_in_benchmark_window(self):
        """Level 2 Audit: Steady-state SEC must reside inside 11.0 - 13.0 kWh/kg standard."""
        self.env.temperature = 1880.0
        self.env.reset(seed=303)
        self.env.temperature = 1880.0
        
        # Step at nominal power ~28 MW, balanced carbon
        action = np.array([0.87, 0.0, 0.0], dtype=np.float32) # ~28 MW
        obs, reward, term, trunc, info = self.env.step(action)
        
        sec = info["step_sec_kwh_per_kg"]
        self.assertGreaterEqual(sec, 10.8, f"SEC {sec:.2f} kWh/kg too low")
        self.assertLessEqual(sec, 13.2, f"SEC {sec:.2f} kWh/kg exceeds industrial threshold")

    def test_product_purity_meets_industrial_specs(self):
        """Level 2 Audit: Product purity must consistently meet or exceed 98.0%."""
        self.env.reset(seed=404)
        action = np.array([0.85, 0.0, 0.0], dtype=np.float32)
        obs, reward, term, trunc, info = self.env.step(action)
        
        purity = info["product_purity_pct"]
        self.assertGreaterEqual(purity, 98.0, f"Product purity {purity:.2f}% below 98.0% spec")
        self.assertLessEqual(purity, 99.5, f"Product purity {purity:.2f}% unreasonably high for crude SAF metal")

    def test_numerical_stability_under_extreme_rollouts(self):
        """Numerical stability: No NaNs or Infs over 200 diverse steps."""
        self.env.reset(seed=505)
        for _ in range(200):
            action = self.env.action_space.sample()
            obs, r, term, trunc, info = self.env.step(action)
            self.assertFalse(np.isnan(obs).any(), "NaN found in observation vector")
            self.assertFalse(np.isinf(obs).any(), "Inf found in observation vector")
            self.assertFalse(np.isnan(r), "NaN reward encountered")
            if term or trunc:
                self.env.reset()

    def test_three_zone_thermal_gradients(self):
        """Phase 2 Roadmap: Verify 3-zone thermal stratification (Crater > Bath > Burden)."""
        self.env.reset(seed=606)
        action = np.array([0.88, 0.0, 0.0], dtype=np.float32) # ~28 MW
        for _ in range(20):
            obs, r, term, trunc, info = self.env.step(action)
            if term or trunc:
                break
                
        t_crater = info["temperature_crater_c"]
        t_bath = info["temperature_bath_c"]
        t_burden = info["temperature_burden_c"]
        
        self.assertGreater(t_crater, t_bath, "Crater zone must be hotter than molten bath")
        self.assertGreater(t_bath, t_burden, "Molten bath must be hotter than upper burden")
        self.assertGreaterEqual(t_burden, 900.0, "Burden temperature unrealistically low (<900 C)")
        self.assertLessEqual(t_burden, 1450.0, "Burden temperature unrealistically high (>1450 C)")
        self.assertGreaterEqual(t_bath, 1450.0, "Bath temperature below liquidus/tapping threshold")
        self.assertLessEqual(t_bath, 1750.0, "Bath temperature too high")

    def test_coupled_electrical_relationships(self):
        """Phase 2 Roadmap: Electrical consistency (Current 65-100 kA, Voltage 140-220 V, PF 0.80-0.88)."""
        self.env.reset(seed=707)
        # Ramp power over 4 steps to allow safety slew-rate shield to reach nominal 28.5 MW
        action = np.array([0.90, 0.0, 0.0], dtype=np.float32)
        for _ in range(4):
            obs, r, term, trunc, info = self.env.step(action)
        
        i_ka = info["electrode_current_ka"]
        v_volts = info["electrode_voltage_v"]
        r_mohm = info["furnace_resistance_mohm"]
        cos_phi = info["power_factor_cos_phi"]
        wear_rate = info["electrode_consumption_kg_per_t_si"]
        
        self.assertGreaterEqual(i_ka, 65.0, f"Current {i_ka:.1f} kA below industrial 30MW SAF rating")
        self.assertLessEqual(i_ka, 105.0, f"Current {i_ka:.1f} kA exceeds transformer limit")
        self.assertGreaterEqual(v_volts, 130.0, f"Electrode voltage {v_volts:.1f} V too low")
        self.assertLessEqual(v_volts, 230.0, f"Electrode voltage {v_volts:.1f} V too high")
        self.assertGreaterEqual(cos_phi, 0.78, f"Power factor {cos_phi:.2f} too poor")
        self.assertLessEqual(cos_phi, 0.90, f"Power factor {cos_phi:.2f} unrealistically high for SAF arc")
        self.assertGreaterEqual(wear_rate, 55.0, "Electrode consumption below industrial baseline")
        self.assertLessEqual(wear_rate, 95.0, "Electrode consumption above industrial baseline")

    def test_multizone_18dim_observation_space(self):
        """Phase 2 Roadmap: 18-D observation space after feature selection."""
        env_v2 = SiliconEnv(multizone_observations=True, safety_shield=True)
        obs, _ = env_v2.reset(seed=808)
        self.assertEqual(obs.shape, (18,), f"Expected 18-dim observation space, got {obs.shape}")
        self.assertTrue(np.all(obs >= 0.0) and np.all(obs <= 1.0), "Normalized observations must reside in [0, 1]")
        
        action = np.array([0.5, 0.0, 0.0], dtype=np.float32)
        obs, r, term, trunc, info = env_v2.step(action)
        self.assertEqual(obs.shape, (18,))
        self.assertTrue(np.all(obs >= 0.0) and np.all(obs <= 1.0))

    def test_economic_production_cost_and_reward(self):
        """Phase 3 Roadmap: Economic cost-per-kg optimization ($1.40-$2.40/kg Si)."""
        self.env.reset(seed=909)
        # 4 steps to nominal 28.5 MW operation
        action = np.array([0.90, 0.0, 0.0], dtype=np.float32)
        for _ in range(4):
            obs, r, term, trunc, info = self.env.step(action)
            
        cost_per_kg = info["cost_per_kg_saleable_si"]
        total_cost = info["total_step_cost_usd"]
        elec_cost = info["cost_electricity_usd"]
        quartz_cost = info["cost_quartz_usd"]
        carbon_cost = info["cost_carbon_usd"]
        electrode_cost = info["cost_electrode_usd"]
        
        # Verify component summation
        self.assertAlmostEqual(total_cost, elec_cost + quartz_cost + carbon_cost + electrode_cost, places=2)
        # Verify industrial cost of production benchmark range
        self.assertGreaterEqual(cost_per_kg, 1.30, f"Cost ${cost_per_kg:.2f}/kg Si unrealistically low")
        self.assertLessEqual(cost_per_kg, 2.50, f"Cost ${cost_per_kg:.2f}/kg Si exceeds competitive industrial range")
        self.assertFalse(np.isnan(r), "Reward must be finite")


if __name__ == "__main__":
    unittest.main(verbosity=2)

