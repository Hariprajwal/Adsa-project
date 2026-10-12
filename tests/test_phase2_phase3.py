"""
Unit & Integration Test Suite for Phase 2 (Simulation) & Phase 3 (Benchmarking & Figures)
Verifies:
1. SWF Parser handles 18-column Standard Workload Format and extracts Table 1 metadata.
2. WorkloadMapper converts SWF records to multi-dimensional Jobs with appropriate JobType.
3. DiscreteEventSimulator executes simulations for both Proposed and Baseline policies.
4. Matplotlib publication figures (Figures 1-5) are correctly rendered.
5. Publication tables (Tables 1-4) are correctly exported.
"""

import os
import unittest
from src.simulation.swf_parser import SWFParser, SWFJobRecord
from src.simulation.workload_mapper import WorkloadMapper
from src.simulation.simulator import DiscreteEventSimulator, SimulationResult
from src.benchmark.plot_figures import generate_all_figures
from src.benchmark.generate_tables import generate_paper_tables

class TestPhase2Phase3(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.trace_path = r"d:\downloads\ADSA Proj\data\traces\LANL-HPC.swf"
        cls.output_dir = r"d:\downloads\ADSA Proj\data\figures"
        cls.tables_md = r"d:\downloads\ADSA Proj\data\paper_tables.md"
        cls.benchmark_json = r"d:\downloads\ADSA Proj\data\benchmark_results.json"

    def test_swf_parser(self):
        """Test SWF parser correctly loads 18-column records and metadata."""
        self.assertTrue(os.path.exists(self.trace_path), f"Trace not found at {self.trace_path}")
        parser = SWFParser(self.trace_path)
        records = parser.parse()
        
        self.assertGreater(len(records), 0)
        first = records[0]
        self.assertIsInstance(first, SWFJobRecord)
        self.assertGreater(first.run_time, 0)
        self.assertGreater(first.alloc_procs, 0)
        
        stats = parser.get_statistics()
        self.assertEqual(stats["node_count"], 1024)
        self.assertGreater(stats["mean_runtime_s"], 0)
        self.assertGreater(stats["total_jobs"], 0)

    def test_workload_mapper(self):
        """Test WorkloadMapper correctly creates multi-dimensional Jobs."""
        parser = SWFParser(self.trace_path)
        records = parser.parse()[:20]
        
        mapper = WorkloadMapper(time_scale_factor=0.05)
        jobs = mapper.map_records(records)
        
        self.assertEqual(len(jobs), 20)
        first = jobs[0]
        self.assertGreater(first.cpu_req, 0.0)
        self.assertLessEqual(first.cpu_req, 100.0)
        self.assertGreater(first.duration, 0.0)
        self.assertIn(first.job_type.value, ["CPU_BOUND", "MEMORY_BOUND", "IO_BOUND", "BALANCED"])

    def test_simulator_execution(self):
        """Test DiscreteEventSimulator runs across both hierarchical and baseline policies."""
        parser = SWFParser(self.trace_path)
        records = parser.parse()[:30]
        mapper = WorkloadMapper(time_scale_factor=0.01)
        jobs = mapper.map_records(records)
        
        sim = DiscreteEventSimulator(num_nodes=32, nodes_per_rack=16, sampling_interval=5.0)
        
        res_prop = sim.run(jobs, policy="hierarchical")
        self.assertIsInstance(res_prop, SimulationResult)
        self.assertGreater(res_prop.makespan_seconds, 0)
        self.assertGreaterEqual(res_prop.jains_fairness_index, 0.0)
        self.assertLessEqual(res_prop.jains_fairness_index, 1.0)
        
        res_rr = sim.run(jobs, policy="round_robin")
        self.assertIsInstance(res_rr, SimulationResult)
        self.assertGreater(res_rr.makespan_seconds, 0)

        res_ws = sim.run(jobs, policy="work_stealing")
        self.assertIsInstance(res_ws, SimulationResult)
        self.assertGreater(res_ws.makespan_seconds, 0)

    def test_matplotlib_figures_exist(self):
        """Test that all 5 Matplotlib publication figures are generated and non-empty."""
        figs = generate_all_figures(self.benchmark_json, self.output_dir)
        self.assertEqual(len(figs), 5)
        
        for fig_key, path in figs.items():
            self.assertTrue(os.path.exists(path), f"Figure {fig_key} missing at {path}")
            self.assertGreater(os.path.getsize(path), 10000, f"Figure {fig_key} too small: {path}")

    def test_paper_tables_exported(self):
        """Test that Markdown publication tables 1-4 are properly generated."""
        content = generate_paper_tables(self.benchmark_json, self.tables_md)
        self.assertIn("Table 1: Workload Trace Dataset Statistics", content)
        self.assertIn("Table 2: Load Imbalance & Fairness Comparison", content)
        self.assertIn("Table 3: Job Performance & Tail Latency Metrics", content)
        self.assertIn("Table 4: Scheduling Overhead & Scalability", content)

if __name__ == "__main__":
    unittest.main()
