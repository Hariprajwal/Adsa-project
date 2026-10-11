"""
Benchmark Execution Engine (Phase 3)
Executes comprehensive empirical evaluation comparing:
- Proposed Entropy-Guided Hierarchical Balancer (O(log N))
- Round-Robin (RR)
- Least-Loaded Node (LLN, O(N))
- Centralized Work Queue
- Random Allocation

Runs across official SWF traces (LANL HPC, LLNL Thunder, CEA Curie)
and scalability sweeps across N in {128, 256, 512, 1024}.
Saves comprehensive results to data/benchmark_results.json.
"""

import os
import sys
import json
import time

# Ensure project root is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from typing import Dict, Any, List

from src.simulation.swf_parser import SWFParser
from src.simulation.workload_mapper import WorkloadMapper
from src.simulation.simulator import DiscreteEventSimulator, SimulationResult

def run_full_benchmark_suite(
    traces_dir: str = r"d:\downloads\ADSA Proj\data\traces",
    output_json: str = r"d:\downloads\ADSA Proj\data\benchmark_results.json",
    time_scale: float = 0.05,
    sample_jobs: int = 500
) -> Dict[str, Any]:
    print("=" * 80)
    print("STARTING FULL EMPIRICAL BENCHMARK SUITE (PHASE 2 & PHASE 3)")
    print("=" * 80)

    # 1. Parse Trace Statistics (Table 1)
    trace_files = ["LANL-HPC.swf", "LLNL-Thunder.swf", "CEA-Curie.swf"]
    trace_stats = []
    
    for tf in trace_files:
        path = os.path.join(traces_dir, tf)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Trace file not found: {path}")
        parser = SWFParser(path)
        stats = parser.get_statistics()
        trace_stats.append(stats)
        print(f"[TRACE PARSED] {tf:18s} | Jobs: {stats['total_jobs']:5d} | Nodes: {stats['node_count']:5d} | Mean RT: {stats['mean_runtime_s']:7.1f}s")

    # 2. Main Comparative Benchmark on Primary Dataset (LANL HPC Trace, N=512)
    print("\n[STEP 1/3] Running Comparative Policy Benchmark on Primary Trace (LANL HPC, N=512)...")
    primary_trace_path = os.path.join(traces_dir, "LANL-HPC.swf")
    parser = SWFParser(primary_trace_path)
    records = parser.parse()
    
    mapper = WorkloadMapper(time_scale_factor=time_scale)
    jobs = mapper.map_records(records, max_jobs=sample_jobs)
    print(f"Mapped {len(jobs)} jobs for discrete-event simulation.")

    policies = ["hierarchical", "least_loaded", "work_queue", "round_robin", "random"]
    policy_labels = {
        "hierarchical": "Proposed Hierarchical Balancer",
        "least_loaded": "Least-Loaded Node (LLN)",
        "work_queue": "Centralized Work Queue",
        "round_robin": "Round-Robin (RR)",
        "random": "Random Allocation"
    }

    sim_n512 = DiscreteEventSimulator(num_nodes=512, nodes_per_rack=32, sampling_interval=15.0)
    policy_results: Dict[str, Any] = {}

    for pol in policies:
        t0 = time.perf_counter()
        res = sim_n512.run(jobs, policy=pol)
        wall_time = time.perf_counter() - t0
        print(f"  -> {policy_labels[pol]:32s} | Makespan: {res.makespan_seconds:7.1f}s | Wait(avg): {res.avg_wait_time_seconds:5.2f}s | 95% Wait: {res.tail_wait_time_95_seconds:5.2f}s | Variance: {res.avg_load_variance:6.2f} | Jain: {res.jains_fairness_index:.3f} ({wall_time:.2f}s)")
        
        policy_results[pol] = {
            "policy_key": pol,
            "policy_label": policy_labels[pol],
            "makespan_seconds": res.makespan_seconds,
            "avg_wait_time_seconds": res.avg_wait_time_seconds,
            "tail_wait_time_95_seconds": res.tail_wait_time_95_seconds,
            "avg_load_variance": res.avg_load_variance,
            "jains_fairness_index": res.jains_fairness_index,
            "avg_dispatch_overhead_ms": res.avg_dispatch_overhead_ms,
            "timestamps": res.time_series_timestamps[:60],
            "variances": res.time_series_variances[:60],
            "wait_times_sample": res.wait_times[:300],
            "heatmap_sample": res.time_series_heatmaps[:30] # 30 time steps x 512 nodes
        }

    # 3. Scalability Sweep across Cluster Sizes N in {128, 256, 512, 1024}
    print("\n[STEP 2/3] Running Cluster Scalability Sweep across N in {128, 256, 512, 1024}...")
    cluster_sizes = [128, 256, 512, 1024]
    scalability_results = {
        "cluster_sizes": cluster_sizes,
        "makespan": {pol: [] for pol in ["hierarchical", "least_loaded", "work_queue", "round_robin"]},
        "overhead_ms": {pol: [] for pol in ["hierarchical", "least_loaded", "work_queue", "round_robin"]}
    }

    for N in cluster_sizes:
        print(f"  Scaling N = {N} compute nodes...")
        sim = DiscreteEventSimulator(num_nodes=N, nodes_per_rack=32, sampling_interval=20.0)
        # Use 300 jobs for quick sweep
        sweep_jobs = mapper.map_records(records, max_jobs=300)
        
        for pol in ["hierarchical", "least_loaded", "work_queue", "round_robin"]:
            res = sim.run(sweep_jobs, policy=pol)
            scalability_results["makespan"][pol].append(res.makespan_seconds)
            scalability_results["overhead_ms"][pol].append(res.avg_dispatch_overhead_ms)

    # 4. Multi-Trace Comparative Summary (LANL vs LLNL Thunder vs CEA Curie)
    print("\n[STEP 3/3] Cross-Evaluating Proposed Balancer across all 3 Official Traces...")
    multi_trace_eval = {}
    for tf in trace_files:
        p_path = os.path.join(traces_dir, tf)
        p_recs = SWFParser(p_path).parse()
        p_jobs = mapper.map_records(p_recs, max_jobs=300)
        sim = DiscreteEventSimulator(num_nodes=512, nodes_per_rack=32)
        
        res_prop = sim.run(p_jobs, policy="hierarchical")
        res_rr = sim.run(p_jobs, policy="round_robin")
        
        variance_reduction = ((res_rr.avg_load_variance - res_prop.avg_load_variance) / max(0.01, res_rr.avg_load_variance)) * 100.0
        makespan_reduction = ((res_rr.makespan_seconds - res_prop.makespan_seconds) / max(0.01, res_rr.makespan_seconds)) * 100.0
        wait_reduction = ((res_rr.avg_wait_time_seconds - res_prop.avg_wait_time_seconds) / max(0.01, res_rr.avg_wait_time_seconds)) * 100.0
        
        multi_trace_eval[tf] = {
            "trace_name": tf,
            "proposed_makespan": res_prop.makespan_seconds,
            "rr_makespan": res_rr.makespan_seconds,
            "makespan_reduction_pct": round(makespan_reduction, 1),
            "variance_reduction_pct": round(variance_reduction, 1),
            "wait_reduction_pct": round(wait_reduction, 1),
            "fairness_proposed": res_prop.jains_fairness_index,
            "fairness_rr": res_rr.jains_fairness_index
        }
        print(f"  -> {tf:18s} | Makespan Reduction: -{makespan_reduction:.1f}% | Variance Reduction: -{variance_reduction:.1f}% | Wait Reduction: -{wait_reduction:.1f}%")

    # Save to JSON
    benchmark_data = {
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "author": "Kr Hariprajwal",
            "course": "ADSA / HPC Course Project (P9)",
            "primary_dataset": "LANL HPC Center SWF Trace",
            "cluster_nodes_evaluated": 512,
            "total_jobs_evaluated": sample_jobs
        },
        "table1_dataset_stats": trace_stats,
        "table2_3_policy_comparison": policy_results,
        "table4_scalability": scalability_results,
        "multi_trace_eval": multi_trace_eval
    }

    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(benchmark_data, f, indent=2)

    print(f"\n[SUCCESS] Benchmark results successfully exported to: {output_json}")
    return benchmark_data

if __name__ == "__main__":
    run_full_benchmark_suite()
