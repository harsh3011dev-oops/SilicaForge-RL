import React, { useState } from 'react';
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
  ChevronDown,
  Sparkles,
  Thermometer
} from 'lucide-react';

interface LandingHeroProps {
  onExplore: () => void;
}

export const LandingHero: React.FC<LandingHeroProps> = ({ onExplore }) => {
  const [activeTab, setActiveTab] = useState<'METRICS' | 'KINETICS' | 'SOURCES'>('METRICS');

  return (
    <div className="min-h-screen w-full bg-[#07090E] text-[#EDE8DF] selection:bg-[#E65100] selection:text-white relative overflow-x-hidden">
      
      {/* =========================================================================
          HERO PHOTO BANNER: Real 28.5 MW Submerged Arc Furnace (User Photo)
          ========================================================================= */}
      <div className="relative w-full h-[720px] sm:h-[820px] overflow-hidden">
        {/* Background Industrial Furnace Photo */}
        <img
          src="/furnace_real.jpg"
          alt="28.5 MW Silicon Submerged Arc Furnace"
          className="w-full h-full object-cover object-center scale-105 filter brightness-[0.78] contrast-[1.12]"
        />

        {/* Artistic Gradient Overlays (Vignette & Deep Molten Glow) */}
        <div className="absolute inset-0 bg-gradient-to-t from-[#07090E] via-[#07090E]/60 to-black/60 pointer-events-none" />
        <div className="absolute inset-0 bg-gradient-to-r from-[#07090E]/85 via-transparent to-[#07090E]/80 pointer-events-none" />
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[1100px] h-[340px] bg-[#E65100]/20 blur-[130px] pointer-events-none" />

        {/* Top Floating Glass Navigation Header */}
        <header className="absolute top-0 left-0 right-0 z-20 max-w-7xl mx-auto px-6 py-7 flex items-center justify-between">
          <div className="flex items-center gap-3.5">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#E65100] via-[#C2410C] to-[#9A3412] flex items-center justify-center shadow-lg shadow-[#E65100]/30 border border-white/20">
              <Flame className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="text-xl font-['Cinzel',serif] tracking-wider text-white font-semibold flex items-center gap-2">
                SILICAFORGE<span className="text-[#FB923C] font-sans text-sm font-bold tracking-tight">RL</span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-[#E65100]/25 text-[#FDBA74] border border-[#E65100]/40">v2.5</span>
              </span>
              <p className="text-[10px] text-slate-300 font-mono tracking-widest uppercase">AUTONOMOUS SAF CYBER-PHYSICAL ENGINE</p>
            </div>
          </div>

          <div className="flex items-center gap-4 text-xs">
            <a
              href="https://github.com/harsh3011dev-oops/SilicaForge-RL"
              target="_blank"
              rel="noopener noreferrer"
              className="hidden sm:flex items-center gap-1.5 px-4 py-2 rounded-lg border border-white/15 bg-black/40 backdrop-blur-md hover:bg-black/60 hover:border-white/30 text-slate-200 transition-all font-mono"
            >
              <span>GitHub</span>
              <ExternalLink className="w-3.5 h-3.5 opacity-70" />
            </a>

            <button
              onClick={onExplore}
              className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-gradient-to-r from-[#E65100] to-[#EA580C] hover:from-[#EA580C] hover:to-[#F97316] text-white font-medium text-xs shadow-lg shadow-[#E65100]/30 border border-white/20 transition-all transform hover:-translate-y-0.5 cursor-pointer"
            >
              <Sparkles className="w-3.5 h-3.5 text-amber-200" />
              <span>Explore 3D Furnace</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </header>

        {/* Hero Content Floating Right on Top of the Real Plant Photo */}
        <div className="absolute inset-0 z-10 flex flex-col justify-end pb-16 sm:pb-24 max-w-5xl mx-auto px-6 text-center sm:text-left">
          {/* Italian Styled Metadata Tag */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-black/60 border border-amber-500/30 backdrop-blur-md w-fit mb-5 self-center sm:self-start">
            <Award className="w-3.5 h-3.5 text-[#FB923C]" />
            <span className="text-xs font-['Cormorant_Garamond',serif] italic text-amber-200 font-medium tracking-wide">
              Fonderia di Silicio &bull; Controllo Ottimale del Forno ad Arco Sommerso (28.5 MW)
            </span>
          </div>

          {/* Italian Styled Rich Headline */}
          <h1 className="text-4xl sm:text-6xl md:text-7xl font-['Cormorant_Garamond',serif] font-normal leading-[1.08] text-white max-w-4xl tracking-tight mb-4 drop-shadow-md">
            L'Arte del Silicio <br />
            <span className="italic font-light bg-gradient-to-r from-[#FED7AA] via-[#FB923C] to-[#E65100] bg-clip-text text-transparent">
              Attraverso l'Intelligenza Artificiale
            </span>
          </h1>

          {/* Elegant Project Description */}
          <p className="text-slate-300 text-sm sm:text-base md:text-lg max-w-2xl font-light leading-relaxed mb-8 drop-shadow font-['Plus_Jakarta_Sans',sans-serif]">
            SilicaForge-RL bridges the violent thermodynamics of a 28.5 MW silicon smelting furnace 
            with continuous Reinforcement Learning. Achieving 14.45 kWh/kg Specific Energy, zero gas blowouts, 
            and closed-loop secondary SiO offgas recovery.
          </p>

          {/* Big Explore More Action Button */}
          <div className="flex flex-col sm:flex-row items-center gap-4 self-center sm:self-start">
            <button
              onClick={onExplore}
              className="group relative px-8 py-4 rounded-xl bg-gradient-to-r from-[#E65100] via-[#EA580C] to-[#F97316] text-white font-semibold text-sm sm:text-base shadow-2xl shadow-[#E65100]/40 hover:shadow-[#E65100]/60 transition-all duration-300 transform hover:-translate-y-1 flex items-center gap-3.5 border border-white/20 cursor-pointer"
            >
              <Flame className="w-5 h-5 text-amber-200 animate-pulse" />
              <span>EXPLORE MORE &bull; 3D DIGITAL TWIN</span>
              <div className="w-7 h-7 rounded-lg bg-white/20 flex items-center justify-center group-hover:translate-x-1.5 transition-transform">
                <ArrowRight className="w-4 h-4" />
              </div>
            </button>

            <a
              href="#literature-sources"
              className="px-6 py-4 rounded-xl border border-white/15 bg-black/40 hover:bg-black/60 text-slate-300 text-xs sm:text-sm font-medium backdrop-blur-md transition-all flex items-center gap-2 font-['Cormorant_Garamond',serif] italic tracking-wide"
            >
              <BookOpen className="w-4 h-4 text-[#FB923C]" />
              <span>Letteratura Scientifica &amp; Fonti</span>
              <ChevronDown className="w-3.5 h-3.5 opacity-60" />
            </a>
          </div>
        </div>
      </div>

      {/* =========================================================================
          INTERACTIVE INDUSTRIAL METRICS STRIP
          ========================================================================= */}
      <div className="max-w-6xl mx-auto px-6 -mt-10 relative z-20">
        <div className="w-full grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-5 rounded-2xl bg-[#0F141E]/90 border border-slate-800/90 backdrop-blur-md shadow-xl hover:border-amber-500/40 transition-all">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">Recupero di Silicio</span>
              <Activity className="w-4 h-4 text-[#FB923C]" />
            </div>
            <div className="text-3xl font-bold font-['Plus_Jakarta_Sans'] text-white">76.92%</div>
            <p className="text-xs text-emerald-400 mt-1 font-medium font-['Cormorant_Garamond',serif] italic">+27.4% rispetto al PID</p>
          </div>

          <div className="p-5 rounded-2xl bg-[#0F141E]/90 border border-slate-800/90 backdrop-blur-md shadow-xl hover:border-amber-500/40 transition-all">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">Consumo Specifico</span>
              <Zap className="w-4 h-4 text-amber-400" />
            </div>
            <div className="text-3xl font-bold font-['Plus_Jakarta_Sans'] text-white">14.45</div>
            <p className="text-xs text-slate-400 mt-1 font-mono">kWh / kg Si (Target Elkem)</p>
          </div>

          <div className="p-5 rounded-2xl bg-[#0F141E]/90 border border-slate-800/90 backdrop-blur-md shadow-xl hover:border-amber-500/40 transition-all">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">Costo Unitario</span>
              <Cpu className="w-4 h-4 text-sky-400" />
            </div>
            <div className="text-3xl font-bold font-['Plus_Jakarta_Sans'] text-white">$1.63</div>
            <p className="text-xs text-emerald-400 mt-1 font-['Cormorant_Garamond',serif] italic">Miglior quartile globale</p>
          </div>

          <div className="p-5 rounded-2xl bg-[#0F141E]/90 border border-slate-800/90 backdrop-blur-md shadow-xl hover:border-amber-500/40 transition-all">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">Rischio di Eruzione</span>
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-3xl font-bold font-['Plus_Jakarta_Sans'] text-white">0.00%</div>
            <p className="text-xs text-emerald-400 mt-1 font-['Cormorant_Garamond',serif] italic">Zero fuoriuscite di SiO</p>
          </div>
        </div>
      </div>

      {/* =========================================================================
          SECTION: SCIENTIFIC FOUNDATION & ITALIAN/INTERNATIONAL LITERATURE
          ========================================================================= */}
      <section id="literature-sources" className="max-w-6xl mx-auto px-6 py-24">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-md bg-slate-800/80 text-xs font-mono text-amber-300 border border-amber-500/20 mb-3">
            <Database className="w-3.5 h-3.5 text-[#FB923C]" />
            <span>FONTI SCIENTIFICHE E TERMODINAMICA</span>
          </div>
          <h2 className="text-3xl sm:text-5xl font-['Cormorant_Garamond',serif] text-white font-normal mb-3">
            Fondamenti Metallurgici &amp; Fonti
          </h2>
          <p className="text-slate-400 text-sm leading-relaxed font-light">
            SilicaForge-RL non è una scatola nera: il simulatore rispetta rigorosamente le equazioni 
            di bilancio di massa, stratificazione termica a tre zone e fluidodinamica pubblicate dai principali istituti mondiali.
          </p>
        </div>

        {/* 3 Core Literary Pillar Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Source 1: Schei & Tveit */}
          <div className="p-7 rounded-2xl bg-gradient-to-b from-[#111624] to-[#0A0E18] border border-slate-800/80 hover:border-amber-500/40 transition-all flex flex-col justify-between group">
            <div>
              <span className="text-[10px] font-mono text-[#FB923C] font-semibold tracking-wider uppercase">[1] La Bibbia del Silicio</span>
              <h3 className="text-xl font-['Cormorant_Garamond',serif] font-bold text-white mt-2 mb-3">
                Schei, Tuset &amp; Tveit (1998)
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed font-light mb-5">
                <em>"Production of High Silicon Alloys"</em> (Tapir Forlag). Modella le reazioni endotermiche nel cratere 
                (SiO₂ + 2C → Si + 2CO a 1880°C), la formazione dell'intermedio carburo di silicio (SiC) e la conservazione a 5 flussi di massa.
              </p>
            </div>
            <div className="pt-4 border-t border-white/5 flex items-center justify-between text-[11px] font-mono text-slate-500">
              <span>CANTERA EQUILIBRIO</span>
              <span className="text-amber-400">YIELD MAX: 88.5%</span>
            </div>
          </div>

          {/* Source 2: SINTEF */}
          <div className="p-7 rounded-2xl bg-gradient-to-b from-[#111624] to-[#0A0E18] border border-slate-800/80 hover:border-sky-500/40 transition-all flex flex-col justify-between group">
            <div>
              <span className="text-[10px] font-mono text-sky-400 font-semibold tracking-wider uppercase">[2] Aerodinamica del Letto</span>
              <h3 className="text-xl font-['Cormorant_Garamond',serif] font-bold text-white mt-2 mb-3">
                SINTEF &amp; NTNU Research (2020)
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed font-light mb-5">
                Studi di permeabilità e velocità superficiale del gas (&lt;0.95 m/s). 
                La matrice porosa creata dai trucioli di legno (woodchips 10%–18%) impedisce la formazione di croste impermeabili e blocca i blowouts eruttivi.
              </p>
            </div>
            <div className="pt-4 border-t border-white/5 flex items-center justify-between text-[11px] font-mono text-slate-500">
              <span>POROSITÀ DARCY</span>
              <span className="text-sky-400">Kp &ge; 0.88 INDICE</span>
            </div>
          </div>

          {/* Source 3: Andreae-Westly */}
          <div className="p-7 rounded-2xl bg-gradient-to-b from-[#111624] to-[#0A0E18] border border-slate-800/80 hover:border-emerald-500/40 transition-all flex flex-col justify-between group">
            <div>
              <span className="text-[10px] font-mono text-emerald-400 font-semibold tracking-wider uppercase">[3] Circuito Trifase</span>
              <h3 className="text-xl font-['Cormorant_Garamond',serif] font-bold text-white mt-2 mb-3">
                Andreae &amp; Westly Formulations
              </h3>
              <p className="text-xs text-slate-400 leading-relaxed font-light mb-5">
                Standard SAIMM sul fattore k di resistenza periferica (k = R · D_elettrodo). 
                Regola la profondità di immersione degli elettrodi in grafite mantenendo R a ~1.35 mΩ e cos φ a ~0.84.
              </p>
            </div>
            <div className="pt-4 border-t border-white/5 flex items-center justify-between text-[11px] font-mono text-slate-500">
              <span>IMPEDENZA D'ARCO</span>
              <span className="text-emerald-400">CORRENTE: 82.5 kA</span>
            </div>
          </div>
        </div>

        {/* Thesis Innovation Banner: Stage 2 SiO Offgas Condensation */}
        <div className="mt-8 p-7 rounded-2xl bg-gradient-to-r from-[#E65100]/15 via-[#1D4ED8]/10 to-black/60 border border-[#E65100]/30 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-[#E65100]/25 border border-[#E65100]/40 flex items-center justify-center shrink-0">
              <Layers className="w-6 h-6 text-[#FB923C]" />
            </div>
            <div>
              <h4 className="text-lg font-['Cormorant_Garamond',serif] font-bold text-white">
                Innovazione della Tesi: Reattore a Condensazione di Gas SiO a Circuito Chiuso
              </h4>
              <p className="text-xs text-slate-300 max-w-2xl leading-relaxed mt-1 font-light">
                Invece di disperdere il monossido di silicio gassoso nei fumi (storicamente 8%–12% di perdita), 
                il sistema modella un reattore di sproporzione esotermica (2SiO → Si + SiO₂), recuperando metallo puro e riciclando ~18.2 MJ/kg 
                di calore nella carica di quarzo discendente.
              </p>
            </div>
          </div>

          <button
            onClick={onExplore}
            className="px-6 py-3 rounded-xl bg-gradient-to-r from-[#E65100] to-[#EA580C] text-white font-semibold text-xs whitespace-nowrap shadow-lg shadow-[#E65100]/30 border border-white/20 transition-all hover:brightness-110 cursor-pointer"
          >
            Avvia Simulatore 3D →
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="max-w-6xl mx-auto px-6 py-12 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-4">
        <p className="font-['Cormorant_Garamond',serif] italic text-sm text-slate-400">
          SilicaForge-RL &bull; Ricerca e Sviluppo sull'Ottimizzazione dei Forni Industriali (2026)
        </p>
        <p className="font-mono text-[11px] text-slate-600">
          Rilasciato sotto licenza open-source MIT
        </p>
      </footer>
    </div>
  );
};
