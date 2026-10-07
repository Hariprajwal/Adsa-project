from typing import List, Tuple, Dict
from .tree import ClusterRoot, ComputeNode, build_hierarchical_tree
from .entropy import EntropyClass

class PeriodicRebalancer:
    """
    Algorithm 3: Periodic Rebalancing
    Evaluates entropy distribution changes across all nodes.
    If more than tau (e.g. 20%) of the nodes transition entropy classes,
    triggers a complete bottom-up tree reconstruction (Algorithm 1).
    Otherwise, refreshes aggregated metrics in-place.
    """
    def __init__(self, tau_shift_threshold: float = 0.20):
        self.tau_shift_threshold = tau_shift_threshold
        self.rebuild_count: int = 0
        self.in_place_refresh_count: int = 0

    def check_and_rebalance(self, root: ClusterRoot, all_nodes: List[ComputeNode]) -> Tuple[ClusterRoot, bool, dict]:
        """
        Executes periodic rebalancing step.
        Returns: (updated_root, was_rebuilt, stats_dict)
        """
        total_nodes = len(all_nodes)
        if total_nodes == 0:
            return root, False, {}

        shift_count = 0
        previous_classes: Dict[int, EntropyClass] = {}

        # Step 1: Detect class changes compared to last rebalanced state
        for node in all_nodes:
            old_class = node.last_rebalanced_class
            # Recompute current variance and classify
            new_var = node.entropy_tracker.compute_variance_entropy()
            node.entropy_tracker.current_variance = new_var
            current_class = node.entropy_tracker.classify()
            node.entropy_tracker.current_class = current_class
            
            if old_class != current_class:
                shift_count += 1
            node.last_rebalanced_class = current_class

        shift_ratio = shift_count / total_nodes
        was_rebuilt = False

        # Step 2: Check threshold condition
        if shift_ratio > self.tau_shift_threshold:
            # Rebuild tree bottom-up via Algorithm 1
            root = build_hierarchical_tree(all_nodes, nodes_per_rack=32)
            self.rebuild_count += 1
            was_rebuilt = True
        else:
            # In-place refresh of all internal nodes
            root.aggregate()
            self.in_place_refresh_count += 1

        stats = {
            "total_nodes": total_nodes,
            "shift_count": shift_count,
            "shift_ratio": round(shift_ratio, 4),
            "threshold": self.tau_shift_threshold,
            "was_rebuilt": was_rebuilt,
            "total_rebuilds": self.rebuild_count,
            "total_refreshes": self.in_place_refresh_count
        }

        return root, was_rebuilt, stats
