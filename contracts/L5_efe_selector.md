# Contract L5 — auto-research: EFE selector over the live experiment menu
Status: OPEN · Worktree: loop/l5-efe-selector · Owner: ralph loop (fresh agent re-entry safe)
Lineage: SPEC §7; docs/efe_port_plan.md (banked scout); prabhasa application/efe (source);
operator standing authorization 2026-07-09 (selector proposes, AGENT disposes).

## Objective (domain)
Close the auto-research loop: port the EFE selector, seed its beliefs by replaying the
program's own closed gates, have it PROPOSE the next experiment from a real menu
(configs/efe_menu.yaml: confirm_e4b, alignment_sampling, tau_sensitivity,
articulation_null, dose_response), then EXECUTE the proposal and feed the resulting gate
back as an observation. The loop is closed when one full propose→run→observe cycle is in
the ledger.

## Design decisions (recorded)
1. Port fidelity: agent.py math preserved exactly (likelihood matrix, entropy, EFE scoring,
   select/rank); only tier field names generalized (bpb→primary, frt→secondary).
2. Observations = gate outcomes discretised by verdict+margin (gate_to_obs: 3 pass-with-
   headroom / 2 pass / 1 near-miss / 0 fail) — the honest, mechanical mapping.
3. Menu beliefs seeded by replaying each candidate's `replay` gates (declared in the menu
   with inline justification); ledger replay covers cross-session observations.
4. Action costs kept at prabhasa defaults (smoke 0.1 / partial 1.0 / full 5.0 GPU-h);
   'full' is inadmissible under the L5 2.0 GPU-h budget by construction (checked in tests —
   the L3 registration-hygiene lesson applied).
5. Disposition: the agent executes the top proposal if it is one of the menu's declared
   runnable knob-sets and fits budget; skips (ledgered with reason) otherwise.

## Deliverables
D1 src/prabodha/efe/{agent,gate_to_obs,ledger,runner} + configs/efe_menu.yaml + tests.
D2 One full cycle in research/efe_ledger.jsonl: observe(replayed gates) -> propose ->
   spend -> observe(new gate).
D3 The proposed experiment's own gate (pre-registered by its menu knobs + the underlying
   experiment configs) + journal entry.
D4 Adversarial review of the CYCLE (did the selector's choice follow from its beliefs and
   the declared math? was the disposition faithful?) + SPEC/PRD evolution + milestone merge.

## Closure criteria
CODE GATE: CI green (EFE tests CPU-only).
DOMAIN GATE: the cycle exists and is coherent — proposal minimizes EFE over the menu given
the replayed beliefs (verifiable from the ledger), the executed run's gate is written, and
its observation updates the ledger. The selected experiment's own hypotheses pass/fail on
their own registered terms (either verdict is a valid cycle).
GPU: within the menu's 2.0 GPU-h dispatch budget.

Operator sign-off: standing authorization (2026-07-09)
