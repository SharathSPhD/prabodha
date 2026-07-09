"""ledger — append-only JSONL record of proposals, observations, spends, skips.
Concept: anusaṃdhāna for the auto-researcher — beliefs are never stored, only re-derived
by replaying the ledger; any fresh agent rebuilds the same selector state (stateless
re-entry, same doctrine as the ralph loops).
Source: prabhasa application/efe/ledger.py (record format preserved; path adapted).
Primitive: EFELedger.log_* / records(); replay in runner.rebuild_selector.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from prabodha.efe.agent import Observation, Proposal


class EFELedger:
    def __init__(self, path: str | Path = "research/efe_ledger.jsonl") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _append(self, record: dict[str, Any]) -> None:
        record["ts"] = time.time()
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def log_proposal(self, proposal: Proposal, *, budget_remaining: float) -> None:
        self._append({"event": "propose", "candidate": proposal.candidate.id,
                      "action": proposal.action.name, "efe": proposal.efe,
                      "epistemic": proposal.epistemic, "pragmatic": proposal.pragmatic,
                      "belief": list(proposal.belief),
                      "budget_remaining": budget_remaining})

    def log_observation(self, candidate_id: str, obs: Observation,
                        posterior: list[float], *, source: str = "") -> None:
        self._append({"event": "observe", "candidate": candidate_id,
                      "primary_tier": obs.primary_tier,
                      "secondary_tier": obs.secondary_tier,
                      "posterior": posterior, "source": source})

    def log_spend(self, candidate_id: str, gpu_hours: float) -> None:
        self._append({"event": "spend", "candidate": candidate_id,
                      "gpu_hours": gpu_hours})

    def log_skip(self, candidate_id: str, reason: str) -> None:
        self._append({"event": "skip", "candidate": candidate_id, "reason": reason})

    def records(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in
                self.path.read_text(encoding="utf-8").splitlines() if line.strip()]
