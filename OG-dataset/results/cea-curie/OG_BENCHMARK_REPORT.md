# Empirical Benchmark Evaluation on Real-World Supercomputing Workload

- **Trace Name:** `CEA Curie Supercomputer (Bullx DLC, 5040 Nodes)`
- **Evaluated Jobs:** 1,500 real completed tasks
- **Cluster Configuration:** 128 Nodes (Heterogeneous Silicon Speeds 0.85-1.15x)
- **Generated At:** 2026-10-22 23:13:10

## 🏆 Key Performance Highlights (Proposed Algorithm vs All 3 Baselines)

### 1. Load Variance Reduction (Lower Imbalance):
- **vs Round-Robin (RR):** **+25.4%** (`181.77` vs `243.75`)
- **vs Least-Loaded Node (LLN):** **+16.9%** (`181.77` vs `218.70`)
- **vs Centralized Work Queue (WQ):** **+73.0%** (`181.77` vs `672.42`)

### 2. Average Job Wait Time Reduction:
- **vs Round-Robin (RR):** **+25.9%** (`141.74s` vs `191.36s`)
- **vs Least-Loaded Node (LLN):** **+8.2%** (`141.74s` vs `154.35s`)
- **vs Centralized Work Queue (WQ):** **+65.0%** (`141.74s` vs `405.25s`)

### 3. 95th Percentile Tail Wait Latency Reduction:
- **vs Round-Robin (RR):** **+17.6%** (`346.70s` vs `420.99s`)
- **vs Least-Loaded Node (LLN):** **+11.0%** (`346.70s` vs `389.63s`)
- **vs Centralized Work Queue (WQ):** **+60.8%** (`346.70s` vs `884.84s`)

### 4. Cluster Load Equity:
- **Jain's Fairness Index:** `0.860` across all nodes.

## 📊 Comprehensive Empirical Metrics Table

| Policy | Makespan (s) | Load Variance ($\sigma^2$) | Avg Wait Time (s) | 95th % Tail Wait (s) | Jain's Fairness | Dispatch Overhead ($\mu s$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Proposed Hierarchical (P9)** | 34,680.0 | **181.77** | **141.74** | **346.70** | 0.860 | 74.4 |
| Least-Loaded Node (LLN) | 34,360.0 | 218.70 | 154.35 | 389.63 | 0.824 | 44.3 |
| Round-Robin (RR) | 34,640.0 | 243.75 | 191.36 | 420.99 | 0.875 | 8.5 |
| Centralized Work Queue (WQ) | 36,930.0 | 672.42 | 405.25 | 884.84 | 0.439 | 9.2 |
| Random Dispatch | 34,540.0 | 353.51 | 222.30 | 716.31 | 0.814 | 8.2 |

## 🖼️ Generated Figures

1. **Figure 1 (Load Heatmap):** [`fig1_og_heatmap_proposed_vs_rr.png`](figures/fig1_og_heatmap_proposed_vs_rr.png)
2. **Figure 2 (Variance Trajectory):** [`fig2_og_variance_trajectory.png`](figures/fig2_og_variance_trajectory.png)
3. **Figure 3 (Wait Time CDF):** [`fig3_og_wait_time_cdf.png`](figures/fig3_og_wait_time_cdf.png)
4. **Figure 4 (4-Metric Bar Charts):** [`fig4_og_policy_metrics_barchart.png`](figures/fig4_og_policy_metrics_barchart.png)
5. **Figure 5 (Fairness/Makespan Tradeoff):** [`fig5_og_fairness_makespan_tradeoff.png`](figures/fig5_og_fairness_makespan_tradeoff.png)
