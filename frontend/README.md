# SilicaForge-RL

> **Warm Industrial SAF Digital Twin & Autonomous RL Control Console**  
> An AI-optimized Submerged Electric Arc Furnace (28.5 MW Commercial Plant) for Carbothermic Silica Reduction:  
> $$\text{SiO}_2 + 2\text{C} \longrightarrow \text{Si} + 2\text{CO}$$

---

## 🌋 Features

1. **3D Macroscopic Submerged Arc Furnace Twin (Three.js)**
   - Cast bronze outer casing (`#3D312A`) with cutaway revealing alumina ceramic firebrick lining (`#C47A47`).
   - 3 heavy graphite electrodes in delta triangular pitch suspended from copper hydraulic clamps.
   - Dynamic real-time electrode stroke translation driven by PPO AI actions.
   - Golden-white electric plasma discharge arcs with stochastic micro-jitter.
   - Molten liquid silicon pool with fluid ripple waves and temperature-sensitive incandescent glow (1450°C cherry red $\to$ 1866.6°C molten gold-orange).
   - Bilowing off-gas chimney smoke system reacting dynamically to live volatile $\text{SiO}$ stack loss.
   - OrbitControls with Isometric, Hearth Arc, and Top Delta camera presets.

2. **Microscopic Atom-to-Atom Reaction Window (Floating PiP Sub-Viewport)**
   - 3D molecular simulation showing quartz ($\text{SiO}_2$), carbon ($C$), and gaseous carbon monoxide ($CO$).
   - Thermal agitation kinetics above 1800°C: bond dissociation, $CO$ gas plume evolution, and pure $Si$ condensation into liquid lattice.
   - Stoichiometric locking gauge tracking $C/\text{Si} = 1.996$.

3. **Telemetry & Real-Time KPI Console**
   - 7 Key Performance Indicator (KPI) cards: Hearth Temperature (1866.6°C Sweet Spot), Si Direct Recovery (94.01%), Specific Energy (11.33 kWh/kg), Off-Gas SiO Loss (2.30%), Active Power (27.57 MW), Electricity Cost ($1,792.08/hr), and Stoichiometry Ratio ($C/\text{Si} = 1.996$).
   - Dual-Channel live SVG strip chart with shaded 1850°C–1900°C sweet-spot band.
   - Monospace streaming feed of PPO agent decisions.
   - Manual SCADA actuator override sliders.

4. **10/10 Metallurgical Scientific Findings Modal**
   - Verified against Schei, Tveit & Vatland (1998) literature standards and NIST-JANAF thermochemical tables.
   - 5 Major thermochemical discovery cards.
   - Full comparative benchmark verification table.

---

## 🚀 Quick Start (Local Setup)

### Prerequisites
- **Node.js**: v18.0.0 or higher (v20+ recommended)
- **npm** or **bun** / **yarn** / **pnpm**

### 1. Installation
Extract the zip file, open your terminal in the extracted folder, and install dependencies:

```bash
npm install
```

*(Note: `.npmrc` is already included to ensure peer dependency resolution across all npm versions.)*

### 2. Running in Development

**Option A — Full-Stack Mode (Recommended, includes live `/api/step` backend):**
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

**Option B — Standalone Vite Client Mode:**
```bash
npm run dev:client
```
Open [http://localhost:5173](http://localhost:5173). The frontend includes a built-in simulation engine fallback that runs smoothly even without the backend.

### 3. Production Build
To create an optimized production bundle:
```bash
npm run build
```
The output will be placed in the `dist/` directory.

To preview the production build locally:
```bash
npm run preview
```

---

## 📂 Project Structure

```
├── public/                 # Static assets & downloadable files
│   └── silicaforge-rl-ui.zip
├── src/
│   ├── components/
│   │   ├── MicroKineticsHUD.tsx          # 3D molecular reaction PiP HUD
│   │   ├── ScientificFindingsModal.tsx   # 10/10 Metallurgical benchmark modal
│   │   ├── TelemetryKPIPanel.tsx         # KPI cards, dual-channel chart & PPO feed
│   │   ├── ThreeFurnaceViewport.tsx      # 3D SAF digital twin with Three.js
│   │   └── TopNavigationBar.tsx          # SCADA header bar & actions
│   ├── types/
│   │   └── furnace.ts                    # Metallurgical types, benchmarks & discoveries
│   ├── App.tsx                           # Root orchestrator with telemetry polling
│   ├── index.css                         # Tailwind CSS base styles & typography
│   └── main.tsx                          # React 19 entry point
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── .npmrc                  # npm configuration for clean peer dependency handling
├── index.html              # HTML entry point with Plus Jakarta Sans & JetBrains Mono
├── package.json            # Project dependencies and run scripts
├── server.ts               # Express full-stack server & /api/step endpoint
├── tsconfig.json           # TypeScript configuration
└── vite.config.ts          # Vite bundler configuration
```

---

## ⚡ Tech Stack

- **Framework**: React 19 + TypeScript
- **3D Engine**: Three.js (r186+) with OrbitControls
- **Styling**: Tailwind CSS v4 (Warm Tactile Industrial Palette)
- **Icons**: Lucide React
- **Full-Stack Server**: Express + TSX
