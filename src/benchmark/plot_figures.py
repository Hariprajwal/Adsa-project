"""
Publication Figure Plotting Engine using Matplotlib (Phase 3)
Generates the 5 publication-grade figures mandated in P9 Section 8.2:
- Figure 1: Load Distribution Over Time Heatmap (Proposed vs Round-Robin)
- Figure 2: Makespan vs Cluster Size (N in {128, 256, 512, 1024})
- Figure 3: Load Variance Over Time (sigma^2(t) continuous curves)
- Figure 4: Scalability Analysis (Dispatch Latency vs N: O(log N) vs O(N))
- Figure 5: Cumulative Distribution Function (CDF) of Job Wait Times
"""

import os
import sys
import json
from typing import Dict, Any
import numpy as np

# Ensure project root is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import matplotlib
matplotlib.use('Agg') # Headless rendering
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Professional IEEE/ACM Publication Styling
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.titlesize': 13,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'axes.grid': True,
    'grid.alpha': 0.35,
    'grid.linestyle': '--',
    'lines.linewidth': 2.0,
    'lines.markersize': 6
})

PALETTE = {
    "proposed": "#0284c7",    # Cyan / Sky 600
    "lln": "#10b981",         # Emerald 500
    "work_queue": "#8b5cf6",  # Violet 500
    "rr": "#f43f5e",          # Rose 500
    "random": "#f59e0b",      # Amber 500
    "slate_dark": "#0f172a",  # Slate 900
    "card_bg": "#f8fafc"
}

def generate_all_figures(
    benchmark_json: str = r"d:\downloads\ADSA Proj\data\benchmark_results.json",
    output_dir: str = r"d:\downloads\ADSA Proj\data\figures"
) -> Dict[str, str]:
    if not os.path.exists(benchmark_json):
        raise FileNotFoundError(f"Benchmark results JSON not found: {benchmark_json}")

    with open(benchmark_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    os.makedirs(output_dir, exist_ok=True)
    generated_figures = {}

    policies = data["table2_3_policy_comparison"]
    scalability = data["table4_scalability"]

    # -------------------------------------------------------------------------
    # FIGURE 1: Load Distribution Over Time Heatmap (Proposed vs Round-Robin)
    # -------------------------------------------------------------------------
    fig1_path = os.path.join(output_dir, "fig1_load_distribution_heatmap.png")
    from src.benchmark.recreate_figure1 import recreate_figure1
    recreate_figure1(
        trace_path=r"d:\downloads\ADSA Proj\data\traces\LANL-HPC.swf",
        output_png=fig1_path,
        num_nodes=64,
        num_jobs=400
    )
    generated_figures["fig1"] = fig1_path
    print(f"[FIGURE 1 SAVED] {fig1_path}")

    # -------------------------------------------------------------------------
    # FIGURE 2: Makespan vs Cluster Size (N in {128, 256, 512, 1024})
    # -------------------------------------------------------------------------
    fig2_path = os.path.join(output_dir, "fig2_makespan_vs_cluster_size.png")
    fig, ax = plt.subplots(figsize=(7.2, 4.8))

    cluster_sizes = scalability["cluster_sizes"]
    ax.plot(cluster_sizes, scalability["makespan"]["hierarchical"], marker='o', color=PALETTE["proposed"], label="Proposed Hierarchical Balancer", linewidth=2.5)
    ax.plot(cluster_sizes, scalability["makespan"]["least_loaded"], marker='s', color=PALETTE["lln"], label="Least-Loaded Node (LLN)", linestyle='--')
    ax.plot(cluster_sizes, scalability["makespan"]["work_queue"], marker='^', color=PALETTE["work_queue"], label="Centralized Work Queue", linestyle='-.')
    ax.plot(cluster_sizes, scalability["makespan"]["round_robin"], marker='x', color=PALETTE["rr"], label="Round-Robin (RR)", linestyle=':')

    # Annotate improvement at N=1024
    ms_prop = scalability["makespan"]["hierarchical"][-1]
    ms_rr = scalability["makespan"]["round_robin"][-1]
    diff_pct = ((ms_rr - ms_prop) / ms_rr) * 100.0
    ax.annotate(
        f"Makespan Reduction: -{diff_pct:.1f}%\nvs. Round-Robin (N=1024)",
        xy=(1024, ms_prop),
        xytext=(680, ms_prop + (ms_rr - ms_prop) * 0.45),
        arrowprops=dict(facecolor=PALETTE["slate_dark"], shrink=0.08, width=1, headwidth=6),
        bbox=dict(boxstyle="round,pad=0.4", fc="#e0f2fe", ec="#0284c7", lw=1),
        fontweight='bold',
        fontsize=8.5
    )

    ax.set_title("Figure 2: Workload Makespan vs. Cluster Dimension ($N$)", fontweight='bold')
    ax.set_xlabel("Number of Compute Nodes ($N$)")
    ax.set_ylabel("Total Workload Makespan (seconds)")
    ax.set_xticks(cluster_sizes)
    ax.legend(frameon=True, facecolor=PALETTE["card_bg"])
    plt.tight_layout()
    plt.savefig(fig2_path, bbox_inches='tight')
    plt.close()
    generated_figures["fig2"] = fig2_path
    print(f"[FIGURE 2 SAVED] {fig2_path}")

    # -------------------------------------------------------------------------
    # FIGURE 3: Load Variance Over Time (sigma^2(t) continuous curves)
    # -------------------------------------------------------------------------
    fig3_path = os.path.join(output_dir, "fig3_load_variance_over_time.png")
    fig, ax = plt.subplots(figsize=(7.5, 4.8))

    t_series = policies["hierarchical"]["timestamps"][:45]
    v_prop = policies["hierarchical"]["variances"][:45]
    v_lln = policies["least_loaded"]["variances"][:45]
    v_wq = policies["work_queue"]["variances"][:45]
    v_rr = policies["round_robin"]["variances"][:45]

    ax.plot(t_series, v_prop, color=PALETTE["proposed"], label=f"Proposed Balancer (Mean: {np.mean(v_prop):.1f})", linewidth=2.5)
    ax.plot(t_series, v_lln, color=PALETTE["lln"], label=f"Least-Loaded Node (Mean: {np.mean(v_lln):.1f})", linestyle='--')
    ax.plot(t_series, v_wq, color=PALETTE["work_queue"], label=f"Centralized Work Queue (Mean: {np.mean(v_wq):.1f})", linestyle='-.')
    ax.plot(t_series, v_rr, color=PALETTE["rr"], label=f"Round-Robin (Mean: {np.mean(v_rr):.1f})", linestyle=':')

    # Shaded stabilization region
    ax.fill_between(t_series, 0, v_prop, color=PALETTE["proposed"], alpha=0.12)

    ax.set_title(r"Figure 3: Instantaneous Load Variance $\sigma^2(t)$ Over Simulation Timeline", fontweight='bold')
    ax.set_xlabel("Elapsed Simulation Time (seconds)")
    ax.set_ylabel(r"Inter-Node Load Variance ($\sigma^2$)")
    ax.set_ylim(bottom=0)
    ax.legend(frameon=True, facecolor=PALETTE["card_bg"])
    plt.tight_layout()
    plt.savefig(fig3_path, bbox_inches='tight')
    plt.close()
    generated_figures["fig3"] = fig3_path
    print(f"[FIGURE 3 SAVED] {fig3_path}")

    # -------------------------------------------------------------------------
    # FIGURE 4: Scalability Analysis (Dispatch Latency vs N: O(log N) vs O(N))
    # -------------------------------------------------------------------------
    fig4_path = os.path.join(output_dir, "fig4_scalability_analysis.png")
    fig, ax = plt.subplots(figsize=(7.2, 4.8))

    # Analytical and empirical points
    ax.plot(cluster_sizes, scalability["overhead_ms"]["hierarchical"], marker='o', color=PALETTE["proposed"], label=r"Proposed Balancer $O(\log N)$ (Hierarchical)", linewidth=2.5)
    ax.plot(cluster_sizes, scalability["overhead_ms"]["least_loaded"], marker='s', color=PALETTE["lln"], label="Least-Loaded Node $O(N)$ (Flat Scan)", linestyle='--', linewidth=2.0)
    ax.plot(cluster_sizes, scalability["overhead_ms"]["work_queue"], marker='^', color=PALETTE["work_queue"], label="Work Queue (Mutex Serialization)", linestyle='-.')
    ax.plot(cluster_sizes, scalability["overhead_ms"]["round_robin"], marker='x', color=PALETTE["rr"], label="Round-Robin $O(1)$ (Load-Blind)", linestyle=':')

    # Annotate algorithmic contrast at N=1024
    oh_prop = scalability["overhead_ms"]["hierarchical"][-1]
    oh_lln = scalability["overhead_ms"]["least_loaded"][-1]
    speedup = oh_lln / max(0.0001, oh_prop)
    ax.annotate(
        f"{speedup:.1f}x Algorithmic Speedup\nover Flat Linear Scan (N=1024)",
        xy=(1024, oh_prop),
        xytext=(550, oh_prop + (oh_lln - oh_prop) * 0.4),
        arrowprops=dict(facecolor=PALETTE["slate_dark"], shrink=0.08, width=1, headwidth=6),
        bbox=dict(boxstyle="round,pad=0.4", fc="#ecfdf5", ec="#10b981", lw=1),
        fontweight='bold',
        fontsize=8.5
    )

    ax.set_title("Figure 4: Per-Decision Dispatch Overhead vs. Cluster Size ($N$)", fontweight='bold')
    ax.set_xlabel("Cluster Dimension ($N$ Compute Nodes)")
    ax.set_ylabel("Dispatch Latency per Job (milliseconds)")
    ax.set_xticks(cluster_sizes)
    ax.legend(frameon=True, facecolor=PALETTE["card_bg"])
    plt.tight_layout()
    plt.savefig(fig4_path, bbox_inches='tight')
    plt.close()
    generated_figures["fig4"] = fig4_path
    print(f"[FIGURE 4 SAVED] {fig4_path}")

    # -------------------------------------------------------------------------
    # FIGURE 5: Cumulative Distribution Function (CDF) of Job Wait Times
    # -------------------------------------------------------------------------
    fig5_path = os.path.join(output_dir, "fig5_cdf_wait_times.png")
    fig, ax = plt.subplots(figsize=(7.5, 4.8))

    for pol_key, color, ls in [
        ("hierarchical", PALETTE["proposed"], "-"),
        ("least_loaded", PALETTE["lln"], "--"),
        ("work_queue", PALETTE["work_queue"], "-."),
        ("round_robin", PALETTE["rr"], ":")
    ]:
        wt = sorted(policies[pol_key]["wait_times_sample"])
        cdf = np.linspace(0, 1, len(wt))
        label_text = f"{policies[pol_key]['policy_label']} (95%: {policies[pol_key]['tail_wait_time_95_seconds']:.1f}s)"
        ax.plot(wt, cdf, color=color, linestyle=ls, label=label_text, linewidth=2.0)

    # 95th Percentile reference horizontal line
    ax.axhline(0.95, color="#64748b", linestyle="--", linewidth=1.2, alpha=0.8)
    ax.text(min(wt), 0.96, "95th Percentile SLA Threshold", color="#475569", fontsize=8.5, fontweight='bold')

    ax.set_title("Figure 5: Cumulative Distribution Function (CDF) of Job Wait Times", fontweight='bold')
    ax.set_xlabel("Job Wait Time (seconds)")
    ax.set_ylabel(r"Empirical Cumulative Probability $P(X \leq x)$")
    ax.set_ylim(-0.02, 1.05)
    ax.legend(loc="lower right", frameon=True, facecolor=PALETTE["card_bg"])
    plt.tight_layout()
    plt.savefig(fig5_path, bbox_inches='tight')
    plt.close()
    generated_figures["fig5"] = fig5_path
    print(f"[FIGURE 5 SAVED] {fig5_path}")

    return generated_figures

if __name__ == "__main__":
    generate_all_figures()
