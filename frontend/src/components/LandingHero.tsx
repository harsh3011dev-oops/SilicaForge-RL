import React from 'react';
import {
  Flame,
  ArrowRight,
  Sparkles,
  ExternalLink,
  ChevronDown,
  Layers,
  Database
} from 'lucide-react';

interface LandingHeroProps {
  onExplore: () => void;
}

export const LandingHero: React.FC<LandingHeroProps> = ({ onExplore }) => {
  return (
    <div className="min-h-screen w-full bg-[#06080D] text-[#F3EFE6] selection:bg-[#E65100] selection:text-white relative overflow-x-hidden">
      
      {/* =========================================================================
          HERO BANNER: High-Visibility Real Factory Photo + Classy Typography
          ========================================================================= */}
      <div className="relative w-full h-[780px] sm:h-[860px] overflow-hidden">
        {/* Background Real Industrial Submerged Arc Furnace Photo */}
        <img
          src="/furnace_real.jpg"
          alt="28.5 MW Silicon Submerged Arc Furnace"
          className="w-full h-full object-cover object-center scale-100 filter brightness-[0.92] contrast-[1.08] saturate-[1.05]"
        />

        {/* Minimal Vignettes so the Factory Machinery & Arc Fire Stay Strikingly Prominent */}
        <div className="absolute inset-0 bg-gradient-to-t from-[#06080D] via-transparent to-black/45 pointer-events-none" />
        <div className="absolute inset-0 bg-gradient-to-r from-black/60 via-transparent to-black/35 pointer-events-none" />

        {/* Top Minimalist Header */}
        <header className="absolute top-0 left-0 right-0 z-20 max-w-7xl mx-auto px-6 py-8 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-[#E65100] to-[#C2410C] flex items-center justify-center text-white shadow-md shadow-[#E65100]/25 border border-white/20">
              <Flame className="w-4 h-4" />
            </div>
            <div>
              <span className="text-lg font-['Cinzel',serif] tracking-wider text-white font-semibold">
                SILICAFORGE<span className="text-[#FB923C] font-['Plus_Jakarta_Sans',sans-serif] text-xs font-bold ml-1">RL</span>
              </span>
              <p className="text-[10px] text-slate-300 font-mono tracking-widest uppercase">28.5 MW INDUSTRIAL DIGITAL TWIN</p>
            </div>
          </div>

          <div className="flex items-center gap-4 text-xs">
            <a
              href="https://github.com/harsh3011dev-oops/SilicaForge-RL"
              target="_blank"
              rel="noopener noreferrer"
              className="hidden sm:flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg border border-white/20 bg-black/40 backdrop-blur-md hover:bg-black/60 text-slate-200 transition-all font-mono"
            >
              <span>GitHub</span>
              <ExternalLink className="w-3.5 h-3.5 opacity-70" />
            </a>

            <button
              onClick={onExplore}
              className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-gradient-to-r from-[#E65100] to-[#EA580C] hover:from-[#EA580C] hover:to-[#F97316] text-white font-medium text-xs shadow-lg shadow-[#E65100]/30 border border-white/20 transition-all transform hover:-translate-y-0.5 cursor-pointer"
            >
              <Sparkles className="w-3.5 h-3.5 text-amber-200" />
              <span>Launch 3D Twin</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </header>

        {/* Hero Content in Classy Minimal Italian Editorial Serif Font (Cormorant Garamond) */}
        <div className="absolute inset-0 z-10 flex flex-col justify-end pb-20 sm:pb-28 max-w-5xl mx-auto px-6 text-left">
          {/* Subtle Benchmark Pill */}
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-black/55 border border-amber-500/30 backdrop-blur-md w-fit mb-5">
            <span className="w-1.5 h-1.5 rounded-full bg-[#FB923C]" />
            <span className="text-[11px] font-['Plus_Jakarta_Sans',sans-serif] text-amber-200/90 tracking-wider uppercase font-medium">
              Calibrated to Schei &amp; Tveit (1998) &bull; 28.5 MW SAF Benchmark
            </span>
          </div>

          {/* Classy Elegant Headline in English using Italian Classical Serif Typography */}
          <h1 className="text-4xl sm:text-6xl md:text-7xl font-['Cormorant_Garamond',serif] font-normal leading-[1.05] text-white max-w-3xl tracking-tight mb-4 drop-shadow-lg">
            Autonomous Silicon Smelting <br />
            <span className="italic font-light text-[#FED7AA]">
              Through Continuous Reinforcement Learning
            </span>
          </h1>

          {/* Clean Minimal Prose */}
          <p className="text-slate-200 text-sm sm:text-base max-w-xl font-light leading-relaxed mb-8 drop-shadow font-['Plus_Jakarta_Sans',sans-serif]">
            Real-time multi-variable control of active electrical power, 3-phase electrode immersion, 
            and burden stoichiometry. Unlocking closed-loop secondary SiO offgas condensation with zero blowout risk.
          </p>

          {/* Explore More CTA Button */}
          <div className="flex flex-col sm:flex-row items-center gap-4">
            <button
              onClick={onExplore}
              className="group px-7 py-3.5 rounded-xl bg-gradient-to-r from-[#E65100] via-[#EA580C] to-[#F97316] text-white font-medium text-sm shadow-xl shadow-[#E65100]/35 hover:shadow-[#E65100]/50 transition-all duration-300 transform hover:-translate-y-0.5 flex items-center gap-3 border border-white/25 cursor-pointer"
            >
              <Flame className="w-4 h-4 text-amber-200" />
              <span className="tracking-wide">EXPLORE 3D DIGITAL TWIN</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>

            <a
              href="#sources"
              className="px-5 py-3.5 rounded-xl border border-white/20 bg-black/40 hover:bg-black/60 text-slate-300 text-xs font-['Cormorant_Garamond',serif] italic tracking-wider transition-all flex items-center gap-2"
            >
              <span>Scientific Literature &amp; Sources</span>
              <ChevronDown className="w-3.5 h-3.5 opacity-60" />
            </a>
          </div>
        </div>
      </div>

      {/* =========================================================================
          KEY NUMBERS: Clean, Minimal, Glass Cards
          ========================================================================= */}
      <div className="max-w-6xl mx-auto px-6 -mt-10 relative z-20">
        <div className="w-full grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-5 rounded-2xl bg-[#0C101A]/90 border border-white/10 backdrop-blur-md shadow-xl">
            <span className="text-[10px] font-mono text-slate-400 uppercase tracking-widest block mb-1">Silicon Recovery</span>
            <div className="text-3xl font-light font-['Cormorant_Garamond',serif] text-white">76.92%</div>
            <p className="text-[11px] text-emerald-400 mt-0.5 font-['Cormorant_Garamond',serif] italic">+27.4% vs Industrial PID</p>
          </div>

          <div className="p-5 rounded-2xl bg-[#0C101A]/90 border border-white/10 backdrop-blur-md shadow-xl">
            <span className="text-[10px] font-mono text-slate-400 uppercase tracking-widest block mb-1">Specific Energy (SEC)</span>
            <div className="text-3xl font-light font-['Cormorant_Garamond',serif] text-white">14.45</div>
            <p className="text-[11px] text-slate-400 mt-0.5 font-mono">kWh / kg Si (Benchmark)</p>
          </div>

          <div className="p-5 rounded-2xl bg-[#0C101A]/90 border border-white/10 backdrop-blur-md shadow-xl">
            <span className="text-[10px] font-mono text-slate-400 uppercase tracking-widest block mb-1">Unit Production Cost</span>
            <div className="text-3xl font-light font-['Cormorant_Garamond',serif] text-white">$1.63</div>
            <p className="text-[11px] text-emerald-400 mt-0.5 font-['Cormorant_Garamond',serif] italic">Top Quartile Market Parity</p>
          </div>

          <div className="p-5 rounded-2xl bg-[#0C101A]/90 border border-white/10 backdrop-blur-md shadow-xl">
            <span className="text-[10px] font-mono text-slate-400 uppercase tracking-widest block mb-1">Channeling Risk</span>
            <div className="text-3xl font-light font-['Cormorant_Garamond',serif] text-white">0.00%</div>
            <p className="text-[11px] text-emerald-400 mt-0.5 font-['Cormorant_Garamond',serif] italic">Zero Explosive Blowouts</p>
          </div>
        </div>
      </div>

      {/* =========================================================================
          SCIENTIFIC SOURCES SECTION: Clean Classy Cards in English
          ========================================================================= */}
      <section id="sources" className="max-w-6xl mx-auto px-6 py-24">
        <div className="max-w-xl mb-14 text-left">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-md bg-white/5 border border-white/10 text-[11px] font-mono text-amber-300/90 mb-3">
            <Database className="w-3.5 h-3.5 text-[#FB923C]" />
            <span>THERMODYNAMIC EQUILIBRIUM &amp; KINETICS</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-['Cormorant_Garamond',serif] text-white font-normal mb-2">
            Scientific Literature &amp; Governing Principles
          </h2>
          <p className="text-slate-400 text-xs sm:text-sm font-light leading-relaxed">
            SilicaForge-RL models real-world thermochemical kinetics, 3-zone energy balances, and gas aerodynamics 
            published by foundational metallurgical research institutes.
          </p>
        </div>

        {/* 3 Literary Pillar Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Card 1 */}
          <div className="p-6 rounded-2xl bg-[#0C101A]/70 border border-white/10 hover:border-amber-500/40 transition-all flex flex-col justify-between">
            <div>
              <span className="text-[10px] font-mono text-[#FB923C] uppercase tracking-wider font-semibold">[1] The Bible of Silicon</span>
              <h3 className="text-xl font-['Cormorant_Garamond',serif] font-bold text-white mt-1.5 mb-2.5">
                Schei, Tuset &amp; Tveit (1998)
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed font-light mb-4">
                <em>"Production of High Silicon Alloys"</em> (Tapir Forlag). Defines endothermic reduction kinetics 
                (SiO₂ + 2C → Si + 2CO at 1880°C), intermediate SiC equilibria, and 5-stream elemental mass conservation.
              </p>
            </div>
            <div className="pt-3 border-t border-white/5 flex items-center justify-between text-[11px] font-mono text-slate-500">
              <span>CANTERA EQUILIBRIUM</span>
              <span className="text-amber-400/90">PEAK: 88.5% YIELD</span>
            </div>
          </div>

          {/* Card 2 */}
          <div className="p-6 rounded-2xl bg-[#0C101A]/70 border border-white/10 hover:border-sky-500/40 transition-all flex flex-col justify-between">
            <div>
              <span className="text-[10px] font-mono text-sky-400 uppercase tracking-wider font-semibold">[2] Burden Aerodynamics</span>
              <h3 className="text-xl font-['Cormorant_Garamond',serif] font-bold text-white mt-1.5 mb-2.5">
                SINTEF &amp; NTNU Research (2020)
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed font-light mb-4">
                Gas permeability and superficial velocity studies (&lt;0.95 m/s). 
                The porous woodchip matrix (10%–18%) prevents impermeable crust formation and suppresses explosive blowouts.
              </p>
            </div>
            <div className="pt-3 border-t border-white/5 flex items-center justify-between text-[11px] font-mono text-slate-500">
              <span>DARCY POROSITY</span>
              <span className="text-sky-400/90">Kp &ge; 0.88 INDEX</span>
            </div>
          </div>

          {/* Card 3 */}
          <div className="p-6 rounded-2xl bg-[#0C101A]/70 border border-white/10 hover:border-emerald-500/40 transition-all flex flex-col justify-between">
            <div>
              <span className="text-[10px] font-mono text-emerald-400 uppercase tracking-wider font-semibold">[3] 3-Phase Circuit</span>
              <h3 className="text-xl font-['Cormorant_Garamond',serif] font-bold text-white mt-1.5 mb-2.5">
                Andreae &amp; Westly Formulations
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed font-light mb-4">
                SAIMM standards on peripheric resistance (k = R · D). Dynamically regulates 
                continuous electrode immersion depth to maintain operating resistance (1.35 mΩ) and power factor (0.84).
              </p>
            </div>
            <div className="pt-3 border-t border-white/5 flex items-center justify-between text-[11px] font-mono text-slate-500">
              <span>ARC IMPEDANCE</span>
              <span className="text-emerald-400/90">CURRENT: 82.5 kA</span>
            </div>
          </div>
        </div>

        {/* Breakthrough Innovation Banner: Stage 2 Closed-Loop SiO Condenser */}
        <div className="mt-8 p-6 rounded-2xl bg-gradient-to-r from-[#E65100]/15 via-black to-black border border-[#E65100]/30 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 rounded-lg bg-[#E65100]/25 border border-[#E65100]/40 flex items-center justify-center shrink-0">
              <Layers className="w-5 h-5 text-[#FB923C]" />
            </div>
            <div>
              <h4 className="text-base font-['Cormorant_Garamond',serif] font-bold text-white">
                Thesis Core Innovation: Stage 2 Closed-Loop SiO Condensation Loop
              </h4>
              <p className="text-xs text-slate-300 max-w-2xl leading-relaxed mt-0.5 font-light">
                Instead of venting unreacted SiO vapor into atmosphere (historically 8%–12% loss), 
                the model introduces an upper-shaft condensation reactor (2SiO → Si + SiO₂), capturing pure metal and 
                recycling ~18.2 MJ/kg of exothermic heat into incoming quartz.
              </p>
            </div>
          </div>

          <button
            onClick={onExplore}
            className="px-5 py-2.5 rounded-lg bg-gradient-to-r from-[#E65100] to-[#EA580C] text-white font-medium text-xs whitespace-nowrap shadow-md shadow-[#E65100]/30 border border-white/20 transition-all hover:brightness-110 cursor-pointer"
          >
            Launch 3D Visualizer →
          </button>
        </div>
      </section>

      {/* Minimal Clean Footer */}
      <footer className="max-w-6xl mx-auto px-6 py-10 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-4">
        <p className="font-['Cormorant_Garamond',serif] italic text-sm text-slate-400">
          SilicaForge-RL &bull; Industrial Submerged Arc Furnace AI Research (2026)
        </p>
        <p className="font-mono text-[11px] text-slate-600">
          Released under MIT License
        </p>
      </footer>
    </div>
  );
};
