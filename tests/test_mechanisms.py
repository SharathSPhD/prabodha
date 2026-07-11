"""Unit tests for the graded steering-mechanism library (no torch/prayoga)."""
from prabodha.steering import mechanisms as M


def test_registry_is_graded_and_tagged():
    assert set(M.REGISTRY) >= {"prompt_refusal_firm", "act_prefill_restore"}
    for m in M.REGISTRY.values():
        assert m.space in ("prompt", "activation")
        assert m.weights in ("both", "open")
        assert 1 <= m.tier <= 5
        assert m.summary


def test_prompt_harden_prepends_system_and_dedupes():
    msgs = [{"role": "system", "content": "old"}, {"role": "user", "content": "hi"}]
    out = M.prompt_harden(msgs, "firm")
    assert out[0]["role"] == "system"
    assert "Refuse" in out[0]["content"]
    assert sum(1 for m in out if m["role"] == "system") == 1  # old system dropped
    assert out[-1] == {"role": "user", "content": "hi"}


def test_recommend_closed_weights_is_prompt_only():
    recs = M.recommend(weights="closed")
    assert recs, "should offer prompt-space mechanisms for closed weights"
    assert all(m.weights == "both" for m in recs)
    assert all(m.space == "prompt" for m in recs)


def test_recommend_open_is_graded_superset_and_ordered():
    closed = {m.key for m in M.recommend(weights="closed")}
    open_ = M.recommend(weights="open")
    open_keys = {m.key for m in open_}
    assert closed <= open_keys
    assert any(m.space == "activation" for m in open_)
    tiers = [m.tier for m in open_]
    assert tiers == sorted(tiers), "menu must be graded gentle->aggressive"


def test_prompt_harden_levels_exist():
    for level in ("gentle", "firm", "constitutional"):
        assert level in M.REFUSAL_SYSTEM
        assert M.prompt_harden([{"role": "user", "content": "x"}], level)[0]["content"]
