import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple, Optional, List
from .tree import ClusterRoot, ComputeNode, RackNode
from .entropy import EntropyClass

class JobType(str, Enum):
    CPU_BOUND = "CPU_BOUND"       # Video transcoding / compute intense
    MEMORY_BOUND = "MEMORY_BOUND" # Frame buffering / chunk caching
    IO_BOUND = "IO_BOUND"         # High-bitrate video segment egress
    BALANCED = "BALANCED"         # Standard general compute

WEIGHT_PROFILES: Dict[JobType, Dict[str, float]] = {
    JobType.CPU_BOUND: {
        "w_cpu": 0.70,
        "w_mem": 0.10,
        "w_net": 0.10,
        "w_disk": 0.10
    },
    JobType.MEMORY_BOUND: {
        "w_cpu": 0.10,
        "w_mem": 0.70,
        "w_net": 0.10,
        "w_disk": 0.10
    },
    JobType.IO_BOUND: {
        "w_cpu": 0.10,
        "w_mem": 0.10,
        "w_net": 0.50,
        "w_disk": 0.30
    },
    JobType.BALANCED: {
        "w_cpu": 0.25,
        "w_mem": 0.25,
        "w_net": 0.25,
        "w_disk": 0.25
    }
}

@dataclass
class Job:
    """
    Representation of an incoming parallel/video workload job.
    """
    job_id: str
    job_type: JobType
    cpu_req: float = 5.0      # CPU utilization percentage requested
    mem_req: float = 4.0      # Memory utilization percentage requested
    net_req: float = 10.0     # Network I/O MB/s requested
    disk_req: float = 5.0     # Disk I/O MB/s requested
    duration: float = 10.0    # Runtime in seconds
    is_predictable: bool = False # Long-running stable job vs short bursty task
    submit_time: float = 0.0


class EntropyHierarchicalBalancer:
    """
    Algorithm 2: Job Assignment with Hierarchical Query
    Traverses the cluster hierarchy top-down in O(log N) to select the optimal node,
    constrained by entropy-guided matching for predictable workloads.
    """
    def __init__(self, root: ClusterRoot, tau_high: float = 50.0):
        self.root = root
        self.tau_high = tau_high
        self.total_dispatches: int = 0
        self.total_query_time_ms: float = 0.0

    def query_and_assign(self, job: Job) -> Tuple[ComputeNode, List[str], float]:
        """
        Executes Algorithm 2:
        1. Evaluates weights from job type.
        2. Top-down traversal through best Rack -> best Node.
        3. Entropy verification: if job is predictable, avoids High Entropy nodes if possible.
        4. Assigns job and updates tree bottom-up in O(log N).
        Returns: (assigned_node, dispatch_path, elapsed_time_ms)
        """
        start_time = time.perf_counter()
        weights = WEIGHT_PROFILES.get(job.job_type, WEIGHT_PROFILES[JobType.BALANCED])
        dispatch_path = ["ClusterRoot"]

        # Step 1: Coarse selection at Rack level (Level 1)
        # Select best rack minimizing subtree minimum composite load
        best_rack: Optional[RackNode] = None
        min_rack_score = float('inf')
        type_key = job.job_type.value

        for rack in self.root.children:
            rack_min = rack.get_min_composite_load(weights, type_key=type_key)
            if rack_min < min_rack_score:
                min_rack_score = rack_min
                best_rack = rack

        if best_rack is None:
            # Fallback if tree has no racks
            best_rack = self.root.children[0]

        dispatch_path.append(f"Rack_{best_rack.rack_id}")

        # Step 2: Fine selection at Compute Node level (Level 2)
        # Evaluate nodes within the chosen rack
        candidate_node: Optional[ComputeNode] = None
        min_node_score = float('inf')

        for node in best_rack.children:
            score = node.get_composite_load(weights)
            if score < min_node_score:
                min_node_score = score
                candidate_node = node

        if candidate_node is None:
            candidate_node = best_rack.children[0]

        # Step 3: Entropy verification for predictable jobs
        # If job is predictable and candidate node has high volatility (high entropy),
        # search for an alternative stable (low/medium entropy) node within acceptable load overhead
        selected_node = candidate_node
        if job.is_predictable and candidate_node.entropy_class == EntropyClass.HIGH:
            alternative = self._find_low_entropy_alternative(best_rack, weights, candidate_node)
            if alternative is not None:
                selected_node = alternative

        dispatch_path.append(f"Node_{selected_node.node_id}")

        # Step 4: Assign job & propagate load upward in O(log N)
        selected_node.assign_job(
            job.job_id,
            job.cpu_req,
            job.mem_req,
            job.net_req,
            job.disk_req
        )
        self.root.propagate_upward(selected_node)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        self.total_dispatches += 1
        self.total_query_time_ms += elapsed_ms

        return selected_node, dispatch_path, elapsed_ms

    def _find_low_entropy_alternative(self, rack: RackNode, weights: dict, 
                                     best_candidate: ComputeNode, 
                                     tolerance_factor: float = 1.25) -> Optional[ComputeNode]:
        """
        Searches candidate nodes in rack (or neighboring racks) that have LOW or MEDIUM entropy
        and whose composite load is within tolerance (e.g. within 25% of the best candidate).
        """
        best_alt: Optional[ComputeNode] = None
        best_alt_score = float('inf')
        threshold_score = best_candidate.get_composite_load(weights) * tolerance_factor + 5.0

        for node in rack.children:
            if node.entropy_class in (EntropyClass.LOW, EntropyClass.MEDIUM):
                score = node.get_composite_load(weights)
                if score <= threshold_score and score < best_alt_score:
                    best_alt_score = score
                    best_alt = node

        # If not found in current rack, inspect adjacent racks
        if best_alt is None:
            for other_rack in self.root.children:
                if other_rack.rack_id == rack.rack_id:
                    continue
                for node in other_rack.children:
                    if node.entropy_class == EntropyClass.LOW:
                        score = node.get_composite_load(weights)
                        if score <= threshold_score and score < best_alt_score:
                            best_alt_score = score
                            best_alt = node

        return best_alt
