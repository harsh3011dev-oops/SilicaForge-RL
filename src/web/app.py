from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from stable_baselines3 import PPO
import sys
import os

# Add required paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'env'))
from silicon_env import SiliconEnv

app = FastAPI()

# Middleware to disable caching so the browser always loads the newest UI
@app.middleware("http")
async def add_no_cache_header(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Mount the static directory
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

# Load Environment and the Trained AI Brain
env = SiliconEnv()
state, _ = env.reset()

model_path = os.path.join(os.path.dirname(__file__), '..', '..', 'best_model.zip')
if os.path.exists(model_path):
    print("Loading Trained AI Agent...")
    model = PPO.load(model_path)
else:
    print("WARNING: Model not found. Did you run train_rl.py?")
    model = None

@app.get("/")
def read_root():
    return FileResponse(os.path.join(os.path.dirname(__file__), "static", "index.html"))

@app.get("/api/reset")
def reset_env():
    global state
    state, _ = env.reset()
    return {"status": "reset", "state": state.tolist()}

@app.get("/api/step")
def step_env():
    global state
    if model is None:
        return {"error": "Model not loaded"}
    
    # Let AI decide the action based on current state
    action, _states = model.predict(state, deterministic=False)
    
    # Take the step in the physics engine
    state, reward, terminated, truncated, info = env.step(action)
    
    # If the episode ends, reset it automatically
    if terminated or truncated:
        state, _ = env.reset()
        
    # Fetch real values directly from info dict instead of unpacking normalized state
    return {
        "temperature": float(info.get('temperature', state[0])),
        "pressure": float(info.get('pressure', 1.0)),
        "argon": float(info.get('argon', 1.0)),
        "yield": float(info.get('yield', state[3])),
        "sio_lost": float(info.get('sio_lost', state[4])),
        "cost": float(info.get('cost', 0.0)),
        "reward": float(reward),
        "mode": "AUTO"
    }

@app.get("/api/manual_step")
def manual_step(temp: float, press: float, argon: float):
    global state
    
    # We query the new thermodynamic simulator directly
    si_yield, sio_lost = env._compute_thermodynamic_yield_and_loss(temp, 2.0)
    
    # Estimate holding power cost for this temperature
    delta_t = temp - 25.0
    q_loss_mw = 3.2 + 0.0078 * delta_t + 2.8e-12 * ((temp + 273.15) ** 4.0)
    q_reaction_mw = 6.5 * si_yield if si_yield > 0.1 else 1.2
    req_power_mw = (q_loss_mw + q_reaction_mw) / 0.88
    cost = req_power_mw * env.ELECTRICITY_PRICE_PER_MWH
    
    return {
        "temperature": temp,
        "pressure": press,
        "argon": argon,
        "yield": float(si_yield),
        "sio_lost": float(sio_lost),
        "cost": float(cost),
        "mode": "MANUAL"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
