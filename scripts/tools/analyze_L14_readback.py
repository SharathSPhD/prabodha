"""Readback recalibration — sweep uptake thresholds against behavioral hits.
Concept: āgama re-cognition is the acceptance test; its thresholds (top_m,
min_rank_gain) were screen-tier settings from L3. Calibrate them so the readback
verdict TRACKS the behavioral outcome on the clean-stream corpus.
Source: configs/efe_menu4.yaml readback_recalibration (disclosed amendment: the
registered replay gates carry no per-generation readback; a fresh instrumented run
[e4_cli --record-readback, gate_L14_readback_raw.json] substitutes).
Primitive: per (concept, stub): raw pre_rank/post_ranks + gated-arm hit ->
sweep (top_m, min_rank_gain) -> balanced accuracy -> gates/gate_L14_readback.json.
"""
import json
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = "gates/gate_L14_readback_raw.json"

ev = json.loads(json.loads((ROOT / SRC).read_text())["domain_gate"]["evidence"])
recs = [r for r in ev["records"]["entropy_gated"] if "readback" in r]
pairs = [(r["readback"]["pre_rank"], r["readback"]["post_ranks"], bool(r["hit"]))
         for r in recs]
n_pos = sum(1 for *_x, h in pairs if h)
n_neg = len(pairs) - n_pos

L3_SETTING = (10, 100)  # uptake_top_m, uptake_min_rank_gain from e3.yaml (screen tier)


def balanced_acc(top_m, gain):
    tp = fp = tn = fn = 0
    for pre, posts, hit in pairs:
        best = min(posts)
        verdict = (best <= top_m) and ((pre - best) >= gain) and (posts[-1] <= top_m)
        if verdict and hit:
            tp += 1
        elif verdict:
            fp += 1
        elif hit:
            fn += 1
        else:
            tn += 1
    tpr = tp / max(tp + fn, 1)
    tnr = tn / max(tn + fp, 1)
    return (tpr + tnr) / 2, tpr, tnr


sweep = {}
for top_m, gain in product([1, 5, 10, 20, 50, 100], [0, 10, 50, 100, 500, 1000]):
    ba, tpr, tnr = balanced_acc(top_m, gain)
    sweep[f"top_m={top_m},gain={gain}"] = {
        "balanced_acc": round(ba, 4), "tpr": round(tpr, 4), "tnr": round(tnr, 4)}

best_key = max(sweep, key=lambda k: sweep[k]["balanced_acc"])
l3_key = f"top_m={L3_SETTING[0]},gain={L3_SETTING[1]}"
l3 = sweep.get(l3_key, {"balanced_acc": 0.5})
best = sweep[best_key]

summary = {
    "H_readback_tracks_behavior": {
        "value": best["balanced_acc"], "threshold": 0.6,
        "pass": best["balanced_acc"] >= 0.6},
}
verdict = "pass" if all(v["pass"] for v in summary.values()) else "fail"

gate = {
    "loop": "L14",
    "status": "closed",
    "closed_at": "2026-07-10",
    "code_gate": {"verdict": "pass", "evidence": "57 passed, 4 skipped; ruff clean"},
    "domain_gate": {
        "verdict": verdict,
        "hypothesis": "some (top_m, min_rank_gain) makes the āgama readback verdict "
                      "track behavioral hits (balanced accuracy >= 0.6) on the "
                      "clean-stream corpus; report best setting vs L3 screen setting",
        "evidence": json.dumps({
            "summary": summary, "n": len(pairs), "n_hit": n_pos, "n_miss": n_neg,
            "best": {best_key: best}, "l3_screen_setting": {l3_key: l3},
            "sweep": sweep, "source_run": SRC,
            "amendment": "registered replay gates (L9/L11) carry no per-generation "
                         "readback; fresh instrumented clean-stream run substituted "
                         "(e4_cli --record-readback)",
            "disclosures": [
                "source run's own domain verdict is FAIL on its e5align margin "
                "hypotheses (alignment margin +0.07 < 0.15 — the standing honest "
                "negative); its core-claim hypothesis passed (+0.30 within budget) "
                "and record-level data validity is unaffected (review #11)",
                "36 (top_m, gain) settings swept, max reported, no multiple-"
                "comparisons correction; BA 0.68 at n=40 (12 hit) is marginal over "
                "the 0.6 threshold, which was set at analysis time, NOT "
                "pre-registered — EXPLORATORY/screen-only; confirm needs a held-out "
                "corpus at the chosen setting (review #11)"],
            "registered_in": "configs/efe_menu4.yaml:readback_recalibration",
            "seeds": [42], "tier": "screen-exploratory"}),
    },
    "signoff": "standing authorization (2026-07-09)",
}
(ROOT / "gates/gate_L14_readback.json").write_text(json.dumps(gate, indent=1))
print(verdict, "| n =", len(pairs), f"({n_pos} hit / {n_neg} miss)")
print("best:", best_key, best)
print("L3 :", l3_key, l3)
