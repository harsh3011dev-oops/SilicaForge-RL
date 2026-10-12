# 🌋 SilicaForge-RL: Autonomous Submerged Arc Furnace (SAF) Optimization

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Gymnasium](https://img.shields.io/badge/Gymnasium-v1.0+-brightgreen.svg)](https://gymnasium.farama.org/)
[![Stable-Baselines3](https://img.shields.io/badge/SB3-PPO-orange.svg)](https://stable-baselines3.readthedocs.io/)

**SilicaForge-RL** is a physics-informed Reinforcement Learning framework and digital twin designed to optimize carbothermic silica reduction inside industrial **Submerged Electric Arc Furnaces (SAF)**. 

Using Proximal Policy Optimization (PPO), the autonomous agent controls electrical power, electrode positioning, and stoichiometry to maximize liquid silicon yield (>85–90%), prevent volatile SiO gas escape, and minimize specific energy consumption (MWh/t Si) while safeguarding refractory integrity (<2250°C).

---

## 🔬 Metallurgical Background & Physics

The carbothermic reduction of silica ($SiO_2$) into high-purity Silicon ($Si$) occurs in high-temperature submerged arc furnaces via multiple interdependent reactions:

1. **Inner High-Temperature Zone (>1811°C)**:
   $$\text{SiO}_2 + 2\text{C} \rightarrow \text{Si (liq)} + 2\text{CO (g)}$$
   $$\text{SiC} + \text{SiO}_2 \rightarrow 3\text{Si (liq)} + 2\text{CO (g)}$$
2. **Intermediate Gas Evolution & Condensation Zone (1500°C – 1800°C)**:
   $$\text{SiO}_2 + \text{C} \rightarrow \text{SiO (g)} + \text{CO (g)}$$
   $$\text{SiO (g)} + 2\text{C} \rightarrow \text{SiC (s)} + \text{CO (g)}$$

### Furnace Physical Challenges Addressed
- **SiO Off-Gas Loss**: Volatile SiO escapes if carbon bed stoichiometry or burden penetration is suboptimal.
- **Thermal Inertia & Refractory Limits**: Thermal mass obeys first-order differential heat transfer equations ($dQ/dt = P_{in} - P_{loss}$). Operating above 2250°C causes catastrophic refractory breakdown.
- **Dynamic Curriculum Annealing**: Smoothly transitions the agent from yield exploration to severe energy penalty optimization to eliminate reward hacking.

---

## ⚡ Reinforcement Learning Architecture

| Dimension | Variable | Range | Description |
|---|---|---|---|
| **Action [0]** | Power Setpoint | $0.0 - 30.0 \text{ MW}$ | Furnace electrical power input |
| **Action [1]** | Electrode Position | $-1.0 \text{ to } +1.0$ | Arc immersion depth & charge penetration |
| **Action [2]** | C/Si Feed Ratio | $1.8 - 2.2$ | Stoichiometric reducing agent feed |

### Observation State (7-Dimensional Continuous)
- Temperature ($T$, °C)
- Silicon Yield ($\%$)
- Carbon Bed Conversion ($\%$)
- SiO Gas Partial Pressure ($P_{SiO}$, bar)
- Cumulative Energy Consumption ($\text{MWh}$)
- Electrode Immersion Depth ($m$)
- Dynamic Curriculum Phase ($\lambda_{cost}$)

---

## 📂 Repository Structure

```text
SilicaForge-RL/
├── src/
│   ├── env/
│   │   └── silicon_env.py          # Gymnasium SAF dynamic environment
│   ├── optimization/
│   │   ├── train_rl.py             # PPO training loop with auto-resume & callbacks
│   │   ├── eval_model.py           # Evaluation & performance benchmarks
│   │   ├── eval_continuous.py      # Multi-episode continuous validation
│   │   └── run_optuna.py           # Hyperparameter tuning pipeline
│   ├── web/
│   │   ├── app.py                  # FastAPI SCADA backend & live telemetry
│   │   └── static/
│   │       └── scada.html          # Industrial SCADA UI dashboard
│   └── validation_plots.py         # Matplotlib phase & thermodynamic plotting
├── phase_diagram.png               # Ellingham & equilibrium phase diagram
├── validation_plot.png             # Yield vs Temperature verification curve
├── requirements.txt                # Python package dependencies
├── .gitignore                      # Git ignore configuration
└── README.md                       # Documentation
```

---

## 🚀 Quick Start

### 1. Installation
Clone the repository and set up a virtual environment:
```bash
git clone https://github.com/harsh3011dev-oops/SilicaForge-RL.git
cd SilicaForge-RL

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Train the RL Agent
Train the agent using PPO with curriculum learning:
```bash
python src/optimization/train_rl.py
```
> *The training loop includes automatic checkpointing and can be paused (`Ctrl+C`) and resumed at any time.*

### 3. Evaluate the Agent
Benchmark the trained policy against industrial baselines:
```bash
python src/optimization/eval_model.py
```

### 4. Launch the SCADA Control Dashboard
Start the real-time furnace telemetry server:
```bash
python src/web/app.py
```
Open [http://localhost:8000/static/scada.html](http://localhost:8000/static/scada.html) in your browser to monitor real-time temperature, electrode immersion, yields, and manual overrides.

---

## 📊 Industrial Target Benchmarks

| Metric | Industrial Benchmark | SilicaForge-RL Agent |
|---|---|---|
| **Furnace Temperature** | 1800°C – 1950°C | ~1860°C (Stable) |
| **Silicon Yield** | 82% – 88% | **>88%** |
| **Specific Power** | 11 – 13 MWh/t Si | Optimized via Annealing |
| **SiO Loss Rate** | < 12% | Substantially Reduced |

---

## 📜 License
This project is open-source and licensed under the [MIT License](LICENSE).
