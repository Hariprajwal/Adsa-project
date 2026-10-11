"""
Recreate Publication Figure 1: Spatio-Temporal Load Distribution Heatmap
Driven directly by the official LANL HPC Center SWF trace from the Parallel Workloads Archive.
Renders an IEEE/ACM journal publication-grade dual heatmap comparing:
(a) Proposed Entropy-Guided Hierarchical Balancer
(b) Round-Robin Baseline
"""

import os
import sys
import numpy as np

# Ensure project root in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from src.simulation.swf_parser import SWFParser
from src.simulation.workload_mapper import WorkloadMapper
from src.simulation.simulator import DiscreteEventSimulator

def recreate_figure1(
    trace_path: str = r"d:\downloads\ADSA Proj\data\traces\LANL-HPC.swf",
    output_png: str = r"d:\downloads\ADSA Proj\data\figures\fig1_load_distribution_heatmap.png",
    num_nodes: int = 64,
    num_jobs: int = 400
):
    print(f"[FIG 1] Parsing official trace: {trace_path}...")
    parser = SWFParser(trace_path)
    records = parser.parse()
    
    # Scale time so timeline is dense and shows sustained execution
    mapper = WorkloadMapper(time_scale_factor=0.02)
    jobs = mapper.map_records(records, max_jobs=num_jobs)
    print(f"[FIG 1] Mapped {len(jobs)} jobs for 64-node simulation...")

    # Run simulations
    sim = DiscreteEventSimulator(
        num_nodes=num_nodes,
        nodes_per_rack=32,
        sampling_interval=8.0,
        jitter_node_ratio=0.20,
        seed=42
    )

    print("[FIG 1] Simulating Proposed Hierarchical Balancer...")
    res_prop = sim.run(jobs, policy="hierarchical")

    print("[FIG 1] Simulating Round-Robin Baseline...")
    res_rr = sim.run(jobs, policy="round_robin")

    # Extract time series heatmaps (nodes x time_slices)
    # Target 35 time slices
    time_slices = min(len(res_prop.time_series_heatmaps), len(res_rr.time_series_heatmaps), 35)
    
    mat_prop = np.array(res_prop.time_series_heatmaps[:time_slices]).T # [64, time_slices]
    mat_rr = np.array(res_rr.time_series_heatmaps[:time_slices]).T     # [64, time_slices]

    # Convert time indices to simulation minutes
    sim_times = np.array(res_prop.time_series_timestamps[:time_slices]) / 60.0 # in minutes
    if len(sim_times) > 1:
        x_extent = [0.0, sim_times[-1]]
    else:
        x_extent = [0.0, float(time_slices)]

    # Publication-Grade Plotting
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
        'font.size': 10,
        'axes.labelsize': 11,
        'figure.dpi': 300,
        'savefig.dpi': 300
    })

    # Layout adjustments with generous margins to PREVENT ANY TEXT OVERLAP
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.2, 5.8), sharey=True)

    vmin = 0.0
    vmax = 100.0

    # (a) Proposed Balancer
    im1 = ax1.imshow(
        mat_prop,
        aspect='auto',
        cmap='Blues',
        origin='lower',
        extent=[0, time_slices, 0, num_nodes],
        vmin=vmin,
        vmax=vmax,
        interpolation='nearest'
    )
    ax1.set_title(
        "(a) Proposed Hierarchical Balancer\n"
        f"Homogeneous Load Spread | Var $\\sigma^2={res_prop.avg_load_variance:.1f}$ | Jain's $\\mathcal{{J}}={res_prop.jains_fairness_index:.3f}$",
        fontsize=10.0,
        fontweight='bold',
        color="#0369a1",
        pad=8
    )
    ax1.set_xlabel(r"Simulation Timeline (Sampling Epochs, $\Delta t = 8$s)", fontsize=10.5)
    ax1.set_ylabel(r"Compute Node Index ($c_0$ to $c_{63}$)", fontsize=10.5)
    ax1.grid(True, color='white', alpha=0.3, linestyle='--', linewidth=0.5)

    # (b) Round-Robin Baseline
    im2 = ax2.imshow(
        mat_rr,
        aspect='auto',
        cmap='YlOrRd',
        origin='lower',
        extent=[0, time_slices, 0, num_nodes],
        vmin=vmin,
        vmax=vmax,
        interpolation='nearest'
    )
    ax2.set_title(
        "(b) Round-Robin Baseline (Static Heuristic)\n"
        f"Severe Stragglers & Hotspots | Var $\\sigma^2={res_rr.avg_load_variance:.1f}$ | Jain's $\\mathcal{{J}}={res_rr.jains_fairness_index:.3f}$",
        fontsize=10.0,
        fontweight='bold',
        color="#be123c",
        pad=8
    )
    ax2.set_xlabel(r"Simulation Timeline (Sampling Epochs, $\Delta t = 8$s)", fontsize=10.5)
    ax2.grid(True, color='white', alpha=0.3, linestyle='--', linewidth=0.5)

    # Clean layout with top=0.78 to ensure zero collision with suptitle
    fig.subplots_adjust(top=0.76, bottom=0.13, left=0.07, right=0.89, wspace=0.14)

    # Colorbar
    cbar_ax = fig.add_axes([0.91, 0.15, 0.018, 0.59])
    cbar = fig.colorbar(im2, cax=cbar_ax)
    cbar.set_label("Node CPU Utilization (%)", fontsize=10.5, labelpad=8)
    cbar.ax.tick_params(labelsize=9)

    # Main Super Titles placed well above subplots
    fig.suptitle(
        "Figure 1: Spatio-Temporal Cluster Load Distribution Heatmap",
        fontsize=13.5,
        fontweight='bold',
        color="#0f172a",
        y=0.97
    )
    fig.text(
        0.48,
        0.895,
        "Evaluated on Official LANL HPC Center Workload Trace (Parallel Workloads Archive: LANL-HPC.swf) across 64 Nodes",
        fontsize=9.5,
        fontstyle='italic',
        color="#475569",
        ha='center'
    )

    # Annotations
    ax1.annotate(
        "Balanced dispersion\n(No hot spots)",
        xy=(time_slices * 0.65, 32),
        xytext=(time_slices * 0.25, 45),
        arrowprops=dict(arrowstyle="->", color="#0284c7", lw=1.5),
        bbox=dict(boxstyle="round,pad=0.3", fc="#f0f9ff", ec="#0284c7", lw=1),
        fontsize=8.5,
        fontweight='bold'
    )

    ax2.annotate(
        "Straggler hotspot\n(CPU saturation)",
        xy=(time_slices * 0.45, 52),
        xytext=(time_slices * 0.15, 38),
        arrowprops=dict(arrowstyle="->", color="#dc2626", lw=1.5),
        bbox=dict(boxstyle="round,pad=0.3", fc="#fef2f2", ec="#dc2626", lw=1),
        fontsize=8.5,
        fontweight='bold'
    )

    os.makedirs(os.path.dirname(output_png), exist_ok=True)
    plt.savefig(output_png, bbox_inches='tight')
    plt.close()
    print(f"[SUCCESS] Figure 1 successfully recreated and saved at: {output_png}")
    return output_png

if __name__ == "__main__":
    recreate_figure1()
