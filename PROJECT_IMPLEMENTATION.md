# Project Implementation Blueprint: Entropy-Guided Hierarchical Load Balancing (P9)

**Project Code:** P9  
**Subject:** Advanced Data Structures & Algorithms (ADSA) / High-Performance Computing (HPC)  
**Author / Contact:** `Krhariprajwal.mitblr2026@learner.manipal.edu`  
**Supervision:** Dr. Megha P Arakeri [MAHE-MITBLR]  
**Documentation Reference:** [P9.md](file:///d:/downloads/ADSA%20Proj/P9.md)

---

## 1. Project Overview & Progress Tracker

This project implements an **Entropy-Guided Hierarchical Load Balancing Framework** for heterogeneous HPC and video streaming cluster workloads. The project combines rigorous algorithmic foundations with empirical HPC trace evaluation and an interactive working video player demo.

### Implementation Status Matrix

| Phase | Milestone | Scope | Status |
| :---: | :--- | :--- | :---: |
| **Phase 1** | **Core DSA Engine** | Hierarchical Tree, Entropy Module, Algorithm 1, 2, 3, Baselines (RR, LLN, Work Queue) | 🟢 **Completed & Verified** |
| **Phase 2** | **Dataset & Simulation** | Parallel Workloads Archive parser (`.swf`), Workload Mapper, Discrete-Event Simulator | 🟡 **Next Up** |
| **Phase 3** | **Benchmarking & Paper Results** | Automated generation of Tables 1–4, publication figures (Heatmap, Makespan, CDF) | ⚪ Pending |
| **Phase 4** | **Interactive Web App & Video Player** | FastAPI backend, WebSocket cluster visualizer, working HTML5 chunked video player | ⚪ Pending |

---

## 2. System Architecture

```text
+---------------------------------------------------------------------------------------+
|                                LAYER 4: WEB DASHBOARD                                 |
|  [ Working Video Player ] <---> [ Real-Time Cluster Visualizer (SVG/Canvas) ]         |
|  (HLS / Segment streaming)      (Color-coded by Entropy: Low/Med/High)                |
+---------------------------------------------------------------------------------------+
                                           | WebSocket / REST API
+---------------------------------------------------------------------------------------+
|                           LAYER 3: DISPATCH & REPLAY SERVER                           |
|  - FastAPI Gateway & Dispatch Router                                                  |
|  - Real-time Trace Replay Controller & Workload Generator                             |
+---------------------------------------------------------------------------------------+
                                           |
+---------------------------------------------------------------------------------------+
|                       LAYER 1: CORE DATA STRUCTURES & ALGORITHMS                      |
|                                                                                       |
|    +-----------------------+     +------------------------+                           |
|    |  Hierarchical Tree    |     |    Entropy Engine      |                           |
|    |  (Cluster->Rack->Node)|<--->|  (H_var, Shannon,      |                           |
|    |  O(log N) Query       |     |   tau_low, tau_high)   |                           |
|    +-----------------------+     +------------------------+                           |
|                |                              |                                       |
|    +-----------------------+     +------------------------+                           |
|    | Algorithm 2: Min-Load |     | Algorithm 3: Periodic  |                           |
|    | Composite Dispatcher  |     | Rebalance & Restruct   |                           |
|    +-----------------------+     +------------------------+                           |
|                |                                                                      |
|    +------------------------------------------------------+                           |
|    | Baselines: Round-Robin (O(1)), Least-Loaded Node     |                           |
|    | (O(N)), Centralized Work Queue, Random               |                           |
|    +------------------------------------------------------+                           |
+---------------------------------------------------------------------------------------+
                                           ^
                                           | Workload Ingestion
+---------------------------------------------------------------------------------------+
|                      LAYER 2: DATASET INGESTION & SIMULATION ENGINE                   |
|  - Standard Workload Format (.swf) Parser (CEA Curie / LLNL Thunder / LANL)           |
|  - Multi-Dimensional Resource Mapper (Transcode / Buffer / Stream Delivery)           |
|  - Discrete-Event Simulator (Time-stepped event queue)                                |
+---------------------------------------------------------------------------------------+
```

---

## 3. Mathematical & Algorithmic Formulations

### 3.1. Multi-Dimensional Composite Load Score
For any candidate node $c_i$:
$$L(c_i) = w_{\text{CPU}} \cdot \text{CPU}_i + w_{\text{mem}} \cdot \text{Mem}_i + w_{\text{net}} \cdot \text{Net}_i + w_{\text{disk}} \cdot \text{Disk}_i$$
where weights $\sum w = 1.0$ adjust dynamically based on job class:
- **CPU-bound (e.g. Transcoding):** $w_{\text{CPU}} = 0.7, w_{\text{mem}} = 0.1, w_{\text{net}} = 0.1, w_{\text{disk}} = 0.1$
- **Memory-bound (e.g. Caching):** $w_{\text{mem}} = 0.7, w_{\text{CPU}} = 0.1, w_{\text{net}} = 0.1, w_{\text{disk}} = 0.1$
- **I/O-bound (e.g. Streaming):** $w_{\text{net}} = 0.5, w_{\text{disk}} = 0.3, w_{\text{CPU}} = 0.1, w_{\text{mem}} = 0.1$

### 3.2. Entropy Formulations
- **Variance-Based Entropy:**
  $$H_{\text{var}}(c_i) = \frac{1}{W} \sum_{t=1}^{W} (\text{CPU}_i(t) - \overline{\text{CPU}_i})^2$$
  over sliding window of size $W = 10$.
- **Shannon Entropy:**
  $$H_{\text{Shannon}}(c_i) = -\sum_{k=1}^{B} p_k \log_2(p_k)$$
  over $B=5$ discrete CPU utilization intervals ($[0,20), [20,40), [40,60), [60,80), [80,100]$).
- **Classification:**
  - Low Entropy: $H(c_i) < \tau_{\text{low}}$ (Optimal for predictable jobs)
  - Medium Entropy: $\tau_{\text{low}} \le H(c_i) \le \tau_{\text{high}}$
  - High Entropy: $H(c_i) > \tau_{\text{high}}$ (Volatile / bursty)

---

## 4. Directory & File Organization

```text
ADSA Proj/
├── P9.docx                              # Original Word specification
├── P9.md                                # Full converted specification
├── PROJECT_IMPLEMENTATION.md            # This live implementation tracker
├── data/                                # Datasets & media
│   ├── traces/                          # .swf trace files
│   └── videos/                          # Video segments for demo player
├── src/
│   ├── core/                            # Phase 1: Core DSA Engine
│   │   ├── __init__.py
│   │   ├── entropy.py                   # Variance and Shannon entropy
│   │   ├── tree.py                      # Hierarchical tree & node aggregates
│   │   ├── balancer.py                  # Proposed Algorithm 2 O(log N)
│   │   ├── baselines.py                 # RR, LLN (O(N)), Work Queue
│   │   └── rebalance.py                 # Algorithm 3 dynamic restructuring
│   ├── simulation/                      # Phase 2: Trace & simulation
│   │   ├── __init__.py
│   │   ├── swf_parser.py                # SWF trace reader
│   │   ├── workload_mapper.py           # Multi-dimensional job mapper
│   │   └── simulator.py                 # Discrete event simulation engine
│   ├── benchmark/                       # Phase 3: Paper generator
│   │   ├── run_benchmarks.py            # Executes full benchmark suite
│   │   ├── generate_tables.py           # Exports Tables 1, 2, 3, 4
│   │   └── plot_figures.py              # Exports Figures 1, 2, 3, 4, 5
│   └── web/                             # Phase 4: Video player & visualizer
│       ├── app.py                       # FastAPI & WebSocket server
│       └── static/                      # HTML5 Player & SVG Cluster Canvas
└── tests/
    └── test_phase1.py                   # Algorithmic unit & performance tests
```
