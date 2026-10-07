import random
import time
from typing import List, Tuple, Optional
from .tree import ComputeNode
from .balancer import Job, WEIGHT_PROFILES, JobType

class RoundRobinBalancer:
    """
    Baseline 1: Round-Robin (RR)
    Assigns jobs cyclically to nodes. Ignores runtime load variations and heterogeneity.
    Complexity: O(1) query time.
    """
    def __init__(self, nodes: List[ComputeNode]):
        self.nodes = nodes
        self.current_idx = 0
        self.total_dispatches = 0

    def query_and_assign(self, job: Job) -> Tuple[ComputeNode, float]:
        start = time.perf_counter()
        node = self.nodes[self.current_idx]
        self.current_idx = (self.current_idx + 1) % len(self.nodes)

        node.assign_job(job.job_id, job.cpu_req, job.mem_req, job.net_req, job.disk_req)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        self.total_dispatches += 1
        return node, elapsed_ms


class LeastLoadedNodeBalancer:
    """
    Baseline 2: Least-Loaded Node (LLN)
    Flat list / array scan finding the node with minimum load.
    Complexity: O(N) linear time per job.
    """
    def __init__(self, nodes: List[ComputeNode], use_composite: bool = True):
        self.nodes = nodes
        self.use_composite = use_composite
        self.total_dispatches = 0

    def query_and_assign(self, job: Job) -> Tuple[ComputeNode, float]:
        start = time.perf_counter()
        weights = WEIGHT_PROFILES.get(job.job_type, WEIGHT_PROFILES[JobType.BALANCED])

        best_node: Optional[ComputeNode] = None
        min_load = float('inf')

        # Linear O(N) search across all nodes in the flat list
        for node in self.nodes:
            if self.use_composite:
                score = node.get_composite_load(weights)
            else:
                score = node.load.cpu
            if score < min_load:
                min_load = score
                best_node = node

        if best_node is None:
            best_node = self.nodes[0]

        best_node.assign_job(job.job_id, job.cpu_req, job.mem_req, job.net_req, job.disk_req)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        self.total_dispatches += 1
        return best_node, elapsed_ms


class WorkQueueBalancer:
    """
    Baseline 3: Centralized Work Queue
    Assigns incoming job to the first node with available capacity, or least busy worker.
    """
    def __init__(self, nodes: List[ComputeNode]):
        self.nodes = nodes
        self.total_dispatches = 0

    def query_and_assign(self, job: Job) -> Tuple[ComputeNode, float]:
        start = time.perf_counter()
        # Find first node with CPU < 80%
        chosen_node = None
        for node in self.nodes:
            if node.load.cpu < 80.0:
                chosen_node = node
                break
        
        if chosen_node is None:
            # Fall back to minimum CPU node
            chosen_node = min(self.nodes, key=lambda n: n.load.cpu)

        chosen_node.assign_job(job.job_id, job.cpu_req, job.mem_req, job.net_req, job.disk_req)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        self.total_dispatches += 1
        return chosen_node, elapsed_ms


class RandomBalancer:
    """
    Baseline 4: Random
    Selects a node uniformly at random.
    """
    def __init__(self, nodes: List[ComputeNode]):
        self.nodes = nodes
        self.total_dispatches = 0

    def query_and_assign(self, job: Job) -> Tuple[ComputeNode, float]:
        start = time.perf_counter()
        node = random.choice(self.nodes)
        node.assign_job(job.job_id, job.cpu_req, job.mem_req, job.net_req, job.disk_req)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        self.total_dispatches += 1
        return node, elapsed_ms
