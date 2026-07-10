"""Compose gates/gate_L16_corpus.json — corpus robustness of the core claim.
Concept: L15 disclosed lift is corpus-dependent; this cycle bounds it. Three
non-registered corpora: e16corpus_a (narrative-past), e16corpus_b (descriptive-scene),
and the L15 held-out reading (replay).
Source: configs/efe_menu6.yaml corpus_robustness (registered success: gated lift >= 0.2
within |dH| <= 0.5 on >= 2 of 3 non-registered corpora).
Secondary (exploratory, no registered criterion): pooled readback verdict-vs-hit
balanced accuracy at the FIXED setting (top_m=5, gain=0) across all instrumented runs
(L15 heldout + both L16 corpora) — grows n toward the n>=100 power debt.
Primitive: gate JSONs -> gates/gate_L16_corpus.json.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORPORA = {
    "narrative_past": "gates/gate_L16_corpus_a.json",
    "descriptive_scene": "gates/gate_L16_corpus_b.json",
    "l15_heldout_replay": "gates/gate_L15_readback_heldout_raw.json",
}
TOP_M, GAIN = 5, 0

per_corpus, pooled = {}, []
for name, path in CORPORA.items():
    ev = json.loads(json.loads((ROOT / path).read_text())["domain_gate"]["evidence"])
    g = ev["aggregates"]["entropy_gated"]
    per_corpus[name] = {"gated_lift": g["lift"], "gated_dH": g["step_entropy_delta"],
                        "prefill_lift": ev["aggregates"]["prefill_only"]["lift"],
                        "source": path}
    pooled += [(r["readback"]["pre_rank"], r["readback"]["post_ranks"], bool(r["hit"]))
               for r in ev["records"]["entropy_gated"] if "readback" in r]

ok = [n for n, v in per_corpus.items()
      if v["gated_lift"] >= 0.2 and abs(v["gated_dH"]) <= 0.5]
summary = {"H_corpus_robustness": {"value": float(len(ok)), "threshold": 2.0,
                                   "pass": len(ok) >= 2}}
verdict = "pass" if summary["H_corpus_robustness"]["pass"] else "fail"

tp = fp = tn = fn = 0
for pre, posts, hit in pooled:
    best = min(posts)
    v = (best <= TOP_M) and ((pre - best) >= GAIN) and (posts[-1] <= TOP_M)
    tp, fp, tn, fn = (tp + (v and hit), fp + (v and not hit),
                      tn + (not v and not hit), fn + (not v and hit))
tpr, tnr = tp / max(tp + fn, 1), tn / max(tn + fp, 1)

gate = {
    "loop": "L16",
    "status": "closed",
    "closed_at": "2026-07-10",
    "code_gate": {"verdict": "pass", "evidence": "pytest green; ruff clean"},
    "domain_gate": {
        "verdict": verdict,
        "hypothesis": "core-claim gated lift (nemotron, e5align settings, alpha=0.1) "
                      "reaches >= 0.2 within budget on >= 2 of 3 non-registered stub "
                      "corpora (two pre-registered styles + the L15 held-out replay)",
        "evidence": json.dumps({
            "summary": summary, "per_corpus": per_corpus, "passing": ok,
            "readback_pooled_exploratory": {
                "note": "NO registered criterion — exploratory n-growth toward the "
                        "n>=100 readback power debt; fixed setting (top_m=5, gain=0)",
                "n": len(pooled), "n_hit": sum(1 for *_, h in pooled if h),
                "balanced_acc": round((tpr + tnr) / 2, 4),
                "tpr": round(tpr, 4), "tnr": round(tnr, 4),
                "confusion": {"tp": tp, "fp": fp, "tn": tn, "fn": fn}},
            "registered_in": "configs/efe_menu6.yaml:corpus_robustness",
            "seeds": [42], "tier": "screen"}),
    },
    "signoff": "standing authorization (2026-07-09)",
}
(ROOT / "gates/gate_L16_corpus.json").write_text(json.dumps(gate, indent=1))
print(verdict, "| passing:", ok)
for n, v in per_corpus.items():
    print(f"  {n}: gated {v['gated_lift']:+.3f} dH {v['gated_dH']:+.2f}")
print(f"  pooled readback (exploratory): n={len(pooled)} "
      f"BA={(tpr + tnr) / 2:.4f} tpr={tpr:.3f} tnr={tnr:.3f}")
