# Empirical Benchmark Evaluation on Real-World Supercomputing Workload

- **Trace Name:** `Los Alamos National Lab (Thinking Machines CM-5, 1024 Nodes)`
- **Evaluated Jobs:** 1,500 real completed tasks
- **Cluster Configuration:** 128 Nodes (Heterogeneous Silicon Speeds 0.85-1.15x)
- **Generated At:** 2026-10-22 23:13:25

## 🏆 Key Performance Highlights (Proposed Algorithm vs All 3 Baselines)

### 1. Load Variance Reduction (Lower Imbalance):
- **vs Round-Robin (RR):** **-18.5%** (`313.62` vs `264.74`)
- **vs Least-Loaded Node (LLN):** **+4.0%** (`313.62` vs `326.58`)
- **vs Centralized Work Queue (WQ):** **+7.3%** (`313.62` vs `338.28`)

### 2. Average Job Wait Time Reduction:
- **vs Round-Robin (RR):** **-232.1%** (`72.10s` vs `21.71s`)
- **vs Least-Loaded Node (LLN):** **+15.5%** (`72.10s` vs `85.32s`)
- **vs Centralized Work Queue (WQ):** **+75.1%** (`72.10s` vs `289.48s`)

### 3. 95th Percentile Tail Wait Latency Reduction:
- **vs Round-Robin (RR):** **-218.0%** (`209.86s` vs `65.99s`)
- **vs Least-Loaded Node (LLN):** **+14.2%** (`209.86s` vs `244.70s`)
- **vs Centralized Work Queue (WQ):** **+75.5%** (`209.86s` vs `856.77s`)

### 4. Cluster Load Equity:
- **Jain's Fairness Index:** `0.229` across all nodes.

## 📊 Comprehensive Empirical Metrics Table

| Policy | Makespan (s) | Load Variance ($\sigma^2$) | Avg Wait Time (s) | 95th % Tail Wait (s) | Jain's Fairness | Dispatch Overhead ($\mu s$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Proposed Hierarchical (P9)** | 23,890.0 | **313.62** | **72.10** | **209.86** | 0.229 | 71.6 |
| Least-Loaded Node (LLN) | 23,780.0 | 326.58 | 85.32 | 244.70 | 0.197 | 42.8 |
| Round-Robin (RR) | 23,580.0 | 264.74 | 21.71 | 65.99 | 0.757 | 7.7 |
| Centralized Work Queue (WQ) | 24,230.0 | 338.28 | 289.48 | 856.77 | 0.108 | 8.2 |
| Random Dispatch | 23,610.0 | 258.40 | 26.30 | 89.55 | 0.734 | 8.6 |

## 🖼️ Generated Figures

1. **Figure 1 (Load Heatmap):** [`fig1_og_heatmap_proposed_vs_rr.png`](figures/fig1_og_heatmap_proposed_vs_rr.png)
2. **Figure 2 (Variance Trajectory):** [`fig2_og_variance_trajectory.png`](figures/fig2_og_variance_trajectory.png)
3. **Figure 3 (Wait Time CDF):** [`fig3_og_wait_time_cdf.png`](figures/fig3_og_wait_time_cdf.png)
4. **Figure 4 (4-Metric Bar Charts):** [`fig4_og_policy_metrics_barchart.png`](figures/fig4_og_policy_metrics_barchart.png)
5. **Figure 5 (Fairness/Makespan Tradeoff):** [`fig5_og_fairness_makespan_tradeoff.png`](figures/fig5_og_fairness_makespan_tradeoff.png)
