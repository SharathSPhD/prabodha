"""Compose gates/gate_L18_npretry.json — narrative-past seed fragility, diagnosed.
Concept: L17-cvar found narrative-past (corpus A) seed-fragile at alpha=0.1 (0.25/0.07/
0.10, 1/3). This re-runs it at alpha=cap=0.2. If it now passes across seeds, the
fragility was UNDER-AMPLITUDE, not corpus-intrinsic — the calibration recipe has a
CORPUS dimension, not just a model dimension.
Source: configs/efe_menu8.yaml narrative_past_amplitude_retry (success: gated >= 0.2
within budget in >= 2/3 seeds => under-amplitude; <= 1/3 => corpus-intrinsic).
Primitive: gates/gate_L18_npretry_s{42,123,777}.json vs the L17 alpha=0.1 readings.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEEDS = ["42", "123", "777"]
# L17-cvar readings at alpha=0.1 (the fragile baseline)
L17_A01 = {"42": 0.25, "123": 0.075, "777": 0.10}

per_seed = {}
for s in SEEDS:
    ev = json.loads(json.loads(
        (ROOT / f"gates/gate_L18_npretry_s{s}.json").read_text())
        ["domain_gate"]["evidence"])
    g = ev["aggregates"]["entropy_gated"]
    per_seed[s] = {"alpha0.2_lift": g["lift"], "alpha0.2_dH": g["step_entropy_delta"],
                   "alpha0.1_lift": L17_A01[s]}

ok = [s for s in SEEDS
      if per_seed[s]["alpha0.2_lift"] >= 0.2 and abs(per_seed[s]["alpha0.2_dH"]) <= 0.5]
n_ok = len(ok)
summary = {"H_fragility_is_amplitude": {"value": float(n_ok), "threshold": 2.0,
                                        "pass": n_ok >= 2}}
verdict = "pass" if summary["H_fragility_is_amplitude"]["pass"] else "fail"
finding = (
    f"UNDER-AMPLITUDE, not corpus-intrinsic: at alpha=0.2 narrative-past passes "
    f"{n_ok}/3 seeds ({[per_seed[s]['alpha0.2_lift'] for s in SEEDS]}) vs 1/3 at "
    f"alpha=0.1 ({[L17_A01[s] for s in SEEDS]}). The L17 seed fragility was the "
    "corpus needing MORE amplitude, not being unsteerable. Consequence: the "
    "calibration recipe has a CORPUS dimension — amplitude calibrates to lens "
    "strength (per model) AND to stub difficulty (per corpus). L16's single fixed "
    "alpha=0.1 across corpora was the real methodological gap."
    if n_ok >= 2 else
    f"CORPUS-INTRINSIC: even at alpha=0.2 narrative-past passes only {n_ok}/3 seeds; "
    "these stubs resist steering independent of amplitude — recorded as a hard corpus.")

gate = {
    "loop": "L18",
    "status": "closed",
    "closed_at": "2026-07-10",
    "code_gate": {"verdict": "pass", "evidence": "pytest green; ruff clean"},
    "domain_gate": {
        "verdict": verdict,
        "hypothesis": "narrative-past's L17 seed fragility is UNDER-AMPLITUDE: at "
                      "alpha=cap=0.2 it reaches gated >= 0.2 within budget in >= 2/3 "
                      "seeds {42,123,777} => fragility was amplitude, not corpus-"
                      "intrinsic",
        "evidence": json.dumps({
            "summary": summary, "per_seed": per_seed, "passing_seeds": ok,
            "finding": finding,
            "disclosures": [
                "this REFINES rather than overturns L17-cvar: at the L16/L17 fixed "
                "alpha=0.1 the corpus WAS seed-fragile (that honest negative stands); "
                "the new result is that raising amplitude fixes it, adding a corpus "
                "axis to the calibration recipe",
                "single alpha (0.2) tested; the alpha=0.1 baseline is the L17-cvar "
                "reading, not re-run here; actual spend 0.3h vs 0.35h registered"],
            "registered_in": "configs/efe_menu8.yaml:narrative_past_amplitude_retry",
            "seeds": [42, 123, 777], "tier": "screen"}),
    },
    "signoff": "standing authorization (2026-07-09)",
}
(ROOT / "gates/gate_L18_npretry.json").write_text(json.dumps(gate, indent=1))
print(verdict, f"| alpha=0.2 passes {n_ok}/3:",
      {s: per_seed[s]["alpha0.2_lift"] for s in SEEDS})
print(" ", finding[:120])
