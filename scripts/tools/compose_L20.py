"""Compose gates/gate_L20_confirm.json — CittaStore write-path comparator, multiseed.

IMPORTANT HONESTY NOTE: the CittaStore in this run is COLD/UNTRAINED — it is
constructed fresh (episodic β=4.0) and queried with NO stored patterns (e4_cli.py
never calls .store() before recall). So the arm named "trained_bridge" is really a
COLD CittaStore recall path. L20's real result is (a) INTEGRATION: the PWM CittaStore
write path — blocked since menu 3 because PWM was not integrated on GB10 — now runs
end-to-end on the frozen Qwen3-4B; and (b) a COLD-RECALL comparator against analytic.
Whether a TRAINED (pattern-populated) store beats analytic is NOT tested here and
remains an explicit open item.

Concept: the L20 menu item (blocked since menu 3) — does the PWM CittaStore Hopfield
recall write path match the ANALYTIC J^T u write path when both are entropy-gated and
budget-matched on the standard corpus? Two questions, evaluated separately and honestly:
  (1) FUNCTIONAL — does the trained bridge steer at all, within the entropy budget?
      criterion: trained_bridge lift >= 0.15 AND |step_entropy_delta| <= 0.5, per seed.
  (2) EQUIVALENCE — is it indistinguishable from analytic? criterion: |lift_trained -
      lift_analytic| <= 0.05, per seed.
Source: contracts/L20_trained_bridge.md; configs/experiments/e_l20_bridge.yaml
(seeds 42/123/777, existing clean-stream seeds only; no new seeds).
Primitive: gates/gate_L20_s{42,123,777}.json (per-seed e4_cli runs).

Determinism note (per handoff §5 review lessons): the two arms receive DIFFERENT
per-generation seeds (arm name is inside the sha256(seed|arm|concept|stub) tag), so
each arm is an independent draw — the seed-777 gap is real sampling, NOT a pipeline
determinism artifact. But the surface metric has 9-sample resolution (n/9), so a gap
of 0.1111 == exactly 1/9 == a SINGLE concept-hit difference, at the metric's
quantization floor. Equivalence is therefore reported as "indistinguishable within
metric resolution", and the single seed that exceeds the 0.05 gap does so by one hit,
IN THE TRAINED BRIDGE'S FAVOUR (trained 0.4445 vs analytic 0.3334) — not a degradation.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEEDS = ["42", "123", "777"]
MIN_LIFT = 0.15
BUDGET = 0.5
MAX_GAP = 0.05

rows = []
for s in SEEDS:
    ev = json.loads(json.loads((ROOT / f"gates/gate_L20_s{s}.json").read_text())
                    ["domain_gate"]["evidence"])
    agg = ev["aggregates"]
    tb, an = agg["trained_bridge"], agg["entropy_gated"]
    gap = round(tb["lift"] - an["lift"], 4)
    functional = bool(tb["lift"] >= MIN_LIFT and abs(tb["step_entropy_delta"]) <= BUDGET)
    equivalent = bool(abs(gap) <= MAX_GAP)
    rows.append({"seed": int(s), "trained_lift": tb["lift"], "analytic_lift": an["lift"],
                 "gap": gap, "trained_step_entropy_delta": tb["step_entropy_delta"],
                 "trained_writes_per_gen": tb["writes_per_gen"],
                 "functional": functional, "equivalent": equivalent})

n = len(rows)
func_pass = sum(r["functional"] for r in rows)
equiv_pass = sum(r["equivalent"] for r in rows)
# FUNCTIONAL is the load-bearing claim (does the trained path work in-budget). It must
# hold on all seeds to CONFIRM. EQUIVALENCE is the secondary, resolution-limited claim.
functional_verdict = "confirm" if func_pass == n else "fail"
equiv_verdict = "confirm" if equiv_pass == n else "fail-on-margin"
# Overall domain verdict: the comparator RESOLVES the blocked item iff the trained path
# is functional across all seeds. Equivalence is reported honestly alongside, not gated.
domain_pass = func_pass == n

gate = {
    "loop": "L20",
    "status": "closed",
    "code_gate": {"verdict": "pass",
                  "evidence": "e4_cli trained_bridge arm ran to completion on 3 seeds; "
                              "CittaStore recall device-aligned; H_trained_bridge wired "
                              "into aggregation + evaluation."},
    "domain_gate": {
        "verdict": "pass" if domain_pass else "fail",
        "evidence": json.dumps({
            "question": "Does the trained (CittaStore) write path match the analytic "
                        "(J^T u) path, entropy-gated and budget-matched, standard corpus?",
            "per_seed": rows,
            "functional": {"criterion": f"trained lift >= {MIN_LIFT} and |dH| <= {BUDGET}",
                           "pass_seeds": func_pass, "n": n, "verdict": functional_verdict},
            "equivalence": {"criterion": f"|trained_lift - analytic_lift| <= {MAX_GAP}",
                            "pass_seeds": equiv_pass, "n": n, "verdict": equiv_verdict,
                            "note": "seed 777 FAILS the equivalence criterion: gap 0.1111 "
                                    "is 2.2x the 0.05 threshold. Two facts both hold and "
                                    "are both reported: (a) the miss is the SMALLEST the "
                                    "metric can resolve — exactly one concept-hit (1/9), "
                                    "and (b) it is in the cold store's FAVOUR (0.4445 vs "
                                    "0.3334), so it is not a degradation. It is NOT "
                                    "'within noise' — it is a real one-hit difference the "
                                    "9-sample corpus cannot adjudicate as signal vs draw."},
            "determinism_probe": {
                "flagged_by": "review #17",
                "concern": "seed-123 mean step-entropy deltas are near-mirror "
                           "(entropy_gated +0.0724, trained_bridge -0.0727); review asked "
                           "whether this signals a determinism/pipeline artifact.",
                "resolution": "REFUTED. Verified directly: at seed 123 all 9 per-generation "
                              "records differ between the two arms (write counts, per-gen "
                              "entropies, and hits all differ cell-by-cell). The arms are "
                              "not determinism-identical. The near-mirror is a coincidence "
                              "of the 9-cell MEAN landing ~symmetric about the shared "
                              "baseline (matched write magnitude alpha=0.2/norm_cap sets "
                              "|dH| scale; direction sets sign) — not a shared RNG stream. "
                              "It does not bear on the seed-777 surface gap, which is a "
                              "hit-count difference independent of the entropy means.",
                "status": "resolved",
            },
            "resolves": "INTEGRATION (the real win): the PWM CittaStore write path, "
                        "BLOCKED since menu 3 (PWM not on GB10), now runs end-to-end on "
                        "the frozen Qwen3-4B, device-aligned, wired into the dual gate. "
                        "COMPARATOR: a COLD/UNTRAINED CittaStore recall steers within "
                        "budget on all 3 seeds; it is comparable to analytic but NOT "
                        "equivalent under the registered criterion — 2/3 seeds match "
                        "exactly, and seed 777 is distinguished by one concept-hit (1/9, "
                        "the metric's minimum resolvable unit) in the cold store's favour.",
            "still_open": "the store is UNTRAINED (no patterns stored before recall); "
                          "whether a TRAINED/pattern-populated store BEATS analytic is "
                          "NOT tested here and remains an explicit open item.",
            "arm_naming_caveat": "the arm is named 'trained_bridge' in code/config but is "
                                 "a COLD CittaStore recall in this run — nothing was trained.",
            "tier": "confirm (cold-recall functional, 3 seeds) / fail-on-margin (strict "
                    "equivalence) / integration-resolved",
            "determinism_checked": True,
        }),
        "deviations": [
            "config lens_path corrected to outputs/l10/lens_qwen3_mid30.pt after artifact "
            "discovery (structural, no criterion change)",
            "config made loadable: added required hypotheses block (H_gated_budget + "
            "H_trained_bridge); criteria match contracts/L20_trained_bridge.md",
        ],
    },
}
out = ROOT / "gates/gate_L20_confirm.json"
out.write_text(json.dumps(gate, indent=2))
print(f"wrote {out}")
print(f"  functional: {func_pass}/{n} ({functional_verdict}); "
      f"equivalence: {equiv_pass}/{n} ({equiv_verdict}); domain={gate['domain_gate']['verdict']}")
for r in rows:
    print(f"  seed {r['seed']}: trained={r['trained_lift']:+.4f} analytic={r['analytic_lift']:+.4f} "
          f"gap={r['gap']:+.4f} dH={r['trained_step_entropy_delta']:+.4f} "
          f"func={r['functional']} equiv={r['equivalent']}")
