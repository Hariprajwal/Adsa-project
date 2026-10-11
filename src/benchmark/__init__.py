"""
Benchmarking & Publication Results Engine (Phase 3)
"""

from .run_benchmarks import run_full_benchmark_suite
from .plot_figures import generate_all_figures
from .generate_tables import generate_paper_tables

__all__ = [
    "run_full_benchmark_suite",
    "generate_all_figures",
    "generate_paper_tables"
]
