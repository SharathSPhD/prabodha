#!/usr/bin/env python3
"""Export moat proof data from gate_L26_moat_proof.json to web app.

Concept: niryātana (emission) — moat proof data flowing to public surfaces.
Source: gates/gate_L26_moat_proof.json
Target: apps/web/public/data/moat.json + site/public/data/moat.json

This script extracts the moat proof results and mechanism library from the gate
and publishes them to both the web app and Astro pages for visualization.

Usage:
    python scripts/tools/export_moat_data.py \\
        --repo-root . \\
        --out-app apps/web/public/data/moat.json \\
        --out-site site/public/data/moat.json
"""

import argparse
import json
from pathlib import Path
from typing import Any


def load_moat_gate(repo_root: Path) -> dict[str, Any]:
    """Load gate_L26_moat_proof.json.

    Raises:
        FileNotFoundError: if gate file doesn't exist
        ValueError: if gate JSON is malformed or missing required sections

    Returns:
        parsed GateReport
    """
    gate_file = repo_root / "gates" / "gate_L26_moat_proof.json"
    if not gate_file.exists():
        raise FileNotFoundError(
            f"Gate file not found at {gate_file}. "
            "Cannot export moat proof without the gate."
        )

    try:
        gate_data = json.loads(gate_file.read_text())
    except json.JSONDecodeError as e:
        raise ValueError(f"Malformed moat gate JSON: {e}")

    # Validate required sections
    required_keys = ["loop", "experiment", "results", "mechanism_registry"]
    for key in required_keys:
        if key not in gate_data:
            raise ValueError(
                f"Gate missing required section '{key}'. "
                f"Available keys: {list(gate_data.keys())}"
            )

    return gate_data


def extract_moat_proof(gate_data: dict[str, Any]) -> dict[str, Any]:
    """Extract moat proof results and metadata for app visualization.

    Returns:
        {
          "headline": "...",
          "model": "...",
          "results": {...},
          "projection": {...},
          "mechanisms": [...],
          "honest_negatives": [...]
        }
    """
    return {
        "headline": gate_data.get("moat_summary", {}).get("headline", ""),
        "operating_point": gate_data.get("moat_summary", {}).get("operating_point", ""),
        "model": gate_data.get("model", ""),
        "threat_model": gate_data.get("threat_model", {}),
        "results": gate_data.get("results", {}),
        "projection": gate_data.get("results", {}).get("projection_analysis", {}),
        "wrapping_resilience": gate_data.get("results", {}).get("jailbreak_wrapping_resilience", {}),
        "mechanisms": gate_data.get("mechanism_registry", {}).get("mechanisms", []),
        "honest_negatives": gate_data.get("honest_negatives", []),
        "product_implication": gate_data.get("moat_summary", {}).get("product_implication", ""),
        "timestamp": gate_data.get("timestamp", ""),
    }


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description="Export moat proof data to web app and Astro")
    ap.add_argument("--repo-root", required=True, help="repository root directory")
    ap.add_argument("--out-app", required=True, help="output file for web app moat.json")
    ap.add_argument("--out-site", required=True, help="output file for Astro site moat.json")
    a = ap.parse_args(argv)

    repo_root = Path(a.repo_root).resolve()
    out_app = Path(a.out_app)
    out_site = Path(a.out_site)

    print(f"loading moat gate from {repo_root / 'gates' / 'gate_L26_moat_proof.json'}")
    gate_data = load_moat_gate(repo_root)

    print(f"extracting moat proof data")
    moat_proof = extract_moat_proof(gate_data)

    # Write to web app
    out_app.parent.mkdir(parents=True, exist_ok=True)
    out_app.write_text(json.dumps(moat_proof, indent=2))
    print(f"wrote {out_app}")

    # Write to Astro site (same content)
    out_site.parent.mkdir(parents=True, exist_ok=True)
    out_site.write_text(json.dumps(moat_proof, indent=2))
    print(f"wrote {out_site}")

    print(f"\nmoat proof exported successfully")
    print(f"  headline: {moat_proof['headline']}")
    print(f"  model: {moat_proof['model']}")
    print(f"  mechanisms: {len(moat_proof['mechanisms'])} graded defenses")
    print(f"  honest negatives: {len(moat_proof['honest_negatives'])} caveats")


if __name__ == "__main__":
    main()
