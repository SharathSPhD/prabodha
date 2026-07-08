# EFE selector port plan (prabhasa → prabodha) — banked 2026-07-08, executes at L5
*Produced by a read-only Explore subagent against prabhasa-samskrutam; verified paths.*
*Concept: the L5 auto-research engine (SPEC §7) — candidates=experiments, observations=gate
outcomes, cost=GPU-hours. This plan is scoping only; the port happens when L5 opens (concepts
lead; building serves concepts).*

## Source interfaces (prabhasa-samskrutam/src/prabhasa/application/efe/)
- agent.py: Action(name, gpu_hours, resolution), Candidate(id, description, knobs,
  prior_value_hint), Observation(bpb_tier 0..3, frt_tier 0..3|None), Proposal(candidate,
  action, efe, epistemic, pragmatic, belief), EFESelector(epistemic_weight, pragmatic_weight,
  cost_penalty, actions) with belief/update/score/select/rank. Bayes over 4 latent value
  levels; hardcoded likelihood matrix (agent.py:115-120); entropy-based epistemic term.
- candidates.py: CandidateRegistry(candidates, budget_gpu_hours, spent_gpu_hours) + spend/by_id/add.
- ledger.py: EFELedger(path) JSONL: propose/observe/spend/skip events; records() replay.
  observation_from_gate(gate, probe) — prabhasa M3-gate specific (MUST be rewritten).
- runner.py: rebuild_selector, skipped_candidates, total_spent_gpu_hours, propose_next,
  apply_observation — ledger-replayed beliefs (stateless re-entry, same as our ralph loops).

## Dependencies: stdlib only (math/json/time/dataclasses/pathlib) — ports clean into prabodha.

## Adaptations required
1. _DEFAULTS candidates (prabhasa trainer knobs) → prabodha experiment menu (E5 sphurattā
   bimodality, E6 anusaṃdhāna reload, E8 ...; knobs from scoping doc §7).
2. observation_from_gate → parse prabodha GateReport (src/prabodha/contracts/closure.py):
   hypothesis verdicts + effect sizes → tiers. Direction preserved (pass→high value).
3. Ledger path → research/efe_ledger.jsonl.
4. Action tiers → prabodha stats tiers (smoke/screen/confirm; resolution ≈ statistical power).
5. Keep exactly: likelihood matrix, _normalise, _entropy, EFESelector methods, ledger record format.

## Execution checklist (L5 loop)
- [ ] Copy agent.py verbatim + unit tests for belief mechanics
- [ ] experiment_candidates.py with E-menu knobs (config-driven from configs/experiments/)
- [ ] gate_to_obs.py: GateReport → Observation (test discretisation)
- [ ] ledger tests (propose/observe/spend replay)
- [ ] runner wiring: propose_next at each gate; human disposes (AGENTS.md)
