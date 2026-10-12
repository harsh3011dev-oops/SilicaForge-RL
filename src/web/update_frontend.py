import re
import os

source_file = "/home/piet/.gemini/antigravity/brain/8236b344-2114-4f76-a264-beb6f67f486d/scratch/new_ui/standalone_ui.html"
dest_file = "/home/piet/Desktop/harsh /rl project/src/web/static/index.html"

with open(source_file, "r", encoding="utf-8") as f:
    html = f.read()

# Replace stepSimulation function
new_step = """
  async function stepSimulation() {
    sim.time++;
    sim.step++;

    try {
      let res;
      if (sim.mode === 'ai_ppo') {
        res = await fetch('/api/step');
      } else {
        res = await fetch(`/api/manual_step?temp=${sim.targetT}&press=${sim.targetP}&argon=${sim.targetAr}`);
      }
      
      if (!res.ok) {
        console.error("API Error");
        return;
      }
      
      const data = await res.json();
      
      sim.temperature = data.temperature;
      sim.pressure = data.pressure;
      sim.argon = data.argon;
      
      if (sim.mode === 'ai_ppo') {
        sim.targetT = data.temperature;
        sim.targetP = data.pressure;
        sim.targetAr = data.argon;
      }
      
      sim.siYield = data.yield * 100;
      sim.sioLoss = data.sio_lost * 100;
      sim.costRate = data.cost;
      if (data.reward !== undefined) sim.reward = data.reward.toFixed(2);

      sim.costTotal += Math.round(sim.costRate / 3600);
      const produced = (45 * data.yield * 0.467) / 3600;
      sim.siYieldKg += produced;
      sim.sioLossKg += (45 * data.sio_lost * 0.4) / 3600;

      sim.poolLevel = Math.min(95, sim.poolLevel + produced * 12);
      sim.smoke = Math.min(1.0, data.sio_lost / 0.6);

      updateUI();
    } catch(e) {
      console.error(e);
    }
  }
"""

html = re.sub(r'function stepSimulation\(\) \{.*?(?=\n  function updateUI\(\))', new_step.strip(), html, flags=re.DOTALL)

# Replace resetSim function
new_reset = """
  async function resetSim() {
    try { await fetch('/api/reset'); } catch(e) {}
    sim.time = 0;
    sim.step = 0;
    sim.temperature = 1000;
    sim.targetT = 1860;
    sim.siYield = 0;
    sim.siYieldKg = 0;
    sim.sioLoss = 0;
    sim.sioLossKg = 0;
    sim.costTotal = 0;
    sim.poolLevel = 10;
    chartHistory.labels = [];
    chartHistory.yieldData = [];
    chartHistory.costData = [];
    updateUI();
  }
"""
html = re.sub(r'function resetSim\(\) \{.*?(?=\n  window\.onload)', new_reset.strip(), html, flags=re.DOTALL)


with open(dest_file, "w", encoding="utf-8") as f:
    f.write(html)

# Clean up unneeded files
import glob
for f in glob.glob("/home/piet/Desktop/harsh /rl project/src/web/static/*.css") + glob.glob("/home/piet/Desktop/harsh /rl project/src/web/static/*.js"):
    os.remove(f)

print("Integration complete!")
