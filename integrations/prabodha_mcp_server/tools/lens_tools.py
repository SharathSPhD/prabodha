"""Lens fitting & evaluation tool implementation.

Concept: band readout mapping via Jacobian lens projection.
Source: WS2 (public API: prabodha.lens.fit, prabodha.lens.eval).
Primitive: CLI dispatch to prabodha lens-fit, lens-eval, lens-vis subcommands.
"""
import subprocess
import json
from pathlib import Path
from typing import Any


async def lens_map_impl(
    model_config: str,
    lens_config: str,
    output_dir: str,
    prompt: str | None = None,
) -> dict[str, Any]:
    """
    Fit a band-targeted Jacobian lens and evaluate it.

    Steps:
    1. prabodha lens-fit --model <model_config> --lens <lens_config> --out <output_dir>/lens.pt
    2. prabodha lens-eval --model <model_config> --lens-file <output_dir>/lens.pt --exp configs/experiments/e1.yaml --out <output_dir>/gate_lens_eval.json
    3. If prompt: prabodha lens-vis --model <model_config> --lens-file <output_dir>/lens.pt --prompt "..." --out <output_dir>/slice.html

    Returns: dict with keys:
      - fit_status: "ok" | error message
      - eval_gate: path to gate JSON (or null if failed)
      - vis_page: path to HTML (or null if skipped)
      - default_gate: "gates/gate_L13_recipe.json"
    """
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)
    lens_path = output_dir_path / "lens.pt"
    gate_path = output_dir_path / "gate_lens_eval.json"
    vis_path = output_dir_path / "slice.html"

    try:
        # Step 1: Fit
        fit_cmd = [
            "prabodha", "lens-fit",
            "--model", model_config,
            "--lens", lens_config,
            "--out", str(lens_path),
        ]
        fit_result = subprocess.run(fit_cmd, capture_output=True, text=True, timeout=3600)
        if fit_result.returncode != 0:
            return {
                "status": "error",
                "fit_status": f"lens-fit failed: {fit_result.stderr}",
                "eval_gate": None,
                "vis_page": None,
                "default_gate": "gates/gate_L13_recipe.json",
            }

        # Step 2: Eval
        eval_cmd = [
            "prabodha", "lens-eval",
            "--model", model_config,
            "--lens-file", str(lens_path),
            "--exp", "configs/experiments/e1.yaml",
            "--out", str(gate_path),
        ]
        eval_result = subprocess.run(eval_cmd, capture_output=True, text=True, timeout=3600)
        if eval_result.returncode != 0:
            return {
                "status": "error",
                "fit_status": "ok",
                "eval_gate": None,
                "vis_page": None,
                "default_gate": "gates/gate_L13_recipe.json",
            }

        # Step 3: Optional Visualize
        vis_page = None
        if prompt:
            vis_cmd = [
                "prabodha", "lens-vis",
                "--model", model_config,
                "--lens-file", str(lens_path),
                "--prompt", prompt,
                "--out", str(vis_path),
            ]
            vis_result = subprocess.run(vis_cmd, capture_output=True, text=True, timeout=600)
            if vis_result.returncode == 0:
                vis_page = str(vis_path)

        return {
            "status": "ok",
            "fit_status": "ok",
            "eval_gate": str(gate_path),
            "vis_page": vis_page,
            "default_gate": "gates/gate_L13_recipe.json",
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "fit_status": "timeout",
            "eval_gate": None,
            "vis_page": None,
            "default_gate": "gates/gate_L13_recipe.json",
        }
    except Exception as e:
        return {
            "status": "error",
            "fit_status": str(e),
            "eval_gate": None,
            "vis_page": None,
            "default_gate": "gates/gate_L13_recipe.json",
        }
