"""gate_to_obs — discretise prabodha GateReports into EFE Observations.
Concept: gates are the selector's senses — each closed gate becomes a tiered observation
updating the belief about the experiment family it informs.
Source: docs/efe_port_plan.md adaptation #2 (prabhasa observation_from_gate was M3-gate
specific and is rewritten here for GateReport, src/prabodha/contracts/closure.py).
Primitive: gate JSON -> primary tier 0..3 from the domain verdict and the registered
hypotheses' value/threshold margins:
  3 = pass with headroom (all hypotheses pass, min margin >= 1.5x threshold)
  2 = pass (all hypotheses pass)
  1 = near-miss fail (best failing hypothesis reached >= 80% of its threshold)
  0 = fail (otherwise)
"""
from __future__ import annotations

import json
from pathlib import Path

from prabodha.efe.agent import Observation


def observation_from_gate(gate_path: str | Path) -> Observation:
    g = json.loads(Path(gate_path).read_text(encoding="utf-8"))
    ev = json.loads(g["domain_gate"]["evidence"])
    summary = ev["summary"]
    if g["domain_gate"]["verdict"] == "pass":
        ratios = [v["value"] / v["threshold"] for v in summary.values()
                  if isinstance(v.get("threshold"), (int, float)) and v["threshold"]]
        tier = 3 if ratios and min(ratios) >= 1.5 else 2
    else:
        failing = [v for v in summary.values() if not v["pass"]]
        ratios = [v["value"] / v["threshold"] for v in failing
                  if isinstance(v.get("threshold"), (int, float)) and v["threshold"] > 0]
        tier = 1 if ratios and max(ratios) >= 0.8 else 0
    return Observation(primary_tier=tier)
