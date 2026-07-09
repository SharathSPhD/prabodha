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
from prabodha.efe.agent import Candidate, EFESelector, Proposal
from prabodha.efe.gate_to_obs import observation_from_gate
from prabodha.efe.ledger import EFELedger


def build_from_configs(menu_path: str | Path, *, ledger: EFELedger | None = None,
                       root: str | Path = ".") -> tuple[EFESelector, list[Candidate], float]:
    menu = load(menu_path, required=("candidates", "budget_gpu_hours"))
    root = Path(root)
    selector = EFESelector()
    candidates: list[Candidate] = []
    for c in menu["candidates"]:
        cand = Candidate(id=c["id"], description=c["description"],
                         knobs=dict(c.get("knobs", {})),
                         prior_value_hint=c.get("prior_value_hint"))
        candidates.append(cand)
        # replay closed gates into this candidate's belief (prior -> posterior)
        for gate in c.get("replay", []):
            gp = root / gate
            if not gp.exists():
                continue
            obs = observation_from_gate(gp)
            post = selector.update(cand.id, obs, prior=selector.belief(cand))
            if ledger is not None:
                ledger.log_observation(cand.id, obs, post, source=str(gate))
    # ledger replay (observations recorded in previous sessions beyond the gate seeds)
    if ledger is not None:
        for rec in ledger.records():
            if rec.get("event") == "observe" and not rec.get("source"):
                from prabodha.efe.agent import Observation
                selector.update(rec["candidate"],
                                Observation(primary_tier=rec["primary_tier"],
                                            secondary_tier=rec.get("secondary_tier")))
    spent = sum(r["gpu_hours"] for r in (ledger.records() if ledger else [])
                if r.get("event") == "spend")
    budget = float(menu["budget_gpu_hours"]) - spent
    return selector, candidates, budget


def propose_next(menu_path: str | Path, *, ledger: EFELedger,
                 root: str | Path = ".") -> Proposal:
    selector, candidates, budget = build_from_configs(menu_path, ledger=ledger, root=root)
    proposal = selector.select(candidates, budget_gpu_hours=budget)
    ledger.log_proposal(proposal, budget_remaining=budget)
    return proposal


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--menu", default="configs/efe_menu.yaml")
    ap.add_argument("--ledger", default="research/efe_ledger.jsonl")
    ap.add_argument("--propose", action="store_true",
                    help="log the top proposal to the ledger (else just print the ranking)")
    a = ap.parse_args(argv)
    ledger = EFELedger(a.ledger)
    selector, candidates, budget = build_from_configs(a.menu, ledger=None)
    print(f"budget remaining: {budget:.2f} GPU-h; ranked menu (best first):")
    for p in selector.rank(candidates):
        b = ", ".join(f"{x:.2f}" for x in p.belief)
        print(f"  {p.candidate.id:20s} action={p.action.name:7s} EFE={p.efe:+.3f} "
              f"epi={p.epistemic:.3f} prag={p.pragmatic:+.3f} belief=[{b}]")
    if a.propose:
        prop = propose_next(a.menu, ledger=ledger)
        print(json.dumps({"proposed": prop.candidate.id, "action": prop.action.name,
                          "efe": round(prop.efe, 4)}))


if __name__ == "__main__":
    main()
