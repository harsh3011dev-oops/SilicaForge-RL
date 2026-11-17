import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path("/home/piet/Desktop/harsh /rl project")
json_path = PROJECT_ROOT / "data" / "validation" / "ppo_vs_sac_benchmark_report.json"

with open(json_path) as f:
    full_report = json.load(f)

# Set high-quality styling
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 11
plt.rcParams['axes.edgecolor'] = '#CBD5E1'
plt.rcParams['axes.linewidth'] = 1.2

fig, axes = plt.subplots(2, 2, figsize=(18, 13), dpi=300)

scenarios = [
    "Nominal_Steady",
    "Heat_Loss_Disturbance",
    "Grid_Power_Derate",
    "Low_Reactivity_Feed",
    "Sensor_Noise_Thermal"
]

scenario_display = [
    "Nominal\nSteady State",
    "Heat Loss\n+25% Spike",
    "Power Grid\n-15% Derate",
    "Low Reactivity\n-10% Feed",
    "Pyrometer Noise\n±15°C Jitter"
]

controllers = ["SAC_v2", "PPO_v2", "Industrial_PID", "Fixed_Baseline"]
ctrl_labels = [
    "Curious SAC v2.5 (Proposed)",
    "PPO v2.5 Policy",
    "Industrial PID Baseline",
    "Fixed Setpoint (28.5 MW)"
]

colors = ["#059669", "#2563EB", "#D97706", "#4B5563"]

x = np.arange(len(scenarios))
width = 0.19

# -------------------------------------------------------------
# SUBPLOT 1: SILICON RECOVERY YIELD (%)
# -------------------------------------------------------------
ax1 = axes[0, 0]
for i, c_key in enumerate(controllers):
    vals = [full_report[s][c_key]["yield_pct_mean"] for s in scenarios]
    errs = [full_report[s][c_key]["yield_pct_std"] for s in scenarios]
    bars = ax1.bar(x + (i - 1.5) * width, vals, width, yerr=errs, capsize=4,
                   label=ctrl_labels[i], color=colors[i], edgecolor='white', linewidth=0.8)
    # Add data labels on top of SAC bars
    if c_key == "SAC_v2":
        for b, v in zip(bars, vals):
            ax1.text(b.get_x() + b.get_width()/2, v + 1.2, f"{v:.1f}%",
                     ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#047857')

ax1.axhline(70.0, color='#DC2626', linestyle='--', linewidth=1.5, alpha=0.8, label="Schei & Tveit Benchmark (70%)")
ax1.set_title("Silicon Recovery Yield (%) — Higher is Better", fontsize=14, fontweight="bold", pad=12, color='#0F172A')
ax1.set_ylabel("Direct Yield (%)", fontsize=12, fontweight="bold", color='#1E293B')
ax1.set_xticks(x)
ax1.set_xticklabels(scenario_display, fontsize=10.5, fontweight="medium")
ax1.set_ylim(35, 100)
ax1.grid(True, linestyle="--", alpha=0.45, axis='y')
ax1.legend(loc="lower left", fontsize=9.5, framealpha=0.95, edgecolor='#CBD5E1')

# -------------------------------------------------------------
# SUBPLOT 2: UNIT PRODUCTION COST ($/kg Si)
# -------------------------------------------------------------
ax2 = axes[0, 1]
for i, c_key in enumerate(controllers):
    vals = [full_report[s][c_key]["cost_per_kg_usd_mean"] for s in scenarios]
    bars = ax2.bar(x + (i - 1.5) * width, vals, width,
                   label=ctrl_labels[i], color=colors[i], edgecolor='white', linewidth=0.8)
    if c_key == "SAC_v2":
        for b, v in zip(bars, vals):
            ax2.text(b.get_x() + b.get_width()/2, v + 0.05, f"${v:.2f}",
                     ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#047857')

ax2.axhline(1.85, color='#DC2626', linestyle='--', linewidth=1.5, alpha=0.8, label="Top-Quartile Market Parity ($1.85/kg)")
ax2.set_title("Unit Production Cost ($/kg Si) — Lower is Better", fontsize=14, fontweight="bold", pad=12, color='#0F172A')
ax2.set_ylabel("Cost (USD / kg Saleable Si)", fontsize=12, fontweight="bold", color='#1E293B')
ax2.set_xticks(x)
ax2.set_xticklabels(scenario_display, fontsize=10.5, fontweight="medium")
ax2.set_ylim(1.0, 3.4)
ax2.grid(True, linestyle="--", alpha=0.45, axis='y')
ax2.legend(loc="upper right", fontsize=9.5, framealpha=0.95, edgecolor='#CBD5E1')

# -------------------------------------------------------------
# SUBPLOT 3: SPECIFIC ENERGY CONSUMPTION (SEC, kWh/kg Si)
# -------------------------------------------------------------
ax3 = axes[1, 0]
for i, c_key in enumerate(controllers):
    vals = [full_report[s][c_key]["sec_kwh_per_kg_mean"] for s in scenarios]
    bars = ax3.bar(x + (i - 1.5) * width, vals, width,
                   label=ctrl_labels[i], color=colors[i], edgecolor='white', linewidth=0.8)
    if c_key == "SAC_v2":
        for b, v in zip(bars, vals):
            ax3.text(b.get_x() + b.get_width()/2, v + 0.4, f"{v:.1f}",
                     ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#047857')

ax3.axhline(15.0, color='#DC2626', linestyle='--', linewidth=1.5, alpha=0.8, label="Global Elkem World-Class Limit (15.0 kWh/kg)")
ax3.set_title("Specific Energy Consumption (kWh/kg Si) — Lower is Better", fontsize=14, fontweight="bold", pad=12, color='#0F172A')
ax3.set_ylabel("SEC (kWh / kg Si)", fontsize=12, fontweight="bold", color='#1E293B')
ax3.set_xticks(x)
ax3.set_xticklabels(scenario_display, fontsize=10.5, fontweight="medium")
ax3.set_ylim(8, 31)
ax3.grid(True, linestyle="--", alpha=0.45, axis='y')
ax3.legend(loc="upper left", fontsize=9.5, framealpha=0.95, edgecolor='#CBD5E1')

# -------------------------------------------------------------
# SUBPLOT 4: CUMULATIVE MULTI-OBJECTIVE EPISODE REWARD
# -------------------------------------------------------------
ax4 = axes[1, 1]
# We plot on symlog scale to clearly see both +1500 and -14295 without squashing!
for i, c_key in enumerate(controllers):
    vals = [full_report[s][c_key]["reward_mean"] for s in scenarios]
    bars = ax4.bar(x + (i - 1.5) * width, vals, width,
                   label=ctrl_labels[i], color=colors[i], edgecolor='white', linewidth=0.8)
    if c_key == "Fixed_Baseline":
        # Annotate catastrophic crash on Low Reactivity Feed
        crash_val = vals[3]
        b_crash = bars[3]
        ax4.text(b_crash.get_x() + b_crash.get_width()/2, -6000, "CATASTROPHIC\nTRIP!\n-14,295",
                 ha='center', va='center', fontsize=9, fontweight='bold', color='#DC2626',
                 bbox=dict(boxstyle='round,pad=0.2', facecolor='#FEF2F2', edgecolor='#EF4444', linewidth=1))

ax4.set_yscale('symlog', linthresh=500)
ax4.set_title("Cumulative Multi-Objective Reward — Higher is Better", fontsize=14, fontweight="bold", pad=12, color='#0F172A')
ax4.set_ylabel("Episode Reward (Symlog Scale)", fontsize=12, fontweight="bold", color='#1E293B')
ax4.set_xticks(x)
ax4.set_xticklabels(scenario_display, fontsize=10.5, fontweight="medium")
ax4.set_ylim(-20000, 3500)
ax4.axhline(0, color='black', linewidth=0.8, linestyle='-')
ax4.grid(True, linestyle="--", alpha=0.45, axis='y')
ax4.legend(loc="upper left", fontsize=9.5, framealpha=0.95, edgecolor='#CBD5E1')

# Super Title & Header Info
plt.suptitle("SilicaForge-RL: Autonomous Industrial Controller Benchmark & Disturbance Audit\n28.5 MW Submerged Arc Furnace (Curious SAC vs PPO vs Industrial PID vs Fixed Baseline)",
             fontsize=16, fontweight="bold", y=0.99, color='#0F172A')

plt.tight_layout(rect=[0, 0, 1, 0.96])

# Save high-res to Desktop and validation directory
desktop_path = Path("/home/piet/Desktop/SilicaForge_RL_Benchmark_Clear.png")
val_path = PROJECT_ROOT / "data" / "validation" / "ppo_vs_sac_comparison.png"

plt.savefig(desktop_path, dpi=300, bbox_inches='tight')
plt.savefig(val_path, dpi=300, bbox_inches='tight')
plt.close()

print(f"[SUCCESS] Ultra-clear benchmark chart saved to:\n  1. {desktop_path}\n  2. {val_path}")
