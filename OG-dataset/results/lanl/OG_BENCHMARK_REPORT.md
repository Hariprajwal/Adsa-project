# Empirical Benchmark Evaluation on Real-World Supercomputing Workload

- **Trace Name:** `Los Alamos National Lab (Thinking Machines CM-5, 1024 Nodes)`
- **Evaluated Jobs:** 1,500 real completed tasks
- **Cluster Configuration:** 128 Nodes (Heterogeneous Silicon Speeds 0.85-1.15x)
- **Generated At:** 2026-10-22 08:13:38

## 🏆 Key Performance Highlights (Proposed Algorithm vs All 3 Baselines)

### 1. Load Variance Reduction (Lower Imbalance):
- **vs Round-Robin (RR):** **-18.7%** (`327.99` vs `276.36`)
- **vs Least-Loaded Node (LLN):** **+3.1%** (`327.99` vs `338.48`)
- **vs Centralized Work Queue (WQ):** **+11.6%** (`327.99` vs `371.03`)

### 2. Average Job Wait Time Reduction:
- **vs Round-Robin (RR):** **-172.1%** (`84.16s` vs `30.93s`)
- **vs Least-Loaded Node (LLN):** **+15.0%** (`84.16s` vs `98.99s`)
- **vs Centralized Work Queue (WQ):** **+71.2%** (`84.16s` vs `291.76s`)

### 3. 95th Percentile Tail Wait Latency Reduction:
- **vs Round-Robin (RR):** **-183.0%** (`256.44s` vs `90.61s`)
- **vs Least-Loaded Node (LLN):** **+7.6%** (`256.44s` vs `277.62s`)
- **vs Centralized Work Queue (WQ):** **+63.9%** (`256.44s` vs `709.67s`)

### 4. Cluster Load Equity:
- **Jain's Fairness Index:** `1.000` across all nodes.

## 📊 Comprehensive Empirical Metrics Table

| Policy | Makespan (s) | Load Variance ($\sigma^2$) | Avg Wait Time (s) | 95th % Tail Wait (s) | Jain's Fairness | Dispatch Overhead ($\mu s$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Proposed Hierarchical (P9)** | 23,820.0 | **327.99** | **84.16** | **256.44** | 1.000 | 174.2 |
| Least-Loaded Node (LLN) | 24,010.0 | 338.48 | 98.99 | 277.62 | 1.000 | 110.1 |
| Round-Robin (RR) | 23,600.0 | 276.36 | 30.93 | 90.61 | 1.000 | 21.8 |
| Centralized Work Queue (WQ) | 25,120.0 | 371.03 | 291.76 | 709.67 | 1.000 | 23.7 |
| Random Dispatch | 23,630.0 | 271.15 | 38.70 | 127.33 | 1.000 | 23.1 |

## 🖼️ Generated Figures

1. **Figure 1 (Load Heatmap):** [`fig1_og_heatmap_proposed_vs_rr.png`](figures/fig1_og_heatmap_proposed_vs_rr.png)
2. **Figure 2 (Variance Trajectory):** [`fig2_og_variance_trajectory.png`](figures/fig2_og_variance_trajectory.png)
3. **Figure 3 (Wait Time CDF):** [`fig3_og_wait_time_cdf.png`](figures/fig3_og_wait_time_cdf.png)
4. **Figure 4 (4-Metric Bar Charts):** [`fig4_og_policy_metrics_barchart.png`](figures/fig4_og_policy_metrics_barchart.png)
5. **Figure 5 (Fairness/Makespan Tradeoff):** [`fig5_og_fairness_makespan_tradeoff.png`](figures/fig5_og_fairness_makespan_tradeoff.png)
