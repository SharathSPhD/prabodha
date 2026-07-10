"""Public API wrappers for lens operations (fit, eval, vis).

Concept: ārambha (inception; the public gate to the instrument).
Source: docs/jspace_pratyabhijna_scoping.md; RULES R8 (public surface).
Primitive: thin wrappers over CLI modules, typed and documented for external callers.
"""
from pathlib import Path
from typing import Optional


def fit(
    model_config_path: str,
    lens_config_path: str,
    out_path: str,
    resume: bool = False
) -> None:
    """Fit a band-targeted Jacobian lens on a model.

    Concept: ārambha (inception; the public gate to the instrument).
    Source: docs/h4_plugin_architecture.md; fit_cli.main().
    Primitive: wraps fit_cli, writes lens checkpoint to disk.

    Args:
        model_config_path: path to model YAML (e.g., configs/models/qwen3.yaml)
        lens_config_path: path to lens config YAML (e.g., configs/lens_mid.yaml)
        out_path: output file path for lens checkpoint (.pt)
        resume: if True, resume from existing checkpoint at out_path

    Raises:
        FileNotFoundError: if config files not found
        RuntimeError: if fitting fails (CUDA, memory, etc.)
    """
    from prabodha.lens import fit_cli
    import sys
    # Construct argv for fit_cli.main() which expects sys.argv
    argv = [
        "fit",
        "--model", model_config_path,
        "--lens", lens_config_path,
        "--out", out_path,
    ]
    if resume:
        argv.append("--resume")
    old_argv = sys.argv
    try:
        sys.argv = argv
        fit_cli.main()
    finally:
        sys.argv = old_argv


def eval(
    model_config_path: str,
    lens_file_path: str,
    exp_config_path: str,
    out_path: str
) -> None:
    """Evaluate a lens on a corpus (e1 metrics).

    Concept: mīmāṃsā (examination; lens fidelity evaluation).
    Source: docs/h4_plugin_architecture.md; e1_cli.main().
    Primitive: wraps e1_cli, writes gate JSON to disk.

    Args:
        model_config_path: path to model YAML
        lens_file_path: path to fitted lens checkpoint (.pt)
        exp_config_path: path to experiment config YAML
        out_path: output gate JSON path

    Raises:
        FileNotFoundError: if config or lens file not found
        RuntimeError: if evaluation fails
    """
    from prabodha.lens import e1_cli
    argv = [
        "--model", model_config_path,
        "--lens-file", lens_file_path,
        "--exp", exp_config_path,
        "--out", out_path,
    ]
    e1_cli.main(argv)


def vis(
    model_config_path: str,
    lens_file_path: str,
    prompt: str,
    out_path: str
) -> None:
    """Visualize lens readout for a prompt (interactive HTML).

    Concept: darśana (seeing; lens-based visualization).
    Source: docs/h4_plugin_architecture.md; vis_cli.main().
    Primitive: wraps vis_cli, writes HTML page to disk.

    Args:
        model_config_path: path to model YAML
        lens_file_path: path to fitted lens checkpoint (.pt)
        prompt: text prompt to visualize
        out_path: output HTML file path

    Raises:
        FileNotFoundError: if config or lens file not found
        RuntimeError: if visualization fails
    """
    from prabodha.lens import vis_cli
    argv = [
        "--model", model_config_path,
        "--lens-file", lens_file_path,
        "--prompt", prompt,
        "--out", out_path,
    ]
    vis_cli.main(argv)
