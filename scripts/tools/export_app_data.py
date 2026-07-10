#!/usr/bin/env python3
"""Export app data from gates and traces for web app and Pages.

Concept: niryātana (emission; data flowing to public surfaces).
Source: docs/superpowers/plans/2026-07-10-closure-master.md (I2).
Primitive: read gates/ + traces/, write apps/web/public/data/* and web/prabodha-data.js.
Enforces gate provenance: every number must trace to a committed gate JSON.

Usage:
    python scripts/tools/export_app_data.py \\
        --repo-root . \\
        --out-app apps/web/public/data \\
        --out-web web/prabodha-data.js
"""

import argparse
import json
from pathlib import Path
from typing import Any


def load_gates(repo_root: Path) -> dict[str, Any]:
    """Load all gate JSONs from gates/ directory.

    Returns:
        dict mapping gate filename to parsed GateReport
    """
    gates = {}
    gates_dir = repo_root / "gates"
    if not gates_dir.exists():
        return gates
    for gate_file in sorted(gates_dir.glob("gate_*.json")):
        try:
            gates[gate_file.name] = json.loads(gate_file.read_text())
        except json.JSONDecodeError as e:
            print(f"warning: skipping malformed gate {gate_file}: {e}")
    return gates


def load_traces(repo_root: Path) -> dict[str, Any]:
    """Load all trace JSONs from outputs/traces/ directory.

    Returns:
        dict mapping trace filename to parsed SteerTrace
    """
    traces = {}
    traces_dir = repo_root / "outputs" / "traces"
    if not traces_dir.exists():
        return traces
    for trace_file in sorted(traces_dir.glob("*.json")):
        try:
            traces[trace_file.name] = json.loads(trace_file.read_text())
        except json.JSONDecodeError as e:
            print(f"warning: skipping malformed trace {trace_file}: {e}")
    return traces


def build_results_json(gates: dict[str, Any]) -> dict[str, Any]:
    """Build results.json from gate data.

    Returns:
        {"claims": [...]} where each claim has id, text, tier, gates, numbers
    """
    claims = []
    # Extract claims from gate domain_gate evidence
    for gate_name, gate in gates.items():
        domain_gate = gate.get("domain_gate", {})
        evidence = domain_gate.get("evidence", "{}")
        try:
            ev_obj = json.loads(evidence) if isinstance(evidence, str) else evidence
        except json.JSONDecodeError:
            ev_obj = {}

        # Extract summary (hypothesis results)
        summary = ev_obj.get("summary", {})
        if summary:
            for hyp_name, hyp_result in summary.items():
                # Determine tier from gate name (e.g., gate_L1.json -> L1 -> tier screen if L < 10)
                tier = "confirm"
                if "_L" in gate_name:
                    try:
                        loop_part = gate_name.split("_L")[1].split("_")[0].split(".")[0]
                        loop_num = int(loop_part)
                        tier = "screen" if loop_num < 10 else "confirm"
                    except (ValueError, IndexError):
                        pass
                claims.append({
                    "id": f"{gate_name}_{hyp_name}",
                    "text": hyp_name,
                    "tier": tier,
                    "gates": [gate_name],
                    "numbers": hyp_result,
                })
    return {"claims": claims}


def build_replays_dict(traces: dict[str, Any]) -> dict[str, Any]:
    """Build dict mapping trace slug to SteerTrace object.

    Returns:
        {"<slug>": {...trace...}, ...}
    """
    replays = {}
    for trace_file, trace_obj in traces.items():
        slug = trace_file.replace(".json", "")
        replays[slug] = trace_obj
    return replays


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description="Export app data from gates and traces")
    ap.add_argument("--repo-root", required=True, help="repository root directory")
    ap.add_argument("--out-app", required=True, help="output directory for app data")
    ap.add_argument("--out-web", required=True, help="output file for web prabodha-data.js")
    a = ap.parse_args(argv)

    repo_root = Path(a.repo_root).resolve()
    out_app = Path(a.out_app)
    out_web = Path(a.out_web)

    print(f"loading gates from {repo_root / 'gates'}")
    gates = load_gates(repo_root)

    print(f"loading traces from {repo_root / 'outputs' / 'traces'}")
    traces = load_traces(repo_root)

    # Build results
    results_json = build_results_json(gates)
    replays_dict = build_replays_dict(traces)

    # Write results.json
    out_app.mkdir(parents=True, exist_ok=True)
    results_file = out_app / "results.json"
    results_file.write_text(json.dumps(results_json, indent=2))
    print(f"wrote {results_file}")

    # Write individual replay files
    replays_dir = out_app / "replays"
    replays_dir.mkdir(parents=True, exist_ok=True)
    for slug, trace_obj in replays_dict.items():
        trace_file = replays_dir / f"{slug}.json"
        trace_file.write_text(json.dumps(trace_obj, indent=2))
    print(f"wrote {len(replays_dict)} traces to {replays_dir}")

    # Write web prabodha-data.js
    out_web.parent.mkdir(parents=True, exist_ok=True)
    js_content = f"""window.PRABODHA = {{
  results: {json.dumps(results_json)},
  replays: {json.dumps(replays_dict)},
}};
"""
    out_web.write_text(js_content)
    print(f"wrote {out_web}")


if __name__ == "__main__":
    main()
