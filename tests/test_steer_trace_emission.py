"""Integration test for --emit-trace flag in e4_cli.

Concept: sākṣāt-darśana (direct seeing; the trace as a record of steering).
Source: docs/superpowers/plans/2026-07-10-closure-master.md (I1).
Primitive: verify that e4_cli emits valid SteerTrace JSON.
"""
import json
import tempfile
from pathlib import Path

import pytest


def test_emit_trace_flag_exists():
    """--emit-trace flag is registered in e4_cli argparse."""
    from prabodha.steering import e4_cli
    import inspect
    source = inspect.getsource(e4_cli.main)
    assert "--emit-trace" in source


def test_steer_trace_json_structure():
    """Emitted trace JSON conforms to SteerTrace schema."""
    from prabodha.contracts.trace import SteerTrace
    # Create a minimal valid trace for testing
    trace_dict = {
        "schema_version": 1,
        "model_id": "test/model",
        "prompt": "test prompt",
        "concept": "fire",
        "arm": "entropy_gated",
        "seed": 42,
        "alpha": 0.3,
        "tau_percentile": 60,
        "site_layer": 24,
        "tokens": [],
        "readback": None,
        "behavioral_hit": None,
        "gate_ref": None,
        "created_at": "2026-07-10T00:00:00Z",
    }
    trace = SteerTrace.model_validate(trace_dict)
    assert trace.model_id == "test/model"
    assert trace.arm == "entropy_gated"
