"""Compose gates/gate_L17_cvar.json — corpus seed variance (the review #13 debt).
Concept: L16's corpus robustness rested on seed-42 singletons. This cycle reruns both
new corpora at seeds {123, 777}. Finding: corpus B (descriptive-scene) is seed-robust;
corpus A (narrative-past) is NOT — its seed-42 pass was a favorable draw. The
pre-registered branch: <= 2/4 => corpus claim stays screen, seed-sensitivity is the
result.
Source: configs/efe_menu7.yaml corpus_seed_variance (success: >= 3/4 seed-corpus cells
gated >= 0.2 within budget => screen -> confirm).
Primitive: gates/gate_L17_cvar_{a,b}_s{123,777}.json + L16 seed-42 replay ->
gate_L17_cvar.json.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# the four NEW cells (registered criterion is over these)
NEW = {
    "a_s123": "gates/gate_L17_cvar_a_s123.json",
    "a_s777": "gates/gate_L17_cvar_a_s777.json",
    "b_s123": "gates/gate_L17_cvar_b_s123.json",
    "b_s777": "gates/gate_L17_cvar_b_s777.json",
}
# seed-42 context (from L16, for the per-corpus picture)
SEED42 = {"a_s42": "gates/gate_L16_corpus_a.json",
          "b_s42": "gates/gate_L16_corpus_b.json"}


def gated(path):
    ev = json.loads(json.loads((ROOT / path).read_text())["domain_gate"]["evidence"])
    g = ev["aggregates"]["entropy_gated"]
    return {"gated_lift": g["lift"], "gated_dH": g["step_entropy_delta"]}


new = {k: gated(v) for k, v in NEW.items()}
s42 = {k: gated(v) for k, v in SEED42.items()}
cells_pass = {k: (v["gated_lift"] >= 0.2 and abs(v["gated_dH"]) <= 0.5)
              for k, v in new.items()}
n_pass = sum(cells_pass.values())

# per-corpus across all 3 seeds (incl. seed 42)
corpus_a = [s42["a_s42"]["gated_lift"], new["a_s123"]["gated_lift"],
            new["a_s777"]["gated_lift"]]
corpus_b = [s42["b_s42"]["gated_lift"], new["b_s123"]["gated_lift"],
            new["b_s777"]["gated_lift"]]

summary = {
    "H_corpus_seed_robust": {"value": float(n_pass), "threshold": 3.0,
                             "pass": n_pass >= 3},
}
verdict = "pass" if summary["H_corpus_seed_robust"]["pass"] else "fail"

gate = {
    "loop": "L17",
    "status": "closed",
    "closed_at": "2026-07-10",
    "code_gate": {"verdict": "pass", "evidence": "pytest green; ruff clean"},
    "domain_gate": {
        "verdict": verdict,
        "hypothesis": ">= 3/4 new seed-corpus cells (corpora A,B x seeds 123,777) "
                      "reach gated lift >= 0.2 within budget => L16 corpus robustness "
                      "graduates screen -> confirm; <= 2/4 => stays screen and seed "
                      "sensitivity is the result (pre-registered branch)",
        "evidence": json.dumps({
            "summary": summary, "new_cells": new, "cells_pass": cells_pass,
            "n_pass": n_pass,
            "per_corpus_across_seeds": {
                "narrative_past_A": {"seed42": corpus_a[0], "seed123": corpus_a[1],
                                     "seed777": corpus_a[2], "verdict": "SEED-SENSITIVE"},
                "descriptive_scene_B": {"seed42": corpus_b[0], "seed123": corpus_b[1],
                                        "seed777": corpus_b[2], "verdict": "seed-robust"}},
            "result": "NEGATIVE for graduation (2/4): corpus B (descriptive-scene) is "
                      "seed-robust (0.30/0.20/0.25, 3/3), but corpus A (narrative-past) "
                      "is NOT (0.25/0.07/0.10, 1/3) — its L16 seed-42 pass was a "
                      "favorable draw. This RETROACTIVELY QUALIFIES the L16 corpus "
                      "claim: 'lift generalizes across stub styles' holds for one of "
                      "two new styles across seeds; the other is seed-fragile. Exactly "
                      "the single-seed risk review #13 flagged.",
            "disclosures": [
                "actual spend 0.35h vs 0.4h registered",
                "the pre-registered <=2/4 branch fires: corpus robustness STAYS "
                "screen; seed-sensitivity of narrative-past stubs is now a recorded "
                "result, not a hidden variance"],
            "registered_in": "configs/efe_menu7.yaml:corpus_seed_variance",
            "seeds": [123, 777], "tier": "screen"}),
    },
    "signoff": "standing authorization (2026-07-09)",
}
(ROOT / "gates/gate_L17_cvar.json").write_text(json.dumps(gate, indent=1))
print(verdict, f"| new cells pass {n_pass}/4")
print("  corpus A (narrative-past):", corpus_a, "SEED-SENSITIVE" if sum(x >= 0.2 for x in corpus_a) < 2 else "ok")
print("  corpus B (descriptive):   ", corpus_b, "seed-robust" if sum(x >= 0.2 for x in corpus_b) >= 2 else "?")
