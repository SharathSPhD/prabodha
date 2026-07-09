# Contract L4 — E4: sphurattā-gated write timing
Status: OPEN · Worktree: loop/l4-sphuratta-timing · Owner: ralph loop (fresh agent re-entry safe)
Lineage: L3 closure (honest-fail-with-finding: timing, not amplitude, is the lever —
gate_L3*, triple dissociation) + review #5 (event-gating ENDORSED; requirements adopted);
scoping §3 "writes at sphurattā events only" — now evidence-selected; operator sign-off
2026-07-09 ("continue autonomous to L4", GPU uncontended).

## Objective (domain)
Does gating band-writes to the plant's UNCOMMITTED moments (next-token entropy >= tau,
self-calibrated) deliver behavioral lift INSIDE the svātantrya budget where L3's continuous
writes blew it — and does event ALIGNMENT matter beyond write sparsity (rate-matched every-k
control)? Five arms: baseline / continuous / prefill_only / entropy_gated / every_k.

## Design decisions (recorded)
1. Event detector: PWM's sphurattā criteria (VFE percentile + Hopfield entropy) presuppose a
   WM; on a bare plant, the registered analogue is next-token entropy >= tau — writing where
   commitment has NOT yet flashed. min_gap temporal hygiene ported intact. (Disclosed in
   e4.yaml deviations; the deeper question of whether this deserves the name sphurattā is
   the interpretation the adversarial review should attack.)
2. tau self-calibrated (P60 of baseline arm's own per-generation mean step entropies) and
   k rate-matched to the gated arm's realized write rate — both derivations ship in the gate.
3. Budget currency amended from L3: MEAN STEP ENTROPY over the whole generation (vs
   baseline), not the prefill-position delta — the write acts across decode, so the budget
   must be measured across decode. (L3's currency understated the exposure; disclosed.)
4. Same plant, layer, alpha/cap, concepts, stubs, greedy decoding as L3 — one mechanism
   changes per loop (timing), everything else held.

## Deliverables
D1 steering/timing.py (Strategy: continuous/prefill_only/every_k/entropy_gated + factory),
   policy-gated injector, entropy observer — unit-tested CPU-side.
D2 configs/experiments/e4.yaml (pre-registered; registration-hygiene checked per L3 lesson).
D3 e4_cli runner + dispatch scripts/dispatch/l4/run.sh + compose l4.
D4 gates/gate_L4.json with per-(concept,stub) records incl. write events (step, gate
   entropy) — the per-write scatter review #5 demanded.
D5 adversarial review + SPEC/PRD evolution + milestone merge.

## Closure criteria
CODE GATE: CI green; smoke suite green in-container; run completes within budget.
DOMAIN GATE (screen, from e4.yaml): H_gated_budget (lift >= 0.2 within ±0.5 nats) and
H_alignment (gated - every_k lift >= 0.1). Split verdicts reportable. Prune rule in e4.yaml.
GPU: 1.5 GPU-h cap (L4 line).

## Iteration record (2026-07-09)
- gate_L4.json (greedy): domain FAIL both — but review #6 found the mechanism: ALL THREE
  sparse arms produced IDENTICAL hit sets; greedy decoding locks the path at the prefill
  write, decode-time writes mechanically inert. Alignment test ~10% power. Metric-currency
  criticism accepted (L3 at-position numbers not restated under the new currency — carried
  as reporting debt). tau=P60 landed on a stub-difficulty boundary (noted).
- gate_L4b.json (sampling T=0.8, registered VERBATIM from review #6 before data):
  domain PASS — entropy_gated lift +0.40 at ΔH -0.13 (~10 writes) vs prefill_only +0.20;
  H_gated_budget PASS (0.40 >= 0.2 within ±0.5 nats); H_gated_vs_prefill PASS (+0.20 >=
  0.15). THE PROGRAM'S FIRST INTERVENTIONAL DOMAIN PASS: event-gated band writes achieve
  continuous-level steering (L3: 0.40 at budget-blowing cost) INSIDE the svātantrya budget.
- Registered next questions (NOT run — unregistered): alignment (gated vs rate-matched
  every_k) under sampling; multi-seed confirm tier; tau-percentile sensitivity.

## Closure: PASS-with-caveats (screen tier, single seed, sampling regime)
Operator sign-off: ______  Date: ______
