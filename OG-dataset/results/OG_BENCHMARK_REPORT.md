# Empirical Benchmark Evaluation on Real-World Supercomputing Workload

- **Trace Name:** `CEA Curie Supercomputer (Bullx DLC, 5040 Nodes)`
- **Evaluated Jobs:** 1,500 real completed tasks
- **Cluster Configuration:** 128 Nodes (Heterogeneous Silicon Speeds 0.85-1.15x)
- **Generated At:** 2026-10-22 07:56:52

## 🏆 Key Performance Highlights (Proposed Algorithm vs All 3 Baselines)

### 1. Load Variance Reduction (Lower Imbalance):
- **vs Round-Robin (RR):** **+26.6%** (`185.95` vs `253.24`)
- **vs Least-Loaded Node (LLN):** **+16.2%** (`185.95` vs `221.78`)
- **vs Centralized Work Queue (WQ):** **+74.2%** (`185.95` vs `720.27`)

### 2. Average Job Wait Time Reduction:
- **vs Round-Robin (RR):** **+27.0%** (`177.32s` vs `242.88s`)
- **vs Least-Loaded Node (LLN):** **+6.5%** (`177.32s` vs `189.56s`)
- **vs Centralized Work Queue (WQ):** **+63.9%** (`177.32s` vs `490.76s`)

### 3. 95th Percentile Tail Wait Latency Reduction:
- **vs Round-Robin (RR):** **+17.2%** (`437.69s` vs `528.84s`)
- **vs Least-Loaded Node (LLN):** **+9.0%** (`437.69s` vs `480.92s`)
- **vs Centralized Work Queue (WQ):** **+62.3%** (`437.69s` vs `1161.50s`)

### 4. Cluster Load Equity:
- **Jain's Fairness Index:** `1.000` across all nodes.

## 📊 Comprehensive Empirical Metrics Table

| Policy | Makespan (s) | Load Variance ($\sigma^2$) | Avg Wait Time (s) | 95th % Tail Wait (s) | Jain's Fairness | Dispatch Overhead ($\mu s$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Proposed Hierarchical (P9)** | 34,360.0 | **185.95** | **177.32** | **437.69** | 1.000 | 188.6 |
| Least-Loaded Node (LLN) | 34,260.0 | 221.78 | 189.56 | 480.92 | 1.000 | 101.3 |
| Round-Robin (RR) | 34,760.0 | 253.24 | 242.88 | 528.84 | 1.000 | 19.8 |
| Centralized Work Queue (WQ) | 35,310.0 | 720.27 | 490.76 | 1161.50 | 1.000 | 18.4 |
| Random Dispatch | 34,380.0 | 368.30 | 294.38 | 934.26 | 1.000 | 18.5 |

## 🖼️ Generated Figures

1. **Figure 1 (Load Heatmap):** [`fig1_og_heatmap_proposed_vs_rr.png`](figures/fig1_og_heatmap_proposed_vs_rr.png)
2. **Figure 2 (Variance Trajectory):** [`fig2_og_variance_trajectory.png`](figures/fig2_og_variance_trajectory.png)
3. **Figure 3 (Wait Time CDF):** [`fig3_og_wait_time_cdf.png`](figures/fig3_og_wait_time_cdf.png)
4. **Figure 4 (4-Metric Bar Charts):** [`fig4_og_policy_metrics_barchart.png`](figures/fig4_og_policy_metrics_barchart.png)
5. **Figure 5 (Fairness/Makespan Tradeoff):** [`fig5_og_fairness_makespan_tradeoff.png`](figures/fig5_og_fairness_makespan_tradeoff.png)
