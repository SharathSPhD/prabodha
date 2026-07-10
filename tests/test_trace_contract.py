"""Trace contract round-trip and validation tests."""
import json

import pytest
from pydantic import ValidationError


def test_steer_trace_round_trip():
    from prabodha.contracts.trace import (
        SCHEMA_VERSION,
        ReadbackResult,
        SteerTrace,
        TraceToken,
    )

    tr = SteerTrace(
        model_id="Qwen/Qwen3-4B",
        prompt="the fire remembers rivers",
        concept="fire",
        arm="entropy_gated",
        seed=42,
        alpha=0.3,
        tau_percentile=60,
        site_layer=24,
        tokens=[
            TraceToken(t=0, token=" The", entropy=2.31, gated=False),
            TraceToken(
                t=1,
                token=" fire",
                entropy=1.02,
                gated=True,
                write_norm=0.30,
                band_topk=["fire", "flame", "ember"],
            ),
        ],
        readback=ReadbackResult(verdict="accepted", top_m=5, gain=0.0, concept_rank=2),
        behavioral_hit=True,
        gate_ref="gates/gate_L13_recipe.json",
        created_at="2026-07-10T00:00:00Z",
    )
    blob = json.loads(tr.model_dump_json())
    assert blob["schema_version"] == SCHEMA_VERSION
    assert SteerTrace.model_validate(blob) == tr


def test_steer_trace_rejects_missing_required():
    from prabodha.contracts.trace import SteerTrace

    with pytest.raises(ValidationError):
        SteerTrace(model_id="x", prompt="p", concept="c")


def test_trace_token_defaults():
    from prabodha.contracts.trace import TraceToken

    tok = TraceToken(t=3, token=" ash", entropy=0.77, gated=False)
    assert tok.write_norm is None
    assert tok.band_topk is None
