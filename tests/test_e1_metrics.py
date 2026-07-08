"""Unit tests for E1 evaluators (CPU, deterministic, no network).
Pure-numpy metric tests need no torch; the end-to-end pipeline test is marked smoke
(tiny random decoder -> jlens fit -> run_e1 -> e1_cli GateReport validation).
"""
from pathlib import Path

import numpy as np
import pytest

from prabodha.lens.e1_metrics import (
    _concept_candidate_ids,
    best_band_partition,
    cka_matrix,
    linear_cka,
    modulation_band_layers,
    permutation_p_mean_rho,
    spearman_rho,
    topk_indices,
    topk_union_indices,
)

ROOT = Path(__file__).resolve().parents[1]


def test_spearman_perfect_and_reversed():
    x = np.array([0.1, 3.0, 2.0, 5.0, 4.0])
    assert spearman_rho(x, x) == pytest.approx(1.0)
    assert spearman_rho(x, -x) == pytest.approx(-1.0)
    assert spearman_rho(x, 2 * x + 7) == pytest.approx(1.0)  # rank-only, scale-invariant


def test_spearman_degenerate_constant_is_zero():
    assert spearman_rho(np.ones(6), np.arange(6.0)) == 0.0


def test_topk_union_logic():
    a = np.arange(20.0)   # top-3: {17, 18, 19}
    b = -np.arange(20.0)  # top-3: {0, 1, 2}
    idx = topk_union_indices(a, b, 3)
    assert set(idx.tolist()) == {0, 1, 2, 17, 18, 19}
    assert spearman_rho(a[idx], b[idx]) == pytest.approx(-1.0)
    # identical inputs: the union collapses to a single top-k set
    assert len(topk_union_indices(a, a, 5)) == 5


def test_union_support_null_floor_is_negative_but_model_topk_null_is_zero():
    """L1 run-1 finding (amendment A1): disjoint top-k sets anti-correlate over the UNION
    support (~ -0.72 floor), while the MODEL-top-k support has a ~0 null — thresholds only
    mean what they say on the calibrated support."""
    rng = np.random.default_rng(0)
    v = rng.normal(0, 1, 30000)
    m = rng.normal(0, 1, 30000)
    v[:50] += 20    # lens mass on tokens 0..49
    m[50:100] += 20  # model mass on tokens 50..99 (disjoint)
    u = topk_union_indices(v, m, 50)
    assert spearman_rho(v[u], m[u]) < -0.6  # structural anti-correlation
    idx = topk_indices(m, 50)
    assert abs(spearman_rho(v[idx], m[idx])) < 0.3  # null ~ 0 on model support
    assert spearman_rho(m[idx], m[idx]) == pytest.approx(1.0)


def test_permutation_p_separates_signal_from_null():
    rng = np.random.default_rng(2)
    m = rng.normal(0, 1, 50)
    signal_pairs = [(m + 0.1 * rng.normal(0, 1, 50), m) for _ in range(8)]
    observed = float(np.mean([spearman_rho(a, b) for a, b in signal_pairs]))
    assert permutation_p_mean_rho(signal_pairs, observed, 200, seed=0) < 0.05
    null_pairs = [(rng.normal(0, 1, 50), m) for _ in range(8)]
    null_obs = float(np.mean([spearman_rho(a, b) for a, b in null_pairs]))
    assert permutation_p_mean_rho(null_pairs, null_obs, 200, seed=0) > 0.05


def test_concept_candidate_ids_strip_bos():
    """L2 run-1 artifact: BOS-prepending tokenizers (SentencePiece/nemotron) made every
    concept's 'first token' the BOS id — hit rate, shuffled null, AND control all read
    exactly 0.0. Candidate ids must be derived WITHOUT special tokens."""
    class BosTok:
        BOS = 1
        vocab = {" fire": [11], "fire": [12], "火": [13]}
        def __call__(self, text, add_special_tokens=True, **kw):
            ids = self.vocab[text]
            return {"input_ids": ([self.BOS] + ids) if add_special_tokens else list(ids)}
    devs: list[str] = []
    ids = _concept_candidate_ids(BosTok(), "fire", {"fire": "火"}, devs)
    assert ids == {"en_mid": 11, "en_bare": 12, "zh": 13}
    assert devs == []  # single-token variants must NOT be flagged multi-token via BOS


def test_concept_candidate_ids_includes_translation():
    class Tok:  # minimal __call__ surface (BatchEncoding-like dict)
        vocab = {" fire": [11], "fire": [12], "火": [13], " water": [21, 22],
                 "water": [23], "水": [24]}
        def __call__(self, text, **kw):
            return {"input_ids": self.vocab[text]}
    devs: list[str] = []
    ids = _concept_candidate_ids(Tok(), "fire", {"fire": "火"}, devs)
    assert ids == {"en_mid": 11, "en_bare": 12, "zh": 13}
    assert devs == []
    ids2 = _concept_candidate_ids(Tok(), "water", {"water": "水"}, devs)
    assert ids2 == {"en_mid": 21, "en_bare": 23, "zh": 24}
    assert any("first id only" in d for d in devs)  # ' water' was multi-token


def test_articulation_negentropy_orders_sharpness():
    """E7 primitive: negentropy of the renormalized top-K lens readout must rank a sharp
    (concentrated) distribution above a flat one, and be 0 for uniform."""
    from prabodha.lens.e1_metrics import topk_negentropy
    rng = np.random.default_rng(3)
    flat = rng.normal(0, 0.01, 1000)
    sharp = rng.normal(0, 0.01, 1000)
    sharp[7] += 30.0  # one dominant token
    assert topk_negentropy(sharp, k=50) > topk_negentropy(flat, k=50)
    uniform = np.zeros(1000)
    assert topk_negentropy(uniform, k=50) == pytest.approx(0.0, abs=1e-9)


def test_articulation_gradient_detects_planted_depth_trend():
    """E7 assembly: layers whose readouts sharpen with depth -> rho ~ +1, small p;
    shuffled depth order -> rho near 0, large p."""
    from prabodha.lens.e1_metrics import articulation_gradient
    rng = np.random.default_rng(4)
    # scores rising with layer index (with mild noise), 3 prompts x 12 layers
    layers = list(range(12))
    scores = {layer: [layer / 12 + 0.01 * rng.normal() for _ in range(3)] for layer in layers}
    rho, p = articulation_gradient(scores, permutation_resamples=200, seed=0)
    assert rho > 0.9 and p < 0.05
    noise = {layer: [rng.normal() for _ in range(3)] for layer in layers}
    rho_n, p_n = articulation_gradient(noise, permutation_resamples=200, seed=0)
    assert abs(rho_n) < 0.6 and p_n > 0.05


def test_modulation_band_modes():
    """L1b circularity rule (review #2): depth_middle_third must IGNORE the CKA result;
    cka_middle must follow it. Unknown modes are errors, not silent fallbacks."""
    layers = list(range(36))
    bands = {"boundaries": [6, 30]}
    fixed = modulation_band_layers("depth_middle_third", layers, bands)
    assert fixed == layers[12:24]  # depth rule, CKA result ignored
    assert modulation_band_layers("depth_middle_third", layers, None) == fixed
    cka = modulation_band_layers("cka_middle", layers, bands)
    assert cka == list(range(6, 30))  # follows the CKA middle band
    with pytest.raises(ValueError):
        modulation_band_layers("nope", layers, bands)


def test_cka_identical_inputs_is_one():
    rng = np.random.default_rng(0)
    x = rng.normal(size=(60, 30))
    assert linear_cka(x, x) == pytest.approx(1.0)


def test_cka_band_search_recovers_planted_blocks():
    # 9 layers in 3 planted blocks of 3: layers within a block share a rank-3
    # random subspace (+ small iid noise); blocks use independent subspaces.
    rng = np.random.default_rng(1)
    acts = []
    for _block in range(3):
        base = rng.normal(size=(60, 3)) @ rng.normal(size=(3, 30))
        acts.extend(base + 0.01 * rng.normal(size=base.shape) for _layer in range(3))
    c = cka_matrix(acts)
    assert np.allclose(np.diag(c), 1.0)
    assert c[0, 1] > 0.9 > c[0, 4]  # within-block high, cross-block lower
    contrast, bounds = best_band_partition(c, min_band_size=2)
    assert bounds == (3, 6)
    assert contrast > 0.1


def test_band_partition_rejects_too_few_layers():
    with pytest.raises(ValueError):
        best_band_partition(np.eye(4), min_band_size=2)


@pytest.mark.smoke
def test_e1_pipeline_end_to_end_tiny(tmp_path):
    pytest.importorskip("torch")
    pytest.importorskip("transformers")
    pytest.importorskip("jlens")
    from prabodha.config import load
    from prabodha.contracts.closure import GateReport
    from prabodha.lens import e1_cli
    from prabodha.lens.adapter import LensAdapter, build_model
    from prabodha.lens.e1_metrics import run_e1

    hf, tok = build_model(load(ROOT / "configs/models/tiny_smoke.yaml"))
    # skip_first=2: vendor default (16) rejects prompts shorter than 18 tokens.
    lens_cfg = {"n_prompts": 2, "corpus": "synthetic_smoke", "seed": 42,
                "prompt_len": 24, "skip_first": 2}
    lens_path = tmp_path / "tiny.pt"
    adapter = LensAdapter("jacobian").fit(hf, tok, lens_cfg, out=lens_path)

    exp = load(ROOT / "configs/experiments/e1.yaml")
    results = run_e1(hf, tok, adapter, exp)
    for h in ("H_report", "H_bands", "H_modulation"):
        assert {"value", "threshold", "pass", "evidence"} <= set(results[h])
        assert isinstance(results[h]["pass"], bool)
    assert isinstance(results["deviations"], list)
    # full per-layer rho curve ships as gate evidence (rise-toward-late check is human/GB10)
    assert set(results["H_report"]["evidence"]["per_layer_rho_model_topk"]) \
        == set(adapter.source_layers)
    assert len(results["H_modulation"]["evidence"]["per_prompt"]) \
        == results["H_modulation"]["evidence"]["n_prompts"]
    assert len(results["H_bands"]["evidence"]["cka_matrix"]) == hf.config.n_layer

    # e1_cli end-to-end: gate JSON must validate as a GateReport. A RANDOM tiny model
    # failing the domain gate is CORRECT behavior -- we assert verdict MECHANICS
    # (dual verdicts, open status, contention recorded), never scientific outcomes.
    out = tmp_path / "gate.json"
    e1_cli.main(["--model", str(ROOT / "configs/models/tiny_smoke.yaml"),
                 "--lens-file", str(lens_path),
                 "--exp", str(ROOT / "configs/experiments/e1.yaml"),
                 "--out", str(out), "--journal", str(tmp_path / "journal.md"),
                 "--contention", "test-fixture"])
    rep = GateReport.model_validate_json(out.read_text())
    assert rep.status == "open"
    assert rep.code_gate.verdict == "pass", rep.code_gate.evidence
    assert rep.domain_gate.verdict in ("pass", "fail")
    assert "test-fixture" in rep.code_gate.evidence
    assert (tmp_path / "journal.md").read_text().strip()
