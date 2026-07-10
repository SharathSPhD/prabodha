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

    Raises:
        FileNotFoundError: if gates/ directory doesn't exist
        ValueError: if no readable gate files found (provenance requirement)

    Returns:
        dict mapping gate filename to parsed GateReport
    """
    gates = {}
    gates_dir = repo_root / "gates"
    if not gates_dir.exists():
        raise FileNotFoundError(
            f"gates/ directory not found at {gates_dir}. "
            "Cannot export data without gate provenance."
        )

    for gate_file in sorted(gates_dir.glob("gate_*.json")):
        try:
            gates[gate_file.name] = json.loads(gate_file.read_text())
        except json.JSONDecodeError as e:
            raise ValueError(f"Malformed gate JSON {gate_file}: {e}")

    if not gates:
        raise ValueError(
            f"No readable gate files found in {gates_dir}. "
            "Every exported claim must be traced to a committed gate JSON."
        )

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
    """Build results.json from gate data with provenance enforcement.

    Every extracted claim must have a valid gate file reference. No silent skips.

    Raises:
        ValueError: if a gate lacks required structure or summary fields

    Returns:
        {"claims": [...]} where each claim has id, text, tier, gates, numbers
    """
    claims = []
    skipped_gates = []

    # Extract claims from gate domain_gate evidence
    for gate_name, gate in gates.items():
        domain_gate = gate.get("domain_gate", {})
        if not domain_gate:
            skipped_gates.append((gate_name, "missing domain_gate"))
            continue

        evidence = domain_gate.get("evidence", "{}")
        try:
            ev_obj = json.loads(evidence) if isinstance(evidence, str) else evidence
        except json.JSONDecodeError:
            # Legitimately prose-evidence gates (e.g. gate_L0.json) carry no
            # machine-readable claims — not an error; skip, never fabricate numbers.
            skipped_gates.append((gate_name, "prose evidence (no structured claims)"))
            continue
        if not isinstance(ev_obj, dict):
            skipped_gates.append((gate_name, "non-object evidence"))
            continue

        # Extract summary (hypothesis results)
        summary = ev_obj.get("summary", {})
        if not summary:
            skipped_gates.append((gate_name, "empty summary (no hypotheses)"))
            continue

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

            # Verify that each claim has the required gate provenance
            if not gate_name or not hyp_name or hyp_result is None:
                raise ValueError(
                    f"Incomplete claim in gate {gate_name}: hyp={hyp_name}, result={hyp_result}. "
                    "All claims must have gate file, hypothesis name, and result value."
                )

            claims.append({
                "id": f"{gate_name}_{hyp_name}",
                "text": hyp_name,
                "tier": tier,
                "gates": [gate_name],
                "numbers": hyp_result,
            })

    # Report any skipped gates but continue (they may have valid reason)
    if skipped_gates:
        print(f"Info: skipped {len(skipped_gates)} gates with no extractable claims:")
        for gate_name, reason in skipped_gates:
            print(f"  - {gate_name}: {reason}")

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

    # Write individual replay files + an index the app's ReplayTheatre loads
    replays_dir = out_app / "replays"
    replays_dir.mkdir(parents=True, exist_ok=True)
    index = []
    for slug, trace_obj in sorted(replays_dict.items()):
        trace_file = replays_dir / f"{slug}.json"
        trace_file.write_text(json.dumps(trace_obj, indent=2))
        index.append({
            "slug": slug,
            "model_id": trace_obj.get("model_id", "unknown"),
            "concept": trace_obj.get("concept", ""),
            "arm": trace_obj.get("arm", ""),
            "prompt": trace_obj.get("prompt", ""),
            "n_tokens": len(trace_obj.get("tokens", [])),
            "gate_ref": trace_obj.get("gate_ref"),
        })
    (replays_dir / "index.json").write_text(json.dumps({"replays": index}, indent=2))
    print(f"wrote {len(replays_dict)} traces + index.json to {replays_dir}")

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
