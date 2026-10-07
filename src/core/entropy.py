import math
from collections import deque
from enum import Enum
from typing import List, Tuple

class EntropyClass(str, Enum):
    LOW = "LOW"         # Stable performance, suitable for predictable long jobs
    MEDIUM = "MEDIUM"   # Moderate variation
    HIGH = "HIGH"       # Bursty, volatile performance

class EntropyTracker:
    """
    Tracks runtime load metrics over a sliding window and computes:
    1. Variance-based entropy: H_var(c_i) = Var(CPU utilization over window)
    2. Shannon entropy: H_Shannon(c_i) = -sum(p_k * log2(p_k)) across discrete bins
    3. Categorical classification into LOW, MEDIUM, or HIGH entropy
    """
    def __init__(self, window_size: int = 10, tau_low: float = 15.0, tau_high: float = 50.0):
        self.window_size = window_size
        self.tau_low = tau_low
        self.tau_high = tau_high
        self.history = deque(maxlen=window_size)
        self.current_variance: float = 0.0
        self.current_shannon: float = 0.0
        self.current_class: EntropyClass = EntropyClass.LOW

    def add_sample(self, cpu_util: float) -> Tuple[float, EntropyClass]:
        """
        Record a new CPU utilization sample (0.0 to 100.0) and update metrics.
        """
        clipped_cpu = max(0.0, min(100.0, float(cpu_util)))
        self.history.append(clipped_cpu)
        self.current_variance = self.compute_variance_entropy()
        self.current_shannon = self.compute_shannon_entropy()
        self.current_class = self.classify()
        return self.current_variance, self.current_class

    def compute_variance_entropy(self) -> float:
        """
        Variance-based entropy formulation from P9 specification:
        H_var(c_i) = Var(CPU utilization over last W samples)
        """
        n = len(self.history)
        if n < 2:
            return 0.0
        mean = sum(self.history) / n
        variance = sum((x - mean) ** 2 for x in self.history) / (n - 1)
        return round(variance, 4)

    def compute_shannon_entropy(self, num_bins: int = 5) -> float:
        """
        Shannon entropy formulation from P9 specification:
        Discretizes CPU utilization into 5 bins: [0-20), [20-40), [40-60), [60-80), [80-100].
        Computes H_Shannon = -sum(p_k * log2(p_k))
        Max theoretical entropy for 5 bins is log2(5) ~= 2.3219 bits.
        """
        n = len(self.history)
        if n == 0:
            return 0.0

        bin_counts = [0] * num_bins
        bin_width = 100.0 / num_bins

        for val in self.history:
            bin_idx = int(val // bin_width)
            if bin_idx >= num_bins:
                bin_idx = num_bins - 1
            bin_counts[bin_idx] += 1

        entropy = 0.0
        for count in bin_counts:
            if count > 0:
                p = count / n
                entropy -= p * math.log2(p)

        return round(entropy, 4)

    def classify(self, tau_low: float = None, tau_high: float = None) -> EntropyClass:
        """
        Classifies node stability according to thresholds:
        - Low-entropy: H(c_i) < tau_low
        - Medium-entropy: tau_low <= H(c_i) <= tau_high
        - High-entropy: H(c_i) > tau_high
        Default uses variance entropy.
        """
        t_low = self.tau_low if tau_low is None else tau_low
        t_high = self.tau_high if tau_high is None else tau_high
        var = self.current_variance

        if var < t_low:
            return EntropyClass.LOW
        elif var <= t_high:
            return EntropyClass.MEDIUM
        else:
            return EntropyClass.HIGH

    def get_summary(self) -> dict:
        return {
            "window_size": len(self.history),
            "variance_entropy": self.current_variance,
            "shannon_entropy": self.current_shannon,
            "entropy_class": self.current_class.value
        }
