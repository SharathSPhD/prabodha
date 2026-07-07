"""Unit tests for E1 evaluators (CPU, deterministic, no network).
Pure-numpy metric tests need no torch; the end-to-end pipeline test is marked smoke
(tiny random decoder -> jlens fit -> run_e1 -> e1_cli GateReport validation).
"""
from pathlib import Path

import numpy as np
import pytest

from prabodha.lens.e1_metrics import (
    best_band_partition,
    cka_matrix,
    linear_cka,
    spearman_rho,
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
    assert set(results["H_report"]["evidence"]["per_layer_rho"]) == set(adapter.source_layers)
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
