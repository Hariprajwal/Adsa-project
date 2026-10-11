import time
import math
import asyncio
import random
from typing import Dict, List, Optional, Any

from src.core.tree import ComputeNode, RackNode, ClusterRoot, build_hierarchical_tree, ResourceVector
from src.core.entropy import EntropyTracker, EntropyClass
from src.core.balancer import EntropyHierarchicalBalancer, Job, JobType, WEIGHT_PROFILES
from src.core.baselines import LeastLoadedNodeBalancer, RoundRobinBalancer
from src.core.rebalance import PeriodicRebalancer

class ClusterManager:
    """
    Manages the live cluster state, video chunk dispatching, real-time telemetry,
    and side-by-side algorithmic comparisons for the Phase 4 web dashboard.
    """
    def __init__(self, num_nodes: int = 16, nodes_per_rack: int = 4):
        self.num_nodes = num_nodes
        self.nodes_per_rack = nodes_per_rack
        
        # 1. Initialize Compute Nodes
        self.nodes: List[ComputeNode] = []
        for i in range(num_nodes):
            rack_id = i // nodes_per_rack
            node = ComputeNode(node_id=i, rack_id=rack_id, cpu_cores=16, mem_gb=64.0)
            # Baseline jitter
            base_cpu = random.uniform(2.0, 8.0)
            base_mem = random.uniform(5.0, 12.0)
            base_net = random.uniform(1.0, 5.0)
            node.load = ResourceVector(cpu=base_cpu, mem=base_mem, net=base_net, disk=2.0)
            for _ in range(5):
                node.entropy_tracker.add_sample(base_cpu + random.uniform(-1.0, 1.0))
            self.nodes.append(node)
            
        # 2. Build Hierarchical Tree (Algorithm 1)
        self.root: ClusterRoot = build_hierarchical_tree(self.nodes, nodes_per_rack=nodes_per_rack)
        
        # 3. Initialize Balancers & Rebalancer
        self.tree_balancer = EntropyHierarchicalBalancer(self.root)
        self.lln_balancer = LeastLoadedNodeBalancer(self.nodes)
        self.rr_balancer = RoundRobinBalancer(self.nodes)
        self.rebalancer = PeriodicRebalancer(tau_shift_threshold=0.20)
        
        # 4. Telemetry and Dispatch History
        self.dispatch_history: List[Dict[str, Any]] = []
        self.latency_stats = {
            "hierarchical_tree": {"samples": [], "avg_us": 0.0},
            "flat_scan_lln": {"samples": [], "avg_us": 0.0}
        }
        self.chunk_counter = 0
        self.last_update_time = time.time()
        self.active_algorithm = "hierarchical"

    def tick_decay(self):
        """
        Simulates completion of video streaming jobs and natural load decay.
        Invoked periodically by the server loop.
        """
        now = time.time()
        dt = max(0.1, now - self.last_update_time)
        self.last_update_time = now
        
        decay_factor = max(0.5, 1.0 - (0.15 * dt))

        for node in self.nodes:
            # Check active jobs and expire old ones
            expired_job_ids = []
            for jid, job_info in list(node.active_jobs.items()):
                rem = job_info.get("remaining_duration", 0) - dt
                job_info["remaining_duration"] = rem
                if rem <= 0:
                    expired_job_ids.append(jid)
            
            for jid in expired_job_ids:
                node.release_job(jid)
            
            # Additional load decay towards baseline
            if len(node.active_jobs) == 0:
                node.load.cpu = max(2.0, node.load.cpu * decay_factor)
                node.load.mem = max(5.0, node.load.mem * decay_factor)
                node.load.net = max(1.0, node.load.net * decay_factor)
                node.load.disk = max(1.0, node.load.disk * decay_factor)
                
            # Sample current CPU for entropy tracking
            node.entropy_tracker.add_sample(node.load.cpu)
            
        # Re-aggregate upward
        self.root.aggregate()

    def dispatch_chunk(self, video_name: str, chunk_index: int, byte_size: int = 250000) -> Dict[str, Any]:
        """
        Dispatches a video stream chunk as a Job to the cluster.
        Simultaneously computes baseline latencies for side-by-side comparison.
        """
        self.chunk_counter += 1
        job_id = f"chunk_{self.chunk_counter}_{chunk_index}"
        
        # Stream job resource footprint based on video chunk size
        cpu_load = random.uniform(3.0, 7.0)
        mem_load = random.uniform(2.0, 5.0)
        net_load = random.uniform(8.0, 15.0)
        duration = random.uniform(2.5, 4.5)
        
        job = Job(
            job_id=job_id,
            job_type=JobType.IO_BOUND,
            cpu_req=cpu_load,
            mem_req=mem_load,
            net_req=net_load,
            disk_req=4.0,
            duration=duration,
            is_predictable=True,
            submit_time=time.time()
        )
        
        # 1. Dispatch using Entropy Hierarchical Balancer (Algorithm 2)
        start_tree = time.perf_counter_ns()
        assigned_node, path, _ = self.tree_balancer.query_and_assign(job)
        end_tree = time.perf_counter_ns()
        tree_time_us = (end_tree - start_tree) / 1000.0

        # Store job remaining duration for decay
        if job_id in assigned_node.active_jobs:
            assigned_node.active_jobs[job_id]["remaining_duration"] = duration

        # 2. Side-by-side benchmark with Flat LLN (without mutating state)
        weights = WEIGHT_PROFILES[JobType.IO_BOUND]
        start_lln = time.perf_counter_ns()
        min_load = float('inf')
        for n in self.nodes:
            score = n.get_composite_load(weights)
            if score < min_load:
                min_load = score
        end_lln = time.perf_counter_ns()
        lln_time_us = (end_lln - start_lln) / 1000.0

        # Update latency statistics
        self._record_latency("hierarchical_tree", tree_time_us)
        self._record_latency("flat_scan_lln", lln_time_us)

        # Calculate cluster entropy
        cluster_entropy, norm_entropy, entropy_class = self.get_cluster_entropy()

        event = {
            "chunk_index": chunk_index,
            "chunk_id": job_id,
            "video_name": video_name,
            "byte_size": byte_size,
            "assigned_node_id": assigned_node.node_id,
            "assigned_rack_id": assigned_node.rack_id,
            "dispatch_path": path,
            "tree_time_us": round(tree_time_us, 2),
            "lln_time_us": round(lln_time_us, 2),
            "speedup_ratio": round(lln_time_us / max(0.1, tree_time_us), 2),
            "node_cpu_after": round(assigned_node.load.cpu, 1),
            "node_entropy_class": assigned_node.entropy_class.value,
            "cluster_entropy": round(cluster_entropy, 3),
            "cluster_norm_entropy": round(norm_entropy, 3),
            "cluster_class": entropy_class.value,
            "timestamp": time.time()
        }

        self.dispatch_history.append(event)
        if len(self.dispatch_history) > 50:
            self.dispatch_history.pop(0)

        return event

    def _record_latency(self, model_key: str, us: float):
        samples = self.latency_stats[model_key]["samples"]
        samples.append(us)
        if len(samples) > 100:
            samples.pop(0)
        self.latency_stats[model_key]["avg_us"] = round(sum(samples) / len(samples), 2)

    def inject_burst(self, rack_id: Optional[int] = None, magnitude: float = 65.0) -> Dict[str, Any]:
        """
        Injects a sudden high-load spike on a rack or specific nodes to trigger
        transitional/critical entropy states and test dynamic load steering.
        """
        target_rack = rack_id if rack_id is not None else random.randint(0, len(self.root.children) - 1)
        affected_nodes = []
        
        for node in self.nodes:
            if node.rack_id == target_rack:
                spike_cpu = min(98.0, node.load.cpu + magnitude + random.uniform(-5.0, 5.0))
                spike_mem = min(95.0, node.load.mem + magnitude * 0.7)
                node.load.cpu = spike_cpu
                node.load.mem = spike_mem
                for _ in range(10):
                    node.entropy_tracker.add_sample(spike_cpu + random.uniform(-15.0, 15.0))
                affected_nodes.append(node.node_id)

        self.root.aggregate()
        c_entropy, norm_entropy, e_class = self.get_cluster_entropy()
        
        return {
            "target_rack": target_rack,
            "affected_nodes": affected_nodes,
            "cluster_entropy": round(c_entropy, 3),
            "cluster_norm_entropy": round(norm_entropy, 3),
            "entropy_class": e_class.value
        }

    def trigger_rebalance(self) -> Dict[str, Any]:
        """
        Forces execution of Algorithm 3 (Periodic Rebalancing).
        """
        self.root, was_rebuilt, stats = self.rebalancer.check_and_rebalance(
            self.root, self.nodes, nodes_per_rack=self.nodes_per_rack
        )
        self.tree_balancer.root = self.root
        return {
            "was_rebuilt": was_rebuilt,
            "rebuild_count": self.rebalancer.rebuild_count,
            "in_place_refresh_count": self.rebalancer.in_place_refresh_count,
            "stats": stats
        }

    def get_cluster_entropy(self):
        """
        Computes overall Shannon entropy across compute nodes.
        """
        tracker = EntropyTracker()
        for node in self.nodes:
            tracker.add_sample(node.load.cpu)
        shannon = tracker.compute_shannon_entropy()
        # Max entropy for 5 bins is log2(5) ~ 2.3219
        max_shannon = math.log2(5)
        norm = min(1.0, shannon / max_shannon) if max_shannon > 0 else 0.0
        e_class = tracker.classify()
        return shannon, norm, e_class

    def get_cluster_state(self) -> Dict[str, Any]:
        """
        Serializes full cluster topology and metrics for WebSocket broadcast.
        """
        shannon, norm_e, e_class = self.get_cluster_entropy()

        racks_data = []
        for rack in self.root.children:
            racks_data.append({
                "rack_id": rack.rack_id,
                "node_count": len(rack.children),
                "avg_cpu": round(rack.aggregated_load.cpu, 1),
                "avg_mem": round(rack.aggregated_load.mem, 1),
                "avg_net": round(rack.aggregated_load.net, 1),
                "avg_disk": round(rack.aggregated_load.disk, 1),
            })

        nodes_data = []
        for n in self.nodes:
            variance = round(n.entropy_tracker.compute_variance_entropy(), 2)
            nodes_data.append({
                "node_id": n.node_id,
                "rack_id": n.rack_id,
                "cpu": round(n.load.cpu, 1),
                "mem": round(n.load.mem, 1),
                "net": round(n.load.net, 1),
                "disk": round(n.load.disk, 1),
                "variance": variance,
                "entropy_class": n.entropy_class.value,
                "active_jobs_count": len(n.active_jobs),
                "recent_history": list(n.entropy_tracker.history)[-8:] if n.entropy_tracker.history else []
            })

        return {
            "root": {
                "avg_cpu": round(self.root.aggregated_load.cpu, 1),
                "avg_mem": round(self.root.aggregated_load.mem, 1),
                "avg_net": round(self.root.aggregated_load.net, 1),
                "total_nodes": self.num_nodes,
                "total_racks": len(self.root.children),
            },
            "entropy": {
                "shannon": round(shannon, 3),
                "normalized": round(norm_e, 3),
                "classification": e_class.value,
                "is_critical": (e_class == EntropyClass.HIGH)
            },
            "racks": racks_data,
            "nodes": nodes_data,
            "latency_comparison": {
                "hierarchical_tree_avg_us": self.latency_stats["hierarchical_tree"]["avg_us"],
                "flat_scan_lln_avg_us": self.latency_stats["flat_scan_lln"]["avg_us"],
                "recent_tree_samples": self.latency_stats["hierarchical_tree"]["samples"][-15:],
                "recent_lln_samples": self.latency_stats["flat_scan_lln"]["samples"][-15:]
            },
            "recent_dispatches": self.dispatch_history[-10:],
            "active_algorithm": self.active_algorithm
        }
