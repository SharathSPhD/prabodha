"""Compose gates/gate_L17_xdose.json — dose response across configs + a stale-gate find.
Concept: review #13 asked whether nemotron's active-range dose response is config-
robust. It is (narrowly: the configs turn out to differ only in arm set) — and the
comparison surfaced a PROVISIONAL sign that gate_L8_dose's LEVELS may be pre-stream-fix
inflated (~0.1 at the one matched alpha=0.02); flagged, not asserted (review #14).
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
                "CANDIDATE NAME OVERREACHES (review #14): registered as "
                "'unified_dose_crossconfig' but e8dose and e5align turn out to "
                "share stubs, concepts, and decoding — they differ ONLY in arm set "
                "(continuous included here). What is actually shown is ARM-SET "
                "robustness: the gated-arm dose numbers are unchanged when the "
                "continuous arm runs alongside. TRUE cross-config robustness "
                "(different stubs/decoding) is NOT tested and remains open",
                "L8 STALENESS is PROVISIONAL (review #14): the pre-stream-fix vs "
                "clean-stream level gap is observed at ONE matched alpha (0.02: L8 "
                "gated 0.375 vs 0.28 here and in L16-fine). L8 predates the L9 "
                "per-generation reseeding fix, so a gap is EXPECTED, but a single "
                "matched point cannot declare all L8 levels stale. Call: L8 "
                "ORDERING conclusions stand; its LEVELS are flagged PROVISIONAL "
                "pending a dedicated canonical re-measurement of L8's full grid "
                "(0.02/0.05/0.1) on fixed code — NOT asserted non-canonical. "
                "Ledgered as a divergence note; fig2/paper carry the provisional "
                "era caveat",
                "matched content = the entropy_gated arm at alpha=0.02, same stubs/"
                "concepts/decoding as L8; the differing arm set does not touch the "
                "gated-arm number being compared",
                "single seed for the grid; one replication seed at the middle "
                "point (seed123 gated 0.325 vs seed42 0.275 at alpha=0.01 — "
                "consistent); actual spend 0.35h vs 0.45h registered"],
            "registered_in": "configs/efe_menu7.yaml:unified_dose_crossconfig",
            "seeds": [42, 123], "tier": "screen"}),
    },
    "signoff": "standing authorization (2026-07-09)",
}
(ROOT / "gates/gate_L17_xdose.json").write_text(json.dumps(gate, indent=1))
print(verdict, "| e8dose gated:", dict(zip(ALPHAS, lifts)),
      f"| rising: {rising}/2 | s123@0.01: {rep['lift']}")
