import numpy as np
from prabodha.stats.core import permutation_p, hedges_g, holm, screen

def test_permutation_detects_effect():
    rng = np.random.default_rng(0)
    x = rng.normal(1.0, 1, 60); y = rng.normal(0.0, 1, 60)
    assert permutation_p(x, y, 2000) < 0.01

def test_permutation_null_uniformish():
    rng = np.random.default_rng(1)
    x = rng.normal(0, 1, 40); y = rng.normal(0, 1, 40)
    assert permutation_p(x, y, 2000) > 0.05

def test_hedges_g_sign_and_magnitude():
    x = np.array([2.0, 2.1, 1.9, 2.2]); y = np.array([1.0, 1.1, 0.9, 1.2])
    g = hedges_g(x, y); assert g > 2

def test_holm_monotone_gate():
    d = holm({"a": 0.001, "b": 0.02, "c": 0.9}, alpha=0.05)
    assert d["a"] and not d["c"]

def test_screen_report_shape():
    rng = np.random.default_rng(2)
    r = screen(rng.normal(0.5, 1, 30), rng.normal(0, 1, 30))
    assert set(r) >= {"p_perm", "hedges_g", "g_ci95", "tier"}
