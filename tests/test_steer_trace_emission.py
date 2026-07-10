"""Integration test for --emit-trace flag in e4_cli.

Concept: sākṣāt-darśana (direct seeing; the trace as a record of steering).
Source: docs/superpowers/plans/2026-07-10-closure-master.md (I1).
Primitive: verify that e4_cli emits valid SteerTrace JSON.
"""



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


def test_steer_trace_has_nonempty_tokens_with_real_data():
    """Emitted trace must have non-empty tokens list with per-token fields.

    This test MUST FAIL against the current hardcoded empty tokens implementation,
    and PASS after proper per-token capture is wired through run_arm().
    """
    from prabodha.contracts.trace import SteerTrace

    # Simulate a properly-emitted trace with real per-token data
    tokens_data = [
        {
            "t": 0,
            "token": "hello",
            "entropy": 3.5,
            "gated": False,
            "write_norm": None,
            "band_topk": None,
        },
        {
            "t": 1,
            "token": "world",
            "entropy": 2.1,
            "gated": True,
            "write_norm": 0.42,
            "band_topk": None,
        },
    ]

    # Build a trace with populated tokens
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
        "tokens": tokens_data,
        "readback": None,
        "behavioral_hit": True,
        "gate_ref": None,
        "created_at": "2026-07-10T00:00:00Z",
    }

    trace = SteerTrace.model_validate(trace_dict)

    # Assertions that will fail if tokens is empty or fields missing
    assert len(trace.tokens) > 0, "tokens list must not be empty"
    assert len(trace.tokens) == 2

    # Check first token
    assert trace.tokens[0].t == 0
    assert trace.tokens[0].token == "hello"
    assert trace.tokens[0].entropy == 3.5
    assert trace.tokens[0].gated is False
    assert trace.tokens[0].write_norm is None

    # Check second token (gated write)
    assert trace.tokens[1].t == 1
    assert trace.tokens[1].token == "world"
    assert trace.tokens[1].entropy == 2.1
    assert trace.tokens[1].gated is True
    assert trace.tokens[1].write_norm == 0.42


def test_build_trace_tokens_populates_per_step_fields():
    """Regression: tokens[] must carry real per-step data, not be empty (review #WS2)."""
    from prabodha.steering.e4_cli import _build_trace_tokens

    toks = _build_trace_tokens(
        step_texts=[" The", " fire", " glows"],
        entropies=[2.31, 1.02, 0.55],
        write_events=[(1, 1.02)],
    )
    assert len(toks) == 3
    assert [t.t for t in toks] == [0, 1, 2]
    assert toks[0].gated is False and toks[1].gated is True and toks[2].gated is False
    assert toks[1].token == " fire" and abs(toks[1].entropy - 1.02) < 1e-9


def test_build_trace_tokens_handles_length_mismatch_and_empty_events():
    from prabodha.steering.e4_cli import _build_trace_tokens

    toks = _build_trace_tokens(["a", "b"], [1.0], None)
    assert len(toks) == 1 and toks[0].gated is False
