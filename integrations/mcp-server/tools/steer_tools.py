"""Steering episode tool implementation.

Concept: recognition-gated write amplification with band readout & readback.
Source: WS2 (public API: prabodha.steer.write, prabodha.steer.gate, prabodha.steer.verify).
Primitive: CLI dispatch to prabodha steer subcommand with --emit-trace JSON output.
"""
import subprocess
import json
from pathlib import Path
from typing import Any


async def steer_generate_impl(
    model_config: str,
    concept: str,
    prompt: str,
    arm: str = "entropy_gated",
    seed: int = 42,
    alpha: float = 0.3,
    tau_percentile: int = 60,
) -> dict[str, Any]:
    """
    Run a steering episode and return the full SteerTrace JSON.

    Invokes: prabodha steer --model <model_config> --concept <concept> --prompt "..."
             --arm <arm> --seed <seed> --alpha <alpha> --tau-percentile <tau_percentile>
             --emit-trace <output>.json

    Returns: dict with keys:
      - status: "ok" | "error"
      - trace: SteerTrace JSON object (if status == "ok")
      - error: error message (if status != "ok")
      - default_gate: "gates/gate_L9_alignconf.json"
    """
    try:
        # Generate output filename
        trace_file = Path("/tmp") / f"steer_{concept}_{seed}_{int(alpha*100)}.json"

        steer_cmd = [
            "prabodha", "steer",
            "--model", model_config,
            "--concept", concept,
            "--prompt", prompt,
            "--arm", arm,
            "--seed", str(seed),
            "--alpha", str(alpha),
            "--tau-percentile", str(tau_percentile),
            "--emit-trace", str(trace_file),
        ]

        result = subprocess.run(steer_cmd, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            return {
                "status": "error",
                "trace": None,
                "error": f"steer failed: {result.stderr}",
                "default_gate": "gates/gate_L9_alignconf.json",
            }

        # Read the emitted trace JSON
        if not trace_file.exists():
            return {
                "status": "error",
                "trace": None,
                "error": f"trace file not created at {trace_file}",
                "default_gate": "gates/gate_L9_alignconf.json",
            }

        with open(trace_file) as f:
            trace_obj = json.load(f)

        return {
            "status": "ok",
            "trace": trace_obj,
            "error": None,
            "default_gate": "gates/gate_L9_alignconf.json",
            "trace_file_path": str(trace_file),
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "trace": None,
            "error": "steer command timeout (>600s)",
            "default_gate": "gates/gate_L9_alignconf.json",
        }
    except Exception as e:
        return {
            "status": "error",
            "trace": None,
            "error": str(e),
            "default_gate": "gates/gate_L9_alignconf.json",
        }
