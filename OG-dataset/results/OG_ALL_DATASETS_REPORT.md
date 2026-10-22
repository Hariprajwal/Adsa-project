# Master Empirical Evaluation Across All 3 Official Supercomputing Traces

- **Evaluated Datasets:** 3 Production Traces (CEA-Curie, LANL-CM5, LLNL-Thunder)
- **Total Workload Traced:** 4,500 real supercomputing tasks
- **Cluster Architecture:** 128 Heterogeneous Compute Nodes (0.85x - 1.15x Silicon Performance Multipliers)
- **Evaluation Timestamp:** 2026-10-22 23:13:41

## 🏆 Cross-Dataset Proposed Algorithm (P9) Performance Summary

| Dataset / Supercomputer | vs Round-Robin Var $\sigma^2$ | vs LLN Var $\sigma^2$ | vs Central WQ Var $\sigma^2$ | Avg Wait Reduction (vs RR) | Tail Wait Reduction (vs RR) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **CEA Curie Supercomputer (Bullx DLC, 5040 Nodes)** | **+25.4%** | **+16.9%** | **+73.0%** | **+25.9%** | **+17.6%** |
| **Los Alamos National Lab (Thinking Machines CM-5, 1024 Nodes)** | **-18.5%** | **+4.0%** | **+7.3%** | **-232.1%** | **-218.0%** |
| **Lawrence Livermore National Lab (Thunder Cluster, 4008 Nodes)** | **+3.7%** | **+0.3%** | **+35.7%** | **+27.4%** | **+42.6%** |

## 📊 Comprehensive Cross-Dataset Metrics Table

| Dataset | Policy | Makespan (s) | Load Variance ($\sigma^2$) | Avg Wait Time (s) | 95th % Tail Wait (s) | Jain's Fairness |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| cea-curie | **Proposed Hierarchical (P9)** | 34,680.0 | **181.77** | **141.74** | **346.70** | 0.860 |
| cea-curie | Least-Loaded Node (LLN) | 34,360.0 | 218.70 | 154.35 | 389.63 | 0.824 |
| cea-curie | Round-Robin (RR) | 34,640.0 | 243.75 | 191.36 | 420.99 | 0.875 |
| cea-curie | Centralized Work Queue (WQ) | 36,930.0 | 672.42 | 405.25 | 884.84 | 0.439 |
| cea-curie | Random Dispatch | 34,540.0 | 353.51 | 222.30 | 716.31 | 0.814 |
| lanl | **Proposed Hierarchical (P9)** | 23,890.0 | **313.62** | **72.10** | **209.86** | 0.229 |
| lanl | Least-Loaded Node (LLN) | 23,780.0 | 326.58 | 85.32 | 244.70 | 0.197 |
| lanl | Round-Robin (RR) | 23,580.0 | 264.74 | 21.71 | 65.99 | 0.757 |
| lanl | Centralized Work Queue (WQ) | 24,230.0 | 338.28 | 289.48 | 856.77 | 0.108 |
| lanl | Random Dispatch | 23,610.0 | 258.40 | 26.30 | 89.55 | 0.734 |
| llnl | **Proposed Hierarchical (P9)** | 30,010.0 | **222.18** | **52.19** | **223.25** | 0.341 |
| llnl | Least-Loaded Node (LLN) | 30,160.0 | 222.81 | 56.68 | 240.87 | 0.315 |
| llnl | Round-Robin (RR) | 30,460.0 | 230.65 | 71.88 | 388.92 | 0.599 |
| llnl | Centralized Work Queue (WQ) | 30,530.0 | 345.52 | 245.91 | 973.15 | 0.165 |
| llnl | Random Dispatch | 30,220.0 | 229.85 | 78.73 | 354.61 | 0.606 |

## 📁 Dataset Results Folders

- **CEA Curie Supercomputer (Bullx DLC, 5040 Nodes):** [`results/cea-curie/`](results/cea-curie/) with [Figures](results/cea-curie/figures/) and [Report](results/cea-curie/OG_BENCHMARK_REPORT.md)
- **Los Alamos National Lab (Thinking Machines CM-5, 1024 Nodes):** [`results/lanl/`](results/lanl/) with [Figures](results/lanl/figures/) and [Report](results/lanl/OG_BENCHMARK_REPORT.md)
- **Lawrence Livermore National Lab (Thunder Cluster, 4008 Nodes):** [`results/llnl/`](results/llnl/) with [Figures](results/llnl/figures/) and [Report](results/llnl/OG_BENCHMARK_REPORT.md)
