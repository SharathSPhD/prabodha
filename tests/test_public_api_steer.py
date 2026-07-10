"""Tests for prabodha.steer public API — write, gate, verify functions.

Concept: likhita (writing; the steering write interface).
Source: docs/jspace_pratyabhijna_scoping.md; RULES R8 (public surface).
Primitive: typed functions callable by external code.
"""



def test_steer_write_signature():
    """Public write function exists with correct signature."""
    from prabodha.steer import write
    import inspect
    sig = inspect.signature(write)
    params = list(sig.parameters.keys())
    assert "model_config_path" in params
    assert "lens_file_path" in params
    assert "exp_config_path" in params
    assert "out_path" in params
    assert "emit_trace" in params
    # Check docstring has Concept/Source/Primitive
    assert "Concept:" in write.__doc__
    assert "Source:" in write.__doc__
    assert "Primitive:" in write.__doc__


def test_steer_gate_signature():
    """Public gate function exists with correct signature."""
    from prabodha.steer import gate
    import inspect
    sig = inspect.signature(gate)
    params = list(sig.parameters.keys())
    assert "model_config_path" in params
    assert "lens_file_path" in params
    assert "exp_config_path" in params


def test_steer_verify_signature():
    """Public verify function exists with correct signature."""
    from prabodha.steer import verify
    import inspect
    sig = inspect.signature(verify)
    params = list(sig.parameters.keys())
    assert "gate_json_path" in params


def test_steer_api_exported():
    """Steer functions are exported at package level."""
    import prabodha.steer
    assert hasattr(prabodha.steer, "write")
    assert hasattr(prabodha.steer, "gate")
    assert hasattr(prabodha.steer, "verify")
