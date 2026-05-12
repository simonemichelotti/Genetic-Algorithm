import pytest
from syntactic_representation.ast_generator import RegexParser

def test_regex_parser_simple():
    parser = RegexParser()
    tree = parser.parse('a|b')
    assert tree is not None
    assert tree.data == 'start'

def test_regex_parser_complex():
    parser = RegexParser()
    tree = parser.parse('(ab|c)*d?')
    assert tree is not None
    assert tree.data == 'start'
