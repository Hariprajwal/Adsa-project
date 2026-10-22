# Empirical Benchmark Evaluation on Real-World Supercomputing Workload

- **Trace Name:** `Lawrence Livermore National Lab (Thunder Cluster, 4008 Nodes)`
- **Evaluated Jobs:** 1,500 real completed tasks
- **Cluster Configuration:** 128 Nodes (Heterogeneous Silicon Speeds 0.85-1.15x)
- **Generated At:** 2026-10-22 08:14:24

## 🏆 Key Performance Highlights (Proposed Algorithm vs All 3 Baselines)

### 1. Load Variance Reduction (Lower Imbalance):
- **vs Round-Robin (RR):** **+4.7%** (`226.71` vs `237.86`)
- **vs Least-Loaded Node (LLN):** **+2.6%** (`226.71` vs `232.69`)
- **vs Centralized Work Queue (WQ):** **+33.6%** (`226.71` vs `341.35`)

### 2. Average Job Wait Time Reduction:
- **vs Round-Robin (RR):** **+31.1%** (`64.52s` vs `93.60s`)
- **vs Least-Loaded Node (LLN):** **+4.6%** (`64.52s` vs `67.61s`)
- **vs Centralized Work Queue (WQ):** **+78.0%** (`64.52s` vs `293.39s`)

### 3. 95th Percentile Tail Wait Latency Reduction:
- **vs Round-Robin (RR):** **+48.5%** (`254.28s` vs `493.39s`)
- **vs Least-Loaded Node (LLN):** **+15.3%** (`254.28s` vs `300.37s`)
- **vs Centralized Work Queue (WQ):** **+80.3%** (`254.28s` vs `1291.74s`)

### 4. Cluster Load Equity:
- **Jain's Fairness Index:** `1.000` across all nodes.

## 📊 Comprehensive Empirical Metrics Table

| Policy | Makespan (s) | Load Variance ($\sigma^2$) | Avg Wait Time (s) | 95th % Tail Wait (s) | Jain's Fairness | Dispatch Overhead ($\mu s$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Proposed Hierarchical (P9)** | 30,120.0 | **226.71** | **64.52** | **254.28** | 1.000 | 173.0 |
| Least-Loaded Node (LLN) | 29,740.0 | 232.69 | 67.61 | 300.37 | 1.000 | 122.6 |
| Round-Robin (RR) | 30,500.0 | 237.86 | 93.60 | 493.39 | 1.000 | 23.3 |
| Centralized Work Queue (WQ) | 31,770.0 | 341.35 | 293.39 | 1291.74 | 1.000 | 27.4 |
| Random Dispatch | 30,140.0 | 253.66 | 110.56 | 504.91 | 1.000 | 28.5 |

## 🖼️ Generated Figures

1. **Figure 1 (Load Heatmap):** [`fig1_og_heatmap_proposed_vs_rr.png`](figures/fig1_og_heatmap_proposed_vs_rr.png)
2. **Figure 2 (Variance Trajectory):** [`fig2_og_variance_trajectory.png`](figures/fig2_og_variance_trajectory.png)
3. **Figure 3 (Wait Time CDF):** [`fig3_og_wait_time_cdf.png`](figures/fig3_og_wait_time_cdf.png)
4. **Figure 4 (4-Metric Bar Charts):** [`fig4_og_policy_metrics_barchart.png`](figures/fig4_og_policy_metrics_barchart.png)
5. **Figure 5 (Fairness/Makespan Tradeoff):** [`fig5_og_fairness_makespan_tradeoff.png`](figures/fig5_og_fairness_makespan_tradeoff.png)
