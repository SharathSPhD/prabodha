"""Steering episode tool implementation.

Concept: recognition-gated write amplification with band readout & readback.
Source: WS2 (public API: prabodha.steer.write, prabodha.steer.gate, prabodha.steer.verify).
Primitive: CLI dispatch to prabodha steer subcommand (config-driven: --model, --mid-lens, --exp) with --emit-trace JSON output.
"""
import subprocess
import json
import tempfile
from pathlib import Path
from typing import Any
import yaml


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

    Generates a temporary experiment YAML from user inputs (concept, arm) and invokes:
      prabodha steer --model <model_config> --mid-lens <lens_checkpoint> --exp <exp.yaml>
                     --out <gate.json> --seed <seed> --alpha <alpha> --tau-percentile <tau_percentile>
                     --emit-trace <trace.json>

    Returns: dict with keys:
      - status: "ok" | "error"
      - trace: SteerTrace JSON object (if status == "ok")
      - error: error message (if status != "ok")
      - default_gate: "gates/gate_L14_alignconf.json"
    """
    try:
        # Find lens checkpoint (assume output/lens_<model>.pt or similar)
        model_path = Path(model_config)
        model_name = model_path.stem
        lens_path = Path("outputs") / f"lens_{model_name}.pt"
        if not lens_path.exists():
            # Fallback: look for any lens.pt in outputs/
            outputs_dir = Path("outputs")
            if outputs_dir.exists():
                lenses = list(outputs_dir.glob("*lens*.pt"))
                if lenses:
                    lens_path = lenses[0]
                else:
                    return {
                        "status": "error",
                        "trace": None,
                        "error": f"No lens checkpoint found. Expected: {lens_path} or similar in outputs/",
                        "default_gate": "gates/gate_L14_alignconf.json",
                    }
            else:
                return {
                    "status": "error",
                    "trace": None,
                    "error": "outputs/ directory not found. Fit a lens first using lens_map tool.",
                    "default_gate": "gates/gate_L14_alignconf.json",
                }

        # Generate temporary experiment YAML from user inputs
        # Mirrors configs/experiments/e13full.yaml shape: concepts, stubs, arms, alpha, tau_percentile, etc.
        exp_config = {
            "concepts": [concept],
            "stubs": [prompt],  # Single stub (the prompt is the seed text)
            "arms": [arm],  # Single arm (user-specified)
            "alpha": alpha,
            "tau_percentile": tau_percentile,
            "write_layer": 20,  # Default write layer (can be calibrated)
            "norm_cap_rel": 1.0,  # Default norm cap
            "max_new_tokens": 50,  # Default generation length
            "min_gap": 1,  # Default minimum gap between writes
            "decoding": {"do_sample": True, "temperature": 0.7},  # Sampling decoding (required)
            "hypotheses": [],  # No special hypotheses
            "seeds": [seed],
        }

        # Create temporary experiment YAML
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(exp_config, f)
            exp_yaml_path = f.name

        # Create temporary gate output path
        gate_output = Path(tempfile.gettempdir()) / f"gate_steer_{concept}_{seed}.json"

        # Create temporary trace output path
        trace_output = Path(tempfile.gettempdir()) / f"trace_{concept}_{seed}_{int(alpha*100)}.json"

        # Invoke prabodha steer CLI with correct arguments
        steer_cmd = [
            "prabodha", "steer",
            "--model", model_config,
            "--mid-lens", str(lens_path),
            "--exp", exp_yaml_path,
            "--out", str(gate_output),
            "--seed", str(seed),
            "--alpha", str(alpha),
            "--tau-percentile", str(tau_percentile),
            "--emit-trace", str(trace_output),
        ]

        result = subprocess.run(steer_cmd, capture_output=True, text=True, timeout=600)

        # Clean up temporary files
        try:
            Path(exp_yaml_path).unlink()
        except Exception:
            pass

        if result.returncode != 0:
            return {
                "status": "error",
                "trace": None,
                "error": f"steer failed: {result.stderr}",
                "default_gate": "gates/gate_L14_alignconf.json",
            }

        # Read the emitted trace JSON
        if not trace_output.exists():
            return {
                "status": "error",
                "trace": None,
                "error": f"trace file not created at {trace_output}",
                "default_gate": "gates/gate_L14_alignconf.json",
            }

        with open(trace_output) as f:
            trace_obj = json.load(f)

        return {
            "status": "ok",
            "trace": trace_obj,
            "error": None,
            "default_gate": "gates/gate_L14_alignconf.json",
            "trace_file_path": str(trace_output),
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "trace": None,
            "error": "steer command timeout (>600s)",
            "default_gate": "gates/gate_L14_alignconf.json",
        }
    except Exception as e:
        return {
            "status": "error",
            "trace": None,
            "error": str(e),
            "default_gate": "gates/gate_L14_alignconf.json",
        }
