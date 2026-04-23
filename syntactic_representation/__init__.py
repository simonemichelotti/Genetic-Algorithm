"""
Modulo 2 – Rappresentazione Sintattica
=======================================
Gestisce la traduzione bidirezionale tra stringhe regex e Abstract Syntax Tree (AST).
Garantisce la validità sintattica di ogni individuo durante le operazioni genetiche.

Componenti:
    - ast_generator : parser LALR(1) che converte una stringa regex in AST (lark.Tree)
    - ast_to_regex  : compilatore inverso che ricostruisce la stringa regex dall'AST
"""

from .ast_generator import RegexParser, genera_ast
from .ast_to_regex import ast_to_regex

__all__ = [
    "RegexParser",
    "genera_ast",
    "ast_to_regex",
]
