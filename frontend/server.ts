import express, { Request, Response } from 'express';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = Number(process.env.PORT) || 3000;

app.use(express.json());

// SAF Twin Simulation State
interface FurnaceState {
  temperature: number;
  power_mw: number;
  sec_kwh: number;
  electrode_delta: number;
  c_si_ratio: number;
  yield: number;
  sio_lost: number;
  cost: number;
  reward: number;
  mode: 'AUTO' | 'MANUAL';
  step_count: number;
  electrode_positions: [number, number, number];
  silicon_tapped_kg: number;
  refractory_temp: number;
}

const state: FurnaceState = {
  temperature: 1866.6,
  power_mw: 27.57,
  sec_kwh: 11.33,
  electrode_delta: -1.0,
  c_si_ratio: 1.996,
  yield: 0.9401,
  sio_lost: 0.023,
  cost: 1792.08,
  reward: 19.52,
  mode: 'AUTO',
  step_count: 51240,
  electrode_positions: [240, 245, 238],
  silicon_tapped_kg: 18450.4,
  refractory_temp: 1483.2,
};

let ppoRunning = true;

// Simulation step tick
function stepSimulation() {
  if (!ppoRunning) return;

  state.step_count += 1;

  if (state.mode === 'AUTO') {
    // PPO autonomous micro-tuning around sweet spot
    const targetTemp = 1866.6;
    const tempNoise = (Math.random() - 0.5) * 0.08;
    state.temperature = +(targetTemp + tempNoise).toFixed(1);

    // Electrode penetration micro-adjustments to balance electric arc impedance
    const delta = +((Math.random() - 0.52) * 2.1).toFixed(1);
    state.electrode_delta = delta;
    state.electrode_positions = [
      Math.max(180, Math.min(320, +(state.electrode_positions[0] + delta * 0.4).toFixed(1))),
      Math.max(180, Math.min(320, +(state.electrode_positions[1] + (Math.random() - 0.5) * 1.2).toFixed(1))),
      Math.max(180, Math.min(320, +(state.electrode_positions[2] + (Math.random() - 0.5) * 1.2).toFixed(1))),
    ];

    // Power modulation
    state.power_mw = +(27.57 + (Math.random() - 0.48) * 0.18).toFixed(2);

    // Stoichiometry
    state.c_si_ratio = +(1.996 + (Math.random() - 0.5) * 0.003).toFixed(3);

    // Yield & Loss
    state.yield = +(0.9401 + (Math.random() - 0.48) * 0.0018).toFixed(4);
    state.sio_lost = +(0.023 + (Math.random() - 0.5) * 0.0012).toFixed(3);

    // SEC & Cost
    state.sec_kwh = +(11.33 + (Math.random() - 0.5) * 0.05).toFixed(2);
    state.cost = +(state.power_mw * 1000 * 0.065).toFixed(2); // ~$65/MWh industrial tariff

    // PPO cumulative reward
    state.reward = +(19.52 + Math.sin(state.step_count * 0.1) * 0.2).toFixed(2);

    // Production accumulation
    state.silicon_tapped_kg = +(state.silicon_tapped_kg + (state.power_mw * 1000 / (state.sec_kwh * 3600)) * 1.5).toFixed(1);
    state.refractory_temp = +(1483.0 + (state.temperature - 1860) * 0.4 + (Math.random() - 0.5) * 0.4).toFixed(1);
  }
}

// Tick interval
setInterval(stepSimulation, 1000);

// API Contract Endpoint
app.get('/api/step', (_req: Request, res: Response) => {
  res.json({
    temperature: state.temperature,
    power_mw: state.power_mw,
    sec_kwh: state.sec_kwh,
    electrode_delta: state.electrode_delta,
    c_si_ratio: state.c_si_ratio,
    yield: state.yield,
    sio_lost: state.sio_lost,
    cost: state.cost,
    reward: state.reward,
    mode: state.mode,
    step_count: state.step_count,
    electrode_positions: state.electrode_positions,
    silicon_tapped_kg: state.silicon_tapped_kg,
    refractory_temp: state.refractory_temp,
  });
});

app.post('/api/action', (req: Request, res: Response) => {
  const { power_mw, electrode_delta, c_si_ratio, mode } = req.body;
  if (typeof power_mw === 'number') state.power_mw = power_mw;
  if (typeof electrode_delta === 'number') state.electrode_delta = electrode_delta;
  if (typeof c_si_ratio === 'number') state.c_si_ratio = c_si_ratio;
  if (mode === 'AUTO' || mode === 'MANUAL') state.mode = mode;
  res.json({ success: true, state });
});

app.post('/api/toggle-mode', (_req: Request, res: Response) => {
  state.mode = state.mode === 'AUTO' ? 'MANUAL' : 'AUTO';
  res.json({ mode: state.mode });
});

app.post('/api/toggle-agent', (_req: Request, res: Response) => {
  ppoRunning = !ppoRunning;
  res.json({ running: ppoRunning });
});

app.post('/api/reset', (_req: Request, res: Response) => {
  state.temperature = 1866.6;
  state.power_mw = 27.57;
  state.sec_kwh = 11.33;
  state.electrode_delta = -1.0;
  state.c_si_ratio = 1.996;
  state.yield = 0.9401;
  state.sio_lost = 0.023;
  state.cost = 1792.08;
  state.reward = 19.52;
  state.mode = 'AUTO';
  ppoRunning = true;
  res.json({ success: true, state });
});

app.get('/api/download-zip', (_req: Request, res: Response) => {
  const zipPath = path.join(__dirname, 'public', 'silicaforge-rl-ui.zip');
  res.download(zipPath, 'silicaforge-rl-ui.zip', (err) => {
    if (err) {
      res.status(500).json({ error: 'Could not download zip file' });
    }
  });
});

// Vite middleware in dev or static serve in prod
async function startServer() {
  if (process.env.NODE_ENV === 'production') {
    app.use(express.static(path.join(__dirname, 'dist')));
    app.get('*', (_req, res) => {
      res.sendFile(path.join(__dirname, 'dist', 'index.html'));
    });
  } else {
    const { createServer: createViteServer } = await import('vite');
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`SilicaForge-RL SCADA server running at http://0.0.0.0:${PORT}`);
  });
}

startServer();
