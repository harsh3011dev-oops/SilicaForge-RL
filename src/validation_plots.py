import sys
import os
import matplotlib.pyplot as plt
import numpy as np

# Add the src folder to the python path so we can import the simulator
sys.path.append(os.path.join(os.path.dirname(__file__), 'simulator'))
from chem_engine import SiliconSimulator

def run_validation():
    print("Loading Simulator...")
    # Go up one directory to access the data folder
    thermo_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'si_c_o_thermo.yaml')
    sim = SiliconSimulator(thermo_path)
    
    temperatures = np.linspace(1400, 2200, 40)
    pressure = 1.0 # 1 atm
    
    # We will test the stoichiometric ratio: 1 SiO2 + 2 C
    quartz_moles = 1.0
    carbon_moles = 2.0
    argon_moles = 0.0 # No sweep gas for this test
    
    si_yields = []
    sio_lost = []
    
    print("Running simulations across temperatures...")
    for T in temperatures:
        si, sio = sim.run_simulation(T, pressure, quartz_moles, carbon_moles, argon_moles)
        si_yields.append(si)
        sio_lost.append(sio)
        
    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(temperatures, si_yields, 'b-', label='Silicon Yield (moles)', linewidth=2)
    plt.plot(temperatures, sio_lost, 'r--', label='SiO Gas Lost (moles)', linewidth=2)
    
    plt.title('Validation: Carbothermic Reduction of SiO2 (1 atm)')
    plt.xlabel('Temperature (°C)')
    plt.ylabel('Moles of Product (from 1 mole SiO2)')
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.legend()
    
    plot_path = os.path.join(os.path.dirname(__file__), '..', 'validation_plot.png')
    plt.savefig(plot_path)
    print(f"Plot saved successfully to {plot_path}")

if __name__ == "__main__":
    run_validation()
