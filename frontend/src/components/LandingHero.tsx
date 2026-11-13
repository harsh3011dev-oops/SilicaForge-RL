import React from 'react';
import {
  Flame,
  ArrowRight,
  BookOpen,
  Cpu,
  Layers,
  ShieldCheck,
  Zap,
  Activity,
  Award,
  Database,
  ExternalLink,
  ChevronDown
} from 'lucide-react';

interface LandingHeroProps {
  onExplore: () => void;
}

export const LandingHero: React.FC<LandingHeroProps> = ({ onExplore }) => {
  return (
    <div className="min-h-screen w-full bg-[#0B0F17] text-[#E2E8F0] selection:bg-[#E65100] selection:text-white relative overflow-x-hidden font-['Plus_Jakarta_Sans',sans-serif]">
      {/* Background Subtle Industrial Ambient Glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[600px] bg-gradient-to-b from-[#E65100]/15 via-[#C2410C]/5 to-transparent blur-[140px] pointer-events-none" />
      <div className="absolute bottom-0 right-0 w-[600px] h-[500px] bg-gradient-to-t from-[#1D4ED8]/10 to-transparent blur-[120px] pointer-events-none" />

      {/* Grid Pattern Overlay */}
      <div 
        className="absolute inset-0 opacity-[0.03] pointer-events-none" 
        style={{ backgroundImage: 'radial-gradient(circle at 1px 1px, #ffffff 1px, transparent 0)', backgroundSize: '40px 40px' }}
      />

      {/* Top Floating Header */}
      <header className="relative z-10 max-w-7xl mx-auto px-6 py-8 flex items-center justify-between border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#E65100] to-[#9A3412] flex items-center justify-center shadow-lg shadow-[#E65100]/20 border border-white/10">
            <Flame className="w-5 h-5 text-white" />
          </div>
          <div>
            <span className="text-lg font-bold tracking-tight text-white flex items-center gap-2">
              SilicaForge-RL
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-[#E65100]/20 text-[#FB923C] border border-[#E65100]/30">v2.5</span>
            </span>
            <p className="text-[11px] text-slate-400 font-mono tracking-wide">AUTONOMOUS SAF CYBER-PHYSICAL TWIN</p>
          </div>
        </div>

        <div className="flex items-center gap-4 text-xs font-medium">
          <a
            href="https://github.com/harsh3011dev-oops/SilicaForge-RL"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden sm:flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg border border-slate-700/60 bg-slate-800/40 hover:bg-slate-800/80 hover:border-slate-600 transition-all text-slate-300"
          >
            <span>GitHub Repository</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
          <button
            onClick={onExplore}
            className="flex items-center gap-2 px-5 py-2 rounded-lg bg-gradient-to-r from-[#E65100] to-[#EA580C] hover:from-[#EA580C] hover:to-[#F97316] text-white font-semibold shadow-lg shadow-[#E65100]/25 transition-all transform hover:-translate-y-0.5 cursor-pointer"
          >
            <span>Launch Digital Twin</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </header>

      {/* Hero Body Section */}
      <main className="relative z-10 max-w-5xl mx-auto px-6 pt-20 pb-28 text-center flex flex-col items-center">
        {/* Academic / Thesis Tag */}
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-slate-800/80 border border-slate-700/80 backdrop-blur-md mb-8 shadow-sm">
          <Award className="w-4 h-4 text-[#FB923C]" />
          <span className="text-xs font-medium tracking-wide text-slate-300">
            Calibrated to Schei-Tveit (1998) &amp; SINTEF Metallurgy Benchmarks
          </span>
        </div>

        {/* Rich Typography Headline */}
        <h1 className="text-4xl sm:text-6xl md:text-7xl font-['Playfair_Display',serif] font-normal tracking-tight text-white max-w-4xl leading-[1.12] mb-6">
          Autonomous Smelting for <br />
          <span className="italic font-light bg-gradient-to-r from-[#FDBA74] via-[#FB923C] to-[#E65100] bg-clip-text text-transparent">
            Submerged Arc Furnaces
          </span>
        </h1>

        {/* Minimal Sub-paragraph */}
        <p className="text-slate-400 text-base sm:text-lg max-w-2xl mx-auto leading-relaxed mb-10 font-normal">
          A continuous Reinforcement Learning controller (Soft Actor-Critic) operating a 
          28.5&nbsp;MW silicon metal furnace. Unlocks closed-loop secondary SiO offgas condensation, 
          eliminates gas blowouts, and optimizes electrical energy to 14.4&nbsp;kWh/kg Si.
        </p>

        {/* Primary CTA Button */}
        <div className="flex flex-col sm:flex-row items-center gap-4 mb-20">
          <button
            onClick={onExplore}
            className="group relative px-8 py-4 rounded-xl bg-gradient-to-r from-[#E65100] via-[#EA580C] to-[#F97316] text-white font-semibold text-base shadow-xl shadow-[#E65100]/30 hover:shadow-[#E65100]/50 transition-all duration-300 transform hover:-translate-y-1 flex items-center gap-3 cursor-pointer"
          >
            <span>Explore 3D Digital Twin</span>
            <div className="w-7 h-7 rounded-lg bg-white/20 flex items-center justify-center group-hover:translate-x-1 transition-transform">
              <ArrowRight className="w-4 h-4" />
            </div>
          </button>

          <a
            href="#sources"
            className="px-6 py-4 rounded-xl border border-slate-700/60 bg-slate-900/40 hover:bg-slate-800/50 text-slate-300 text-sm font-medium transition-all flex items-center gap-2"
          >
            <BookOpen className="w-4 h-4 text-slate-400" />
            <span>Literature &amp; Sources</span>
            <ChevronDown className="w-3.5 h-3.5 opacity-60" />
          </a>
        </div>

        {/* Key Real-World Metrics Grid */}
        <div className="w-full grid grid-cols-2 md:grid-cols-4 gap-4 text-left">
          <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-sm hover:border-slate-700 transition-colors">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Silicon Recovery</span>
              <Activity className="w-4 h-4 text-[#FB923C]" />
            </div>
            <div className="text-3xl font-bold font-['Plus_Jakarta_Sans'] text-white">76.9%</div>
            <p className="text-xs text-emerald-400 mt-1 font-medium">+27.4% vs Industrial PID</p>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-sm hover:border-slate-700 transition-colors">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Specific Energy (SEC)</span>
              <Zap className="w-4 h-4 text-[#FBBF24]" />
            </div>
            <div className="text-3xl font-bold font-['Plus_Jakarta_Sans'] text-white">14.45</div>
            <p className="text-xs text-slate-400 mt-1">kWh / kg Si (Global Benchmark)</p>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-sm hover:border-slate-700 transition-colors">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Production Cost</span>
              <Cpu className="w-4 h-4 text-[#38BDF8]" />
            </div>
            <div className="text-3xl font-bold font-['Plus_Jakarta_Sans'] text-white">$1.63</div>
            <p className="text-xs text-emerald-400 mt-1 font-medium">Top Quartile Market Parity</p>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-sm hover:border-slate-700 transition-colors">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Channeling Risk</span>
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-3xl font-bold font-['Plus_Jakarta_Sans'] text-white">0.00%</div>
            <p className="text-xs text-emerald-400 mt-1 font-medium">Zero Explosive Blowouts</p>
          </div>
        </div>
      </main>

      {/* Scientific Foundation & Literature Sources Section */}
      <section id="sources" className="relative z-10 max-w-5xl mx-auto px-6 py-20 border-t border-white/5">
        <div className="text-center max-w-2xl mx-auto mb-14">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-md bg-[#1E293B] text-xs font-mono text-slate-300 mb-3">
            <Database className="w-3.5 h-3.5 text-[#38BDF8]" />
            <span>THERMODYNAMIC EQUILIBRIUM &amp; VALIDATION</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-['Playfair_Display',serif] text-white font-normal mb-3">
            Grounded in Metallurgical Literature
          </h2>
          <p className="text-slate-400 text-sm">
            SilicaForge-RL models real thermochemical equilibrium, 3-zone energy balances, and gas aerodynamics 
            published by the world's leading silicon smelting institutes.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Card 1 */}
          <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800/80 hover:border-slate-700 transition-all flex flex-col justify-between">
            <div>
              <div className="text-xs font-mono text-[#FB923C] mb-2 font-semibold">[1] THE BIBLE OF SILICON</div>
              <h3 className="text-lg font-bold text-white mb-2">Schei, Tuset &amp; Tveit (1998)</h3>
              <p className="text-xs text-slate-400 leading-relaxed mb-4">
                <em>"Production of High Silicon Alloys"</em>, Tapir Forlag. Provides the governing carbothermic reduction 
                kinetics (SiO₂ + 2C → Si + 2CO), intermediate SiC equilibria, and mass closure calculations.
              </p>
            </div>
            <div className="pt-3 border-t border-white/5 flex items-center justify-between text-[11px] text-slate-500 font-mono">
              <span>CANTERA / EQUILIBRIUM</span>
              <span>PEAK YIELD: 88.5%</span>
            </div>
          </div>

          {/* Card 2 */}
          <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800/80 hover:border-slate-700 transition-all flex flex-col justify-between">
            <div>
              <div className="text-xs font-mono text-[#38BDF8] mb-2 font-semibold">[2] BURDEN AERODYNAMICS</div>
              <h3 className="text-lg font-bold text-white mb-2">SINTEF &amp; NTNU Research (2020)</h3>
              <p className="text-xs text-slate-400 leading-relaxed mb-4">
                Furnace gas permeability studies. Establishes the relationship between woodchip matrix (8%–18%), 
                superficial gas velocity (&lt;0.95 m/s), and condensation of volatile SiO gas.
              </p>
            </div>
            <div className="pt-3 border-t border-white/5 flex items-center justify-between text-[11px] text-slate-500 font-mono">
              <span>BURDEN POROSITY</span>
              <span>Kp &ge; 0.88 INDEX</span>
            </div>
          </div>

          {/* Card 3 */}
          <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800/80 hover:border-slate-700 transition-all flex flex-col justify-between">
            <div>
              <div className="text-xs font-mono text-emerald-400 mb-2 font-semibold">[3] ELECTRICAL SCALING</div>
              <h3 className="text-lg font-bold text-white mb-2">Andreae &amp; Westly Formulations</h3>
              <p className="text-xs text-slate-400 leading-relaxed mb-4">
                SAIMM Pyrometallurgy SAF k-Factor standards (k = R · D). Models dynamic arc length, 
                operating resistance (1.35 mΩ), current (82 kA), and power factor (cos φ = 0.84).
              </p>
            </div>
            <div className="pt-3 border-t border-white/5 flex items-center justify-between text-[11px] text-slate-500 font-mono">
              <span>3-PHASE IMPEDANCE</span>
              <span>28.5 MW POWER</span>
            </div>
          </div>
        </div>

        {/* Secondary Offgas Innovation Highlight Box */}
        <div className="mt-8 p-6 rounded-2xl bg-gradient-to-r from-[#E65100]/10 via-[#1D4ED8]/10 to-transparent border border-[#E65100]/20 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-[#E65100]/20 border border-[#E65100]/30 flex items-center justify-center shrink-0">
              <Layers className="w-6 h-6 text-[#FB923C]" />
            </div>
            <div>
              <h4 className="text-base font-bold text-white mb-1">
                Thesis Breakthrough: Stage 2 Closed-Loop SiO Condensation Loop
              </h4>
              <p className="text-xs text-slate-300 max-w-2xl leading-relaxed">
                Rather than treating offgas as a lost stream, the simulator models an upper-shaft condensation reactor 
                (2SiO → Si + SiO₂), capturing unreacted silicon and recycling ~18.2 MJ/kg of exothermic heat into incoming quartz.
              </p>
            </div>
          </div>
          <button
            onClick={onExplore}
            className="px-5 py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-medium text-xs whitespace-nowrap border border-slate-700 transition-all cursor-pointer"
          >
            Launch Visualizer →
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 max-w-7xl mx-auto px-6 py-10 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-4">
        <p>SilicaForge-RL &copy; 2026. Released under the MIT License.</p>
        <p className="font-mono text-[11px]">Industrial AI &amp; Metallurgy Research Group</p>
      </footer>
    </div>
  );
};
