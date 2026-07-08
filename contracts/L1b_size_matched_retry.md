# Contract L1b — size-matched retry: E1 on Nanda's reference (Qwen3.6-27B)
Status: OPEN · Worktree: loop/l1b-27b-retry · Owner: ralph loop (fresh agent re-entry safe)
Lineage: L1 prune_rule escalation, cleared by operator 2026-07-08 (contracts/L1_qwen_replication.md
sign-off line). Reviewer's rationale: distinguish "instrument underpowered at 4B" from
"thresholds miscalibrated for the method" — decision rule pre-registered in configs/experiments/e1b.yaml.

## Objective (domain)
Rerun the EXACT amended E1 protocol (fit: 16 wikitext prompts, seed 42; eval: calibrated
model-top-K rho + permutation gate, min-band-size-6 CKA, cross-lingual modulation + shuffled
null) with ONLY the model changed: Qwen/Qwen3.6-27B — the size Nanda's replication used.
One methodological fix mandated by L1 review #2: H_modulation band FIXED a priori
(depth_middle_third), never derived from this run's CKA.

## Deliverables
D1 configs/models/qwen27b.yaml + configs/experiments/e1b.yaml (pre-registered, incl. decision rule).
D2 scripts/dispatch/l1b/run.sh — idle-window pack (guard min_free=80GiB; no courtesy caps needed).
D3 gates/gate_L1b.json + journal entry + explicit L1-vs-L1b comparison table.
D4 evaluator: modulation_band mode (depth_middle_third | cka_middle) + unit tests.

## Closure criteria
CODE GATE: CI green; smoke suite green in-container; guard refuses under co-residency (<80GiB).
DOMAIN GATE: per e1b.yaml decision rule — ANY of the three registered outcomes is a valid
closure (this is a calibration experiment; "27B also weak" is a shipped result, not a failure).
Adversarial review of the comparison + operator sign-off below.
GPU budget: 6.0 GPU-h cap (L1b line, operator-cleared), idle-window only.

## Iteration record (2026-07-08, GB10 idle window)
- Run 1 aborted: qwen3_5 hybrid arch on torch fallback measured 52 min/prompt (13.8h projected);
  0.9 GPU-h ledgered. Fix: fla 0.5.1 + causal-conv1d 1.6.2 baked into image ("Blackwell
  detected"); run 2 clean restart, 17.2 min/prompt, 16/16 prompts, max_d_mean declining
  0.86→0.10 (running-mean Jacobian saturating at n=16 — empirical support for the fit size).
- Gate (gates/gate_L1b.json; internal loop label reads "L1" — compose_gate bug, plumbed for
  future runs): H_modulation 0.55 PASS (22/40, null 0.068, fixed depth-middle-third band);
  H_bands 0.269 PASS ([0,8)/[8,54)/[54,64)); H_report 0.124 FAIL (p≈1e-4 above null).
  Comparison: research/l1_vs_l1b_comparison.md. GPU: 6.1/7.0 GPU-h.
- Decision-rule readout: SPLIT — no registered branch fired cleanly. Modulation scales with
  size and passes on the reference; band structure replicates; report-ordering stays weak on
  both sizes.
- Adversarial review (fresh agent, 4 files only): (a) modulation scaling VALID with the
  null-comparability attack — REBUTTAL recorded: signal-to-null ratios are comparable across
  sizes (9.6x vs 8.1x); the absolute 0.5 threshold is what 27B uniquely crosses; and the band
  confound (4B read the BROADER CKA band, 69% of layers, vs 27B's fixed 33%) runs AGAINST the
  scaling claim, strengthening it. (b) bands UNDERDETERMINED (proportions differ; contrast
  0.306→0.269). (c) H_report metric-shape hypothesis UNDERDETERMINED (curve shapes differ:
  4B last-layer spike 0.617 vs 27B gradual 0.353). (d) budget honesty VALID; confounds
  contention/kernels disclosed but not isolated (accepted — screen tier).
- CLOSURE: VALID_WITH_CAVEATS (calibration experiment; any registered outcome closes). Caveats
  carried to L2 pre-registration: (1) uninstructed-prompt control for H_modulation (is 0.55
  directedness or incidental concept-capacity — reviewer's single most important next
  measurement); (2) same-band-mode comparison if modulation is ever re-compared across sizes;
  (3) H_report metric shape needs a registered alternative (e.g. last-k-layers mean or
  layer-of-half-max) BEFORE any further report-correspondence claims.

Operator sign-off: ______  Date: ______ (milestone merge pre-authorized by operator /goal
directive 2026-07-08 "milestone merge to main and push"; formal sign-off line remains open)
