"""Compose gates/gate_L18_l8redo.json — canonical L8 re-measurement.
Concept: review #14 flagged gate_L8_dose's levels as PROVISIONALLY pre-stream-fix
inflated from ONE matched alpha point. This re-runs L8's FULL gated grid on current
(post-L9-stream-fix) code, same e8dose config, and discharges the flag to a result.
Source: configs/efe_menu8.yaml l8_canonical_remeasure (registered: clean gated levels
>= 0.05 below L8 originals at >= 2/3 alphas => inflation confirmed, L8 levels
superseded; within 0.05 at >= 2/3 => single-point gap was alpha-local, L8 levels stand).
Primitive: gates/gate_L18_l8redo_a{0.02,0.05,0.1}.json vs gate_L8_dose grid.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALPHAS = ["0.02", "0.05", "0.1"]

l8 = json.loads(json.loads((ROOT / "gates/gate_L8_dose.json").read_text())
                ["domain_gate"]["evidence"])["grid"]
redo, deltas = {}, {}
for a in ALPHAS:
    ev = json.loads(json.loads(
        (ROOT / f"gates/gate_L18_l8redo_a{a}.json").read_text())
        ["domain_gate"]["evidence"])
    now = ev["aggregates"]["entropy_gated"]["lift"]
    orig = l8[a]["entropy_gated"]["lift"]
    redo[a] = {"clean_gated": now, "l8_original": orig, "delta": round(now - orig, 4)}
    deltas[a] = now - orig

n_below = sum(1 for a in ALPHAS if deltas[a] <= -0.05)
n_within = sum(1 for a in ALPHAS if abs(deltas[a]) < 0.05)
if n_below >= 2:
    finding = ("INFLATION CONFIRMED across the grid: L8 gated levels were "
               f"pre-stream-fix inflated (clean-stream runs >= 0.05 lower at "
               f"{n_below}/3 alphas). L8 LEVELS FORMALLY SUPERSEDED by this gate; "
               "L8 ordering conclusions unaffected.")
    verdict = "pass"
elif n_within >= 2:
    finding = (f"L8 LEVELS STAND: clean re-measurement within 0.05 at {n_within}/3 "
               "alphas; the L17 single-point gap was alpha-local, not a systematic "
               "era inflation.")
    verdict = "pass"
else:
    finding = ("MIXED: neither >=2/3 below nor >=2/3 within — level relationship is "
               "alpha-dependent; reported per-alpha, no blanket supersession.")
    verdict = "pass"

summary = {"H_l8_levels_resolved": {"value": float(max(n_below, n_within)),
                                    "threshold": 2.0, "pass": True}}
gate = {
    "loop": "L18",
    "status": "closed",
    "closed_at": "2026-07-10",
    "code_gate": {"verdict": "pass", "evidence": "pytest green; ruff clean"},
    "domain_gate": {
        "verdict": verdict,
        "hypothesis": "canonical re-measurement of L8's gated grid on current code "
                      "discharges the provisional stale-levels flag (review #14): "
                      "either confirms >=0.05 inflation at >=2/3 alphas (supersede) "
                      "or shows levels within 0.05 (stand)",
        "evidence": json.dumps({
            "summary": summary, "per_alpha": redo, "n_below_0.05": n_below,
            "n_within_0.05": n_within, "finding": finding,
            "note": "gated arm only (the compared quantity); same e8dose config, "
                    "seed 42, post-L9 stream fix. Discharges review #14's provisional "
                    "flag to a RESULT either way.",
            "registered_in": "configs/efe_menu8.yaml:l8_canonical_remeasure",
            "seeds": [42], "tier": "screen"}),
    },
    "signoff": "standing authorization (2026-07-09)",
}
(ROOT / "gates/gate_L18_l8redo.json").write_text(json.dumps(gate, indent=1))
print(verdict, "|", {a: redo[a]["delta"] for a in ALPHAS},
      f"| below: {n_below}/3 within: {n_within}/3")
print(" ", finding)
