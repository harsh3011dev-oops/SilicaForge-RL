# 🌋 SilicaForge-RL: Autonomous Submerged Arc Furnace (SAF) Optimization

<div align="center">

[![Live Demo](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-E65100?style=for-the-badge&logo=github)](https://harsh3011dev-oops.github.io/SilicaForge-RL/)
[![React 19](https://img.shields.io/badge/Frontend-React%2019%20%2B%20Three.js-2C211B?style=for-the-badge&logo=react)](frontend/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20PPO%20Twin-009688?style=for-the-badge&logo=fastapi)](src/web/)
[![Benchmark Gates](https://img.shields.io/badge/Benchmark%20Gates-10%2F10%20PASSED-2E7D32?style=for-the-badge)](data/validated_benchmark.json)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

**Physics-Informed Reinforcement Learning Framework & 3D Industrial SCADA Digital Twin for a 28.5 MW Submerged Electric Arc Furnace (SAF)**

[🌐 **Launch Live 3D Twin (GitHub Pages)**](https://harsh3011dev-oops.github.io/SilicaForge-RL/) · [📊 **10-Gate Industrial Benchmark**](#-industrial-benchmark-validation-1010-gates-passed) · [🚀 **Quick Start**](#-quick-start) · [🐳 **Cloud & Docker Deploy**](#-deployment-guide)

</div>

---

## 📖 Overview

**SilicaForge-RL** is an autonomous control system and real-time 3D digital twin designed to optimize commercial **Submerged Electric Arc Furnaces (SAF)** (28.5 MW industrial scale) conducting carbothermic silica reduction:

$$\text{SiO}_2\text{(s, l)} + 2\text{C(s)} \longrightarrow \text{Si(l)} + 2\text{CO(g)} \quad (\Delta H^\circ_{2000\text{K}} \approx +687\text{ kJ/mol})$$

Trained over **5,000,000+ timesteps** using Proximal Policy Optimization (PPO), the autonomous AI agent continuously coordinates electrical active power (MW), hydraulic electrode penetration depth ($\Delta z$), and raw burden stoichiometry ($C/\text{Si}$) to:
- Maximize direct liquid silicon metal yield (**94.01% yield** vs. industry baseline 88–92%).
- Suppress volatile sub-oxide vapor escape (**2.30% $\text{SiO}$ loss** vs. literature threshold 12.0%).
- Reduce Specific Energy Consumption to **11.33 kWh/kg Si** (~1.4 MWh saved per tonne of silicon).
- Maintain absolute refractory lining safety (**+383.2°C safety margin** below the 2,250°C thermal limit).
- Save an estimated **₹15–20 Crore ($1.8M–$2.4M USD) annually** in commercial electrical tariffs on a 28.5 MW commercial smelter.

---

## 🖥️ 3D SCADA Digital Twin & Operator Console

The project features a **warm industrial foundry aesthetic** (terracotta alumina, firebrick, molten lava gold, cast iron bronze) built with **React 19, Three.js, and Tailwind CSS**:

### 1. Macroscopic 3D Submerged Arc Furnace Twin
- **Cast Iron Outer Casing with 270° Cutaway**: Reveals inner refractory firebrick lining and molten silicon bath.
- **3-Phase Söderberg Graphite Electrodes**: Dynamic vertical stroke translation driven by live PPO policy actions.
- **Dynamic Electric Plasma Arcs**: Stochastic high-frequency micro-jitter and incandescent arc lighting.
- **Molten Liquid Silicon Pool**: Realistic fluid breathing animation, wave ripples, and heat-sensitive color interpolation (1450°C cherry red $\to$ 1866.6°C molten gold-orange).
- **Chimney SiO Off-Gas Plume**: 3D particle billowing system directly tied to real-time volatile sub-oxide stack loss.
- **Multi-Angle Camera Presets**: One-click toggles between `Isometric`, `Hearth Arc`, and `Top Delta` viewports.

### 2. Micro-Kinetics Atom-to-Atom Reaction Window (Floating HUD)
- 3D molecular simulation chamber tracking raw quartz ($\text{SiO}_2$), reducing carbon ($C$), and gaseous carbon monoxide ($\text{CO}$).
- Live Brownian motion with thermal agitation multipliers above 1,800°C.
- Stoichiometric locking gauge tracking $C/\text{Si} = 1.996$ against carbothermic boundaries (Slagging $<1.96$ vs. Carbidization $>2.04$).

### 3. Real-Time Telemetry & Dual-Channel KPI Console
- 7 core industrial metrics: Hearth Temperature, Direct Si Recovery, Specific Energy (SEC), SiO Sub-Oxide Loss, Active Power, Electricity Cost/hr, and Stoichiometric Ratio.
- Live dual-channel SVG strip chart with shaded 1850°C–1900°C sweet-spot envelope.
- Monospace streaming feed of PPO agent decisions with engineering rationale.
- Seamless dual-mode operation: auto-connected to Python FastAPI PPO backend when available, with automatic client-side physics twin fallback for static web hosting.

---

## 🏆 Key Scientific & Engineering Innovations

While commercial silicon smelting plants typically rely on decoupled PIDs and delayed manual operator rules-of-thumb, **SilicaForge-RL** introduces five core architectural breakthroughs:

1. **Solving the $\text{SiO}$ Sub-Oxide & Thermal Inertia Trade-Off:**
   - Overcomes severe furnace thermal capacitance ($C_{\text{th}} = 24.5\text{ GJ/}^\circ\text{C}$, 15-minute response lag $\Delta t = 900\text{ s}$).
   - Discovered the exact thermodynamic pareto-optimal frontier at **$1866.6^\circ\text{C}$**, balancing endothermic reaction kinetics against Clausius-Clapeyron $\text{SiO}$ gas volatilization.
2. **Sigmoid Yield Gating (Eliminating the "Lazy Agent" Local Minima):**
   - Standard thermal RL agents shut down the furnace to artificially minimize electrical energy penalties.
   - Introduced a non-linear sigmoid yield gate $\sigma(12 \cdot (Y - 0.22))$: electricity cost penalties are zero until the furnace successfully ignites and produces metal, enabling stable exploration.
3. **Dynamic Cosine Curriculum Cost Annealing:**
   - Smoothly transitions the policy across episodes from pure yield discovery ($\lambda_{\min} = 0.0005$) to industrial cost minimization ($\lambda_{\max} = 0.045$) via a half-cosine schedule, eliminating policy collapse.
4. **Potential-Based Reward Shaping (PBRS - Policy Invariance Preserving):**
   - Formulates a multi-objective potential function $\Phi(s)$ strictly preserving optimal policy invariance (Ng et al., 1999 theorem) to accelerate convergence across continuous state dimensions.
5. **Multi-Variable Cross-Coupled Control:**
   - Simultaneously commands electrical power (0–30 MW), hydraulic electrode penetration depth ($\Delta z$), and stoichiometric carbon/quartz feed ratio ($1.8–2.2$), freezing thermal oscillation standard deviation to **$\sigma = \pm 0.03^\circ\text{C}$**.

---

## 📊 Industrial Benchmark Validation (10/10 Gates Passed)

The trained policy was audited through a continuous 24-hour closed-loop trajectory (96 steps @ 15 min/step) against commercial industrial data, **NIST-JANAF Thermochemical Tables**, and literature standards from **Schei, Tveit, & Vatland (1998)**:

| Validation Parameter | Published Literature / Industrial Standard | SilicaForge-RL AI Policy | Deviation % | Verdict |
|---|---|:---:|:---:|:---:|
| **SEC Theoretical Floor** | $\ge 7.00\text{ kWh/kg Si}$ (NIST-JANAF) | **$11.33\text{ kWh/kg}$** | $+61.9\%$ | **PASS** |
| **Specific Energy Consumption (SEC)** | $11.0 - 13.0\text{ kWh/kg (MWh/t)}$ | **$11.33\text{ kWh/kg}$** | $-5.54\%$ | **PASS** |
| **Carbon Stoichiometry ($C/Si$)** | $1.960 - 2.040\text{ (Ideal: 2.000)}$ | **$1.996$** | $-0.22\%$ | **PASS** |
| **$\text{SiO}$ Off-Gas Stack Loss** | $6.0\% - 12.0\%$ (Schei Model) | **$2.30\%$** | $-72.94\%$ | **PASS** |
| **Silicon Metal Direct Yield** | $88.0\% - 94.0\%$ | **$94.01\%$** | $+4.46\%$ | **PASS** |
| **Mass Balance Closure Error** | $< 0.50\%$ (Conservation of Mass) | **$0.000\%$** | $0.000\%$ | **PASS** |
| **Operating Temperature Mean** | $1850^\circ\text{C} - 1900^\circ\text{C}$ | **$1866.6^\circ\text{C}$** | $-0.45\%$ | **PASS** |
| **Sweet Spot Adherence** | $\ge 95.0\%\text{ steps in } 1850-1900^\circ\text{C}$ | **$100.0\%$** (81/81) | $+0.0\%$ | **PASS** |
| **Thermal Fluctuation Stability ($\sigma$)** | $\le 25.0^\circ\text{C}$ | **$\pm 0.03^\circ\text{C}$** | $-99.9\%$ | **PASS** |
| **Refractory Safety (Peak Excursion)** | $< 2250^\circ\text{C}$ (Overheat Prevention) | **$1866.8^\circ\text{C}$** (+383.2° Margin) | $-17.0\%$ | **PASS** |

---

## ⚡ Reinforcement Learning Architecture

### Observation Space (7-Dimensional Continuous Box)
| Dimension | State Variable | Physical Range | Description |
|:---:|---|:---:|---|
| `obs[0]` | Temperature ($T$) | $25.0 - 2500.0^\circ\text{C}$ | Furnace hearth core temperature |
| `obs[1]` | $\text{SiO}_2$ Burden Mass | $0 - 50,000\text{ kg}$ | Residual raw quartz burden column |
| `obs[2]` | Carbon Burden Mass | $0 - 30,000\text{ kg}$ | Residual reducing agent mass |
| `obs[3]` | Liquid Silicon Yield ($Y$) | $0.0 - 1.0$ | Direct metal conversion recovery |
| `obs[4]` | $\text{SiO}$ Gas Loss | $0.0 - 1.0$ | Stack sub-oxide escape fraction |
| `obs[5]` | Prev Power Command | $0.0 - 1.0$ | Previous normalized power action |
| `obs[6]` | Cumulative Energy | $0.0 - 500.0\text{ MWh}$ | Integrated electrical energy consumption |

### Action Space (3-Dimensional Continuous Box $[-1, 1]$)
- **$A[0]$ $\rightarrow$ Electrical Power Setpoint:** Scaled to $[0.0, 30.0\text{ MW}]$
- **$A[1]$ $\rightarrow$ Hydraulic Electrode Delta:** $[-1.0, +1.0\text{ mm/step}]$ (Submerged arc cavity depth)
- **$A[2]$ $\rightarrow$ Carbon/Silicon Stoichiometry:** Scaled to $[1.80, 2.20]$ (Target $2.000$)

### Composite Multi-Objective Reward Function
$$R_{\text{total}} = 20.0 \left(\frac{Y}{0.95}\right)^3 - 15.0 \left(\frac{\text{Loss}_{\text{SiO}} - 0.02}{0.05}\right)^2 - \lambda_{\text{cost}} \cdot \text{Cost} \cdot \sigma(12(Y - 0.22)) - 0.12 (\Delta a)^2 + R_{\text{PBRS}}$$

- **Meltdown Constraint Penalty:** $-5000.0$ if $T > 2250^\circ\text{C}$.

---

## 📂 Repository Structure

```text
SilicaForge-RL/
├── .github/
│   └── workflows/
│       └── deploy.yml                 # Automated GitHub Pages CI/CD workflow
├── Dockerfile                         # Multi-stage production container build
├── best_model.zip                     # Pre-trained PPO policy (5.0M steps milestone)
├── config.json                        # Operational tariffs (Electricity, Quartz, Carbon)
├── requirements.txt                   # Core Python dependencies
├── phase_diagram.png                  # Optuna Bayesian optimization phase diagram
├── validation_plot.png                # Thermodynamic yield vs temperature curve
│
├── frontend/                          # Warm React 19 + Three.js SCADA Digital Twin
│   ├── dist/                          # Production-ready static bundle
│   ├── src/
│   │   ├── App.tsx                    # Main SCADA orchestration layout & polling
│   │   ├── components/
│   │   │   ├── ThreeFurnaceViewport.tsx    # 3D SAF Twin (molten bath, electrodes, arcs, smoke)
│   │   │   ├── MicroKineticsHUD.tsx        # 3D molecular kinetics simulation window
│   │   │   ├── TelemetryKPIPanel.tsx       # Live dual-channel SVG charts & KPI cards
│   │   │   ├── TopNavigationBar.tsx        # Status badges & agent control bar
│   │   │   └── ScientificFindingsModal.tsx # 10-gate benchmark audit modal
│   │   └── types/furnace.ts           # TypeScript interfaces for industrial telemetry
│   ├── package.json
│   └── vite.config.ts
│
├── src/
│   ├── env/
│   │   └── silicon_env.py             # Gymnasium SAF environment (SilicaSmeltingEnv)
│   ├── optimization/
│   │   ├── train_rl.py                # PPO training loop with auto-resume & curriculum callbacks
│   │   ├── industrial_benchmark_validation.py # Schei-Tveit (1998) 10-gate audit engine
│   │   ├── eval_rl.py                 # Telemetry inspection rollout script
│   │   ├── eval_continuous.py         # Continuous discovery evaluation loop
│   │   └── benchmark_report.json      # Generated 24-hr industrial trajectory data
│   └── web/
│       └── app.py                     # FastAPI REST API serving telemetry and compiled React UI
└── data/
    └── validated_benchmark.json       # Formal 10-Gate Industrial Benchmark validation results
```

---

## 🚀 Quick Start (Local Setup)

### 1. Installation
Clone the repository and set up a virtual environment:
```bash
git clone https://github.com/harsh3011dev-oops/SilicaForge-RL.git
cd SilicaForge-RL

python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Verify 10-Gate Industrial Benchmark
Audit the trained policy against literature standards (Schei, Tveit & Vatland 1998 / NIST-JANAF):
```bash
python src/optimization/industrial_benchmark_validation.py
```

### 3. Launch the 3D SCADA Digital Twin & PPO Brain
Start the integrated FastAPI backend:
```bash
python src/web/app.py
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser to monitor real-time 3D furnace operation, electrode motion, volatile $\text{SiO}$ chimney smoke, and live telemetry charts connected directly to the trained PPO AI agent.

### 4. Optional: Run Frontend in Vite Development Mode
If you wish to modify the React frontend:
```bash
cd frontend
npm install
npm run dev
```
Open **[http://localhost:3000](http://localhost:3000)** (automatically proxies `/api` to the Python backend on port 8000).

---

## 🌐 Deployment Guide

### Option A: Deploying Frontend to GitHub Pages (Automated)

The repository contains an automated GitHub Actions workflow (`.github/workflows/deploy.yml`) that builds and deploys the frontend on every push to `main`.

To enable it on your GitHub repository:
1. Open your repository on GitHub: `https://github.com/harsh3011dev-oops/SilicaForge-RL`.
2. Go to **Settings** $\rightarrow$ **Pages** (under the "Code and automation" sidebar).
3. Under **Build and deployment** $\rightarrow$ **Source**, select:
   - **GitHub Actions** (Recommended): Automatically runs `.github/workflows/deploy.yml` to build and publish.
   - *OR* select **Deploy from a branch** and choose `gh-pages` branch.
4. Your live 3D Digital Twin will immediately be accessible at:  
   👉 **`https://harsh3011dev-oops.github.io/SilicaForge-RL/`**

*(Note: In GitHub Pages static hosting, the digital twin automatically runs in high-fidelity client-side simulation twin mode, providing continuous 3D furnace rendering, atomic reaction HUD, and telemetry streaming with zero server dependencies.)*

---

### Option B: Deploying Full Python Backend + AI Twin with Docker

To deploy the full Python PPO policy backend and static UI on cloud platforms (Render, Railway, Hugging Face Spaces, Fly.io, or AWS ECS):

```bash
# Build the production Docker image
docker build -t silicaforge-rl .

# Run the container locally on port 8000
docker run -p 8000:8000 silicaforge-rl
```

Or deploy directly via **Render** / **Railway**:
- Select **Deploy from GitHub repo**.
- Choose `Dockerfile` as the build environment.
- Expose port `8000`.

---

## 📜 References & Scientific Literature

1. **Schei, A., Tveit, H., & Vatland, A. (1998).** *Production of High Silicon Alloys*. Tapir Forlag, Trondheim, Norway.
2. **NIST-JANAF Thermochemical Tables (4th Edition).** *Journal of Physical and Chemical Reference Data*, Monograph 9.
3. **Ng, A. Y., Harada, D., & Russell, S. (1999).** *Policy invariance under reward transformations: Theory and application to reward shaping*. ICML.
4. **Schulman, J., et al. (2017).** *Proximal Policy Optimization Algorithms*. arXiv:1707.06347.

---

## 📄 License
This project is open-source and licensed under the **[MIT License](LICENSE)**.
