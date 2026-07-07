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

Operator sign-off: ______  Date: ______
