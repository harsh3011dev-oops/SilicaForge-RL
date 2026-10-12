# SCADA-84: Carbothermic Reduction of Silica (SiO2)

A retro-styled industrial metallurgical console simulating Reinforcement Learning (PPO Agent) control of quartz reduction to liquid Silicon.

## Key Features
1. **Retro Vessel Display**:
   - Dynamic temperature glow from cold dark steel (1000°C) to incandescent white plasma (2200°C).
   - Molten liquid Silicon pool filling at the bottom crucible with level ticks.
   - Real-time rising volatile SiO smoke plume escaping from the exhaust stack.
   - Graphite electrodes with high-energy electrical discharge arcs.

2. **Autonomous PPO Agent (Virtual Operator)**:
   - Controls Temperature (1000°C - 2200°C), Chamber Pressure (0.1 - 10.0 atm), and Argon Sweep Gas Flow (0.0 - 5.0 L/min) every second.
   - Maximizes Silicon Yield (SiO2 + 2C -> Si + 2CO) while minimizing Electricity Operating Cost (₹) and volatile SiO Gas Loss.

3. **Retro CRT Oscilloscope Line Chart**:
   - Dual-channel trace tracking Cost (₹/hr) vs Silicon Yield (%) over time.

4. **Modes**:
   - [AUTO] PPO Virtual Operator.
   - [MANUAL] Tactile Operator Override with sliders and presets.

## Installation & Running
```bash
npm install
npm run dev
```
