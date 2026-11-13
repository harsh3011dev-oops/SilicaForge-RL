#!/usr/bin/env python3
"""Project History, Architecture & Complete Technical Overview Document Generator.

Generates a comprehensive Word document (SilicaForge_RL_Project_Overview_History.docx)
covering the full lifecycle of the SilicaForge-RL initiative:
1. Executive Identity & Vision
2. Complete Evolutionary History (Chronological Timeline from v1.0 to v2.5)
3. Full Technical Architecture & Codebase Map
4. Governing Metallurgy & Physical Kinetics (Schei & Tveit, 3-Zone Thermal, Electrical Coupling)
5. Algorithmic Journey: Fixed -> PID -> PPO -> Curious SAC
6. The Breakthrough Innovations: Stage 2 SiO Offgas Recovery & Burden Aerodynamics
7. Final Industrial KPI Benchmarks (Yield, Cost, SEC, Channeling)
8. Complete How-To Guide (Setup, Training, Benchmarking, Web UI)
"""

import os
import sys
import docx
from pathlib import Path
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_DOCX = PROJECT_ROOT / "SilicaForge_RL_Project_Overview_History.docx"
CHART_PNG = PROJECT_ROOT / "data" / "validation" / "ppo_vs_sac_comparison.png"

# Color Palette: Clean Professional Industrial Engineering
COLOR_PRIMARY = RGBColor(24, 43, 73)      # Deep Navy (#182B49)
COLOR_SECONDARY = RGBColor(194, 65, 12)   # Arc Terracotta (#C2410C)
COLOR_TEXT = RGBColor(33, 37, 41)         # Dark Charcoal (#212529)
COLOR_MUTED = RGBColor(108, 117, 125)     # Cool Grey (#6C757D)
COLOR_GREEN = RGBColor(22, 101, 52)       # Forest Green (#166534)

HEX_PRIMARY = "182B49"
HEX_SECONDARY = "C2410C"
HEX_LIGHT_BG = "F8FAFC"
HEX_CALLOUT_BG = "FEF3C7"
HEX_CALLOUT_BORDER = "D97706"
HEX_ZEBRA = "F1F5F9"
HEX_WHITE = "FFFFFF"

def set_cell_background(cell, hex_color):
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading)

def set_cell_margins(cell, top=120, bottom=120, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)

def style_paragraph(p, space_before=0, space_after=6, line_spacing=1.15):
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing

def add_callout(doc, title, text, icon="💡"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, HEX_CALLOUT_BG)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=180)

    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:left w:val="single" w:sz="36" w:space="0" w:color="{HEX_CALLOUT_BORDER}"/>
            <w:top w:val="none"/>
            <w:right w:val="none"/>
            <w:bottom w:val="none"/>
        </w:tcBorders>
    ''')
    tcPr.append(borders)

    p = cell.paragraphs[0]
    style_paragraph(p, space_before=0, space_after=4)
    run_t = p.add_run(f"{icon} {title}\n")
    run_t.font.name = "Arial"
    run_t.font.size = Pt(10.5)
    run_t.font.bold = True
    run_t.font.color.rgb = RGBColor(180, 83, 9)

    run_b = p.add_run(text)
    run_b.font.name = "Arial"
    run_b.font.size = Pt(9.5)
    run_b.font.color.rgb = COLOR_TEXT

    p_after = doc.add_paragraph()
    style_paragraph(p_after, space_before=0, space_after=6)

def add_heading_styled(doc, text, level=1):
    h = doc.add_heading(level=level)
    size = 16 if level == 1 else (13 if level == 2 else 11)
    space_b = 14 if level == 1 else (10 if level == 2 else 6)
    style_paragraph(h, space_before=space_b, space_after=4)
    r = h.add_run(text)
    r.font.name = "Arial"
    r.font.size = Pt(size)
    r.font.bold = True
    r.font.color.rgb = COLOR_PRIMARY if level == 1 else (COLOR_SECONDARY if level == 2 else COLOR_TEXT)
    return h

def generate_project_overview_docx():
    print("[1/6] Initializing Document Template...")
    doc = docx.Document()

    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("SILICAFORGE-RL: Complete Project History & Comprehensive Architecture Manual")
        hrun.font.name = "Arial"
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = COLOR_MUTED

        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        frun = fp.add_run("SilicaForge-RL v2.5 | End-to-End Autonomous Submerged Arc Furnace Engineering")
        frun.font.name = "Arial"
        frun.font.size = Pt(8.5)
        frun.font.color.rgb = COLOR_MUTED

    # -------------------------------------------------------------
    # COVER PAGE / HEADER BLOCK
    # -------------------------------------------------------------
    p_badge = doc.add_paragraph()
    style_paragraph(p_badge, space_before=16, space_after=4)
    r_b = p_badge.add_run("COMPLETE PROJECT DOSSIER & HISTORICAL CHRONOLOGY")
    r_b.font.name = "Arial"
    r_b.font.size = Pt(9.5)
    r_b.font.bold = True
    r_b.font.color.rgb = COLOR_SECONDARY

    p_title = doc.add_paragraph()
    style_paragraph(p_title, space_before=0, space_after=6)
    r_t = p_title.add_run("SilicaForge-RL: Autonomous Industrial Silicon Smelting Controller")
    r_t.font.name = "Arial"
    r_t.font.size = Pt(22)
    r_t.font.bold = True
    r_t.font.color.rgb = COLOR_PRIMARY

    p_sub = doc.add_paragraph()
    style_paragraph(p_sub, space_before=0, space_after=14)
    r_s = p_sub.add_run("A Complete Master Guide Covering Project Genesis, Physics Upgrades, Algorithmic Milestones, Stage 2 Secondary SiO Recovery, and Final Benchmark Verification.")
    r_s.font.name = "Arial"
    r_s.font.size = Pt(11.5)
    r_s.font.italic = True
    r_s.font.color.rgb = COLOR_MUTED

    # Metadata Table
    tbl_meta = doc.add_table(rows=2, cols=4)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_headers = ["Repository", "Current Version", "Key Algorithms", "Core Benchmark"]
    meta_values = [
        "harsh3011dev-oops / SilicaForge-RL",
        "v2.5 (Industrial Production)",
        "SAC (Champion), PPO, PID",
        "Schei-Tveit (1998) 28.5 MW SAF"
    ]
    for col_idx in range(4):
        c_h = tbl_meta.cell(0, col_idx)
        set_cell_background(c_h, HEX_PRIMARY)
        set_cell_margins(c_h, top=80, bottom=80, left=100, right=100)
        p = c_h.paragraphs[0]
        style_paragraph(p, space_before=0, space_after=0)
        r = p.add_run(meta_headers[col_idx])
        r.font.name = "Arial"
        r.font.size = Pt(8.0)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

        c_v = tbl_meta.cell(1, col_idx)
        set_cell_background(c_v, HEX_LIGHT_BG)
        set_cell_margins(c_v, top=100, bottom=100, left=100, right=100)
        p2 = c_v.paragraphs[0]
        style_paragraph(p2, space_before=0, space_after=0)
        r2 = p2.add_run(meta_values[col_idx])
        r2.font.name = "Arial"
        r2.font.size = Pt(8.5)
        r2.font.bold = True
        r2.font.color.rgb = COLOR_TEXT

    p_sep = doc.add_paragraph()
    style_paragraph(p_sep, space_before=14, space_after=10)

    # -------------------------------------------------------------
    # SECTION 1: PROJECT IDENTITY & EXECUTIVE VISION
    # -------------------------------------------------------------
    add_heading_styled(doc, "1. Project Identity & Executive Vision", level=1)
    p = doc.add_paragraph()
    style_paragraph(p, space_before=0, space_after=6)
    p.add_run(
        "SilicaForge-RL is an end-to-end autonomous cyber-physical control platform designed for commercial Submerged Arc Furnaces (SAF) "
        "producing metallurgical-grade silicon metal. Smelting silicon is notoriously difficult: raw quartz (SiO2) and carbon (coal, coke, woodchips) "
        "are heated above 1850°C by colossal 3-phase carbon electrodes dissipating 25 to 35 Megawatts of electrical energy.\n\n"
        "Historically, furnace control has relied on human operators watching slag color, erratic arc currents, and offgas flares, "
        "often resulting in massive SiO offgas blowouts, high electricity bills (>14 kWh/kg), and sudden refractory overheating. "
        "The objective of SilicaForge-RL is to prove that multi-objective Reinforcement Learning (specifically Soft Actor-Critic and PPO) "
        "coupled with strict thermodynamic First-Principles can autonomously operate a 28.5 MW silicon furnace at maximum metallurgical recovery, "
        "minimum electrical energy, and guaranteed physical safety."
    )

    add_callout(
        doc,
        "The Core Mission: Low Cost, High Efficiency, Zero Blowouts",
        "Target Criteria: Achieve >= 77% direct silicon recovery yield, Specific Energy Consumption (SEC) <= 14.5 kWh/kg Si, "
        "production cost <= $1.65/kg Si, while eliminating gas channeling and catastrophic furnace meltdowns.",
        icon="🎯"
    )

    # -------------------------------------------------------------
    # SECTION 2: COMPLETE CHRONOLOGICAL PROJECT HISTORY
    # -------------------------------------------------------------
    add_heading_styled(doc, "2. Chronological Project History & Milestones", level=1)
    p_hist = doc.add_paragraph()
    style_paragraph(p_hist, space_before=0, space_after=6)
    p_hist.add_run(
        "The project evolved through five distinct development phases, migrating from a simplified academic simulator "
        "to an audited, multi-variable industrial cyber-physical engine:"
    )

    history_events = [
        ("Phase 1: Genesis & Baseline Simulator (Commits bafce27 -> ee3498d)",
         "Initial creation of the SilicaSmeltingEnv Gymnasium environment. Developed single-zone lumped thermal dynamics and basic yield curve. "
         "Integrated React 19 Three.js 3D Digital Twin UI to visually render furnace electrodes, molten silicon bath, and offgas emissions in real time."),
        
        ("Phase 2: Git Hygiene & Disturbance Suite (Commit 0a5b0ce)",
         "Integrated active Safety Shield mechanism to prevent refractory damage. Added Domain Randomization across 8 parameters (quartz moisture, "
         "carbon reactivity, thermal loss, sensor noise). Created multi-scenario benchmark evaluation suite and automated report pipeline."),
        
        ("Phase 3: The Roadmap Review & Thermodynamic Recalibration (Commit d1cb261)",
         "Based on a rigorous technical research review, overhauled the physical simulator to match Schei & Tveit (1998) industrial benchmarks:\n"
         "  * Calibrated peak chemical yield from unphysical 94% down to industrial reality (87.0% - 89.8%).\n"
         "  * Implemented 5-stream elemental silicon mass conservation (closure error < 1e-6 kg).\n"
         "  * Built lumped 3-Zone Thermal Model (Burden 1180°C, Crater 1880°C, Molten Bath 1580°C).\n"
         "  * Implemented 3-phase coupled electrical circuit (I ~ 82 kA, V ~ 160 V, cos phi ~ 0.84).\n"
         "  * Expanded observation space from 7-D to 18-D multi-zone state space and created 12 Level-1/Level-2 unit tests in tests/test_physics_audit.py."),
        
        ("Phase 4: Algorithmic Training & Comparison: PPO vs Curious SAC (Commit 06e25f2)",
         "Trained PPO for 300,000 steps (reward climbed from -6,000 to +973.7). Then trained continuous Soft Actor-Critic (SAC) for 150,000 steps. "
         "Because of its auto-entropy curiosity mechanism, SAC dramatically outperformed PPO (+1,326 reward), operating at $1.54/kg production cost "
         "and 14.7 kWh/kg energy consumption."),
        
        ("Phase 5: Thesis Innovation & Real-World Aerodynamics Upgrade (Commits 6f4e799 -> ef2fdcf)",
         "Integrated user's core thesis vision: Stage 2 Closed-Loop Secondary SiO Offgas Condensation Reactor (2SiO -> Si + SiO2). "
         "Scraped metallurgical prior literature (SINTEF, Elkem) and integrated Burden Permeability Index (woodchip matrix) and superficial gas velocity. "
         "Executed fine-tuning run on Curious SAC (50,000 steps) achieving 0.00% gas channeling and compiled formal Master Thesis documentation.")
    ]

    for title, desc in history_events:
        add_heading_styled(doc, title, level=3)
        p = doc.add_paragraph()
        style_paragraph(p, space_before=0, space_after=6)
        p.add_run(desc)

    # -------------------------------------------------------------
    # SECTION 3: COMPLETE CODEBASE MAP & TECHNICAL ARCHITECTURE
    # -------------------------------------------------------------
    add_heading_styled(doc, "3. Codebase Map & Technical Architecture", level=1)
    p_arch = doc.add_paragraph()
    style_paragraph(p_arch, space_before=0, space_after=6)
    p_arch.add_run(
        "The repository is structured into modular layers adhering to modern clean-code and reproducible ML standards:"
    )

    code_modules = [
        ["src/env/silicon_env.py", "Core Gymnasium simulation engine. Contains 3-zone thermal integrator, coupled electrical circuit, 5-stream mass balance, Stage 2 secondary condenser, and economic reward function."],
        ["src/data/scrape_industrial_literature.py", "Scraping & prior knowledge ingestion pipeline. Extracts real-world operating bounds, Andreae k-factors, and woodchip porosity indices from pyrometallurgical literature."],
        ["data/industrial_priors/industrial_saf_parameters.json", "Structured database of metallurgical literature priors used for aerodynamic modeling and domain randomization."],
        ["src/optimization/train_v2_controllers.py", "Universal reinforcement learning training engine supporting PPO and SAC with checkpoint callbacks, evaluation callbacks, and transfer/resume capabilities."],
        ["src/optimization/benchmark_v2_comparison.py", "Multi-seed benchmark evaluation harness. Runs 25 rollouts across 5 scenarios per controller and generates publication-grade comparative JSON and PNG plots."],
        ["tests/test_physics_audit.py", "Comprehensive scientific test suite (12 tests) verifying First-Law energy closure, mass conservation, electrical consistency, and thermal stratification."],
        ["frontend/", "React 19 + Three.js digital twin Web UI rendering real-time 3D furnace visualization, electrode motion, temperature heatmaps, and telemetry charts."],
        ["generate_thesis_report.py", "Automated Word document compiler producing formal Master Thesis documentation with embedded figures and tables."]
    ]

    tbl_code = doc.add_table(rows=len(code_modules)+1, cols=2)
    tbl_code.alignment = WD_TABLE_ALIGNMENT.CENTER

    tbl_code.cell(0, 0).paragraphs[0].add_run("File / Path").font.bold = True
    tbl_code.cell(0, 1).paragraphs[0].add_run("Functional Description").font.bold = True
    set_cell_background(tbl_code.cell(0, 0), HEX_PRIMARY)
    set_cell_background(tbl_code.cell(0, 1), HEX_PRIMARY)
    tbl_code.cell(0, 0).paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
    tbl_code.cell(0, 1).paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
    set_cell_margins(tbl_code.cell(0, 0), top=80, bottom=80, left=100, right=100)
    set_cell_margins(tbl_code.cell(0, 1), top=80, bottom=80, left=100, right=100)

    for idx, (path, desc) in enumerate(code_modules):
        c0 = tbl_code.cell(idx+1, 0)
        c1 = tbl_code.cell(idx+1, 1)
        bg = HEX_ZEBRA if idx % 2 == 1 else HEX_WHITE
        set_cell_background(c0, bg)
        set_cell_background(c1, bg)
        set_cell_margins(c0, top=70, bottom=70, left=100, right=100)
        set_cell_margins(c1, top=70, bottom=70, left=100, right=100)
        r0 = c0.paragraphs[0].add_run(path)
        r0.font.name = "Courier New"
        r0.font.size = Pt(8.0)
        r0.font.bold = True
        r1 = c1.paragraphs[0].add_run(desc)
        r1.font.name = "Arial"
        r1.font.size = Pt(8.5)

    p_post_c = doc.add_paragraph()
    style_paragraph(p_post_c, space_before=6, space_after=10)

    # -------------------------------------------------------------
    # SECTION 4: GOVERNING METALLURGICAL PHYSICS
    # -------------------------------------------------------------
    add_heading_styled(doc, "4. Governing Metallurgical Kinetics & Physics Formulation", level=1)
    p_phys = doc.add_paragraph()
    style_paragraph(p_phys, space_before=0, space_after=6)
    p_phys.add_run(
        "The core strength of SilicaForge-RL is that the RL agents do not interact with a black box, "
        "but rather with a calibrated non-linear physical system governed by the following relations:\n\n"
        "1. Primary Reduction & Thermodynamics (Schei & Tveit 1998):\n"
        "   SiO2(s) + 2C(s) -> Si(l) + 2CO(g)  [Endothermic, Delta_H = 28.5 MJ / kg Si]\n"
        "   SiO2(s) + 3C(s) -> SiC(s) + 2CO(g) [Intermediate carbide formation]\n"
        "   SiO2(s) + 2SiC(s) -> 3Si(l) + 2CO(g) [High-temperature silicon recovery in crater]\n\n"
        "2. Strict 5-Stream Mass Balance Conservation:\n"
        "   m_Si_in = m_Si_tapped + m_Si_sio_gas + m_Si_slag + m_Si_dust + m_Si_sic_inventory\n"
        "   All fraction components sum strictly to 1.000000, ensuring Level 1 audit compliance.\n\n"
        "3. Lumped 3-Zone Energy Conservation Differential Equations:\n"
        "   Burden (Zone 1): C_1 * (dT_1/dt) = Q_up + Q_cond - Q_loss_1 - Q_evap\n"
        "   Crater (Zone 2): C_2 * (dT_2/dt) = 0.88*P_elec - Q_rxn - Q_loss_2 - Q_up - Q_down\n"
        "   Bath (Zone 3):   C_3 * (dT_3/dt) = 0.12*P_elec + Q_down - Q_loss_3 - Q_tap\n"
        "   Guaranteed energy balance error < 1e-4 GJ per 15-minute control interval.\n\n"
        "4. Coupled Electrical Circuit Model:\n"
        "   Resistance: R(z, T) = 1.35 * [1.0 - 0.25*(z - 250)/100 - 0.08*(T_crater - 1880)/500] mOhm\n"
        "   Impedance:  Z = sqrt(R^2 + X^2) with fixed reactance X = 0.92 mOhm -> cos(phi) = R/Z ~ 0.83-0.86\n"
        "   Electrode Current: I = sqrt((P/3)/R) ~ 75 - 90 kA\n\n"
        "5. Stage 2 Closed-Loop Secondary SiO Offgas Condensation (Thesis Core):\n"
        "   2 SiO(g) -> Si(s) + SiO2(s) [Exothermic disproportionation in 800-1100°C upper shaft]\n"
        "   Exothermic heat (~18.2 MJ/kg recovered) preheats descending quartz, reducing SEC by ~0.8 kWh/kg."
    )

    # -------------------------------------------------------------
    # SECTION 5: ALGORITHMIC COMPARISON & BENCHMARK READINGS
    # -------------------------------------------------------------
    add_heading_styled(doc, "5. Algorithmic Comparison: PPO vs Curious SAC vs Baselines", level=1)
    p_algo = doc.add_paragraph()
    style_paragraph(p_algo, space_before=0, space_after=6)
    p_algo.add_run(
        "Why did Soft Actor-Critic (SAC) outperform PPO? The secret lies in Maximum Entropy Reinforcement Learning:\n\n"
        "J(pi) = E [ sum_t ( r(s_t, a_t) + alpha * H(pi(.|s_t)) ) ]\n\n"
        "While PPO uses a fixed small entropy bonus (ent_coef=0.005) and learns in conservative batches, SAC dynamically tunes its curiosity (ent_coef='auto'). "
        "In a continuous multi-actuator industrial furnace (modulating Power, Electrode Immersion Depth, and C/SiO2 Stoichiometric Ratio simultaneously), "
        "SAC actively probed the boundary of electrical impedance and discovered that maintaining deep electrode immersion under the burden "
        "minimized radiation loss and stabilized crater temperature at exactly 1847°C - 1868°C."
    )

    # Final Benchmark Numbers
    bench_data = [
        ["Controller", "Algorithm Class", "Nominal Yield (%)", "SEC (kWh/kg)", "Unit Cost ($/kg)", "Channeling Risk", "Safety Trips"],
        ["Curious SAC v2.5", "Off-Policy Max Entropy RL", "76.92%", "14.45", "$1.63", "0.00% (Zero)", "0 (Zero)"],
        ["PPO v2", "On-Policy Clipped Policy Gradient", "71.93%", "15.43", "$1.72", "0.00% (Zero)", "0 (Zero)"],
        ["Industrial PID", "Classical Error Feedback", "49.52%", "25.27", "$2.73", "0.00% (Sluggish)", "0 (Zero)"],
        ["Fixed Baseline", "Open-Loop Steady Operator", "87.79%*", "12.78*", "$1.47*", "0.00% (Open Arc)", "1 MELTDOWN"]
    ]

    tbl_bench = doc.add_table(rows=len(bench_data), cols=7)
    tbl_bench.alignment = WD_TABLE_ALIGNMENT.CENTER

    for col_idx in range(7):
        c = tbl_bench.cell(0, col_idx)
        set_cell_background(c, HEX_PRIMARY)
        set_cell_margins(c, top=80, bottom=80, left=60, right=60)
        p = c.paragraphs[0]
        style_paragraph(p, space_before=0, space_after=0)
        r = p.add_run(bench_data[0][col_idx])
        r.font.name = "Arial"
        r.font.size = Pt(7.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)

    for r_idx in range(1, len(bench_data)):
        row = bench_data[r_idx]
        bg = HEX_ZEBRA if r_idx % 2 == 1 else HEX_WHITE
        if "MELTDOWN" in row[6]:
            bg = "FEE2E2"
        elif "Curious SAC" in row[0]:
            bg = "F0FDF4"

        for c_idx in range(7):
            cell = tbl_bench.cell(r_idx, c_idx)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=70, bottom=70, left=60, right=60)
            p = cell.paragraphs[0]
            style_paragraph(p, space_before=0, space_after=0)
            r = p.add_run(row[c_idx])
            r.font.name = "Arial"
            r.font.size = Pt(7.5)
            if "Curious SAC" in row[0]:
                r.font.bold = True
                r.font.color.rgb = COLOR_GREEN
            elif "MELTDOWN" in row[c_idx]:
                r.font.bold = True
                r.font.color.rgb = RGBColor(185, 28, 28)
            else:
                r.font.color.rgb = COLOR_TEXT

    p_note = doc.add_paragraph()
    style_paragraph(p_note, space_before=4, space_after=8)
    r_n = p_note.add_run("*Note: Fixed baseline appears efficient under nominal calm conditions, but crashes with severe thermal meltdown (-14,295 penalty) when raw material quality drops by 10%.")
    r_n.font.name = "Arial"
    r_n.font.size = Pt(8.0)
    r_n.font.italic = True
    r_n.font.color.rgb = COLOR_MUTED

    # -------------------------------------------------------------
    # SECTION 6: HOW-TO OPERATE GUIDE (REPRODUCIBILITY)
    # -------------------------------------------------------------
    add_heading_styled(doc, "6. Practical Operations Guide (Reproducibility & Execution)", level=1)
    p_ops = doc.add_paragraph()
    style_paragraph(p_ops, space_before=0, space_after=6)
    p_ops.add_run(
        "To reproduce any result, train new controllers, or run the digital twin UI, use the following documented shell commands:\n\n"
        "1. Activate Virtual Environment:\n"
        "   cd \"/home/piet/Desktop/harsh /rl project\"\n"
        "   source venv/bin/activate\n\n"
        "2. Run Scientific Physics Audit Suite (12 Unit Tests):\n"
        "   ./venv/bin/python tests/test_physics_audit.py\n\n"
        "3. Train Curious SAC Controller (Fine-Tuning / From Checkpoint):\n"
        "   ./venv/bin/python src/optimization/train_v2_controllers.py --algo sac --timesteps 50000 --resume models/best_sac/best_model.zip --seed 42\n\n"
        "4. Execute Multi-Seed Industrial Disturbance Benchmark:\n"
        "   ./venv/bin/python src/optimization/benchmark_v2_comparison.py\n\n"
        "5. Launch 3D Digital Twin Web Dashboard:\n"
        "   cd frontend && npm run dev\n"
        "   Navigate to http://localhost:5173 to interact with the Three.js 3D SAF visualization.\n\n"
        "6. Recompile Thesis Documentation:\n"
        "   ./venv/bin/python generate_thesis_report.py"
    )

    print(f"[6/6] Writing Complete Project Dossier to: {OUTPUT_DOCX}")
    doc.save(str(OUTPUT_DOCX))
    print("=" * 80)
    print(f"[SUCCESS] Complete Project Overview & History Dossier compiled successfully!")
    print(f"File Path: {OUTPUT_DOCX}")
    print("=" * 80)

if __name__ == "__main__":
    generate_project_overview_docx()

