"""
Modulo 3 – Motore Evolutivo
============================
Implementa l'algoritmo genetico per l'inferenza automatica di regex a partire
da tracce positive e negative. Supporta sia la modalità classica (popolazione
casuale) sia quella ibrida (semi-inizializzazione LLM via Ollama).

Componenti:
    - engine : ciclo evolutivo completo (inizializzazione, selezione, crossover,
               mutazione, elitismo) con supporto a callback per generazione.
"""

from .engine import evoluzione, calcola_fitness, inizializza, carica_tracce

__all__ = [
    "evoluzione",
    "calcola_fitness",
    "inizializza",
    "carica_tracce",
]
