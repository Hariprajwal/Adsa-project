"""
generate_architecture_diagram.py
Generates a publication-grade, high-resolution System Architecture Diagram
for the Entropy-Guided Hierarchical Load Balancing Framework.
Saves to data/figures/fig0_system_architecture.png and OG-dataset/results/figures/fig0_system_architecture.png.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ArrowStyle

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_FIG_DIR = os.path.join(BASE_DIR, "data", "figures")
OG_FIG_DIR = os.path.join(BASE_DIR, "OG-dataset", "results", "figures")

def create_system_architecture_diagram():
    fig, ax = plt.subplots(figsize=(14, 7.8), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')

    # Color Palette (IEEE Modern Publication Style)
    c_bg = '#f8fafc'
    c_border = '#cbd5e1'
    c_dark = '#0f172a'
    c_blue = '#0284c7'
    c_blue_dark = '#0369a1'
    c_blue_light = '#e0f2fe'
    c_indigo = '#4f46e5'
    c_emerald = '#059669'
    c_emerald_light = '#ecfdf5'
    c_amber = '#d97706'
    c_amber_light = '#fffbeb'
    c_rose = '#e11d48'
    c_rose_light = '#fff1f2'
    c_purple = '#7c3aed'
    c_purple_light = '#f5f3ff'

    # Title Banner
    ax.text(50, 97.2, "Entropy-Guided Hierarchical Load Balancing: End-to-End System Architecture", 
            ha='center', va='center', fontsize=14, fontweight='bold', color=c_dark, fontfamily='sans-serif')
    ax.text(50, 94.6, "Augmented Multi-Tier Interval Tree Topology  •  Dual-Entropy Volatility Engine  •  Dynamic Multi-Resource Scoring", 
            ha='center', va='center', fontsize=9, color='#475569', fontfamily='sans-serif')

    # Outer Container Boxes (3 Major Architectural Sections)
    # Box 1: Workload Ingestion & Dynamic Profiling
    box1 = FancyBboxPatch((2, 3), 27, 88, boxstyle="round,pad=0.8,rounding_size=1.5",
                          facecolor='#f8fafc', edgecolor='#94a3b8', linewidth=1.2, linestyle='--')
    ax.add_patch(box1)
    ax.text(15.5, 89.2, "MODULE 1: WORKLOAD & PROFILER", ha='center', va='center', 
            fontsize=10, fontweight='bold', color=c_dark)

    # Box 2: Hierarchical Aggregation Tree Topology
    box2 = FancyBboxPatch((31, 3), 38, 88, boxstyle="round,pad=0.8,rounding_size=1.5",
                          facecolor='#ffffff', edgecolor=c_blue_dark, linewidth=1.5)
    ax.add_patch(box2)
    ax.text(50, 89.2, "MODULE 2: HIERARCHICAL TOPOLOGY TREE [O(log N)]", ha='center', va='center', 
            fontsize=10, fontweight='bold', color=c_blue_dark)

    # Box 3: Dual-Entropy Volatility Engine & Telemetry Feedback
    box3 = FancyBboxPatch((71, 3), 27, 88, boxstyle="round,pad=0.8,rounding_size=1.5",
                          facecolor='#f8fafc', edgecolor='#94a3b8', linewidth=1.2, linestyle='--')
    ax.add_patch(box3)
    ax.text(84.5, 89.2, "MODULE 3: DUAL-ENTROPY ENGINE", ha='center', va='center', 
            fontsize=10, fontweight='bold', color=c_dark)

    # =========================================================================
    # MODULE 1: INGESTION & PROFILER DETAILS
    # =========================================================================
    # Sub-card: Trace Feeder
    c1 = FancyBboxPatch((4, 71), 23, 14, boxstyle="round,pad=0.5,rounding_size=1.0",
                        facecolor='#f1f5f9', edgecolor='#64748b', linewidth=1.0)
    ax.add_patch(c1)
    ax.text(15.5, 82.5, "Authentic Trace Feeder", ha='center', va='center', fontsize=9, fontweight='bold', color=c_dark)
    ax.text(15.5, 78.5, "Standard Workload Format (.swf)\n18-Field Parsing (CEA-Curie, Thunder, LANL)\nSubmitTime, Cores, RunTime, ReqMem", 
            ha='center', va='center', fontsize=7.2, color='#334155')

    # Sub-card: Dynamic Profiler
    c2 = FancyBboxPatch((4, 47), 23, 19, boxstyle="round,pad=0.5,rounding_size=1.0",
                        facecolor='#eff6ff', edgecolor=c_blue, linewidth=1.2)
    ax.add_patch(c2)
    ax.text(15.5, 63.5, "Dynamic Workload Profiler", ha='center', va='center', fontsize=9, fontweight='bold', color=c_blue_dark)
    ax.text(15.5, 59.2, "Job Classification & Weight Extraction:", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#1e293b')
    ax.text(15.5, 53.5, "• CPU-Bound (MPI): w = [0.70, 0.10, 0.10, 0.10]\n• Mem-Bound (Graph): w = [0.10, 0.70, 0.10, 0.10]\n• I/O-Bound (Stream): w = [0.10, 0.10, 0.50, 0.30]\n• Balanced: w = [0.40, 0.30, 0.15, 0.15]", 
            ha='center', va='center', fontsize=6.8, color='#0f172a', fontfamily='monospace')

    # Sub-card: Composite Scoring
    c3 = FancyBboxPatch((4, 21), 23, 21, boxstyle="round,pad=0.5,rounding_size=1.0",
                        facecolor='#fdf4ff', edgecolor=c_purple, linewidth=1.0)
    ax.add_patch(c3)
    ax.text(15.5, 39.5, "Composite Load Scoring Function", ha='center', va='center', fontsize=8.5, fontweight='bold', color=c_purple)
    ax.text(15.5, 34.5, "L(c_i) = w · U(c_i)\n= w_cpu·CPU + w_mem·Mem\n+ w_net·Net + w_disk·Disk", 
            ha='center', va='center', fontsize=7.5, fontweight='bold', color='#4c1d95', fontfamily='monospace')
    ax.text(15.5, 26.5, "4-Dimensional Resource State Vector:\nU(c_i) in [0, 100]%,   ∑ w_r = 1.0", 
            ha='center', va='center', fontsize=7.0, color='#6b21a8')

    # Connectors in Module 1
    ax.annotate('', xy=(15.5, 66), xytext=(15.5, 71),
                arrowprops=dict(arrowstyle="->", color='#64748b', lw=1.5))
    ax.annotate('', xy=(15.5, 42), xytext=(15.5, 47),
                arrowprops=dict(arrowstyle="->", color=c_blue, lw=1.5))

    # =========================================================================
    # MODULE 2: HIERARCHICAL TOPOLOGY TREE DETAILS
    # =========================================================================
    # Level 0: ClusterRoot
    t_root = FancyBboxPatch((40, 74), 20, 11, boxstyle="round,pad=0.5,rounding_size=1.0",
                            facecolor=c_blue_dark, edgecolor='#0c4a6e', linewidth=1.5)
    ax.add_patch(t_root)
    ax.text(50, 81.5, "Level 0: ClusterRoot", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#ffffff')
    ax.text(50, 77.2, "Global Min/Max Load • Subtree Pointers\nglobal_min_load = Min(r.min_load)", 
            ha='center', va='center', fontsize=7.0, color='#e0f2fe')

    # Level 1: Racks
    rack0 = FancyBboxPatch((33, 50), 15, 14, boxstyle="round,pad=0.4,rounding_size=0.8",
                           facecolor='#e0f2fe', edgecolor=c_blue, linewidth=1.2)
    ax.add_patch(rack0)
    ax.text(40.5, 60.5, "Rack 0 (ToR Switch)", ha='center', va='center', fontsize=8.2, fontweight='bold', color=c_blue_dark)
    ax.text(40.5, 55.0, "Aggregated Vector\nmin_load(R0) = 28.4%\nCapacity: K = 32 Nodes", 
            ha='center', va='center', fontsize=6.8, color='#0369a1')

    rackN = FancyBboxPatch((52, 50), 15, 14, boxstyle="round,pad=0.4,rounding_size=0.8",
                           facecolor='#e0f2fe', edgecolor=c_blue, linewidth=1.2)
    ax.add_patch(rackN)
    ax.text(59.5, 60.5, f"Rack R-1 (ToR)", ha='center', va='center', fontsize=8.2, fontweight='bold', color=c_blue_dark)
    ax.text(59.5, 55.0, "Aggregated Vector\nmin_load(R-1) = 45.1%\nCapacity: K = 32 Nodes", 
            ha='center', va='center', fontsize=6.8, color='#0369a1')

    ax.text(50, 57, "• • •", ha='center', va='center', fontsize=12, fontweight='bold', color='#64748b')

    # Level 2: ComputeNodes
    node0 = FancyBboxPatch((32.5, 18), 10.5, 23, boxstyle="round,pad=0.4,rounding_size=0.8",
                           facecolor=c_emerald_light, edgecolor=c_emerald, linewidth=1.2)
    ax.add_patch(node0)
    ax.text(37.75, 38.0, "Node c_0\n[LOW/Stable]", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#065f46')
    ax.text(37.75, 30.5, "Speed: 1.12x\nCPU: 24%\nMem: 30%\nH_var: 8.2\nFIFO Q: 1", 
            ha='center', va='center', fontsize=6.8, color='#047857')
    ax.text(37.75, 21.0, "Target Node", ha='center', va='center', fontsize=7.0, fontweight='bold', color='#059669')

    node1 = FancyBboxPatch((44.5, 18), 10.5, 23, boxstyle="round,pad=0.4,rounding_size=0.8",
                           facecolor=c_amber_light, edgecolor=c_amber, linewidth=1.2)
    ax.add_patch(node1)
    ax.text(49.75, 38.0, "Node c_1\n[MEDIUM]", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#92400e')
    ax.text(49.75, 30.5, "Speed: 0.98x\nCPU: 58%\nMem: 45%\nH_var: 26.5\nFIFO Q: 3", 
            ha='center', va='center', fontsize=6.8, color='#b45309')
    ax.text(49.75, 21.0, "Transition", ha='center', va='center', fontsize=7.0, color='#d97706')

    nodeN = FancyBboxPatch((57.0, 18), 10.5, 23, boxstyle="round,pad=0.4,rounding_size=0.8",
                           facecolor=c_rose_light, edgecolor=c_rose, linewidth=1.2)
    ax.add_patch(nodeN)
    ax.text(62.25, 38.0, "Node c_N-1\n[HIGH/Jitter]", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#9f1239')
    ax.text(62.25, 30.5, "Speed: 0.88x\nCPU: 88%\nMem: 75%\nH_var: 68.4\nFIFO Q: 8", 
            ha='center', va='center', fontsize=6.8, color='#be123c')
    ax.text(62.25, 21.0, "Evaded!", ha='center', va='center', fontsize=7.0, fontweight='bold', color='#e11d48')

    # Tree Connecting Lines
    ax.annotate('', xy=(42, 64), xytext=(48, 74),
                arrowprops=dict(arrowstyle="->", color=c_blue_dark, lw=1.5))
    ax.annotate('', xy=(58, 64), xytext=(52, 74),
                arrowprops=dict(arrowstyle="->", color=c_blue_dark, lw=1.5))
    ax.annotate('', xy=(37.75, 41), xytext=(39.5, 50),
                arrowprops=dict(arrowstyle="->", color=c_blue, lw=1.2))
    ax.annotate('', xy=(49.75, 41), xytext=(41.5, 50),
                arrowprops=dict(arrowstyle="->", color=c_blue, lw=1.2))
    ax.annotate('', xy=(62.25, 41), xytext=(59.5, 50),
                arrowprops=dict(arrowstyle="->", color=c_blue, lw=1.2))

    # O(log N) Search Callout
    ax.text(50, 10.5, "Coarse-to-Fine Search Complexity: O(R + K) = O(log N) Time\nUpward Telemetry Propagation: O(log N) Depth", 
            ha='center', va='center', fontsize=8.0, fontweight='bold', color=c_dark, 
            bbox=dict(boxstyle="round,pad=0.4", facecolor='#f8fafc', edgecolor='#94a3b8', lw=0.8))

    # Inter-Module Arrows (Module 1 -> Module 2)
    ax.annotate('Job J\n[Weights w]', xy=(31, 78), xytext=(27, 78),
                arrowprops=dict(arrowstyle="-|>", color=c_blue_dark, lw=2.0),
                ha='center', va='bottom', fontsize=7.5, fontweight='bold', color=c_blue_dark)

    # =========================================================================
    # MODULE 3: DUAL-ENTROPY ENGINE & TELEMETRY FEEDBACK
    # =========================================================================
    # Sub-card: Local Variance Engine
    e1 = FancyBboxPatch((73, 67), 23, 18, boxstyle="round,pad=0.5,rounding_size=1.0",
                        facecolor='#ecfdf5', edgecolor=c_emerald, linewidth=1.2)
    ax.add_patch(e1)
    ax.text(84.5, 81.5, "1. Sliding-Window Variance (H_var)", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#065f46')
    ax.text(84.5, 76.0, "H_var(c_i) = [1/(W-1)] ∑ (u_t - u_bar)²\nWindow: W = 10 Telemetry Samples\nEvaluated in O(1) Time per Node", 
            ha='center', va='center', fontsize=7.0, color='#047857', fontfamily='monospace')
    ax.text(84.5, 70.0, "Thresholds: τ_low = 15.0, τ_high = 50.0\nClassifies: LOW, MEDIUM, HIGH", 
            ha='center', va='center', fontsize=6.8, fontweight='bold', color='#065f46')

    # Sub-card: Shannon Entropy Engine
    e2 = FancyBboxPatch((73, 44), 23, 19, boxstyle="round,pad=0.5,rounding_size=1.0",
                        facecolor='#eff6ff', edgecolor=c_blue, linewidth=1.2)
    ax.add_patch(e2)
    ax.text(84.5, 59.5, "2. Shannon Entropy (H_Shannon)", ha='center', va='center', fontsize=8.5, fontweight='bold', color=c_blue_dark)
    ax.text(84.5, 54.0, "H_Shannon = - ∑ p_k · log₂(p_k)\nB = 5 Equiprobable Operational Bins\n[0,20), [20,40), [40,60), [60,80), [80,100]%", 
            ha='center', va='center', fontsize=6.8, color='#0369a1', fontfamily='monospace')
    ax.text(84.5, 47.5, "Normalized Entropy: H_norm = H / log₂(5)\nCluster Thermodynamic Disorder Metric", 
            ha='center', va='center', fontsize=6.8, fontweight='bold', color='#0284c7')

    # Sub-card: Volatility Guardrail & Macro Rebalancer
    e3 = FancyBboxPatch((73, 18), 23, 22, boxstyle="round,pad=0.5,rounding_size=1.0",
                        facecolor='#fffbeb', edgecolor=c_amber, linewidth=1.2)
    ax.add_patch(e3)
    ax.text(84.5, 36.5, "Volatility Guardrail & Rebalancer", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#92400e')
    ax.text(84.5, 30.5, "• Guardrail: Evade HIGH-entropy node\n  via lateral rack neighbor probing.\n• EWMA Predictor: α = 0.30\n  L_hat(t+1) = α·L_curr + (1-α)·L_hat\n• Macro Rebalancer (Algorithm 3):\n  Rebuilds tree when drift > 20%", 
            ha='center', va='center', fontsize=6.8, color='#78350f')

    # Connectors in Module 3
    ax.annotate('', xy=(84.5, 63), xytext=(84.5, 67),
                arrowprops=dict(arrowstyle="->", color=c_emerald, lw=1.2))
    ax.annotate('', xy=(84.5, 40), xytext=(84.5, 44),
                arrowprops=dict(arrowstyle="->", color=c_blue, lw=1.2))

    # Feedback Loop: Module 3 to Module 2
    ax.annotate('Continuous Telemetry Feedback\n& Upward Metric Propagation', 
                xy=(69, 57), xytext=(73, 57),
                arrowprops=dict(arrowstyle="<|-", color=c_emerald, lw=2.0),
                ha='left', va='bottom', fontsize=7.5, fontweight='bold', color='#065f46')

    # Lateral Evasion Arrow in Module 2 (Node N-1 to Node 0)
    ax.annotate('Guardrail Evasion:\nLateral Stable Neighbor', 
                xy=(37.75, 14), xytext=(62.25, 14),
                arrowprops=dict(arrowstyle="->", color=c_rose, lw=1.8, linestyle='--'),
                ha='center', va='top', fontsize=7.2, fontweight='bold', color=c_rose)

    plt.tight_layout()
    
    # Save to both target directories
    os.makedirs(DATA_FIG_DIR, exist_ok=True)
    os.makedirs(OG_FIG_DIR, exist_ok=True)
    out1 = os.path.join(DATA_FIG_DIR, "fig0_system_architecture.png")
    out2 = os.path.join(OG_FIG_DIR, "fig0_system_architecture.png")
    plt.savefig(out1, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.savefig(out2, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"[SUCCESS] High-resolution System Architecture Diagram generated at:\n  - {out1}\n  - {out2}")

if __name__ == "__main__":
    create_system_architecture_diagram()
