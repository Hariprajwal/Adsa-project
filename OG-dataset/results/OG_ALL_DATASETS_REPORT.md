# Master Empirical Evaluation Across All 3 Official Supercomputing Traces

- **Evaluated Datasets:** 3 Production Traces (CEA-Curie, LANL-CM5, LLNL-Thunder)
- **Total Workload Traced:** 4,500 real supercomputing tasks
- **Cluster Architecture:** 128 Heterogeneous Compute Nodes (0.85x - 1.15x Silicon Performance Multipliers)
- **Evaluation Timestamp:** 2026-10-22 08:14:24

## 🏆 Cross-Dataset Proposed Algorithm (P9) Performance Summary

| Dataset / Supercomputer | vs Round-Robin Var $\sigma^2$ | vs LLN Var $\sigma^2$ | vs Central WQ Var $\sigma^2$ | Avg Wait Reduction (vs RR) | Tail Wait Reduction (vs RR) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **CEA Curie Supercomputer (Bullx DLC, 5040 Nodes)** | **+26.6%** | **+16.2%** | **+74.2%** | **+27.0%** | **+17.2%** |
| **Los Alamos National Lab (Thinking Machines CM-5, 1024 Nodes)** | **-18.7%** | **+3.1%** | **+11.6%** | **-172.1%** | **-183.0%** |
| **Lawrence Livermore National Lab (Thunder Cluster, 4008 Nodes)** | **+4.7%** | **+2.6%** | **+33.6%** | **+31.1%** | **+48.5%** |

## 📊 Comprehensive Cross-Dataset Metrics Table

| Dataset | Policy | Makespan (s) | Load Variance ($\sigma^2$) | Avg Wait Time (s) | 95th % Tail Wait (s) | Jain's Fairness |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| cea-curie | **Proposed Hierarchical (P9)** | 34,360.0 | **185.95** | **177.32** | **437.69** | 1.000 |
| cea-curie | Least-Loaded Node (LLN) | 34,260.0 | 221.78 | 189.56 | 480.92 | 1.000 |
| cea-curie | Round-Robin (RR) | 34,760.0 | 253.24 | 242.88 | 528.84 | 1.000 |
| cea-curie | Centralized Work Queue (WQ) | 35,310.0 | 720.27 | 490.76 | 1161.50 | 1.000 |
| cea-curie | Random Dispatch | 34,380.0 | 368.30 | 294.38 | 934.26 | 1.000 |
| lanl | **Proposed Hierarchical (P9)** | 23,820.0 | **327.99** | **84.16** | **256.44** | 1.000 |
| lanl | Least-Loaded Node (LLN) | 24,010.0 | 338.48 | 98.99 | 277.62 | 1.000 |
| lanl | Round-Robin (RR) | 23,600.0 | 276.36 | 30.93 | 90.61 | 1.000 |
| lanl | Centralized Work Queue (WQ) | 25,120.0 | 371.03 | 291.76 | 709.67 | 1.000 |
| lanl | Random Dispatch | 23,630.0 | 271.15 | 38.70 | 127.33 | 1.000 |
| llnl | **Proposed Hierarchical (P9)** | 30,120.0 | **226.71** | **64.52** | **254.28** | 1.000 |
| llnl | Least-Loaded Node (LLN) | 29,740.0 | 232.69 | 67.61 | 300.37 | 1.000 |
| llnl | Round-Robin (RR) | 30,500.0 | 237.86 | 93.60 | 493.39 | 1.000 |
| llnl | Centralized Work Queue (WQ) | 31,770.0 | 341.35 | 293.39 | 1291.74 | 1.000 |
| llnl | Random Dispatch | 30,140.0 | 253.66 | 110.56 | 504.91 | 1.000 |

## 📁 Dataset Results Folders

- **CEA Curie Supercomputer (Bullx DLC, 5040 Nodes):** [`results/cea-curie/`](results/cea-curie/) with [Figures](results/cea-curie/figures/) and [Report](results/cea-curie/OG_BENCHMARK_REPORT.md)
- **Los Alamos National Lab (Thinking Machines CM-5, 1024 Nodes):** [`results/lanl/`](results/lanl/) with [Figures](results/lanl/figures/) and [Report](results/lanl/OG_BENCHMARK_REPORT.md)
- **Lawrence Livermore National Lab (Thunder Cluster, 4008 Nodes):** [`results/llnl/`](results/llnl/) with [Figures](results/llnl/figures/) and [Report](results/llnl/OG_BENCHMARK_REPORT.md)
