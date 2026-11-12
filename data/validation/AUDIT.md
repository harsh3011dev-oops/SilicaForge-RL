# Simulation Validation Audit

## Scope

This audit compares four controllers only inside the current `SiliconEnv`
simulation. It is not evidence of performance on a physical submerged arc
furnace.

- Runs per controller: 30
- Rollout horizon: 96 steps (24 simulated hours at 15 minutes per step)
- Initial-state seeds: 2026 through 2055
- Controllers: PPO, fixed power, temperature PID, seeded random

## Results

| Controller | Mean yield | Mean SEC | Mean SiO loss | Mean maximum temperature | Safety terminations |
|---|---:|---:|---:|---:|---:|
| PPO | 92.42% +/- 0.12% | 11.337 +/- 0.015 kWh/kg | 2.435% +/- 0.055% | 1931.6 C | 0/30 |
| Fixed power | 92.42% +/- 0.12% | 11.337 +/- 0.015 kWh/kg | 2.432% +/- 0.055% | 1931.6 C | 0/30 |
| PID temperature | 93.03% +/- 0.03% | 11.273 +/- 0.004 kWh/kg | 2.267% +/- 0.014% | 1896.0 C | 0/30 |
| Seeded random | 2.93% +/- 1.73% | 345.524 +/- 370.177 kWh/kg | 0.258% +/- 0.315% | 1866.8 C | 0/30 |

## Finding

The PPO policy is effectively a fixed operating-point policy in this test. For
the first test seed, PPO selected 27.5704 MW and C/Si 1.9956 while the fixed
baseline selected 27.5700 MW and C/Si 1.9960. Their aggregate results are
therefore indistinguishable at the reported precision.

The tuned temperature PID baseline performed better than PPO in this simulator:

- Yield: +0.61 percentage points.
- SEC: -0.065 kWh/kg.
- Mean SiO loss: -0.168 percentage points.
- Mean peak temperature: -35.5 C.

## Interpretation

The test establishes that the PPO model is much better than random actions in
the current simulator, but it does not establish an advantage over a simple
feedback controller. The present claim should be: "PPO reaches a good simulated
operating point," not "PPO outperforms conventional control."

## Limits of This Test

- All controllers use the same simplified environment and its heuristic yield
  and SiO-loss curves.
- The rollouts vary only their initial temperature; they do not include feed
  disturbances, sensor noise, power failures, or changing heat loss.
- The environment currently does not make electrode movement affect the furnace
  dynamics, so no controller can demonstrate electrode-control benefit.
- The temperature standard deviation includes the cold-start period. Report
  steady-state metrics separately before comparing thermal stability claims.

## Next Work

1. Add disturbance scenarios and evaluate all controllers on held-out seeds.
2. Make electrode position and burden mass influence the simulated dynamics.
3. Calculate mass balance from species/feed quantities rather than a fixed value.
4. Calibrate simulator parameters against historical furnace data.
5. Repeat this comparison in shadow mode before any operator-facing use.
