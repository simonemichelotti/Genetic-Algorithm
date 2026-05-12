import pytest
from evolutionary_engine import engine

def test_engine_constants():
    # Test that main fitness weights are within [0, 1]
    assert 0 <= engine.WEIGHT_F1 <= 1
    assert 0 <= engine.WEIGHT_SPECIFICITY <= 1
    assert 0 <= engine.SIMPLICITY_WEIGHT <= 1

def test_nodi_scambiabili_sicuri():
    # Test that safe node set is not empty
    assert isinstance(engine.NODI_SCAMBIABILI_SICURI, set)
    assert len(engine.NODI_SCAMBIABILI_SICURI) > 0
