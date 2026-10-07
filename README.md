# Entropy-Guided Hierarchical Load Balancing for Heterogeneous HPC Workloads

**Course:** Advanced Data Structures & Algorithms (ADSA) / High-Performance Computing (HPC)  
**Author:** Kr Hariprajwal (`Krhariprajwal.mitblr2026@learner.manipal.edu`)  
**Supervision:** Dr. Megha P Arakeri [MAHE-MITBLR]  
**Repository:** [https://github.com/Hariprajwal/Adsa-project.git](https://github.com/Hariprajwal/Adsa-project.git)

---

## 📌 Project Overview
This repository contains the complete implementation and empirical evaluation framework for an **Entropy-Guided Hierarchical Load Balancing Architecture** designed for heterogeneous High-Performance Computing (HPC) clusters and distributed video streaming/transcoding workloads.

### Key Algorithmic Innovations
1. **Multi-Level Aggregation Tree ($O(\log N)$ Dispatch):** Replaces traditional $O(N)$ flat scan searches with a coarse-to-fine hierarchical tree structure (`ClusterRoot` $\to$ `RackNode` $\to$ `ComputeNode`).
2. **Multi-Dimensional Resource Vectors:** Balances heterogeneous demands simultaneously (CPU %, Memory %, Network I/O MB/s, Disk I/O MB/s) with dynamic weighting based on job class (CPU-bound transcoding, memory-bound caching, or I/O-bound streaming).
3. **Entropy-Guided Stability Classification:** Tracks sliding-window variance ($H_{\text{var}}$) and Shannon entropy ($H_{\text{Shannon}}$) to distinguish predictable compute nodes from volatile/jittery nodes.
4. **Dynamic Rebalancing (Algorithm 3):** Reconstructs the hierarchy dynamically bottom-up when $>20\%$ of nodes transition entropy states.

---

## 🏗️ Architecture & Directory Structure

```text
ADSA Proj/
├── P9.docx                     # Original project proposal document
├── P9.md                       # Full Markdown specification (Math, Algorithms, References)
├── PROJECT_IMPLEMENTATION.md   # Detailed implementation plan and tracking
├── src/
│   ├── core/                   # Layer 1: Core DSA Engine
│   │   ├── entropy.py          # Variance & Shannon entropy calculations
│   │   ├── tree.py             # Hierarchical tree & multi-dimensional metrics
│   │   ├── balancer.py         # Algorithm 2 (O(log N) Min-load query)
│   │   ├── baselines.py        # Round-Robin, LLN (O(N)), Work Queue, Random
│   │   └── rebalance.py        # Algorithm 3 (Periodic dynamic rebalancer)
│   ├── simulation/             # Layer 2: Trace replay & simulator (In progress)
│   ├── benchmark/              # Layer 3: Paper tables & figure generator (In progress)
│   └── web/                    # Layer 4: Live video player & visualizer (In progress)
└── tests/
    └── test_phase1.py          # Micro-benchmarks & verification test suite
```

---

## 🚀 Getting Started

### 1. Requirements
- Python 3.10+

### 2. Run Algorithmic Tests & Microbenchmarks
```bash
python -m unittest discover -s tests -p "test_*.py"
```

### Empirical Results ($O(\log N)$ Scaling Advantage)
```text
Cluster Size N= 128 | Hierarchical Tree: 0.1250 ms | LLN (Flat Scan): 0.1393 ms
Cluster Size N= 512 | Hierarchical Tree: 0.1295 ms | LLN (Flat Scan): 0.2873 ms
Cluster Size N=1024 | Hierarchical Tree: 0.1236 ms | LLN (Flat Scan): 0.6010 ms (~4.9x faster)
```

---

## 📜 Documentation & Reference
- See [`P9.md`](./P9.md) for full mathematical definitions, 15 IEEE references (2024–2026), and journal paper reporting criteria.
- See [`PROJECT_IMPLEMENTATION.md`](./PROJECT_IMPLEMENTATION.md) for phase-wise progress tracking.
