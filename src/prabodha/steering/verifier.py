"""verifier — readback verdicts (āgama re-cognition) + svātantrya entropy budget.
Concept: an offered content counts as taken up only if the workspace RE-COGNIZES it —
the concept's rank under the band-targeted lens must improve past a registered bar within
a bounded readback window; and the write must not have cost the plant its freedom
(svātantrya: output-entropy change bounded by epsilon).
Source: scoping §3.3 uptake criteria (loading, amplification, persistence); SPEC §6;
RULES R3 (svātantrya budget). Malas (failure taxonomy) classified from the verdict pattern:
āṇava (no loading at all), māyīya (loaded but not amplified/broadcast), kārma (loaded but
transient — no persistence).
Primitive: pure numpy/python — host-testable; GPU code hands in plain rank/entropy numbers.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def entropy(logits: np.ndarray) -> float:
    """Shannon entropy (nats) of softmax(logits) — the svātantrya currency."""
    v = np.asarray(logits, dtype=np.float64)
    v = v - v.max()
    p = np.exp(v)
    p /= p.sum()
    return float(-(p * np.log(np.maximum(p, 1e-300))).sum())


@dataclass(frozen=True)
class Uptake:
    ok: bool
    loaded: bool            # rank reached <= top_m at ANY readback point
    amplified: bool         # rank improved by >= min_rank_gain vs pre-write
    persistent: bool        # still <= top_m at the LAST readback point
    mala: str | None        # None if ok, else āṇava | māyīya | kārma
    best_rank: int
    pre_rank: int
    entropy_delta: float
    within_budget: bool     # |entropy_delta| <= epsilon


def readback_verdict(pre_rank: int, readback_ranks: list[int], *,
                     top_m: int, min_rank_gain: int,
                     entropy_before: float, entropy_after: float,
                     epsilon: float) -> Uptake:
    """Judge one write from its readback rank trajectory (<= 3 points per SPEC §6).
    Verdict requires ALL of: loading (<= top_m somewhere), amplification (rank gain >=
    min_rank_gain), persistence (<= top_m at the end), and the entropy budget."""
    if not readback_ranks:
        raise ValueError("no readback points")
    best = min(readback_ranks)
    loaded = best <= top_m
    amplified = (pre_rank - best) >= min_rank_gain
    persistent = readback_ranks[-1] <= top_m
    delta = entropy_after - entropy_before
    within = abs(delta) <= epsilon
    ok = loaded and amplified and persistent and within
    mala = None
    if not ok:
        if not loaded:
            mala = "anava"       # never entered the workspace at all
        elif not amplified:
            mala = "mayiya"      # present but not differentiated/strengthened
        elif not persistent:
            mala = "karma"       # flashed and faded — no continuity
        else:
            mala = "svatantrya"  # uptake fine but the write cost too much freedom
    return Uptake(ok=ok, loaded=loaded, amplified=amplified, persistent=persistent,
                  mala=mala, best_rank=best, pre_rank=pre_rank,
                  entropy_delta=delta, within_budget=within)
