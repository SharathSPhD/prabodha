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

Operator sign-off: ______  Date: ______
