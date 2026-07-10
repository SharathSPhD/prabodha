"""Public API wrappers for steering operations (write, gate, verify).

Concept: likhita (writing; the steering write interface).
Source: docs/jspace_pratyabhijna_scoping.md; RULES R8 (public surface).
Primitive: thin wrappers over e4_cli, typed and documented for external callers.
"""
from typing import Optional, Any


def write(
    model_config_path: str,
    lens_file_path: str,
    exp_config_path: str,
    out_path: str,
    alpha: Optional[float] = None,
    tau_percentile: Optional[float] = None,
    seed: Optional[int] = None,
    emit_trace: Optional[str] = None,
) -> None:
    """Steer a model using recognition-gated writes, emit gate JSON and optionally trace.

    Concept: likhita (writing; the steering write interface).
    Source: docs/h4_plugin_architecture.md; e4_cli.main().
    Primitive: wraps e4_cli, writes gate JSON and optional trace JSON to disk.

    Args:
        model_config_path: path to model YAML
        lens_file_path: path to fitted lens checkpoint (.pt)
        exp_config_path: path to experiment config YAML (stubs, concepts, arms, hypotheses)
        out_path: output gate JSON path
        alpha: optional override of exp alpha (dose-response sweep)
        tau_percentile: optional override of tau percentile (timing calibration)
        seed: optional override of seeds[0] (reproducibility / multi-seed runs)
        emit_trace: optional path to write SteerTrace JSON (per-token entropy, gate events)

    Raises:
        FileNotFoundError: if config or lens file not found
        RuntimeError: if steering run fails (CUDA, model loading, etc.)
    """
    from prabodha.steering import e4_cli
    argv = [
        "--model", model_config_path,
        "--mid-lens", lens_file_path,
        "--exp", exp_config_path,
        "--out", out_path,
    ]
    if alpha is not None:
        argv.extend(["--alpha", str(alpha)])
    if tau_percentile is not None:
        argv.extend(["--tau-percentile", str(tau_percentile)])
    if seed is not None:
        argv.extend(["--seed", str(seed)])
    if emit_trace is not None:
        argv.extend(["--emit-trace", emit_trace])
    e4_cli.main(argv)


def gate(
    model_config_path: str,
    lens_file_path: str,
    exp_config_path: str,
) -> dict[str, Any]:
    """Run steering and return the gate report (domain verdict, summary).

    Concept: dūta (messenger; gate as the verdict's carrier).
    Source: docs/h4_plugin_architecture.md; contracts/closure.GateReport.
    Primitive: wraps e4_cli in-memory, parses and returns gate dict.

    Args:
        model_config_path: path to model YAML
        lens_file_path: path to fitted lens checkpoint (.pt)
        exp_config_path: path to experiment config YAML

    Returns:
        dict with keys: loop, status, code_gate, domain_gate, timestamp
        (parsed from GateReport JSON structure)

    Raises:
        FileNotFoundError: if config or lens file not found
        RuntimeError: if steering run fails
    """
    import json
    import tempfile
    from pathlib import Path
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        gate_path = f.name
    try:
        write(model_config_path, lens_file_path, exp_config_path, gate_path)
        gate_json = json.loads(Path(gate_path).read_text())
        return gate_json
    finally:
        Path(gate_path).unlink(missing_ok=True)


def verify(gate_json_path: str) -> dict[str, Any]:
    """Verify a gate JSON file; return parsed verdict and evidence.

    Concept: parikṣā (examination; gate inspection).
    Source: docs/h4_plugin_architecture.md; contracts/closure.GateReport.
    Primitive: reads gate JSON, extracts code_gate and domain_gate verdicts.

    Args:
        gate_json_path: path to gate JSON file

    Returns:
        dict with keys: code_gate (verdict, evidence), domain_gate (verdict, evidence, deviations)

    Raises:
        FileNotFoundError: if gate file not found
        json.JSONDecodeError: if gate JSON is malformed
    """
    import json
    from pathlib import Path
    gate_json = json.loads(Path(gate_json_path).read_text())
    return {
        "code_gate": {
            "verdict": gate_json.get("code_gate", {}).get("verdict"),
            "evidence": gate_json.get("code_gate", {}).get("evidence"),
        },
        "domain_gate": {
            "verdict": gate_json.get("domain_gate", {}).get("verdict"),
            "evidence": gate_json.get("domain_gate", {}).get("evidence"),
            "deviations": gate_json.get("domain_gate", {}).get("deviations", []),
        },
    }
