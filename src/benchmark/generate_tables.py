"""
Table Generator for Paper Results (Phase 3)
Extracts empirical simulation measurements from benchmark_results.json
and generates publication-ready Tables 1, 2, 3, and 4 in Markdown and LaTeX.
"""

import os
import sys
import json

# Ensure project root is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from typing import Dict, Any

def generate_paper_tables(
    benchmark_json: str = r"d:\downloads\ADSA Proj\data\benchmark_results.json",
    output_md: str = r"d:\downloads\ADSA Proj\data\paper_tables.md"
) -> str:
    with open(benchmark_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    trace_stats = data["table1_dataset_stats"]
    policies = data["table2_3_policy_comparison"]
    scalability = data["table4_scalability"]
    multi_trace = data["multi_trace_eval"]

    md = []
    md.append("# Publication Tables: Empirical Evaluation Results\n")
    md.append("**Project Track:** P9 - Entropy-Guided Hierarchical Load Balancing  \n")
    md.append("**Evaluation Workloads:** Official Parallel Workloads Archive Traces (LANL HPC, LLNL Thunder, CEA Curie)\n\n")

    # -------------------------------------------------------------------------
    # TABLE 1: Workload Trace Dataset Statistics
    # -------------------------------------------------------------------------
    md.append("### Table 1: Workload Trace Dataset Statistics\n")
    md.append("| Dataset Name | HPC System Description | Recorded Jobs | Total Nodes | Trace Duration (h) | Mean Job Runtime (s) | Std Dev Runtime (s) |\n")
    md.append("| :--- | :--- | :---: | :---: | :---: | :---: | :---: |\n")
    for ts in trace_stats:
        md.append(f"| **{ts['trace_name']}** | {ts['system_name']} | {ts['total_jobs']:,} | {ts['node_count']:,} | {ts['trace_duration_hours']} h | {ts['mean_runtime_s']:.1f} s | {ts['std_runtime_s']:.1f} s |\n")
    md.append("\n---\n\n")

    # -------------------------------------------------------------------------
    # TABLE 2: Load Imbalance & Fairness Evaluation
    # -------------------------------------------------------------------------
    md.append("### Table 2: Load Imbalance & Fairness Comparison (N=512 Nodes)\n")
    md.append("| Scheduling Policy | Load Variance ($\\sigma^2$) | Standard Deviation ($\\sigma$) | Jain's Fairness Index ($\\mathcal{J}$) | Improvement vs. RR Baseline |\n")
    md.append("| :--- | :---: | :---: | :---: | :---: |\n")
    
    rr_var = policies["round_robin"]["avg_load_variance"]
    for pol_key in ["round_robin", "least_loaded", "work_queue", "random", "hierarchical"]:
        p = policies[pol_key]
        var = p["avg_load_variance"]
        std = var ** 0.5
        jain = p["jains_fairness_index"]
        
        if pol_key == "round_robin":
            imp = "Baseline"
            prefix = ""
            suffix = ""
        else:
            diff = ((rr_var - var) / rr_var) * 100.0
            imp = f"{'+' if diff > 0 else ''}{diff:.1f}% variance"
            if pol_key == "hierarchical":
                prefix = "**"
                suffix = "**"
            else:
                prefix = ""
                suffix = ""
        md.append(f"| {prefix}{p['policy_label']}{suffix} | {prefix}{var:.2f}{suffix} | {prefix}{std:.2f}{suffix} | {prefix}{jain:.3f}{suffix} | {prefix}{imp}{suffix} |\n")
    md.append("\n---\n\n")

    # -------------------------------------------------------------------------
    # TABLE 3: Job Performance & Tail Latency Metrics
    # -------------------------------------------------------------------------
    md.append("### Table 3: Job Performance & Tail Latency Metrics (N=512 Nodes)\n")
    md.append("| Scheduling Policy | Workload Makespan (s) | Avg. Wait Time (s) | 95th Percentile Wait Time (s) | Tail Latency Reduction |\n")
    md.append("| :--- | :---: | :---: | :---: | :---: |\n")

    rr_tail = policies["round_robin"]["tail_wait_time_95_seconds"]
    for pol_key in ["round_robin", "least_loaded", "work_queue", "hierarchical"]:
        p = policies[pol_key]
        ms = p["makespan_seconds"]
        avg_w = p["avg_wait_time_seconds"]
        tail_w = p["tail_wait_time_95_seconds"]
        
        if pol_key == "round_robin":
            imp = "Baseline"
            prefix = ""
            suffix = ""
        else:
            diff = ((rr_tail - tail_w) / rr_tail) * 100.0
            imp = f"-{diff:.1f}% tail wait"
            if pol_key == "hierarchical":
                prefix = "**"
                suffix = "**"
            else:
                prefix = ""
                suffix = ""
        md.append(f"| {prefix}{p['policy_label']}{suffix} | {prefix}{ms:.1f} s{suffix} | {prefix}{avg_w:.2f} s{suffix} | {prefix}{tail_w:.2f} s{suffix} | {prefix}{imp}{suffix} |\n")
    md.append("\n---\n\n")

    # -------------------------------------------------------------------------
    # TABLE 4: Scheduling Overhead & Scalability Trends
    # -------------------------------------------------------------------------
    md.append("### Table 4: Scheduling Overhead & Scalability (N=128 to 1024)\n")
    md.append("| Scheduling Method | Overhead per Job (N=128) | Overhead per Job (N=512) | Overhead per Job (N=1024) | Complexity Class | Scalability Trend at $N \\ge 1000$ |\n")
    md.append("| :--- | :---: | :---: | :---: | :---: | :---: |\n")
    
    c_sizes = scalability["cluster_sizes"]
    idx_128 = c_sizes.index(128)
    idx_512 = c_sizes.index(512)
    idx_1024 = c_sizes.index(1024)

    rows = [
        ("Round-Robin (RR)", "round_robin", "$O(1)$", "Constant time, load-blind"),
        ("Least-Loaded Node (LLN)", "least_loaded", "$O(N)$", "Severe linear search degradation"),
        ("Centralized Work Queue", "work_queue", "$O(1) - O(N)$", "Queue lock serialization contention"),
        ("Proposed Hierarchical Balancer", "hierarchical", "$\\mathbf{O(\\log N)}$", "Flat logarithmic scaling (sub-millisecond)")
    ]

    for label, pol_key, comp, trend in rows:
        oh_128 = scalability["overhead_ms"][pol_key][idx_128]
        oh_512 = scalability["overhead_ms"][pol_key][idx_512]
        oh_1024 = scalability["overhead_ms"][pol_key][idx_1024]
        
        prefix = "**" if pol_key == "hierarchical" else ""
        suffix = "**" if pol_key == "hierarchical" else ""
        md.append(f"| {prefix}{label}{suffix} | {prefix}{oh_128:.4f} ms{suffix} | {prefix}{oh_512:.4f} ms{suffix} | {prefix}{oh_1024:.4f} ms{suffix} | {prefix}{comp}{suffix} | {prefix}{trend}{suffix} |\n")

    content = "".join(md)
    os.makedirs(os.path.dirname(output_md), exist_ok=True)
    with open(output_md, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[SUCCESS] Paper tables written to: {output_md}")
    return content

if __name__ == "__main__":
    generate_paper_tables()
