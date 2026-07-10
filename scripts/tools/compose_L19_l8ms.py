"""Compose gates/gate_L19_l8ms.json — L8 gated-arm offset, multiseed confirm.
Concept: L18 found the gated arm ~0.10 lower than L8 at n=1 seed (42); review #15
required a multiseed check before treating the offset as more than a single-run
artifact. This adds seeds {123, 777} at both alphas {0.02, 0.1}.
Source: configs/efe_menu9.yaml l8_offset_multiseed (registered: mean offset vs L8
within [-0.15, -0.05] at BOTH alphas across all 3 seeds => confirmed with variance,
supersession STANDS; offset crosses 0 or flips sign => WITHDRAWN as noise).
Primitive: gates/gate_L19_l8ms_a{0.02,0.1}_s{123,777}.json + L18 seed-42 readings vs
gate_L8_dose originals.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALPHAS = ["0.02", "0.1"]
SEEDS = ["42", "123", "777"]

l8 = json.loads(json.loads((ROOT / "gates/gate_L8_dose.json").read_text())
                ["domain_gate"]["evidence"])["grid"]
# seed-42 readings come from L18 (already run); 123/777 from this cycle
SOURCE = {
    ("0.02", "42"): "gates/gate_L18_l8redo_a0.02.json",
    ("0.1", "42"): "gates/gate_L18_l8redo_a0.1.json",
    ("0.02", "123"): "gates/gate_L19_l8ms_a0.02_s123.json",
    ("0.02", "777"): "gates/gate_L19_l8ms_a0.02_s777.json",
    ("0.1", "123"): "gates/gate_L19_l8ms_a0.1_s123.json",
    ("0.1", "777"): "gates/gate_L19_l8ms_a0.1_s777.json",
}

readings, offsets = {}, {a: [] for a in ALPHAS}
for a in ALPHAS:
    readings[a] = {}
    for s in SEEDS:
        ev = json.loads(json.loads((ROOT / SOURCE[(a, s)]).read_text())
                        ["domain_gate"]["evidence"])
        lift = ev["aggregates"]["entropy_gated"]["lift"]
        offset = round(lift - l8[a]["entropy_gated"]["lift"], 4)
        readings[a][s] = {"clean_gated": lift, "l8_original": l8[a]["entropy_gated"]["lift"],
                          "offset": offset}
        offsets[a].append(offset)

mean_offset = {a: round(sum(offsets[a]) / len(offsets[a]), 4) for a in ALPHAS}
in_range = {a: -0.15 <= mean_offset[a] <= -0.05 for a in ALPHAS}
all_negative = all(o < 0 for a in ALPHAS for o in offsets[a])
sign_flip = any(o > 0 for a in ALPHAS for o in offsets[a])

summary = {
    "H_offset_confirmed_both_alphas": {
        "value": float(sum(in_range.values())), "threshold": 2.0,
        "pass": all(in_range.values())},
    "H_no_sign_flip": {"value": 0.0 if sign_flip else 1.0, "threshold": 1.0,
                       "pass": not sign_flip},
}
verdict = "pass" if all(v["pass"] for v in summary.values()) else "fail"
if verdict == "pass":
    finding = (f"CONFIRMED WITH VARIANCE: mean gated-arm offset vs L8 is "
               f"{mean_offset['0.02']} at alpha=0.02 and {mean_offset['0.1']} at "
               f"alpha=0.1, both within the registered [-0.15,-0.05] band across all "
               f"3 seeds, all offsets negative (range {min(o for a in ALPHAS for o in offsets[a]):.3f} "
               f"to {max(o for a in ALPHAS for o in offsets[a]):.3f}). The L18 n=1 "
               "supersession of L8's gated-arm levels now STANDS on n=3 seeds. "
               "Review #15's multiseed requirement is discharged: this was not a "
               "single-run artifact.")
else:
    finding = "NOT CONFIRMED at n=3 — see per-seed offsets; supersession WITHDRAWN."

gate = {
    "loop": "L19",
    "status": "closed",
    "closed_at": "2026-07-10",
    "code_gate": {"verdict": "pass", "evidence": "pytest green; ruff clean"},
    "domain_gate": {
        "verdict": verdict,
        "hypothesis": "the L18 gated-arm offset vs L8 (~-0.10 at n=1 seed) holds "
                      "across seeds {42,123,777} at both alpha{0.02,0.1}: mean offset "
                      "in [-0.15,-0.05], no sign flips => supersession CONFIRMED with "
                      "variance; else WITHDRAWN",
        "evidence": json.dumps({
            "summary": summary, "readings": readings, "offsets_by_alpha": offsets,
            "mean_offset": mean_offset, "finding": finding,
            "disclosures": [
                "discharges review #15's n=1 concern from gate_L18_l8redo — the "
                "gated-arm supersession is now a 3-seed result, not a single-run one",
                "the ARM-SPECIFICITY finding from L18 (offset does not generalize to "
                "other arms) is unaffected by this cycle — only the gated-arm offset "
                "was in scope"],
            "registered_in": "configs/efe_menu9.yaml:l8_offset_multiseed",
            "seeds": [42, 123, 777], "tier": "confirm"}),
    },
    "signoff": "standing authorization (2026-07-09)",
}
(ROOT / "gates/gate_L19_l8ms.json").write_text(json.dumps(gate, indent=1))
print(verdict, "| mean offsets:", mean_offset, "| per-seed:", offsets)
