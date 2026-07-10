"""Unit tests for the L5 EFE port (CPU, stdlib+yaml only)."""
from pathlib import Path

import pytest

from prabodha.efe.agent import Candidate, EFESelector, Observation
from prabodha.efe.gate_to_obs import observation_from_gate
from prabodha.efe.ledger import EFELedger
from prabodha.efe.runner import build_from_configs, propose_next

ROOT = Path(__file__).resolve().parents[1]


def test_belief_update_moves_toward_observed_tier():
    s = EFESelector()
    c = Candidate(id="x", description="")
    prior = s.belief(c)
    post = s.update("x", Observation(primary_tier=3), prior=prior)
    assert post[3] > prior[3] and post[0] < prior[0]
    post2 = s.update("x", Observation(primary_tier=3))
    assert post2[3] > post[3]  # repeated high tiers concentrate belief


def test_observation_tier_bounds():
    with pytest.raises(ValueError):
        Observation(primary_tier=4)


def test_select_respects_budget_and_explore_confirm():
    s = EFESelector()
    fresh = Candidate(id="unknown", description="")          # high entropy -> explore
    known = Candidate(id="strong", description="", prior_value_hint=3)
    s.update("strong", Observation(primary_tier=3), prior=s.belief(known))
    props = {p.candidate.id: p for p in s.rank([fresh, known])}
    # high-belief candidate pulls pragmatic value; fresh one pulls epistemic smoke
    assert props["unknown"].action.name == "smoke"
    tight = s.select([fresh, known], budget_gpu_hours=0.1)
    assert tight.action.gpu_hours <= 0.1


def test_gate_discretisation_on_real_gates():
    # L4b passed both hypotheses (0.40/0.2, 0.20/0.15 -> min ratio 1.33) -> tier 2
    assert observation_from_gate(ROOT / "gates/gate_L4b.json").primary_tier == 2
    # L2 failed with near-misses (0.384/0.4 = 0.96 >= 0.8) -> tier 1
    assert observation_from_gate(ROOT / "gates/gate_L2.json").primary_tier == 1
    # L1 run-1 failed hard (all failing ratios < 0.8... H_bands passed though) -> 0 or 1
    t = observation_from_gate(ROOT / "gates/gate_L1_run1.json").primary_tier
    assert t in (0, 1)


def test_ledger_roundtrip_and_replay(tmp_path):
    led = EFELedger(tmp_path / "led.jsonl")
    s = EFESelector()
    c = Candidate(id="x", description="")
    post = s.update("x", Observation(primary_tier=2), prior=s.belief(c))
    led.log_observation("x", Observation(primary_tier=2), post)
    led.log_spend("x", 0.4)
    recs = led.records()
    assert [r["event"] for r in recs] == ["observe", "spend"]
    assert recs[1]["gpu_hours"] == 0.4


def test_menu_build_and_proposal(tmp_path):
    selector, candidates, budget, actions = build_from_configs(
        ROOT / "configs/efe_menu.yaml", root=ROOT)
    ids = {c.id for c in candidates}
    assert {"confirm_e4b", "alignment_sampling", "tau_sensitivity",
            "articulation_null", "dose_response"} <= ids
    assert budget == pytest.approx(2.0)
    # review #7 P0: every menu candidate carries its own registered composite cost
    assert set(actions) == ids
    assert actions["tau_sensitivity"].gpu_hours == pytest.approx(0.3)
    # confirm_e4b replayed gate_L4b (tier 2): belief should lean moderate/high
    b = selector.belief(next(c for c in candidates if c.id == "confirm_e4b"))
    assert b[2] + b[3] > 0.5
    led = EFELedger(tmp_path / "led.jsonl")
    prop = propose_next(ROOT / "configs/efe_menu.yaml", ledger=led, root=ROOT)
    assert prop.candidate.id in ids
    assert any(r["event"] == "propose" for r in led.records())


def test_actions_are_not_capped_by_each_other():
    """L3 registration-hygiene lesson, applied to the port: every default action must be
    admissible under the menu budget (2.0 GPU-h) except 'full' — which the selector must
    silently skip, not crash on."""
    s = EFESelector()
    c = Candidate(id="x", description="")
    p = s.select([c], budget_gpu_hours=2.0)
    assert p.action.gpu_hours <= 2.0


def test_run_observations_replay_into_beliefs(tmp_path):
    """Cycle-2 live bug: an observation sourced from a NEW gate (not in the menu's replay
    list) must update beliefs on rebuild — else the selector re-proposes completed work."""
    from prabodha.efe.agent import Observation
    led = EFELedger(tmp_path / "led.jsonl")
    _, _, _, _ = build_from_configs(ROOT / "configs/efe_menu.yaml", ledger=led, root=ROOT)
    p1 = propose_next(ROOT / "configs/efe_menu.yaml", ledger=led, root=ROOT)
    led.log_observation(p1.candidate.id, Observation(primary_tier=3),
                        [0.05, 0.1, 0.35, 0.5], source="gates/some_new_gate.json")
    led.log_spend(p1.candidate.id, 0.1)
    p2 = propose_next(ROOT / "configs/efe_menu.yaml", ledger=led, root=ROOT)
    assert not (p2.candidate.id == p1.candidate.id and abs(p2.efe - p1.efe) < 1e-9), \
        "completed run's observation was lost on rebuild"


def test_consumed_candidates_not_reproposed(tmp_path):
    from prabodha.efe.agent import Observation
    led = EFELedger(tmp_path / "led.jsonl")
    p1 = propose_next(ROOT / "configs/efe_menu.yaml", ledger=led, root=ROOT)
    led.log_observation(p1.candidate.id, Observation(primary_tier=3),
                        [0.05, 0.1, 0.35, 0.5], source="gates/run_gate.json")
    p2 = propose_next(ROOT / "configs/efe_menu.yaml", ledger=led, root=ROOT)
    assert p2.candidate.id != p1.candidate.id


def test_menu_budget_scoped_to_its_own_candidates(tmp_path):
    """Cycle-7 live bug: menu-2's budget was debited by menu-1 spends (global ledger)."""
    led = EFELedger(tmp_path / "led.jsonl")
    led.log_spend("some_menu1_candidate", 1.9)  # not in this menu
    _, _, budget, _ = build_from_configs(ROOT / "configs/efe_menu.yaml", ledger=led,
                                         root=ROOT)
    assert budget == pytest.approx(2.0)  # untouched by foreign spends
    led.log_spend("tau_sensitivity", 0.3)  # in this menu
    _, _, budget2, _ = build_from_configs(ROOT / "configs/efe_menu.yaml", ledger=led,
                                          root=ROOT)
    assert budget2 == pytest.approx(1.7)


def test_blocked_candidates_skipped_with_ledger_entry(tmp_path):
    led = EFELedger(tmp_path / "led.jsonl")
    p = propose_next(ROOT / "configs/efe_menu3.yaml", ledger=led, root=ROOT)
    assert p.candidate.id != "trained_bridge_arm"
    skips = [r for r in led.records() if r["event"] == "skip"]
    assert any(r["candidate"] == "trained_bridge_arm" and "blocked" in r["reason"]
               for r in skips)
    # skip is logged once, not every proposal
    propose_next(ROOT / "configs/efe_menu3.yaml", ledger=led, root=ROOT)
    assert sum(r["candidate"] == "trained_bridge_arm"
               for r in led.records() if r["event"] == "skip") == 1


def test_cycle_integrity_lint(tmp_path):
    from prabodha.config import load
    from prabodha.efe.lint import lint_cycles, log_divergence
    led = EFELedger(tmp_path / "led.jsonl")
    menu = load(ROOT / "configs/efe_menu3.yaml")
    menu_sources = {g for c in menu["candidates"] for g in c.get("replay", [])}
    p1 = propose_next(ROOT / "configs/efe_menu3.yaml", ledger=led, root=ROOT)
    from prabodha.efe.agent import Observation
    # legal: observe the proposed candidate
    led.log_observation(p1.candidate.id, Observation(primary_tier=2), [0.2] * 4,
                        source="gates/run1.json")
    assert lint_cycles(led.records(), menu_sources=menu_sources) == []
    # illegal: observe a different candidate with no divergence event
    led.log_observation("flash_multiseed", Observation(primary_tier=2), [0.2] * 4,
                        source="gates/run2.json")
    v = lint_cycles(led.records(), menu_sources=menu_sources)
    assert len(v) == 1 and "flash_multiseed" in v[0]
    # legal with an explicit ledgered divergence
    log_divergence(led, "gated_confirm_replication", "staleness: replay gates invalidated")
    led.log_observation("gated_confirm_replication", Observation(primary_tier=2),
                        [0.2] * 4, source="gates/run3.json")
    v2 = lint_cycles(led.records(), menu_sources=menu_sources)
    assert len(v2) == 1  # only the earlier violation remains


def test_cli_dispatch_help_and_unknown(capsys, monkeypatch):
    from prabodha import cli
    monkeypatch.setattr("sys.argv", ["prabodha", "--help"])
    try:
        cli.main()
    except SystemExit as e:
        assert e.code == 0
    assert "lens-fit" in capsys.readouterr().out
    monkeypatch.setattr("sys.argv", ["prabodha", "nope"])
    try:
        cli.main()
    except SystemExit as e:
        assert e.code == 2
