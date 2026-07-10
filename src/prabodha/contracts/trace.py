"""Steering episode trace — the shared record consumed by app replay, Pages, and gateway.

Concept: sākṣāt-darśana (direct seeing) extended to the steering episode as a whole.
Source: paper §steering; gate_L9_alignconf.json (arm/seed semantics).
Primitive: trace emission (pure record; no behavior).
"""
from __future__ import annotations

from pydantic import BaseModel, Field

SCHEMA_VERSION = 1


class TraceToken(BaseModel):
    t: int                              # decode step index (0-based)
    token: str                          # decoded token text
    entropy: float                      # per-token predictive entropy in nats, measured pre-write
    gated: bool                         # True iff a sphuraṭṭā-gated write was applied at this step
    write_norm: float | None = None     # L2 norm of the applied write (None when not gated)
    band_topk: list[str] | None = None  # band-lens readout top-k tokens (None if not sampled at this step)


class ReadbackResult(BaseModel):
    verdict: str                        # "accepted" | "rejected"
    top_m: int
    gain: float
    concept_rank: int | None = None


class SteerTrace(BaseModel):
    schema_version: int = SCHEMA_VERSION
    model_id: str                       # e.g. "Qwen/Qwen3-4B"
    prompt: str
    concept: str                        # e.g. "fire"
    arm: str                            # baseline|prefill|entropy_gated|rate_matched|continuous|trained_bridge
    seed: int
    alpha: float
    tau_percentile: int
    site_layer: int
    tokens: list[TraceToken] = Field(default_factory=list)
    readback: ReadbackResult | None = None
    behavioral_hit: bool | None = None
    gate_ref: str | None = None         # repo-relative path of the gate JSON this run fed, if any
    created_at: str                     # ISO-8601 UTC
