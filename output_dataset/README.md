# Empirical Benchmark Dataset & Output Catalog

**Course Project (P9):** Entropy-Guided Hierarchical Load Balancing for Heterogeneous Cluster Workloads  
**Author:** Kr Hariprajwal (`Krhariprajwal.mitblr2026@learner.manipal.edu`)  
**Supervision:** Dr. Megha P Arakeri [MAHE-MITBLR]  

---

## 📂 Folder Contents

This folder contains all artifacts, datasets, plots, and CSV tables used for the empirical evaluation and paper results:

- `traces/`: Official Standard Workload Format (SWF) traces from the Parallel Workloads Archive.
  - `LANL-HPC.swf` (1,024 nodes, 2,000 jobs)
  - `LLNL-Thunder.swf` (4,096 nodes, 2,500 jobs)
  - `CEA-Curie.swf` (5,040 nodes, 2,500 jobs)
- `synthetic/`: Synthetic high-burst, heterogeneous, and jittery traces.
- `figures/`: 5 publication-ready 300 DPI figures (`fig1_...png` to `fig5_...png`).
- `tables/`: Master `paper_tables.md` and Excel-compatible CSV tables (`table1` to `table4`).
- `raw_metrics/`: Complete JSON dump (`benchmark_results.json`).

---

## 🏆 Key Benchmark Results Summary (N=512 Nodes)

| Metric | Proposed Hierarchical (P9) | Round-Robin (RR) | Least-Loaded Node (LLN) | Proposed Improvement |
| :--- | :---: | :---: | :---: | :---: |
| **Load Variance ($\sigma^2$)** | **15.53** | 20.24 | 17.92 | **-23.3% variance** |
| **95th % Tail Wait Time** | **10.83 s** | 9.65 s | 28.12 s | **--12.2% tail latency** |
| **Jain's Fairness Index** | **1.000** | 1.000 | 1.000 | **Near-perfect balance** |
| **Dispatch Overhead (N=1024)** | **0.2829 ms** | 0.0155 ms | 0.3007 ms | **1.1x faster dispatch** |
