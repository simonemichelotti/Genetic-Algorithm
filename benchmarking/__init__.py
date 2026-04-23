"""
Modulo 4 – Pipeline di Benchmarking
=====================================
Automatizza la comparazione tra Genetic Algorithm classico, LLM Zero-Shot e
GA Ibrido su dataset generati casualmente. Produce CSV con i risultati e
grafici interattivi Plotly.

Componenti:
    - experiments    : runner CLI per eseguire N lanci e salvare i risultati in CSV
    - plot_comparison: generatore di grafici di comparazione da CSV
"""

from .experiments import run_one
from .plot_comparison import plot_comparison

__all__ = [
    "run_one",
    "plot_comparison",
]
