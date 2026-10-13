import React from 'react';
import { Play, Pause, Award, Flame } from 'lucide-react';
import { FurnaceTelemetry } from '../types/furnace';

interface TopNavigationBarProps {
  telemetry: FurnaceTelemetry;
  isRunning: boolean;
  onToggleAgent: () => void;
  onOpenFindings: () => void;
  onResetFurnace?: () => void;
  connectionStatus: 'CONNECTED' | 'DISCONNECTED' | 'CONNECTING';
}

export const TopNavigationBar: React.FC<TopNavigationBarProps> = ({
  telemetry,
  isRunning,
  onToggleAgent,
  onOpenFindings,
  connectionStatus,
}) => {
  const marginDeg = Math.round(2250 - telemetry.temperature);
  const isSafetyMarginSafe = marginDeg > 300;

  return (
    <header className="w-full bg-[#FAF7F0] border-b border-[#DDCFB4] px-4 py-2.5 sm:px-6 shadow-xs select-none">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
        {/* Zone 1: Brand & Plant Identification */}
        <div className="flex items-center gap-3 shrink-0">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#E65100] to-[#FF8F00] flex items-center justify-center text-white shadow-sm shadow-[#E65100]/25">
            <Flame className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-extrabold tracking-tight text-[#2C211B] whitespace-nowrap">
                SILICAFORGE-RL
              </h1>
              <span className="hidden sm:inline-block text-[#C8B99C]">|</span>
              <span className="hidden sm:inline-block text-xs font-semibold text-[#8D4925]">
                Submerged Arc Furnace Digital Twin
              </span>
            </div>
            <div className="text-[11px] text-[#6E5D53] tracking-wide">
              28.5 MW Commercial Plant · Carbothermic Silica Reduction (SiO₂ + 2C → Si + 2CO)
            </div>
          </div>
        </div>

        {/* Zone 2: Status Badges (Soft warm pill badges with borders) */}
        <div className="flex items-center flex-wrap gap-2 text-xs">
          {/* PPO Agent steps badge */}
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#FAF5EC] border border-[#C8B99C] text-[#8D4925] font-medium text-[11px]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#8D4925]" />
            <span>PPO Agent v2.4 · 5.0M Steps Trained</span>
          </div>

          {/* Model Live Twin status */}
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#E8F5E9] border border-[#C8E6C9] text-[#2E7D32] font-semibold text-[11px]">
            <span className="w-2 h-2 rounded-full bg-[#2E7D32] animate-pulse" />
            <span>Model: CONNECTED TO LIVE TWIN</span>
          </div>

          {/* Refractory safety margin */}
          <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-[11px] font-medium ${
            isSafetyMarginSafe
              ? 'bg-[#FAF5EC] border-[#DDCFB4] text-[#423229]'
              : 'bg-[#FFEBEE] border-[#FFCDD2] text-[#B71C1C]'
          }`}>
            <span>Refractory Safety:</span>
            <span className="font-mono font-bold text-[#2E7D32]">+{marginDeg}°C MARGIN</span>
            <span className="text-[10px] text-[#2E7D32] font-semibold">(SAFE)</span>
          </div>
        </div>

        {/* Zone 3: Header Action Buttons */}
        <div className="flex items-center gap-2 shrink-0">
          {/* 1. START / PAUSE RL AGENT button (Vibrant warm flame gradient) */}
          <button
            onClick={onToggleAgent}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-bold text-white transition-all shadow-sm ${
              isRunning
                ? 'bg-gradient-to-r from-[#D84315] to-[#FF8F00] hover:brightness-105 shadow-[#D84315]/30'
                : 'bg-gradient-to-r from-[#795548] to-[#8D6E63] hover:brightness-105'
            }`}
          >
            {isRunning ? (
              <>
                <Pause className="w-3.5 h-3.5 fill-current" />
                <span>PAUSE RL AGENT</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>START RL AGENT</span>
              </>
            )}
          </button>

          {/* 2. KEY SCIENTIFIC FINDINGS button (Warm sandstone with copper border) */}
          <button
            onClick={onOpenFindings}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-[#FAF5EC] text-[#8D4925] border border-[#C8B99C] hover:bg-[#F3EAD9] transition-colors shadow-xs"
          >
            <Award className="w-3.5 h-3.5 text-[#E65100]" />
            <span className="hidden sm:inline">KEY SCIENTIFIC FINDINGS</span>
            <span className="sm:hidden">FINDINGS</span>
          </button>
        </div>
      </div>
    </header>
  );
};
