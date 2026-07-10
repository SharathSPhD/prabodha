"""lint — cycle-integrity checks over the EFE ledger (the staleness invariant as CODE).
Concept: review #10's rule, adopted as loop law — a disposition may only execute the
LATEST proposal; if new observations land after a proposal, it is STALE and must be
re-proposed; divergences are legal only as explicit ledgered events with reasons.
Source: contracts/L6_cycles.md loop mechanics; review #10 (d); journal 2026-07-10.
Primitive: lint_cycles(records) -> list of violations (empty = clean). Historical
divergences before the law's adoption are grandfathered via the cutoff timestamp.
"""
from __future__ import annotations

from typing import Any


def lint_cycles(records: list[dict[str, Any]], *, adopted_ts: float = 0.0,
                menu_sources: set[str] | frozenset[str] = frozenset()) -> list[str]:
    """Check: every run-sourced observe (source set, and not a menu replay echo — pass the
    menu's declared replay gates as menu_sources) must be preceded by either (a) a propose
    for the SAME candidate, or (b) a ledgered divergence event naming it."""
    violations: list[str] = []
    last_propose: str | None = None
    last_divergence: str | None = None
    for rec in records:
        ev = rec.get("event")
        if ev == "propose":
            last_propose = rec["candidate"]
        elif ev == "divergence":
            last_divergence = rec["candidate"]
        elif (ev == "observe" and rec.get("source")
              and rec.get("source") not in menu_sources):
            cand = rec["candidate"]
            if rec.get("ts", 0) < adopted_ts:
                continue  # grandfathered (pre-law history)
            if cand != last_propose and cand != last_divergence:
                violations.append(
                    f"run observation for '{cand}' (source={rec['source']}) executed "
                    f"without a matching proposal or ledgered divergence "
                    f"(last propose: {last_propose!r})")
            last_divergence = None
    return violations


def log_divergence(ledger, candidate_id: str, reason: str) -> None:
    """Explicit, auditable divergence from the selector's latest proposal."""
    ledger._append({"event": "divergence", "candidate": candidate_id, "reason": reason})
