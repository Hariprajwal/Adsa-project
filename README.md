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

### 2. Quick Start: Launch the Live Video Player Dashboard
You can run the entire cluster streamer with a single double-click on Windows:

```cmd
run.bat
```
This automatically verifies dependencies, starts the FastAPI server on **http://127.0.0.1:8080**, and opens the dashboard in your default browser.

Or run manually with Python:
```bash
pip install -r requirements.txt
python -m uvicorn src.web.app:app --host 127.0.0.1 --port 8080 --reload
```

---

## 🎬 Live Dashboard Features (Phase 4)
- **Embedded HTML5 Video Player:** Real-time video streaming with HTTP 206 Partial Content byte-range delivery. As the player buffers video segments, each chunk is dynamically dispatched across cluster nodes.
- **Drag-and-Drop Video Ingestion:** Upload any MP4, WEBM, or MKV video. Uploaded files are chunked and ingested into the cluster storage.
- **Interactive SVG Topology Tree:** Real-time visual representation of `ClusterRoot` $\to$ 4 Racks $\to$ 16 Compute Nodes. Watch animated electric cyan routes trace $O(\log N)$ dispatch paths down the tree as chunks arrive!
- **Entropy Stability Classification:** Live Shannon entropy calculation $H(S)$ and stability state indicators (`STABLE`, `TRANSITIONAL`, `CRITICAL`).
- **Interactive Chaos Injection:** 
  - ⚡ **Inject Burst Spike:** Spikes rack utilization to trigger entropy transitions and verify that the tree steers traffic away from volatile racks.
  - 🔄 **Algorithm 3 Dynamic Rebalancing:** Dynamically restructures the hierarchical tree bottom-up when entropy shift exceeds threshold $\tau$.
  - 🚀 **Simulate Traffic:** Generates rapid video chunk traffic to observe real-time load distribution.
- **O(log N) vs O(N) Benchmark HUD:** Side-by-side latency comparison comparing P9 Hierarchical traversal against flat array scans in microseconds.

---

## 🧪 Verification & Automated Tests
Run the complete test suite covering the core DSA algorithms and the web streaming layer:
```bash
pytest tests/
```
All 7 unit and integration tests verify:
- Algorithm 1: Bottom-up tree construction
- Algorithm 2: $O(\log N)$ min-load dispatch with entropy-guided matching
- Algorithm 3: Dynamic periodic rebalancing
- HTTP 206 Partial Content video streaming & chunk dispatch
- WebSocket cluster telemetry broadcast

---

## 📜 Documentation & Reference
- See [`P9.md`](./P9.md) for full mathematical definitions, 15 IEEE references (2024–2026), and journal paper reporting criteria.
- See [`PROJECT_IMPLEMENTATION.md`](./PROJECT_IMPLEMENTATION.md) for phase-wise progress tracking.
