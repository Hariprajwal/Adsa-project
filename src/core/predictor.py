"""
Lightweight Learning-Augmented Load Predictor (P9 Section 3.4)
Provides proactive load prediction over future scheduling horizons
using linear autoregression and exponential smoothing trends.
"""

from enum import Enum
from typing import List, Tuple, Optional
import numpy as np

class LoadTrend(Enum):
    STABLE = "STABLE"
    UPWARD = "UPWARD"
    DOWNWARD = "DOWNWARD"

class LightweightPredictor:
    """
    Lightweight predictive module estimating near-future compute node utilization.
    Enables proactive scheduling by forecasting load trajectories before congestion manifests.
    Complexity: O(W) where W is the sliding window size (default 10 samples).
    """
    def __init__(self, horizon_steps: int = 5, slope_threshold: float = 0.5):
        self.horizon_steps = horizon_steps
        self.slope_threshold = slope_threshold

    def predict_future_load(self, history: List[float]) -> Tuple[float, float, LoadTrend]:
        """
        Fits an ordinary least squares (OLS) linear trend across recent history samples:
        u(t) = m * t + c
        Returns:
            predicted_load: Estimated utilization at t = len(history) + horizon_steps
            slope: Rate of change (% per sample interval)
            trend: LoadTrend enum (UPWARD, DOWNWARD, STABLE)
        """
        if not history:
            return 0.0, 0.0, LoadTrend.STABLE
        
        n = len(history)
        if n < 2:
            return history[-1], 0.0, LoadTrend.STABLE

        t = np.arange(n, dtype=float)
        u = np.array(history, dtype=float)

        t_mean = np.mean(t)
        u_mean = np.mean(u)

        numerator = np.sum((t - t_mean) * (u - u_mean))
        denominator = np.sum((t - t_mean) ** 2)

        if abs(denominator) < 1e-9:
            slope = 0.0
        else:
            slope = float(numerator / denominator)

        intercept = float(u_mean - slope * t_mean)

        # Forecast at future horizon
        target_t = n + self.horizon_steps
        raw_pred = slope * target_t + intercept
        predicted_load = float(np.clip(raw_pred, 0.0, 100.0))

        if slope > self.slope_threshold:
            trend = LoadTrend.UPWARD
        elif slope < -self.slope_threshold:
            trend = LoadTrend.DOWNWARD
        else:
            trend = LoadTrend.STABLE

        return predicted_load, slope, trend

    def proactive_composite_load(
        self,
        current_load: float,
        predicted_load: float,
        alpha: float = 0.30
    ) -> float:
        """
        Blends instantaneous composite load with proactive predicted load:
        L_proactive = (1 - alpha) * L_current + alpha * L_predicted
        """
        return (1.0 - alpha) * current_load + alpha * predicted_load
