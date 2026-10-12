import cantera as ct
import os

class SiliconSimulator:
    def __init__(self, thermo_file="data/si_c_o_thermo.yaml"):
        # Ensure the file exists
        if not os.path.exists(thermo_file):
            raise FileNotFoundError(f"Thermodynamics database {thermo_file} not found.")
        
        # Load the custom multiphase mechanism
        self.gas = ct.Solution(thermo_file, 'gas')
        self.quartz = ct.Solution(thermo_file, 'quartz')
        self.graphite = ct.Solution(thermo_file, 'graphite')
        self.liquid_silicon = ct.Solution(thermo_file, 'liquid_silicon')

    def run_simulation(self, temperature_c, pressure_atm, quartz_moles, carbon_moles, argon_moles):
        """
        Runs the thermodynamic equilibrium simulation.
        Returns the moles of Liquid Silicon produced and moles of SiO gas lost.
        """
        T_kelvin = temperature_c + 273.15
        P_pascal = pressure_atm * ct.one_atm
        
        # Set the state of each phase before mixing
        self.gas.TPX = T_kelvin, P_pascal, f'Ar:{argon_moles}' if argon_moles > 0 else 'Ar:1e-10'
        self.quartz.TPX = T_kelvin, P_pascal, 'SiO2(s):1.0'
        self.graphite.TPX = T_kelvin, P_pascal, 'C(gr):1.0'
        self.liquid_silicon.TPX = T_kelvin, P_pascal, 'Si(l):1.0'
        
        # Create the mixture
        self.mix = ct.Mixture([(self.gas, argon_moles if argon_moles > 0 else 1e-10), 
                               (self.quartz, quartz_moles), 
                               (self.graphite, carbon_moles), 
                               (self.liquid_silicon, 0.0)])
        
        # Set the temperature and pressure of the mixture
        self.mix.T = T_kelvin
        self.mix.P = P_pascal
        
        # Equilibrate keeping Temperature and Pressure constant
        try:
            self.mix.equilibrate('TP', max_steps=10000, log_level=0)
        except ct.CanteraError:
            # We silently catch the error and return 0 yield
            # This happens when AI explores impossibly low temperatures
            return 0.0, 0.0
            
        # Extract results
        # Find the index of the phases
        gas_idx = 0
        liquid_si_idx = 3
        
        # Moles of the liquid silicon phase
        si_yield_moles = self.mix.phase_moles(liquid_si_idx)
        
        # Moles of SiO gas lost
        # total gas moles * mole fraction of SiO in gas phase
        total_gas_moles = self.mix.phase_moles(gas_idx)
        sio_fraction = self.gas['SiO'].X[0]
        sio_lost_moles = total_gas_moles * sio_fraction
        
        return si_yield_moles, sio_lost_moles

if __name__ == "__main__":
    # Quick test
    sim = SiliconSimulator("../../data/si_c_o_thermo.yaml")
    
    # Test at 1700 C, 1 atm, 1 mole SiO2, 2 moles Carbon, 0 Argon
    si_moles, sio_lost = sim.run_simulation(1700, 1.0, 1.0, 2.0, 0.0)
    print(f"At 1700°C: Silicon Yield = {si_moles:.4f} moles, SiO Lost = {sio_lost:.4f} moles")
