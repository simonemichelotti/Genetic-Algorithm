import pytest
from data_simulation.regex_generator import split_top_level_alternatives

def test_split_top_level_alternatives_basic():
    pattern = "a|b|c"
    parts = split_top_level_alternatives(pattern)
    assert parts == ["a", "b", "c"]

def test_split_top_level_alternatives_nested():
    pattern = "a|(b|c)|d"
    parts = split_top_level_alternatives(pattern)
    assert parts == ["a", "(b|c)", "d"]

def test_split_top_level_alternatives_char_class():
    pattern = "a|[b|c]|d"
    parts = split_top_level_alternatives(pattern)
    assert parts == ["a", "[b|c]", "d"]
