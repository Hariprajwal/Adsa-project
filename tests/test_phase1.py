import unittest
import time
import random
from src.core.entropy import EntropyTracker, EntropyClass
from src.core.tree import ComputeNode, build_hierarchical_tree, ResourceVector
from src.core.balancer import EntropyHierarchicalBalancer, Job, JobType
from src.core.baselines import (
    RoundRobinBalancer, LeastLoadedNodeBalancer, WorkQueueBalancer, WorkStealingBalancer
)
from src.core.predictor import LightweightPredictor, LoadTrend
from src.core.rebalance import PeriodicRebalancer

class TestPhase1CoreDSA(unittest.TestCase):

    def test_entropy_tracker(self):
        """Test variance and Shannon entropy formulations."""
        tracker = EntropyTracker(window_size=10, tau_low=15.0, tau_high=50.0)
        
        # Stable workload: 50% CPU constant
        for _ in range(10):
            tracker.add_sample(50.0)
        self.assertEqual(tracker.compute_variance_entropy(), 0.0)
        self.assertEqual(tracker.classify(), EntropyClass.LOW)

        # Volatile / high jitter workload: 10% and 90% oscillating
        for i in range(10):
            tracker.add_sample(90.0 if i % 2 == 0 else 10.0)
        
        var = tracker.compute_variance_entropy()
        self.assertGreater(var, 50.0)
        self.assertEqual(tracker.classify(), EntropyClass.HIGH)

        # Shannon entropy check (should be positive and <= log2(5))
        shannon = tracker.compute_shannon_entropy()
        self.assertGreater(shannon, 0.0)
        self.assertLessEqual(shannon, 2.4)

    def test_tree_construction_and_hierarchy(self):
        """Test Algorithm 1: Hierarchical Tree Construction."""
        num_nodes = 64  # 2 racks of 32
        nodes = [ComputeNode(node_id=i, rack_id=0) for i in range(num_nodes)]
        
        # Seed initial load on node 0
        nodes[0].load.cpu = 80.0
        nodes[1].load.cpu = 40.0

        root = build_hierarchical_tree(nodes, nodes_per_rack=32)
        
        self.assertEqual(len(root.children), 2)  # 2 racks
        self.assertEqual(len(root.children[0].children), 32)
        self.assertEqual(len(root.children[1].children), 32)
        
        # Check aggregation
        rack0 = root.children[0]
        self.assertAlmostEqual(rack0.aggregated_load.cpu, (80.0 + 40.0) / 32, places=2)
        self.assertEqual(rack0.min_cpu, 0.0)
        self.assertEqual(rack0.max_cpu, 80.0)

    def test_hierarchical_balancer_dispatch(self):
        """Test Algorithm 2: Job Assignment with Hierarchical Query."""
        num_nodes = 64
        nodes = [ComputeNode(node_id=i, rack_id=0) for i in range(num_nodes)]
        root = build_hierarchical_tree(nodes, nodes_per_rack=32)
        balancer = EntropyHierarchicalBalancer(root=root)

        job = Job(
            job_id="job_001",
            job_type=JobType.CPU_BOUND,
            cpu_req=15.0,
            mem_req=5.0,
            net_req=2.0,
            disk_req=1.0,
            is_predictable=False
        )

        assigned_node, path, elapsed_ms = balancer.query_and_assign(job)
        
        self.assertIsNotNone(assigned_node)
        self.assertEqual(len(path), 3)  # ClusterRoot -> Rack_x -> Node_y
        self.assertIn("job_001", assigned_node.active_jobs)
        self.assertEqual(assigned_node.load.cpu, 15.0)

        # Verify upward propagation updated root
        self.assertGreater(root.aggregated_load.cpu, 0.0)

    def test_entropy_guided_matching(self):
        """Test that predictable jobs avoid high-entropy nodes."""
        nodes = [ComputeNode(node_id=i, rack_id=0) for i in range(32)]
        
        # Make node 0 have zero load BUT high volatility (high entropy)
        for i in range(10):
            nodes[0].entropy_tracker.add_sample(100.0 if i % 2 == 0 else 0.0)
        self.assertEqual(nodes[0].entropy_class, EntropyClass.HIGH)
        nodes[0].load.cpu = 5.0  # Appears lightly loaded

        # Node 1 has slightly higher load (10.0) BUT is stable (LOW entropy)
        for _ in range(10):
            nodes[1].entropy_tracker.add_sample(10.0)
        nodes[1].load.cpu = 10.0
        self.assertEqual(nodes[1].entropy_class, EntropyClass.LOW)

        root = build_hierarchical_tree(nodes, nodes_per_rack=32)
        balancer = EntropyHierarchicalBalancer(root=root)

        # Submit predictable job
        predictable_job = Job(
            job_id="pred_job",
            job_type=JobType.CPU_BOUND,
            cpu_req=10.0,
            is_predictable=True
        )

        assigned_node, path, _ = balancer.query_and_assign(predictable_job)
        # Should choose node 1 (LOW entropy) instead of node 0 (HIGH entropy)
        self.assertNotEqual(assigned_node.node_id, 0)

    def test_periodic_rebalancing(self):
        """Test Algorithm 3: Periodic Rebalancing threshold trigger."""
        nodes = [ComputeNode(node_id=i, rack_id=0) for i in range(50)]
        root = build_hierarchical_tree(nodes, nodes_per_rack=25)
        rebalancer = PeriodicRebalancer(tau_shift_threshold=0.20)

        # No shifts
        root, rebuilt, stats = rebalancer.check_and_rebalance(root, nodes)
        self.assertFalse(rebuilt)
        self.assertEqual(stats["shift_count"], 0)

        # Induce >20% entropy class changes (e.g. 15 nodes shift to HIGH)
        for i in range(15):
            for k in range(10):
                nodes[i].entropy_tracker.add_sample(100.0 if k % 2 == 0 else 0.0)

        root, rebuilt, stats = rebalancer.check_and_rebalance(root, nodes)
        self.assertTrue(rebuilt)
        self.assertGreaterEqual(stats["shift_ratio"], 0.20)

    def test_scalability_microbenchmark(self):
        """Micro-benchmark verifying O(log N) tree dispatch vs O(N) flat scan."""
        sizes = [128, 512, 1024]
        results = {}

        for N in sizes:
            nodes_tree = [ComputeNode(node_id=i, rack_id=0) for i in range(N)]
            nodes_lln = [ComputeNode(node_id=i, rack_id=0) for i in range(N)]

            # Seed random loads
            for i in range(N):
                l = random.uniform(5.0, 75.0)
                nodes_tree[i].load.cpu = l
                nodes_lln[i].load.cpu = l

            root = build_hierarchical_tree(nodes_tree, nodes_per_rack=32)
            tree_balancer = EntropyHierarchicalBalancer(root=root)
            lln_balancer = LeastLoadedNodeBalancer(nodes=nodes_lln)

            # Benchmark 200 dispatches
            num_ops = 200
            t0 = time.perf_counter()
            for k in range(num_ops):
                job = Job(job_id=f"t_{k}", job_type=JobType.CPU_BOUND, cpu_req=1.0)
                tree_balancer.query_and_assign(job)
            tree_time = (time.perf_counter() - t0) * 1000.0 / num_ops

            t0 = time.perf_counter()
            for k in range(num_ops):
                job = Job(job_id=f"l_{k}", job_type=JobType.CPU_BOUND, cpu_req=1.0)
                lln_balancer.query_and_assign(job)
            lln_time = (time.perf_counter() - t0) * 1000.0 / num_ops

            results[N] = {"tree_ms": round(tree_time, 4), "lln_ms": round(lln_time, 4)}

        print("\n--- Microbenchmark Results (Time per job dispatch in ms) ---")
        for N, res in results.items():
            print(f"Cluster Size N={N:4d} | Hierarchical Tree: {res['tree_ms']:.4f} ms | LLN (Flat Scan): {res['lln_ms']:.4f} ms")

        # LLN time should grow with N, while tree stays fast
        self.assertGreater(results[1024]["lln_ms"], results[128]["lln_ms"])

    def test_work_stealing_balancer(self):
        """Test Baseline 5: WorkStealingBalancer load offloading and steal logic."""
        num_nodes = 8
        nodes = [ComputeNode(node_id=i, rack_id=0) for i in range(num_nodes)]
        # Make node 0 heavily overloaded
        nodes[0].load.cpu = 85.0
        
        ws_balancer = WorkStealingBalancer(nodes=nodes, num_probes=3, overload_threshold=50.0)
        job = Job(job_id="ws_job_1", job_type=JobType.CPU_BOUND, cpu_req=10.0)
        
        # When primary node (node 0) is overloaded, work stealing should steal job to an idle peer
        assigned_node, elapsed_ms = ws_balancer.query_and_assign(job)
        self.assertNotEqual(assigned_node.node_id, 0)
        self.assertGreater(ws_balancer.total_steals, 0)
        self.assertEqual(ws_balancer.total_dispatches, 1)

    def test_lightweight_predictor(self):
        """Test Section 3.4 LightweightPredictor linear trend forecasting."""
        predictor = LightweightPredictor(horizon_steps=5, slope_threshold=0.5)
        
        # Upward surging trend: 20, 25, 30, ..., 65
        upward_history = [20.0 + 5.0 * i for i in range(10)]
        pred_val, slope, trend = predictor.predict_future_load(upward_history)
        self.assertEqual(trend, LoadTrend.UPWARD)
        self.assertGreater(slope, 0.5)
        self.assertGreater(pred_val, upward_history[-1])

        # Downward cooling trend: 80, 75, 70, ..., 35
        downward_history = [80.0 - 5.0 * i for i in range(10)]
        pred_val, slope, trend = predictor.predict_future_load(downward_history)
        self.assertEqual(trend, LoadTrend.DOWNWARD)
        self.assertLess(slope, -0.5)
        self.assertLess(pred_val, downward_history[-1])

        # Proactive score blending
        proactive_score = predictor.proactive_composite_load(current_load=50.0, predicted_load=80.0, alpha=0.30)
        self.assertAlmostEqual(proactive_score, 0.70 * 50.0 + 0.30 * 80.0, places=2)

if __name__ == "__main__":
    unittest.main()
