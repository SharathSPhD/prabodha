"""runner — rebuild the selector from menu + gates + ledger; propose the next experiment.
Concept: the proposing half of the auto-research loop. Beliefs are seeded by replaying the
menu's `replay` gates (what we HAVE seen) and any ledger observations, then EFE ranks the
menu within the remaining budget. Disposition is the agent's (standing authorization);
every proposal and disposition lands in the ledger.
Source: prabhasa application/efe/runner.py pattern; docs/efe_port_plan.md phase 2/3.
Primitive: build_from_configs -> (selector, candidates, budget); propose_next; CLI prints
the ranked menu (python -m prabodha.efe.runner --menu configs/efe_menu.yaml).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from prabodha.config import load
from prabodha.efe.agent import Action, Candidate, EFESelector, Proposal
from prabodha.efe.gate_to_obs import observation_from_gate
from prabodha.efe.ledger import EFELedger


def build_from_configs(menu_path: str | Path, *, ledger: EFELedger | None = None,
                       root: str | Path = ".") -> tuple[EFESelector, list[Candidate], float, dict[str, Action]]:
    menu = load(menu_path, required=("candidates", "budget_gpu_hours"))
    root = Path(root)
    selector = EFESelector()
    candidates: list[Candidate] = []
    actions_by_id: dict[str, Action] = {}
    for c in menu["candidates"]:
        cand = Candidate(id=c["id"], description=c["description"],
                         knobs=dict(c.get("knobs", {})),
                         prior_value_hint=c.get("prior_value_hint"))
        candidates.append(cand)
        if "cost_gpu_hours" in c:
            # review #7 P0: composite as-registered cost replaces the generic ladder
            actions_by_id[cand.id] = Action("as-registered",
                                            gpu_hours=float(c["cost_gpu_hours"]),
                                            resolution=float(c.get("resolution", 0.6)))
        # replay closed gates into this candidate's belief (prior -> posterior)
        for gate in c.get("replay", []):
            gp = root / gate
            if not gp.exists():
                continue
            obs = observation_from_gate(gp)
            post = selector.update(cand.id, obs, prior=selector.belief(cand))
            if ledger is not None:
                ledger.log_observation(cand.id, obs, post, source=str(gate))
    # ledger replay: observations from RUNS (sources not among the menu's declared replay
    # gates — those were already seeded above; without this, a completed run's observation
    # is silently lost and the selector re-proposes it. Found live in cycle 2.)
    menu_sources = {g for c in menu["candidates"] for g in c.get("replay", [])}
    if ledger is not None:
        from prabodha.efe.agent import Observation
        for rec in ledger.records():
            if rec.get("event") == "observe" and rec.get("source", "") not in menu_sources:
                selector.update(rec["candidate"],
                                Observation(primary_tier=rec["primary_tier"],
                                            secondary_tier=rec.get("secondary_tier")))
    # budget scope: a menu's budget is debited ONLY by spends on ITS candidates
    # (the ledger is program-global and spans menu generations — found live in cycle 7)
    menu_ids = {c["id"] for c in menu["candidates"]}
    spent = sum(r["gpu_hours"] for r in (ledger.records() if ledger else [])
                if r.get("event") == "spend" and r.get("candidate") in menu_ids)
    budget = float(menu["budget_gpu_hours"]) - spent
    return selector, candidates, budget, actions_by_id


def propose_next(menu_path: str | Path, *, ledger: EFELedger,
                 root: str | Path = ".") -> Proposal:
    selector, candidates, budget, actions = build_from_configs(menu_path, ledger=ledger,
                                                               root=root)
    # consumption rule: a candidate whose registered question already has a RUN-sourced
    # observation is consumed — re-running it verbatim has no marginal value; follow-ups
    # are new menu entries. (Cycle-3 live finding: a tier-3 result raises pragmatic value
    # and the raw EFE wants to re-run its winner.)
    menu = load(menu_path, required=("candidates",))
    menu_sources = {g for c in menu["candidates"] for g in c.get("replay", [])}
    consumed = {rec["candidate"] for rec in ledger.records()
                if rec.get("event") == "observe"
                and rec.get("source", "") not in menu_sources and rec.get("source")}
    blocked = {c["id"]: c["blocked"] for c in menu["candidates"] if c.get("blocked")}
    best: Proposal | None = None
    for cand in candidates:
        act = actions.get(cand.id)
        if cand.id in blocked:
            if not any(r.get("event") == "skip" and r.get("candidate") == cand.id
                       for r in ledger.records()):
                ledger.log_skip(cand.id, f"blocked: {blocked[cand.id]}")
            continue
        if act is None or act.gpu_hours > budget or cand.id in consumed:
            continue
        prop = selector.score(cand, act)
        if best is None or prop.efe < best.efe:
            best = prop
    if best is None:
        raise ValueError("no candidate fits the remaining budget")
    ledger.log_proposal(best, budget_remaining=budget)
    return best


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--menu", default="configs/efe_menu.yaml")
    ap.add_argument("--ledger", default="research/efe_ledger.jsonl")
    ap.add_argument("--propose", action="store_true",
                    help="log the top proposal to the ledger (else just print the ranking)")
    a = ap.parse_args(argv)
    ledger = EFELedger(a.ledger)
    selector, candidates, budget, actions = build_from_configs(a.menu, ledger=None)
    print(f"budget remaining: {budget:.2f} GPU-h; ranked menu (best first):")
    ranked = sorted((selector.score(c, actions[c.id]) for c in candidates
                     if c.id in actions), key=lambda p: p.efe)
    for p in ranked:
        b = ", ".join(f"{x:.2f}" for x in p.belief)
        print(f"  {p.candidate.id:20s} action={p.action.name:7s} EFE={p.efe:+.3f} "
              f"epi={p.epistemic:.3f} prag={p.pragmatic:+.3f} belief=[{b}]")
    if a.propose:
        prop = propose_next(a.menu, ledger=ledger)
        print(json.dumps({"proposed": prop.candidate.id, "action": prop.action.name,
                          "efe": round(prop.efe, 4)}))


if __name__ == "__main__":
    main()
