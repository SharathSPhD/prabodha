# Contract L1 — E1: Qwen lens replication
Status: OPEN · Worktree: loop/l1-e1-qwen · Owner: ralph loop (fresh agent re-entry safe)

## Objective (domain)
Independently reproduce, on a GB10-sized Qwen3 model, the core J-lens findings that Nanda's
commentary already replicated on Qwen 3.6 27B: (a) verbal-report correspondence — lens token
ordering correlates with output ordering, rising toward late layers; (b) CKA layer-band structure
(sensory/workspace/motor); (c) directed modulation — instructed concepts appear in workspace band.
This validates our pipeline against known-good results BEFORE pointing it at PWM's stack (L2).

## Deliverables
D1 `src/prabodha/lens/` adapter fitting/applying vendor jlens from configs (no vendor edits — R7).
D2 configs/models/qwen3.yaml + configs/lens/fit_default.yaml + configs/experiments/e1.yaml
   (hypotheses, metrics, thresholds, seeds — pre-registered per R4).
D3 scripts/dispatch/l1/run.sh — GB10 job pack, guard-wrapped, checkpoint-resume, ≤2 GPU-h budget.
D4 tests: unit (config/adapter, CPU, no download) + smoke (tiny random decoder fit end-to-end, CPU).
D5 gates/gate_L1.json (dual verdict) + research/journal.md entry + slice-vis sample page.

## Closure criteria
CODE GATE: CI green; smoke fit runs end-to-end on CPU tiny model; job pack dry-runs (guard passes
in simulate mode); lint clean.
DOMAIN GATE (from e1.yaml, screen tier): report-ordering Spearman rho >= rho_min in late-layer third;
CKA band structure visually present AND band-contrast >= c_min; modulation hit-rate >= h_min over
n_prompts; deviations disclosed. Adversarial review (AGENTS.md point 5) + operator sign-off line below.
PRUNED closure permitted if lens fails on chosen Qwen size with documented diagnosis (then L1 retries
with Nanda's exact size/config before pruning the instrument itself).

## Iteration record (2026-07-07, GB10 session)
- Run 1 (pre-registered config): domain FAIL 1/3 — gates/gate_L1_run1.json. Diagnosis: union-top-K
  rho has a structural null floor ≈ -0.72 (verified synthetically); band partition degenerate;
  H_modulation inherited the bad band and counted English-only tokens.
- Adversarial review #1 (fresh agent, contract+gate only): H_report ARTIFACT-SUSPECT, H_bands
  PLAUSIBLE-unvalidated, H_modulation ARTIFACT-SUSPECT; five evidence demands.
- Amendments A1–A3 (disclosed in e1.yaml; eval-only, lens unchanged): calibrated H_report support
  (model top-K, null≈0) + permutation gate; min_band_size 6; cross-lingual variants + shuffled null.
- Run 2: domain FAIL 1/3 but interpretable — H_report 0.180 (thr 0.4) with permutation p≈1e-4,
  rising to ρ=0.62 at L34; H_bands PASS 0.306 with bands [0,6)/[6,30)/[30,36); H_modulation 0.10
  vs null 0.0104 (~10× chance). gates/gate_L1.json.
- Adversarial review #2: demands 1,2,4,5 met; demand 3 (functional band validation) unmet —
  circular at screen tier; verdict "UNDERPOWERED, not broken"; recommends 27B size-matched retry.
- Fit-corpus deviation: n_prompts 64→16 under contention=psalm (budget cap binding). GPU spent
  1.45h of 2.0h cap.

## Disposition (operator decision at gate, per prune_rule)
(a) accept screen-tier evidence (signatures present, significant vs null; thresholds 27B-calibrated)
    → proceed to L2 on the PWM stack with disclosed caveats;
(b) fund 27B size-matched retry (~6–7 GPU-h shared; exceeds L1 cap — new budget line);
(c) prune instrument-at-4B.
Builder's note: (a) keeps momentum toward the actual target (PWM stack, L2) and defers the size
question to the EFE selector at L5; (b) is the reviewer's recommendation for gate credibility;
next pre-registration MUST fix bands before modulation (review #2's circularity finding).

Operator sign-off: ______  Date: ______
