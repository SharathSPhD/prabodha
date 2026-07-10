"""Compose gates/gate_L17_xdose.json — dose response across configs + a stale-gate find.
Concept: review #13 asked whether nemotron's active-range dose response is config-
robust. It is (narrowly: the configs turn out to differ only in arm set) — and the
comparison surfaced that gate_L8_dose's LEVELS are pre-stream-fix era and inflated
~0.1 vs clean-stream re-measurement at matched alpha and content.
Source: configs/efe_menu7.yaml unified_dose_crossconfig (success: >= 1/2 adjacent
pairs rising > 0.05 on the e8dose config too).
Primitive: gates/gate_L17_xdose_s42_a{0.005,0.01,0.02}.json + s123_a0.01 ->
gate_L17_xdose.json (+ ledger divergence note for the L8 staleness).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALPHAS = ["0.005", "0.01", "0.02"]

grid = {}
for a in ALPHAS:
    ev = json.loads(json.loads(
        (ROOT / f"gates/gate_L17_xdose_s42_a{a}.json").read_text())
        ["domain_gate"]["evidence"])
    g = ev["aggregates"]
    grid[a] = {"gated_lift": g["entropy_gated"]["lift"],
               "gated_dH": g["entropy_gated"]["step_entropy_delta"],
               "continuous_lift": g["continuous"]["lift"]}
rep = json.loads(json.loads(
    (ROOT / "gates/gate_L17_xdose_s123_a0.01.json").read_text())
    ["domain_gate"]["evidence"])["aggregates"]["entropy_gated"]

lifts = [grid[a]["gated_lift"] for a in ALPHAS]
rising = sum(1 for i in range(2) if lifts[i + 1] - lifts[i] > 0.05)
within = all(abs(grid[a]["gated_dH"]) <= 0.5 for a in ALPHAS)
summary = {
    "H_dose_config_robust": {"value": float(rising), "threshold": 1.0,
                             "pass": rising >= 1},
    "H_budget_all_points": {"value": 1.0 if within else 0.0, "threshold": 1.0,
                            "pass": within},
}
verdict = "pass" if all(v["pass"] for v in summary.values()) else "fail"

gate = {
    "loop": "L17",
    "status": "closed",
    "closed_at": "2026-07-10",
    "code_gate": {"verdict": "pass", "evidence": "pytest green; ruff clean"},
    "domain_gate": {
        "verdict": verdict,
        "hypothesis": "nemotron's active-range dose response holds on the e8dose "
                      "config (>= 1/2 adjacent pairs rising > 0.05 at alpha "
                      "{0.005, 0.01, 0.02}), within budget, with a second-seed "
                      "replication at the middle point",
        "evidence": json.dumps({
            "summary": summary, "grid": grid,
            "seed123_replication_at_0.01": {"gated_lift": rep["lift"],
                                            "gated_dH": rep["step_entropy_delta"]},
            "disclosures": [
                "SCOPE NARROWER THAN INTENDED: e8dose and e5align share stubs, "
                "concepts, and decoding — they differ only in arm set (continuous "
                "included here). This is arm-set robustness (gated-arm numbers "
                "unchanged when the continuous arm runs alongside), not full "
                "config robustness",
                "STALE-GATE FINDING (unregistered, follows from matched content): "
                "gate_L8_dose's levels (e.g. gated 0.375 at alpha=0.02) are "
                "PRE-stream-fix era (L8 predates the L9 per-generation reseeding "
                "fix) and run ~0.1 above clean-stream re-measurement at matched "
                "alpha and content (0.28 here and in L16-fine). L8's ORDERING "
                "conclusions stand; its LEVELS are not canonical. Ledgered as a "
                "divergence note; figures/paper citing L8 levels now carry the "
                "era caveat",
                "single seed for the grid; one replication seed at one point "
                "(0.33 vs 0.28 — consistent); actual spend 0.35h vs 0.45h "
                "registered"],
            "registered_in": "configs/efe_menu7.yaml:unified_dose_crossconfig",
            "seeds": [42, 123], "tier": "screen"}),
    },
    "signoff": "standing authorization (2026-07-09)",
}
(ROOT / "gates/gate_L17_xdose.json").write_text(json.dumps(gate, indent=1))
print(verdict, "| e8dose gated:", dict(zip(ALPHAS, lifts)),
      f"| rising: {rising}/2 | s123@0.01: {rep['lift']}")
