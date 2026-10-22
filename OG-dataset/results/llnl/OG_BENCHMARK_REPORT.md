# Empirical Benchmark Evaluation on Real-World Supercomputing Workload

- **Trace Name:** `Lawrence Livermore National Lab (Thunder Cluster, 4008 Nodes)`
- **Evaluated Jobs:** 1,500 real completed tasks
- **Cluster Configuration:** 128 Nodes (Heterogeneous Silicon Speeds 0.85-1.15x)
- **Generated At:** 2026-10-22 23:13:41

## 🏆 Key Performance Highlights (Proposed Algorithm vs All 3 Baselines)

### 1. Load Variance Reduction (Lower Imbalance):
- **vs Round-Robin (RR):** **+3.7%** (`222.18` vs `230.65`)
- **vs Least-Loaded Node (LLN):** **+0.3%** (`222.18` vs `222.81`)
- **vs Centralized Work Queue (WQ):** **+35.7%** (`222.18` vs `345.52`)

### 2. Average Job Wait Time Reduction:
- **vs Round-Robin (RR):** **+27.4%** (`52.19s` vs `71.88s`)
- **vs Least-Loaded Node (LLN):** **+7.9%** (`52.19s` vs `56.68s`)
- **vs Centralized Work Queue (WQ):** **+78.8%** (`52.19s` vs `245.91s`)

### 3. 95th Percentile Tail Wait Latency Reduction:
- **vs Round-Robin (RR):** **+42.6%** (`223.25s` vs `388.92s`)
- **vs Least-Loaded Node (LLN):** **+7.3%** (`223.25s` vs `240.87s`)
- **vs Centralized Work Queue (WQ):** **+77.1%** (`223.25s` vs `973.15s`)

### 4. Cluster Load Equity:
- **Jain's Fairness Index:** `0.341` across all nodes.

## 📊 Comprehensive Empirical Metrics Table

| Policy | Makespan (s) | Load Variance ($\sigma^2$) | Avg Wait Time (s) | 95th % Tail Wait (s) | Jain's Fairness | Dispatch Overhead ($\mu s$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Proposed Hierarchical (P9)** | 30,010.0 | **222.18** | **52.19** | **223.25** | 0.341 | 65.2 |
| Least-Loaded Node (LLN) | 30,160.0 | 222.81 | 56.68 | 240.87 | 0.315 | 44.4 |
| Round-Robin (RR) | 30,460.0 | 230.65 | 71.88 | 388.92 | 0.599 | 7.7 |
| Centralized Work Queue (WQ) | 30,530.0 | 345.52 | 245.91 | 973.15 | 0.165 | 8.1 |
| Random Dispatch | 30,220.0 | 229.85 | 78.73 | 354.61 | 0.606 | 8.2 |

## 🖼️ Generated Figures

1. **Figure 1 (Load Heatmap):** [`fig1_og_heatmap_proposed_vs_rr.png`](figures/fig1_og_heatmap_proposed_vs_rr.png)
2. **Figure 2 (Variance Trajectory):** [`fig2_og_variance_trajectory.png`](figures/fig2_og_variance_trajectory.png)
3. **Figure 3 (Wait Time CDF):** [`fig3_og_wait_time_cdf.png`](figures/fig3_og_wait_time_cdf.png)
4. **Figure 4 (4-Metric Bar Charts):** [`fig4_og_policy_metrics_barchart.png`](figures/fig4_og_policy_metrics_barchart.png)
5. **Figure 5 (Fairness/Makespan Tradeoff):** [`fig5_og_fairness_makespan_tradeoff.png`](figures/fig5_og_fairness_makespan_tradeoff.png)
