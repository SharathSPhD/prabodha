"""Tests for prabodha.lens public API — fit, eval, vis functions.

Concept: ārambha (inception; the public gate to the instrument).
Source: docs/jspace_pratyabhijna_scoping.md; RULES R8 (public surface).
Primitive: typed, docstringed functions callable by external code.
"""



def test_lens_fit_signature():
    """Public fit function exists with correct signature."""
    from prabodha.lens import fit
    import inspect
    sig = inspect.signature(fit)
    params = list(sig.parameters.keys())
    assert "model_config_path" in params
    assert "lens_config_path" in params
    assert "out_path" in params
    assert "resume" in params
    # Check docstring has Concept/Source/Primitive
    assert "Concept:" in fit.__doc__
    assert "Source:" in fit.__doc__
    assert "Primitive:" in fit.__doc__


def test_lens_eval_signature():
    """Public eval function exists with correct signature."""
    from prabodha.lens import eval as lens_eval
    import inspect
    sig = inspect.signature(lens_eval)
    params = list(sig.parameters.keys())
    assert "model_config_path" in params
    assert "lens_file_path" in params
    assert "exp_config_path" in params
    assert "out_path" in params


def test_lens_vis_signature():
    """Public vis function exists with correct signature."""
    from prabodha.lens import vis
    import inspect
    sig = inspect.signature(vis)
    params = list(sig.parameters.keys())
    assert "model_config_path" in params
    assert "lens_file_path" in params
    assert "prompt" in params
    assert "out_path" in params


def test_lens_api_exported():
    """Lens functions are exported at package level."""
    import prabodha.lens
    assert hasattr(prabodha.lens, "fit")
    assert hasattr(prabodha.lens, "eval")
    assert hasattr(prabodha.lens, "vis")
