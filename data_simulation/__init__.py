"""
Modulo 1 – Simulazione Dati
===========================
Responsabile della generazione del ground-truth e della sintesi dei dataset
di tracce (positive e negative) usati dall'algoritmo evolutivo.

Componenti:
    - trace_generator : genera tracce da un pattern regex ground-truth
    - regex_generator : genera regex casuali valide per inizializzare la popolazione
    - llm_prompt      : costruisce i prompt da inviare all'LLM (singolo e multi-candidato)
"""

from .trace_generator import classify_and_save_traces, generate_simple_pattern
from .regex_generator import generate_random_regex, sanitize_regex_pattern, safe_compile
from .llm_prompt import build_llm_prompt, build_llm_prompt_multi

__all__ = [
    "classify_and_save_traces",
    "generate_simple_pattern",
    "generate_random_regex",
    "sanitize_regex_pattern",
    "safe_compile",
    "build_llm_prompt",
    "build_llm_prompt_multi",
]
