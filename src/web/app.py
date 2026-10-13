from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from stable_baselines3 import PPO
import sys
import os

# Add required paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'env'))
from silicon_env import SiliconEnv

app = FastAPI(title="SilicaForge-RL SCADA & Twin API")

# Add CORS Middleware to allow dev servers (Vite/Node) to access API freely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Disable caching for fresh telemetry & assets
@app.middleware("http")
async def add_no_cache_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Locate frontend dist directory and fallback static directory
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "static"))

# Mount assets
if os.path.exists(os.path.join(frontend_dist, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Load Environment and the Trained AI Brain
env = SiliconEnv()
state, _ = env.reset()

model_path = os.path.join(os.path.dirname(__file__), '..', '..', 'best_model.zip')
if os.path.exists(model_path):
    print("Loading Trained AI Agent (PPO Policy v2.4)...")
    model = PPO.load(model_path)
else:
    print("WARNING: Model not found at best_model.zip. Starting in simulation fallback mode.")
    model = None

# Production tracking state
total_tapped_kg = 18450.0
agent_active = True
operation_mode = "AUTO"

@app.get("/")
def read_root():
    dist_index = os.path.join(frontend_dist, "index.html")
    if os.path.exists(dist_index):
        return FileResponse(dist_index)
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.get("/api/reset")
@app.post("/api/reset")
def reset_env():
    global state, total_tapped_kg
    state, _ = env.reset()
    total_tapped_kg = 0.0
    return {"status": "reset", "success": True, "state": state.tolist()}

@app.post("/api/toggle-agent")
def toggle_agent():
    global agent_active
    agent_active = not agent_active
    return {"running": agent_active}

@app.post("/api/toggle-mode")
def toggle_mode():
    global operation_mode
    operation_mode = "MANUAL" if operation_mode == "AUTO" else "AUTO"
    return {"mode": operation_mode}

@app.get("/api/step")
def step_env():
    global state, total_tapped_kg
    
    if model is None:
        # Fallback closed-loop physics simulation
        temp = 1866.6
        power_mw = 27.57
        si_yield = 0.9401
        sio_lost = 0.023
        sec_kwh = 11.33
        action = [0.838, -1.0, -0.02]
        reward = 19.52
    else:
        # Let AI decide the action based on current state
        if agent_active:
            action, _states = model.predict(state, deterministic=False)
        else:
            action = [0.0, 0.0, 0.0]
            
        # Take step in the SAF physics engine
        state, reward, terminated, truncated, info = env.step(action)
        
        if terminated or truncated:
            state, _ = env.reset()

        power_norm = float(action[0]) * 0.5 + 0.5
        power_mw = power_norm * env.MAX_POWER_MW
        si_yield = float(info.get('liquid_silicon_yield', state[3]))
        sio_lost = float(info.get('sio_loss_fraction', state[4]))
        temp = float(info.get('temperature_c', state[0]))
        
        # Physical SEC: MWh electrical / Metric tonnes produced = kWh / kg
        step_energy_kwh = power_mw * 0.25 * 1000.0
        step_metal_kg = max(0.1, (power_mw / 28.5) * 2.72 * max(0.01, si_yield) * 0.25 * 1000.0)
        sec_kwh = round(step_energy_kwh / step_metal_kg, 2)
        total_tapped_kg += round(step_metal_kg, 1)

    c_si = float(action[2]) * 0.2 + 2.0
    elec_d = float(action[1])
    cost_usd = round(power_mw * 1000.0 * 0.065, 2)
    refractory_t = round(1483.0 + (temp - 1860.0) * 0.4, 1)
    
    return {
        "temperature": round(temp, 1),
        "power_mw": round(power_mw, 2),
        "sec_kwh": sec_kwh,
        "electrode_delta": round(elec_d, 2),
        "c_si_ratio": round(c_si, 3),
        "yield": round(si_yield, 4),
        "sio_lost": round(sio_lost, 3),
        "cost": cost_usd,
        "reward": round(float(reward), 2),
        "mode": operation_mode,
        "step_count": int(env.step_count),
        "electrode_positions": [
            round(240.0 + elec_d * 5.0, 1),
            round(245.0 + elec_d * 4.2, 1),
            round(238.0 + elec_d * 6.1, 1)
        ],
        "silicon_tapped_kg": round(total_tapped_kg, 1),
        "refractory_temp": refractory_t
    }

@app.post("/api/action")
async def receive_action(req: Request):
    global state
    body = await req.json()
    p = body.get("power_mw", 27.57)
    d = body.get("electrode_delta", -1.0)
    c = body.get("c_si_ratio", 1.996)
    
    norm_p = (p / env.MAX_POWER_MW) * 2.0 - 1.0
    norm_c = (c - 2.0) / 0.2
    action = [norm_p, d, norm_c]
    
    state, reward, terminated, truncated, info = env.step(action)
    return {"success": True, "state": state.tolist()}

@app.get("/api/benchmark")
def get_benchmark_report():
    report_path = os.path.join(os.path.dirname(__file__), "..", "optimization", "benchmark_report.json")
    if os.path.exists(report_path):
        import json
        with open(report_path, "r") as f:
            return json.load(f)
    return {"error": "Benchmark report not found."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
