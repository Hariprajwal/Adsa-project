from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from .entropy import EntropyTracker, EntropyClass

@dataclass
class ResourceVector:
    """
    Multi-dimensional resource vector:
    - cpu: CPU utilization percentage (0 - 100)
    - mem: Memory utilization percentage (0 - 100)
    - net: Network I/O in MB/s (normalized or raw)
    - disk: Disk I/O in MB/s (normalized or raw)
    """
    cpu: float = 0.0
    mem: float = 0.0
    net: float = 0.0
    disk: float = 0.0

    def composite_score(self, w_cpu: float = 0.25, w_mem: float = 0.25, 
                        w_net: float = 0.25, w_disk: float = 0.25) -> float:
        """
        L(c_i) = w_cpu * CPU + w_mem * Mem + w_net * Net + w_disk * Disk
        """
        return (w_cpu * self.cpu + 
                w_mem * self.mem + 
                w_net * self.net + 
                w_disk * self.disk)

    def add(self, other: 'ResourceVector') -> 'ResourceVector':
        return ResourceVector(
            cpu=min(100.0, self.cpu + other.cpu),
            mem=min(100.0, self.mem + other.mem),
            net=self.net + other.net,
            disk=self.disk + other.disk
        )

    def subtract(self, other: 'ResourceVector') -> 'ResourceVector':
        return ResourceVector(
            cpu=max(0.0, self.cpu - other.cpu),
            mem=max(0.0, self.mem - other.mem),
            net=max(0.0, self.net - other.net),
            disk=max(0.0, self.disk - other.disk)
        )


class ComputeNode:
    """
    Leaf node in the hierarchical tree representing an individual physical/simulated compute server.
    """
    def __init__(self, node_id: int, rack_id: int, cpu_cores: int = 16, mem_gb: float = 64.0):
        self.node_id = node_id
        self.rack_id = rack_id
        self.cpu_cores = cpu_cores
        self.mem_gb = mem_gb
        
        self.load = ResourceVector()
        self.entropy_tracker = EntropyTracker()
        self.last_rebalanced_class: EntropyClass = EntropyClass.LOW
        self.active_jobs: Dict[str, dict] = {}
        self.parent: Optional['RackNode'] = None

    @property
    def entropy_class(self) -> EntropyClass:
        return self.entropy_tracker.current_class

    @property
    def entropy_value(self) -> float:
        return self.entropy_tracker.current_variance

    def sample_heartbeat(self, new_cpu: float, new_mem: float, new_net: float, new_disk: float):
        """
        Periodic telemetry heartbeat update.
        """
        self.load.cpu = max(0.0, min(100.0, new_cpu))
        self.load.mem = max(0.0, min(100.0, new_mem))
        self.load.net = max(0.0, new_net)
        self.load.disk = max(0.0, new_disk)
        self.entropy_tracker.add_sample(self.load.cpu)

    def assign_job(self, job_id: str, cpu_req: float, mem_req: float, net_req: float, disk_req: float):
        """
        Allocate resources for incoming job.
        """
        self.load.cpu = min(100.0, self.load.cpu + cpu_req)
        self.load.mem = min(100.0, self.load.mem + mem_req)
        self.load.net += net_req
        self.load.disk += disk_req
        self.entropy_tracker.add_sample(self.load.cpu)
        self.active_jobs[job_id] = {
            "cpu": cpu_req,
            "mem": mem_req,
            "net": net_req,
            "disk": disk_req
        }

    def release_job(self, job_id: str):
        """
        Release job resources on completion.
        """
        if job_id in self.active_jobs:
            reqs = self.active_jobs.pop(job_id)
            self.load.cpu = max(0.0, self.load.cpu - reqs["cpu"])
            self.load.mem = max(0.0, self.load.mem - reqs["mem"])
            self.load.net = max(0.0, self.load.net - reqs["net"])
            self.load.disk = max(0.0, self.load.disk - reqs["disk"])
            self.entropy_tracker.add_sample(self.load.cpu)

    def get_composite_load(self, weights: dict) -> float:
        return self.load.composite_score(
            weights.get("w_cpu", 0.25),
            weights.get("w_mem", 0.25),
            weights.get("w_net", 0.25),
            weights.get("w_disk", 0.25)
        )


class RackNode:
    """
    Level 1 Internal Node representing a rack grouping (e.g. 16–32 compute nodes).
    Maintains aggregated load metrics and subtree minimums/maximums for fast coarse-to-fine query.
    """
    def __init__(self, rack_id: int):
        self.rack_id = rack_id
        self.children: List[ComputeNode] = []
        self.parent: Optional['ClusterRoot'] = None
        
        self.aggregated_load = ResourceVector()
        self.min_cpu: float = 0.0
        self.max_cpu: float = 0.0
        self.low_entropy_count: int = 0
        self.high_entropy_count: int = 0
        self.min_composite_cache: Dict[str, float] = {}

    def add_child(self, node: ComputeNode):
        node.parent = self
        self.children.append(node)

    def aggregate(self):
        """
        Bottom-up aggregation of child loads and metadata.
        """
        if not self.children:
            return

        total_cpu = sum(c.load.cpu for c in self.children)
        total_mem = sum(c.load.mem for c in self.children)
        total_net = sum(c.load.net for c in self.children)
        total_disk = sum(c.load.disk for c in self.children)
        n = len(self.children)

        self.aggregated_load = ResourceVector(
            cpu=total_cpu / n,
            mem=total_mem / n,
            net=total_net / n,
            disk=total_disk / n
        )
        self.min_cpu = min(c.load.cpu for c in self.children)
        self.max_cpu = max(c.load.cpu for c in self.children)

        self.low_entropy_count = sum(1 for c in self.children if c.entropy_class == EntropyClass.LOW)
        self.high_entropy_count = sum(1 for c in self.children if c.entropy_class == EntropyClass.HIGH)
        # Clear composite cache so next query re-computes
        self.min_composite_cache.clear()

    def get_min_composite_load(self, weights: dict, type_key: str = "default") -> float:
        """
        Computes minimum composite score among children in this rack with caching.
        """
        if not self.children:
            return 100.0
        if type_key in self.min_composite_cache:
            return self.min_composite_cache[type_key]

        min_val = min(c.get_composite_load(weights) for c in self.children)
        self.min_composite_cache[type_key] = min_val
        return min_val


class ClusterRoot:
    """
    Root Node of the hierarchical cluster tree.
    Aggregates metrics across all racks and acts as the entry point for O(log N) scheduling queries.
    """
    def __init__(self, cluster_name: str = "HPC_Cluster"):
        self.cluster_name = cluster_name
        self.children: List[RackNode] = []
        self.aggregated_load = ResourceVector()
        self.node_lookup: Dict[int, ComputeNode] = {}

    def add_rack(self, rack: RackNode):
        rack.parent = self
        self.children.append(rack)
        for node in rack.children:
            self.node_lookup[node.node_id] = node

    def aggregate(self):
        """
        Aggregates metrics across all racks bottom-up.
        """
        if not self.children:
            return

        for rack in self.children:
            rack.aggregate()

        total_cpu = sum(r.aggregated_load.cpu for r in self.children)
        total_mem = sum(r.aggregated_load.mem for r in self.children)
        total_net = sum(r.aggregated_load.net for r in self.children)
        total_disk = sum(r.aggregated_load.disk for r in self.children)
        r_count = len(self.children)

        self.aggregated_load = ResourceVector(
            cpu=total_cpu / r_count,
            mem=total_mem / r_count,
            net=total_net / r_count,
            disk=total_disk / r_count
        )

    def propagate_upward(self, node: ComputeNode):
        """
        Propagates load update upward in O(log N) time: Leaf -> Rack -> Root.
        """
        if node.parent:
            node.parent.aggregate()
        # Refresh cluster level aggregated load
        r_count = len(self.children)
        if r_count > 0:
            self.aggregated_load.cpu = sum(r.aggregated_load.cpu for r in self.children) / r_count
            self.aggregated_load.mem = sum(r.aggregated_load.mem for r in self.children) / r_count
            self.aggregated_load.net = sum(r.aggregated_load.net for r in self.children) / r_count
            self.aggregated_load.disk = sum(r.aggregated_load.disk for r in self.children) / r_count


def build_hierarchical_tree(nodes: List[ComputeNode], nodes_per_rack: int = 32) -> ClusterRoot:
    """
    Algorithm 1: Hierarchical Tree Construction
    Constructs a multi-level tree (Cluster -> Racks -> Nodes) bottom-up from a set of compute nodes.
    """
    root = ClusterRoot()
    
    # Group nodes into racks
    num_nodes = len(nodes)
    rack_count = (num_nodes + nodes_per_rack - 1) // nodes_per_rack
    
    racks = [RackNode(rack_id=i) for i in range(rack_count)]
    for idx, node in enumerate(nodes):
        rack_idx = idx // nodes_per_rack
        node.rack_id = rack_idx
        racks[rack_idx].add_child(node)

    for rack in racks:
        rack.aggregate()
        root.add_rack(rack)

    root.aggregate()
    return root
