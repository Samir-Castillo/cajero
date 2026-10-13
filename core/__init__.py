"""
Paquete core del modelo de simulación de cajas de supermercado.
"""
from .generators import RandomVariateGenerator, lcg_generator
from .simulator import SupermarketSimulation, run_experiment
from .statistics import (
    calculate_descriptive_stats,
    calculate_confidence_interval,
    two_sample_hypothesis_test,
    theoretical_erlang_c
)

__all__ = [
    "RandomVariateGenerator",
    "lcg_generator",
    "SupermarketSimulation",
    "run_experiment",
    "calculate_descriptive_stats",
    "calculate_confidence_interval",
    "two_sample_hypothesis_test",
    "theoretical_erlang_c"
]
