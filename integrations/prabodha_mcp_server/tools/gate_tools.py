"""Readback verification and gate enumeration tool implementations.

Concept: readback as probabilistic readout verification (weak signal).
Source: WS2 (public API: prabodha.steer.verify) & gates/ commit convention.
Primitive: CLI dispatch to prabodha steer --readback; gate file enumeration.
"""
import subprocess
import json
from pathlib import Path
from typing import Any


async def readback_verify_impl(trace_json_path: str) -> dict[str, Any]:
    """
    Run readback verification on a steering trace.

    Invokes: prabodha steer --readback <trace_json_path>
    (or imports prabodha.steer.verify if available)

    Returns: dict with keys:
      - status: "ok" | "error"
      - verdict: "accepted" | "rejected" (if status == "ok")
      - top_m: int (readback rank threshold)
      - gain: float (readback gain in nats or prob)
      - concept_rank: int | None (concept's rank in readout, if measured)
      - error: error message (if status != "ok")
      - caveat: "readback is probabilistic and noisy; single runs not confirmatory"
      - default_gate: "gates/gate_L9_readback.json"
    """
    try:
        readback_cmd = [
            "prabodha", "steer",
            "--readback",
            trace_json_path,
        ]

        result = subprocess.run(readback_cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            return {
                "status": "error",
                "verdict": None,
                "top_m": None,
                "gain": None,
                "concept_rank": None,
                "error": f"readback failed: {result.stderr}",
                "caveat": "readback is probabilistic and noisy; single runs not confirmatory",
                "default_gate": "gates/gate_L9_readback.json",
            }

        # Parse output (assume CLI outputs JSON)
        try:
            output_obj = json.loads(result.stdout)
        except json.JSONDecodeError:
            # Fallback: extract from text output
            output_obj = {
                "verdict": "unknown",
                "top_m": None,
                "gain": None,
                "concept_rank": None,
            }

        return {
            "status": "ok",
            "verdict": output_obj.get("verdict"),
            "top_m": output_obj.get("top_m"),
            "gain": output_obj.get("gain"),
            "concept_rank": output_obj.get("concept_rank"),
            "error": None,
            "caveat": "readback is probabilistic and noisy; single runs not confirmatory",
            "default_gate": "gates/gate_L9_readback.json",
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "verdict": None,
            "top_m": None,
            "gain": None,
            "concept_rank": None,
            "error": "readback timeout (>120s)",
            "caveat": "readback is probabilistic and noisy; single runs not confirmatory",
            "default_gate": "gates/gate_L9_readback.json",
        }
    except Exception as e:
        return {
            "status": "error",
            "verdict": None,
            "top_m": None,
            "gain": None,
            "concept_rank": None,
            "error": str(e),
            "caveat": "readback is probabilistic and noisy; single runs not confirmatory",
            "default_gate": "gates/gate_L9_readback.json",
        }


async def list_gates_impl(
    filter_arm: str | None = None,
    filter_concept: str | None = None,
) -> dict[str, Any]:
    """
    Enumerate all committed gates in gates/*.json.

    Reads gates/ directory (relative to repo root, found by walking up from prabodha CLI).
    Filters by arm and/or concept if requested.

    Returns: dict with keys:
      - status: "ok" | "error"
      - gates: list of dicts, each with keys:
        - path: relative path (e.g., "gates/gate_L9_alignconf.json")
        - name: short name (filename without .json)
        - verdict: if readable, "pass" | "fail" | "block" (or null)
        - arm: steering arm if readable
        - concept: steering concept if readable
      - count: total gate count
      - filtered_count: after applying filters
      - error: error message (if status != "ok")
    """
    try:
        # Find repo root by looking for .git or pyproject.toml
        cwd = Path.cwd()
        repo_root = None
        for candidate in [cwd] + list(cwd.parents):
            if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists():
                repo_root = candidate
                break

        if not repo_root:
            repo_root = cwd

        gates_dir = repo_root / "gates"
        if not gates_dir.exists():
            return {
                "status": "error",
                "gates": [],
                "count": 0,
                "filtered_count": 0,
                "error": f"gates/ directory not found at {gates_dir}",
            }

        gates_list = []
        for gate_file in sorted(gates_dir.glob("*.json")):
            gate_name = gate_file.stem
            gate_data = {"path": str(gate_file.relative_to(repo_root)), "name": gate_name}

            # Try to read and extract arm/concept/verdict
            try:
                with open(gate_file) as f:
                    obj = json.load(f)
                    gate_data["arm"] = obj.get("arm")
                    gate_data["concept"] = obj.get("concept")
                    gate_data["verdict"] = obj.get("verdict")
            except Exception:
                gate_data["arm"] = None
                gate_data["concept"] = None
                gate_data["verdict"] = None

            # Apply filters
            if filter_arm and gate_data.get("arm") != filter_arm:
                continue
            if filter_concept and gate_data.get("concept") != filter_concept:
                continue

            gates_list.append(gate_data)

        return {
            "status": "ok",
            "gates": gates_list,
            "count": len(list(gates_dir.glob("*.json"))),
            "filtered_count": len(gates_list),
            "error": None,
        }

    except Exception as e:
        return {
            "status": "error",
            "gates": [],
            "count": 0,
            "filtered_count": 0,
            "error": str(e),
        }
