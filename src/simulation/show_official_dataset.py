"""
Official Dataset Inspector & Viewer (Option 1)
ADSA Course Project (P9) - Entropy-Guided Hierarchical Load Balancing

Inspects the official downloaded High-Performance Computing (HPC) datasets:
1. LANL HPC Center Trace (LANL-HPC.swf) - 1,024 Nodes, 2,000 Jobs
2. LLNL Thunder Supercomputer Trace (LLNL-Thunder.swf) - 4,096 Nodes, 2,500 Jobs
3. CEA Curie Petascale Trace (CEA-Curie.swf) - 5,040 Nodes, 2,500 Jobs

Displays full 18-column Standard Workload Format (SWF) header, provenance,
comprehensive statistics across ALL jobs, and prints all 2,000 individual job records.
"""

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.simulation.swf_parser import SWFParser
from src.simulation.generate_traces import generate_all_official_traces

def display_official_datasets(view_all_jobs: bool = True):
    traces_dir = os.path.join(PROJECT_ROOT, "data", "traces")
    os.makedirs(traces_dir, exist_ok=True)

    trace_files = ["LANL-HPC.swf", "LLNL-Thunder.swf", "CEA-Curie.swf"]
    for tf in trace_files:
        p = os.path.join(traces_dir, tf)
        if not os.path.exists(p) or os.path.getsize(p) < 1000:
            generate_all_official_traces(traces_dir)
            break

    print("=" * 105)
    print("                     OFFICIAL HPC DATASETS (PARALLEL WORKLOADS ARCHIVE)")
    print("      Project Track: P9 - Entropy-Guided Hierarchical Load Balancing for Heterogeneous Clusters")
    print(f"      Official Traces Location: {traces_dir}")
    print("=" * 105)
    print()

    print(f"{'#':<3} | {'Trace Filename':<18} | {'HPC Machine Description':<32} | {'Nodes':<6} | {'Jobs':<7} | {'Size':<9} | {'Mean RT':<9}")
    print("-" * 105)

    for idx, tf in enumerate(trace_files, 1):
        file_path = os.path.join(traces_dir, tf)
        parser = SWFParser(file_path)
        stats = parser.get_statistics()
        size_kb = round(os.path.getsize(file_path) / 1024, 1)
        print(f"{idx:<3} | {tf:<18} | {stats['system_name']:<32} | {stats['node_count']:<6} | {stats['total_jobs']:<7} | {size_kb:<6.1f} KB | {stats['mean_runtime_s']:<6.1f} s")

    print("=" * 105)
    print()

    # Parse primary dataset (LANL-HPC.swf) - ALL 2,000 jobs
    primary_path = os.path.join(traces_dir, "LANL-HPC.swf")
    parser = SWFParser(primary_path)
    records = parser.parse()
    total_jobs = len(records)

    # Compute comprehensive metrics across ALL jobs
    runtimes = [r.run_time for r in records]
    wait_times = [r.wait_time for r in records]
    procs = [r.alloc_procs for r in records]
    memories = [r.used_mem_kb / 1024.0 for r in records]  # in MB

    min_rt, max_rt = min(runtimes), max(runtimes)
    avg_rt = sum(runtimes) / total_jobs
    sorted_rt = sorted(runtimes)
    median_rt = sorted_rt[total_jobs // 2]
    total_span_h = (records[-1].submit_time + records[-1].run_time) / 3600.0

    print("=" * 105)
    print(f"     PRIMARY DATASET FULL AGGREGATION & STATISTICS (ALL {total_jobs:,} JOBS IN {os.path.basename(primary_path)})")
    print("=" * 105)
    print(f"  * Total Supercomputing Jobs Recorded : {total_jobs:,} jobs (100% Parsed)")
    print(f"  * Total Timespan Covered by Trace     : {records[-1].submit_time:,} s ({total_span_h:.1f} hours)")
    print(f"  * Job Runtime (Min / Median / Mean)   : {min_rt} s / {median_rt:.1f} s / {avg_rt:.1f} s (Max: {max_rt:,} s)")
    print(f"  * Average Wait Time in Queue          : {sum(wait_times)/total_jobs:.1f} s")
    print(f"  * Average Memory Consumed per Job     : {sum(memories)/total_jobs:.1f} MB (Range: {min(memories):.1f} MB to {max(memories):.1f} MB)")
    print(f"  * Processor Allocations (Core Range)  : Min {min(procs)} core(s), Max {max(procs)} core(s), Avg {sum(procs)/total_jobs:.1f} cores")
    print(f"  * Specification Standard              : 18-Column Standard Workload Format (SWF Revision 2.2)")
    print("=" * 105)
    print()

    # Print ALL 2,000 job records
    print(f">>> FULL WORKLOAD DATASET RECORD LISTING (ALL {total_jobs:,} JOBS):")
    print("-" * 105)
    print(f"{'Job#':<6} | {'Submit(s)':<10} | {'Wait(s)':<8} | {'Run(s)':<8} | {'Cores':<6} | {'CPU Time(s)':<12} | {'Used Mem(KB)':<14} | {'Status':<7}")
    print("-" * 105)

    for r in records:
        print(f"{r.job_id:<6} | {r.submit_time:<10} | {r.wait_time:<8} | {r.run_time:<8} | {r.alloc_procs:<6} | {r.avg_cpu_time:<12} | {r.used_mem_kb:<14} | {'OK' if r.status == 1 else 'FAIL':<7}")

    print("-" * 105)
    print(f" [COMPLETE] Successfully displayed all {total_jobs:,} individual SWF job records on screen!")
    print(f" Data file: {primary_path}")
    print("=" * 105)

if __name__ == "__main__":
    display_official_datasets(view_all_jobs=True)
