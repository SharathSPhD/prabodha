# Contract L6 — auto-research cycles 2–3 (selector-driven)
Status: OPEN · Worktree: loop/l6-cycle2 · Owner: ralph loop
Lineage: L5 cycle 1; review #7 P1/P2; standing authorization.

## Cycle 2 — alignment_sampling (selector EFE -4.32 under true costs)
Pre-registered configs/experiments/e5align.yaml BEFORE the run (proposal ledgered first).
RESULT (gates/gate_L6_align.json, domain PASS): under sampling, entropy-gated writes lift
+0.40 vs rate-matched every-k +0.23 (advantage 0.17 >= 0.1) vs prefill +0.20. Event
ALIGNMENT matters beyond write rate. Caveat recorded: realized rates imperfectly matched
(7.15 vs 5.0 writes/gen); per-write efficiency still favors gated (0.056 vs 0.046).

## Cycle 3 — confirm_e4b (proposed after consumption rule; see loop fixes below)
Seeds 42 (= gate_L4b, deterministic reuse disclosed) + 123 + 777 fresh.
RESULT (gates/gate_L6_confirm.json, domain SPLIT):
- H_gated_budget CONFIRMS 3/3 (lifts 0.40/0.35/0.23, all within ±0.5 nats) — the core
  claim (event-gated band writes deliver real lift within the svātantrya budget) holds
  at confirm tier.
- H_gated_vs_prefill does NOT confirm (advantages 0.20/0.12/0.03; only seed 42 clears the
  0.15 margin) — the advantage over a single prefill write is real-but-small (~0.1) and
  underpowered at n=40/seed. Claims are hereby stated at the confirmed strength only.

## Loop mechanics hardened by running it (regression-tested)
1. Ledger-replay bug: run-sourced observations (gates not in the menu replay list) were
   silently dropped on rebuild — the selector re-proposed completed work. Fixed.
2. Consumption rule: a tier-3 result RAISES pragmatic value, so raw EFE wants to re-run its
   winner; candidates with run-sourced observations are now consumed (follow-ups = new menu
   entries). This is the EXPLORE->CONFIRM edge case prabhasa's exclude param anticipated.

## Closure: cycles coherent; claims restated at confirmed strength
Ledger: 3 full cycles (propose->run->observe->spend). Spent 0.9/2.0 GPU-h cumulative (L5+L6).
Operator sign-off: standing authorization (2026-07-09)
