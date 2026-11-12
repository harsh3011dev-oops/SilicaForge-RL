# Disturbance Validation Audit

## Scope

This is a 30-seed, 96-step simulator-only comparison. It tests four
controllers against five scenarios. It is not a claim about physical furnace
performance.

## Scenarios

| Scenario | Simulator disturbance |
|---|---|
| Nominal | No added disturbance |
| High heat loss | Heat-loss term multiplied by 1.25 |
| Power derate | Available power reduced by 12% |
| Low-reactivity feed | Yield factor reduced to 0.92 |
| Sensor noise | Temperature observation noise: 10 C standard deviation |

## Decision Results

| Scenario | PPO yield / SEC / safety | PID yield / SEC / safety | Finding |
|---|---|---|---|
| Nominal | 92.42% / 11.34 / 0 of 30 | 93.03% / 11.27 / 0 of 30 | PID is slightly better. |
| High heat loss | 39.62% / 26.45 / 0 of 30 | 50.93% / 20.28 / 0 of 30 | PPO does not add enough power. |
| Power derate | 57.55% / 18.21 / 0 of 30 | 62.11% / 16.71 / 0 of 30 | PID adapts better to reduced available power. |
| Low-reactivity feed | 45.35% / 26.26 / 30 of 30 | 85.84% / 12.22 / 0 of 30 | PPO causes a safety failure in every run. |
| Sensor noise | 92.42% / 11.34 / 0 of 30 | 92.18% / 11.38 / 0 of 30 | PPO is unchanged because it behaves as a near-fixed policy. |

SEC is reported in kWh/kg. Values are means across 30 rollouts.

## Conclusion

The current PPO policy is not robust enough for an industrial-control claim.
It performs like the fixed-power baseline under nominal, heat-loss, and
power-derate cases. Under low-reactivity feed it overheats above the 2250 C
safety threshold in all 30 trials, while the simple PID controller stays safe.

The PPO policy should not move to real data, shadow mode, PLC integration, or
plant operation until it is retrained and passes this disturbance suite.

## Required Next Changes

1. Make electrode position affect thermal and chemical dynamics; otherwise the
   third action cannot be learned or validated.
2. Add feed/reactivity, heat-loss, and power-availability randomization during
   PPO training, not only during evaluation.
3. Add a safety shield that clips unsafe power commands before `env.step`.
4. Retain PID as the mandatory baseline and accept PPO only if it exceeds PID
   across every held-out scenario without safety failures.
5. After simulator robustness is demonstrated, calibrate against historical
   plant data before any shadow-mode evaluation.
