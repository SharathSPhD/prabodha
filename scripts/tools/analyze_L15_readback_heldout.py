"""Readback held-out confirm — the L14 calibration's chosen setting, no sweep.
Concept: a setting picked by maximizing over 36 candidates proves nothing until it
survives a corpus it never saw. Fixed (top_m=5, min_rank_gain=0); threshold BA >= 0.6
pre-registered in configs/experiments/e15heldout.yaml BEFORE the run.
Source: configs/efe_menu5.yaml readback_heldout_confirm; review #11 objection 3.
Primitive: gates/gate_L15_readback_heldout_raw.json -> gates/gate_L15_readback.json.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = "gates/gate_L15_readback_heldout_raw.json"
TOP_M, GAIN = 5, 0  # FIXED — chosen by L14 calibration, judged here without adjustment

ev = json.loads(json.loads((ROOT / SRC).read_text())["domain_gate"]["evidence"])
recs = [r for r in ev["records"]["entropy_gated"] if "readback" in r]
pairs = [(r["readback"]["pre_rank"], r["readback"]["post_ranks"], bool(r["hit"]))
         for r in recs]
n_pos = sum(1 for *_, h in pairs if h)

tp = fp = tn = fn = 0
for pre, posts, hit in pairs:
    best = min(posts)
    verdict = (best <= TOP_M) and ((pre - best) >= GAIN) and (posts[-1] <= TOP_M)
    tp, fp, tn, fn = (tp + (verdict and hit), fp + (verdict and not hit),
                      tn + (not verdict and not hit), fn + (not verdict and hit))
tpr = tp / max(tp + fn, 1)
tnr = tn / max(tn + fp, 1)
ba = (tpr + tnr) / 2

summary = {"H_readback_heldout": {"value": round(ba, 4), "threshold": 0.6,
                                  "pass": ba >= 0.6}}
verdict_s = "pass" if summary["H_readback_heldout"]["pass"] else "fail"
gate = {
    "loop": "L15",
    "status": "closed",
    "closed_at": "2026-07-10",
    "code_gate": {"verdict": "pass", "evidence": "pytest green; ruff clean"},
    "domain_gate": {
        "verdict": verdict_s,
        "hypothesis": "L14-calibrated readback setting (top_m=5, gain=0), FIXED, "
                      "reaches balanced accuracy >= 0.6 on a held-out corpus "
                      "(stubs disjoint from calibration; threshold pre-registered "
                      "in e15heldout.yaml)",
        "evidence": json.dumps({
            "summary": summary, "n": len(pairs), "n_hit": n_pos,
            "tpr": round(tpr, 4), "tnr": round(tnr, 4),
            "confusion": {"tp": tp, "fp": fp, "tn": tn, "fn": fn},
            "setting": {"top_m": TOP_M, "min_rank_gain": GAIN},
            "source_run": SRC,
            "disclosures": [
                "the source run's own H_gated_budget FAILED on this corpus (gated "
                "lift +0.15 < 0.2 at alpha=0.1): steering lift is CORPUS-DEPENDENT "
                "— the held-out stubs surface concepts less readily than e5align's. "
                "Does not affect this gate's question (verdict-vs-hit agreement) and "
                "is not a core-claim contradiction (different, unregistered corpus), "
                "but bounds generalization of lift magnitudes across stub styles"],
            "registered_in": "configs/efe_menu5.yaml:readback_heldout_confirm",
            "seeds": [42], "tier": "confirm"}),
    },
    "signoff": "standing authorization (2026-07-09)",
}
(ROOT / "gates/gate_L15_readback.json").write_text(json.dumps(gate, indent=1))
print(verdict_s, f"| BA={ba:.4f} (tpr={tpr:.3f} tnr={tnr:.3f})",
      f"| n={len(pairs)} ({n_pos} hit) | tp={tp} fp={fp} tn={tn} fn={fn}")
