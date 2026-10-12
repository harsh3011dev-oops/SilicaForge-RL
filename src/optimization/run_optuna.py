import os
import sys
import optuna
import matplotlib.pyplot as plt
import numpy as np

# Add required paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'env'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'simulator'))
from chem_engine import SiliconSimulator
from cost_model import CostModel

def objective(trial):
    # Optuna acts as the "Senior Scientist" trying random recipes
    temp = trial.suggest_float("temperature", 1000.0, 2200.0)
    press = trial.suggest_float("pressure", 0.1, 10.0)
    argon = trial.suggest_float("argon", 0.0, 5.0)
    
    thermo_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'si_c_o_thermo.yaml')
    simulator = SiliconSimulator(thermo_path)
    config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')
    cost_model = CostModel(config_path)
    
    si_yield, sio_lost = simulator.run_simulation(temp, press, 1.0, 2.0, argon)
    cost = cost_model.calculate_cost(temp, press, 1.0, 2.0, argon)
    
    # We want to MAXIMIZE this score
    if si_yield == 0.0 and sio_lost == 0.0 and temp > 1300:
        score = -500.0 - cost
    else:
        score = (si_yield * 5000.0) - cost - (sio_lost * 1000.0)
        
    return score

def run_optimization():
    print("Starting Bayesian Optimization (Phase 5)...")
    # We want to maximize the score
    study = optuna.create_study(direction="maximize")
    
    # Run 100 rapid experiments
    study.optimize(objective, n_trials=100)
    
    print("\nOptimization Finished!")
    print(f"Best Score: {study.best_value}")
    print(f"Best Recipe found by Optuna: {study.best_params}")
    
    # Generate Phase Diagram
    plot_phase_diagram(study)

def plot_phase_diagram(study):
    print("Generating Phase Diagram...")
    temps = [t.params["temperature"] for t in study.trials]
    pressures = [t.params["pressure"] for t in study.trials]
    scores = [t.value for t in study.trials]
    
    plt.figure(figsize=(10, 6))
    sc = plt.scatter(temps, pressures, c=scores, cmap='viridis', s=100, alpha=0.8)
    plt.colorbar(sc, label='Optimization Score (Higher is better)')
    plt.xlabel('Temperature (°C)')
    plt.ylabel('Pressure (atm)')
    plt.title('Silicon Production Phase Diagram (Optuna)')
    plt.grid(True, alpha=0.3)
    
    save_path = os.path.join(os.path.dirname(__file__), '..', '..', 'phase_diagram.png')
    plt.savefig(save_path)
    print(f"Phase Diagram saved to: {save_path}")

if __name__ == "__main__":
    import logging
    # Silence optuna logs to make it cleaner
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    run_optimization()
