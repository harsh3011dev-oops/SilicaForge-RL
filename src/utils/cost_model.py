import json
import os

class CostModel:
    def __init__(self, config_path="config.json"):
        # Resolve path relative to the project root
        if not os.path.isabs(config_path):
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            config_path = os.path.join(base_dir, config_path)
            
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        self.costs = config.get("costs", {})
        self.elec_price = self.costs.get("electricity_per_kwh", 7.0)
        self.quartz_price = self.costs.get("quartz_per_kg", 5.0)
        self.carbon_price = self.costs.get("carbon_per_kg", 20.0)
        self.argon_price = self.costs.get("argon_per_liter", 0.5)

    def calculate_cost(self, temperature_c, pressure_atm, quartz_moles, carbon_moles, argon_moles):
        """
        Calculates the approximate operational cost for a single simulation step.
        Returns cost in INR (₹).
        """
        # 1. Material Costs
        # Molar mass: SiO2 = ~60g/mol, C = ~12g/mol
        quartz_kg = (quartz_moles * 60.0) / 1000.0
        carbon_kg = (carbon_moles * 12.0) / 1000.0
        argon_liters = argon_moles * 24.0 # approximate volume at room temp
        
        mat_cost = (quartz_kg * self.quartz_price) + \
                   (carbon_kg * self.carbon_price) + \
                   (argon_liters * self.argon_price)
                   
        # 2. Energy Cost (Heuristic for Heating)
        # Base energy to heat from 25C to target temperature
        # Just a dummy heuristic: higher temp = exponentially more electricity
        # E.g., 1000C = 10 kWh, 2000C = 40 kWh
        energy_kwh = (temperature_c / 1000.0) ** 2 * 10.0
        
        # Extra energy for compression if pressure > 1 atm
        compression_energy = max(0, pressure_atm - 1.0) * 2.0
        
        total_energy = energy_kwh + compression_energy
        energy_cost = total_energy * self.elec_price
        
        total_cost = mat_cost + energy_cost
        
        return total_cost

if __name__ == "__main__":
    cm = CostModel()
    cost = cm.calculate_cost(1700, 1.0, 1.0, 2.0, 0.0)
    print(f"Estimated Cost for baseline reaction: ₹{cost:.2f}")
