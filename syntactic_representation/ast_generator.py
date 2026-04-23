from lark import Lark, Tree, Token

# Grammatica EBNF per espressioni regolari
REGEX_GRAMMAR = r"""
    start: alternation

    alternation: concatenation ("|" concatenation)*

    concatenation: repetition+

    repetition: atom quantifier?

    quantifier: "*" | "+" | "?" | range_quantifier

    range_quantifier: "{" NUMBER "}" -> range_exact
                    | "{" NUMBER "," "}" -> range_min
                    | "{" NUMBER "," NUMBER "}" -> range_minmax

    atom: char
        | char_class
        | escape_sequence
        | group
        | anchor
        | wildcard

    wildcard: "."

    char_class: "[" char_class_content "]"
              | "[^" char_class_content "]"

    char_class_content: (char_range | CHAR)+

    char_range: CHAR "-" CHAR

    escape_sequence: "\\d" | "\\D"
                   | "\\w" | "\\W"
                   | "\\s" | "\\S"
                   | "\\b" | "\\B"
                   | unicode_property
                   | "\\" CHAR

    unicode_property: "\\p{" PROPERTY_NAME "}"
                    | "\\P{" PROPERTY_NAME "}"

    anchor: "^" | "$"

    group: "(" alternation ")"

    char: CHAR

    CHAR: /[a-zA-Z0-9]/
    PROPERTY_NAME: /[A-Z][a-z]?/
    NUMBER: /[0-9]+/

    %import common.WS
    %ignore WS
"""


class RegexParser:
    """Parser LALR(1) per convertire stringhe regex in AST strutturati."""

    def __init__(self):
        self.parser = Lark(REGEX_GRAMMAR, start='start', parser='lalr')

    def parse(self, regex_str, silent=False):
        """
        Parsa una stringa regex e restituisce il corrispondente AST (lark.Tree).
        Ritorna None in caso di errore sintattico.
        """
        try:
            return self.parser.parse(regex_str)
        except Exception:
            return None

    def print_ast(self, ast, indent=0):
        """Stampa l'AST in modo leggibile (utile per debug)."""
        if isinstance(ast, Tree):
            print("  " * indent + f"Tree({ast.data})")
            for child in ast.children:
                self.print_ast(child, indent + 1)
        elif isinstance(ast, Token):
            print("  " * indent + f"Token({ast.type}: '{ast.value}')")
        else:
            print("  " * indent + str(ast))


def genera_ast(regex_str, silent=False):
    """
    Funzione di convenienza: parsa regex_str e restituisce l'AST.
    Restituisce None se il parsing fallisce.
    """
    parser = RegexParser()
    return parser.parse(regex_str, silent=silent)
