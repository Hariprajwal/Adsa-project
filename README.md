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
├── docs/                       # Technical reports, paper manuscripts, and PDF generators
│   ├── pdf/                    # Official compiled PDFs (Research Paper, Final Report, Dossier, etc.)
│   ├── scripts/                # Automated ReportLab PDF compilation scripts
│   ├── P9.docx                 # Original course project proposal document
│   ├── P9.md                   # Full Markdown specification (Math, Algorithms, References)
│   ├── PROJECT_IMPLEMENTATION.md # Detailed implementation plan and tracking
│   └── README.md               # Complete documentation catalog & reproduction guide
├── src/
│   ├── core/                   # Layer 1: Core DSA Engine (Hierarchical Tree, Balancer, Entropy)
│   ├── simulation/             # Layer 2: Trace replay & discrete-event cluster simulator
│   ├── benchmark/              # Layer 3: Paper tables & figure generator
│   └── web/                    # Layer 4: Live video player & interactive topology dashboard
├── tests/                      # Automated test suite (Phases 1-4, 100% pass rate)
├── data/                       # SWF traces, benchmark JSONs, and generated figure assets
├── run.bat                     # Windows 1-click launcher for the web dashboard
└── requirements.txt            # Python dependencies
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

## 📜 Documentation & Technical Reports
All documentation, paper manuscripts, and compilation pipelines are organized inside [`docs/`](./docs/README.md):
- **Full Documentation Index:** [`docs/README.md`](./docs/README.md)
- **Mathematical Specification & Foundations:** [`docs/P9.md`](./docs/P9.md)
- **Phase-wise Progress Tracking:** [`docs/PROJECT_IMPLEMENTATION.md`](./docs/PROJECT_IMPLEMENTATION.md)
- **Springer CCIS / LNCS Publication Manuscript:** [`docs/pdf/SPRINGER_CONFERENCE_PROCEEDINGS_REPORT.pdf`](./docs/pdf/SPRINGER_CONFERENCE_PROCEEDINGS_REPORT.pdf)
- **Comprehensive Faculty Audit Dossier:** [`docs/pdf/FACULTY_COMPREHENSIVE_AUDIT_DOSSIER.pdf`](./docs/pdf/FACULTY_COMPREHENSIVE_AUDIT_DOSSIER.pdf)
- **Final Project Report:** [`docs/pdf/FINAL_PROJECT_REPORT.pdf`](./docs/pdf/FINAL_PROJECT_REPORT.pdf)
- **Oral Defense & Presentation Guide:** [`docs/pdf/FACULTY_PRESENTATION_AND_JUSTIFICATION_GUIDE.pdf`](./docs/pdf/FACULTY_PRESENTATION_AND_JUSTIFICATION_GUIDE.pdf)
- **PDF Compilation Scripts:** [`docs/scripts/`](./docs/scripts/)
