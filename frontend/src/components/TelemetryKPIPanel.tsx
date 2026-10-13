import React, { useState } from 'react';
import {
  Flame,
  Zap,
  TrendingUp,
  Wind,
  DollarSign,
  Compass,
  Sliders,
  Radio,
  CheckCircle2,
  AlertTriangle,
  ChevronRight,
  ShieldCheck,
} from 'lucide-react';
import { FurnaceTelemetry, TelemetryPoint, AgentActionLog } from '../types/furnace';

interface TelemetryKPIPanelProps {
  telemetry: FurnaceTelemetry;
  history: TelemetryPoint[];
  actionLogs: AgentActionLog[];
  onManualAction: (updates: Partial<FurnaceTelemetry>) => void;
  onToggleMode: () => void;
}

export const TelemetryKPIPanel: React.FC<TelemetryKPIPanelProps> = ({
  telemetry,
  history,
  actionLogs,
  onManualAction,
  onToggleMode,
}) => {
  const [activeChartTab, setActiveChartTab] = useState<'DUAL_CHANNEL' | 'TEMPERATURE' | 'ENERGY_YIELD'>('DUAL_CHANNEL');
  const [manualPower, setManualPower] = useState<number>(telemetry.power_mw);
  const [manualDelta, setManualDelta] = useState<number>(telemetry.electrode_delta);
  const [manualCSi, setManualCSi] = useState<number>(telemetry.c_si_ratio);

  // Temperature status calculation
  const isSweetSpot = telemetry.temperature >= 1850 && telemetry.temperature <= 1900;
  const isOverheating = telemetry.temperature > 1950;

  // Chart coordinate calculations
  const chartWidth = 380;
  const chartHeight = 170;
  const padding = { top: 16, right: 38, bottom: 24, left: 42 };
  const graphWidth = chartWidth - padding.left - padding.right;
  const graphHeight = chartHeight - padding.top - padding.bottom;

  // Scales
  const minTemp = 1830;
  const maxTemp = 1910;
  const minSec = 10.5;
  const maxSec = 12.5;

  const getTempY = (temp: number) => {
    const clamped = Math.max(minTemp, Math.min(maxTemp, temp));
    return padding.top + graphHeight - ((clamped - minTemp) / (maxTemp - minTemp)) * graphHeight;
  };

  const getSecY = (sec: number) => {
    const clamped = Math.max(minSec, Math.min(maxSec, sec));
    return padding.top + graphHeight - ((clamped - minSec) / (maxSec - minSec)) * graphHeight;
  };

  const sweetSpotTopY = getTempY(1900);
  const sweetSpotBottomY = getTempY(1850);
  const sweetSpotHeight = Math.abs(sweetSpotBottomY - sweetSpotTopY);

  // SVG path generation
  const tempPath = history.length > 1
    ? history.map((pt, i) => {
        const x = padding.left + (i / (history.length - 1)) * graphWidth;
        const y = getTempY(pt.temperature);
        return `${i === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`;
      }).join(' ')
    : '';

  const secPath = history.length > 1
    ? history.map((pt, i) => {
        const x = padding.left + (i / (history.length - 1)) * graphWidth;
        const y = getSecY(pt.sec_kwh);
        return `${i === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`;
      }).join(' ')
    : '';

  return (
    <aside className="w-full lg:w-[440px] xl:w-[480px] shrink-0 bg-[#F7F4EB] flex flex-col gap-3.5 p-3.5 sm:p-4 border-l border-[#DDCFB4] overflow-y-auto">
      {/* Operating Mode Header & Override Switch */}
      <div className="bg-[#FAF7F0] p-3 rounded-xl border border-[#DDCFB4] shadow-xs flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className={`p-2 rounded-lg ${telemetry.mode === 'AUTO' ? 'bg-[#FFF3E0] text-[#E65100]' : 'bg-[#EFE8D8] text-[#5D4037]'}`}>
            <Radio className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs font-bold text-[#2C211B] flex items-center gap-1.5">
              <span>{telemetry.mode === 'AUTO' ? 'PPO Closed-Loop Control' : 'Manual SCADA Override'}</span>
              <span className={`text-[10px] px-1.5 py-0.2 rounded font-medium ${
                telemetry.mode === 'AUTO' ? 'bg-[#E8F5E9] text-[#2E7D32]' : 'bg-[#FFF3E0] text-[#E65100]'
              }`}>
                {telemetry.mode}
              </span>
            </div>
            <div className="text-[11px] text-[#6E5D53]">
              {telemetry.mode === 'AUTO' ? '5.0M Step Pretrained Policy' : 'Operator fine-tuning active'}
            </div>
          </div>
        </div>

        <button
          onClick={onToggleMode}
          className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-[#FAF5EC] text-[#8D4925] border border-[#C8B99C] hover:bg-[#F0E6D2] transition-colors whitespace-nowrap shadow-xs"
        >
          {telemetry.mode === 'AUTO' ? 'Switch to Manual' : 'Engage PPO Auto'}
        </button>
      </div>

      {/* KPI METRIC CARDS (Warm Ivory cards with soft terracotta borders) */}
      <div className="grid grid-cols-2 gap-2.5">
        {/* 1. Furnace Temperature */}
        <div className="col-span-2 bg-[#FAF7F0] p-3.5 rounded-xl border border-[#DDCFB4] shadow-xs hover:border-[#C8B99C] transition-all">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs font-semibold text-[#6E5D53] flex items-center gap-1.5">
              <Flame className="w-3.5 h-3.5 text-[#D84315]" />
              Hearth Core Temperature
            </span>
            <span
              className={`text-[10px] font-medium px-2 py-0.5 rounded ${
                isOverheating
                  ? 'bg-[#FFEBEE] text-[#B71C1C]'
                  : isSweetSpot
                  ? 'bg-[#FFF3E0] text-[#E65100] font-semibold border border-[#FFE0B2]'
                  : 'bg-[#EFE8D8] text-[#5D4037]'
              }`}
            >
              {isSweetSpot ? '1850-1900°C Sweet Spot' : isOverheating ? 'Overheat Alert' : 'Sub-Optimal'}
            </span>
          </div>
          <div className="flex items-baseline justify-between mt-1">
            <div className="text-3xl font-extrabold font-mono text-[#2C211B] tracking-tight tabular-nums">
              {telemetry.temperature.toFixed(1)}°C
            </div>
            <div className="text-[11px] text-[#6E5D53] text-right">
              <div>Target: 1866.6°C</div>
              <div className="text-[#2E7D32] font-semibold">Margin: +383.2°C (Safe)</div>
            </div>
          </div>
        </div>

        {/* 2. Silicon Yield Recovery */}
        <div className="bg-[#FAF7F0] p-3 rounded-xl border border-[#DDCFB4] shadow-xs">
          <div className="text-[11px] font-semibold text-[#6E5D53] flex items-center justify-between">
            <span className="flex items-center gap-1">
              <TrendingUp className="w-3 h-3 text-[#2E7D32]" />
              Si Direct Yield
            </span>
            <span className="text-[10px] text-[#2E7D32] font-medium">Target &gt;88.0%</span>
          </div>
          <div className="text-xl font-bold font-mono text-[#2C211B] mt-1 tabular-nums">
            {(telemetry.yield * 100).toFixed(2)}%
          </div>
          <div className="text-[10px] text-[#2E7D32] font-medium mt-0.5">
            +4.46% vs Baseline (94.01% peak)
          </div>
        </div>

        {/* 3. Specific Energy (SEC) */}
        <div className="bg-[#FAF7F0] p-3 rounded-xl border border-[#DDCFB4] shadow-xs">
          <div className="text-[11px] font-semibold text-[#6E5D53] flex items-center justify-between">
            <span className="flex items-center gap-1">
              <Zap className="w-3 h-3 text-[#F57F17]" />
              Specific Energy (SEC)
            </span>
            <span className="text-[10px] text-[#6E5D53]">Std: 11-13</span>
          </div>
          <div className="text-xl font-bold font-mono text-[#2C211B] mt-1 tabular-nums">
            {telemetry.sec_kwh.toFixed(2)} <span className="text-xs font-normal text-[#6E5D53]">kWh/kg</span>
          </div>
          <div className="text-[10px] text-[#2E7D32] font-medium mt-0.5">
            -11.1% vs Commercial 12.75
          </div>
        </div>

        {/* 4. Off-Gas SiO Loss */}
        <div className="bg-[#FAF7F0] p-3 rounded-xl border border-[#DDCFB4] shadow-xs">
          <div className="text-[11px] font-semibold text-[#6E5D53] flex items-center justify-between">
            <span className="flex items-center gap-1">
              <Wind className="w-3 h-3 text-[#8D4925]" />
              Off-Gas SiO Loss
            </span>
            <span className="text-[10px] text-[#2E7D32] font-medium">&lt;12.0%</span>
          </div>
          <div className="text-xl font-bold font-mono text-[#2C211B] mt-1 tabular-nums">
            {(telemetry.sio_lost * 100).toFixed(2)}%
          </div>
          <div className="text-[10px] text-[#2E7D32] font-medium mt-0.5">
            -72.9% reduced vapor loss
          </div>
        </div>

        {/* 5. Electrical Power Input */}
        <div className="bg-[#FAF7F0] p-3 rounded-xl border border-[#DDCFB4] shadow-xs">
          <div className="text-[11px] font-semibold text-[#6E5D53] flex items-center justify-between">
            <span>Power Active</span>
            <span className="text-[10px] text-[#6E5D53]">Nominal 28.5 MW</span>
          </div>
          <div className="text-xl font-bold font-mono text-[#2C211B] mt-1 tabular-nums">
            {telemetry.power_mw.toFixed(2)} <span className="text-xs font-normal text-[#6E5D53]">MW</span>
          </div>
          <div className="text-[10px] text-[#6E5D53] mt-0.5">
            Load factor: 96.7%
          </div>
        </div>

        {/* 6. Operating Electricity Cost */}
        <div className="bg-[#FAF7F0] p-3 rounded-xl border border-[#DDCFB4] shadow-xs">
          <div className="text-[11px] font-semibold text-[#6E5D53] flex items-center justify-between">
            <span className="flex items-center gap-1">
              <DollarSign className="w-3 h-3 text-[#5D4037]" />
              Power Cost
            </span>
            <span className="text-[10px] text-[#6E5D53]">$65/MWh</span>
          </div>
          <div className="text-xl font-bold font-mono text-[#2C211B] mt-1 tabular-nums">
            ${telemetry.cost.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            <span className="text-xs font-normal text-[#6E5D53]">/hr</span>
          </div>
          <div className="text-[10px] text-[#2E7D32] font-medium mt-0.5">
            Est. Savings: $214/hr
          </div>
        </div>

        {/* 7. Stoichiometry Ratio */}
        <div className="bg-[#FAF7F0] p-3 rounded-xl border border-[#DDCFB4] shadow-xs">
          <div className="text-[11px] font-semibold text-[#6E5D53] flex items-center justify-between">
            <span className="flex items-center gap-1">
              <Compass className="w-3 h-3 text-[#8D4925]" />
              Stoichiometry
            </span>
            <span className="text-[10px] text-[#2E7D32] font-medium">Ideal: 2.000</span>
          </div>
          <div className="text-xl font-bold font-mono text-[#2C211B] mt-1 tabular-nums">
            C/Si = {telemetry.c_si_ratio.toFixed(3)}
          </div>
          <div className="text-[10px] text-[#2E7D32] font-medium mt-0.5">
            -0.22% tight lock
          </div>
        </div>
      </div>

      {/* DUAL-CHANNEL LIVE STRIP CHART (Warm Theme) */}
      <div className="bg-[#FAF7F0] p-3.5 rounded-xl border border-[#DDCFB4] shadow-xs">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-[#D84315]" />
            <h3 className="text-xs font-bold text-[#2C211B]">Dual-Channel Real-Time Telemetry Strip</h3>
          </div>
          <div className="flex items-center gap-2 text-[10px]">
            <span className="flex items-center gap-1 text-[#D84315] font-semibold">
              <span className="w-2.5 h-0.5 bg-[#D84315] rounded-full inline-block" />
              Temp (°C)
            </span>
            <span className="flex items-center gap-1 text-[#F57F17] font-semibold">
              <span className="w-2.5 h-0.5 bg-[#F57F17] rounded-full inline-block" />
              SEC (kWh/kg)
            </span>
          </div>
        </div>

        {/* Chart Canvas Area */}
        <div className="relative w-full overflow-hidden rounded-lg border border-[#EAE2D2] bg-[#FAF7F0]">
          <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} className="w-full h-auto block select-none">
            {/* Shaded Sweet-Spot Band (1850°C - 1900°C) */}
            <rect
              x={padding.left}
              y={sweetSpotTopY}
              width={graphWidth}
              height={sweetSpotHeight}
              fill="#FFF3E0"
              opacity="0.85"
            />
            <text
              x={padding.left + 6}
              y={sweetSpotTopY + 12}
              fill="#E65100"
              fontSize="9"
              fontWeight="600"
              fontFamily="sans-serif"
            >
              1850 - 1900°C Sweet Spot
            </text>

            {/* Horizontal Grid lines */}
            {[1840, 1860, 1880, 1900].map((temp) => {
              const y = getTempY(temp);
              return (
                <g key={temp}>
                  <line
                    x1={padding.left}
                    y1={y}
                    x2={chartWidth - padding.right}
                    y2={y}
                    stroke="#EAE2D2"
                    strokeDasharray="3 3"
                  />
                  <text
                    x={padding.left - 6}
                    y={y + 3}
                    textAnchor="end"
                    fill="#8D7B68"
                    fontSize="9"
                    fontFamily="JetBrains Mono"
                  >
                    {temp}
                  </text>
                </g>
              );
            })}

            {/* Right Y-Axis labels (SEC kWh/kg) */}
            {[11.0, 11.5, 12.0].map((sec) => {
              const y = getSecY(sec);
              return (
                <text
                  key={sec}
                  x={chartWidth - padding.right + 6}
                  y={y + 3}
                  textAnchor="start"
                  fill="#F57F17"
                  fontSize="9"
                  fontFamily="JetBrains Mono"
                >
                  {sec.toFixed(1)}
                </text>
              );
            })}

            {/* Trace 1: Burnt Terracotta (#D84315) Temperature */}
            {tempPath && (
              <path
                d={tempPath}
                fill="none"
                stroke="#D84315"
                strokeWidth="2.2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            )}

            {/* Trace 2: Warm Golden Ochre (#F57F17) SEC kWh/kg */}
            {secPath && (
              <path
                d={secPath}
                fill="none"
                stroke="#F57F17"
                strokeWidth="1.8"
                strokeDasharray="4 2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            )}

            {/* Current head dot */}
            {history.length > 0 && (
              <>
                <circle
                  cx={padding.left + graphWidth}
                  cy={getTempY(telemetry.temperature)}
                  r="3.5"
                  fill="#D84315"
                  stroke="#FFFFFF"
                  strokeWidth="1.5"
                />
                <circle
                  cx={padding.left + graphWidth}
                  cy={getSecY(telemetry.sec_kwh)}
                  r="3"
                  fill="#F57F17"
                  stroke="#FFFFFF"
                  strokeWidth="1.5"
                />
              </>
            )}
          </svg>
        </div>

        <div className="flex items-center justify-between text-[10px] text-[#6E5D53] mt-1.5 px-1">
          <span>Live 60-second Rolling Window</span>
          <span className="font-mono">Current: {telemetry.temperature.toFixed(1)}°C / {telemetry.sec_kwh.toFixed(2)} kWh/kg</span>
        </div>
      </div>

      {/* Manual Override Controls (Visible in MANUAL mode) */}
      {telemetry.mode === 'MANUAL' && (
        <div className="bg-[#FAF7F0] p-3.5 rounded-xl border border-[#DDCFB4] shadow-xs space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-bold text-[#8D4925] flex items-center gap-1.5">
              <Sliders className="w-3.5 h-3.5" />
              Manual SCADA Actuator Controls
            </h4>
            <span className="text-[10px] text-[#D84315] font-semibold">Live Overrides Active</span>
          </div>

          {/* Power MW Slider */}
          <div>
            <div className="flex justify-between text-[11px] text-[#5D4037] mb-1">
              <span>Active Power Setpoint</span>
              <span className="font-mono font-bold">{manualPower.toFixed(2)} MW</span>
            </div>
            <input
              type="range"
              min="20.0"
              max="30.0"
              step="0.1"
              value={manualPower}
              onChange={(e) => {
                const val = parseFloat(e.target.value);
                setManualPower(val);
                onManualAction({ power_mw: val });
              }}
              className="w-full accent-[#D84315] cursor-pointer"
            />
          </div>

          {/* Electrode Delta */}
          <div>
            <div className="flex justify-between text-[11px] text-[#5D4037] mb-1">
              <span>Electrode Stroke Position</span>
              <span className="font-mono font-bold">{manualDelta > 0 ? `+${manualDelta}` : manualDelta} mm</span>
            </div>
            <input
              type="range"
              min="-5.0"
              max="5.0"
              step="0.5"
              value={manualDelta}
              onChange={(e) => {
                const val = parseFloat(e.target.value);
                setManualDelta(val);
                onManualAction({ electrode_delta: val });
              }}
              className="w-full accent-[#8D4925] cursor-pointer"
            />
          </div>

          {/* C/Si ratio */}
          <div>
            <div className="flex justify-between text-[11px] text-[#5D4037] mb-1">
              <span>C/Si Burden Feeding Ratio</span>
              <span className="font-mono font-bold">{manualCSi.toFixed(3)}</span>
            </div>
            <input
              type="range"
              min="1.850"
              max="2.150"
              step="0.005"
              value={manualCSi}
              onChange={(e) => {
                const val = parseFloat(e.target.value);
                setManualCSi(val);
                onManualAction({ c_si_ratio: val });
              }}
              className="w-full accent-[#2E7D32] cursor-pointer"
            />
          </div>
        </div>
      )}

      {/* AGENT DECISION STREAM (Monospace live feed of PPO actions) */}
      <div className="bg-[#FAF7F0] p-3.5 rounded-xl border border-[#DDCFB4] shadow-xs flex-1 flex flex-col min-h-[220px]">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-[#2E7D32]" />
            <h3 className="text-xs font-bold text-[#2C211B]">PPO Agent Decision Stream</h3>
          </div>
          <span className="text-[10px] font-mono text-[#8D4925] bg-[#EFE8D8] px-2 py-0.5 rounded">
            Reward: +{telemetry.reward.toFixed(2)}
          </span>
        </div>

        {/* Streaming log items */}
        <div className="flex-1 overflow-y-auto space-y-1.5 pr-1 max-h-[260px] text-[11px] font-mono">
          {actionLogs.map((log) => (
            <div
              key={log.id}
              className="bg-[#F7F4EB] p-2 rounded border border-[#EAE2D2] hover:border-[#DDCFB4] transition-colors"
            >
              <div className="flex items-center justify-between text-[10px] text-[#8D7B68] mb-0.5">
                <span>{log.timestamp}</span>
                <span className={`px-1.5 py-0.2 rounded text-[9px] font-semibold ${
                  log.category === 'ELECTRODE'
                    ? 'bg-[#FFF3E0] text-[#E65100]'
                    : log.category === 'STOICHIOMETRY'
                    ? 'bg-[#E8F5E9] text-[#2E7D32]'
                    : log.category === 'POWER'
                    ? 'bg-[#EDE7F6] text-[#5E35B1]'
                    : 'bg-[#ECEFF1] text-[#37474F]'
                }`}>
                  {log.category}
                </span>
              </div>
              <div className="font-semibold text-[#2C211B] text-[11px]">{log.action}</div>
              <div className="text-[10px] text-[#5D4037] mt-0.5 font-sans leading-tight">{log.rationale}</div>
              <div className="text-[9px] text-[#8D4925] mt-0.5 font-mono">{log.metricDelta}</div>
            </div>
          ))}
        </div>
      </div>
    </aside>
  );
};
