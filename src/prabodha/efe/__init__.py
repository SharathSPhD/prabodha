"""prabodha.efe — auto-research: EFE selection over the experiment menu (L5).
Concept: the selector proposes the next experiment by expected information gain per
GPU-hour; the agent disposes (operator standing authorization 2026-07-09); gates record.
Source: prabhasa application/efe (ported per docs/efe_port_plan.md; math preserved exactly);
SPEC §7. Primitive: menu (configs/efe_menu.yaml) -> EFESelector.rank/select -> Proposal;
gate_to_obs replays closed gates into beliefs; EFELedger (JSONL) makes beliefs re-entrant.
"""
