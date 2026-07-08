"""E1 evaluation CLI (screen tier): report-ordering rho, CKA bands, modulation hit-rate.
Concept: dvara-pariksha -- the run composes the dual gate (R1) from pre-registered metrics (R4).
Source: contracts/L1_qwen_replication.md; configs/experiments/e1.yaml; scoping doc #7 (E1).
Primitive: build model + load lens -> run_e1 -> GateReport JSON (gates/gate_L1.json).
Gate semantics: code_gate passes iff the evaluation ran to completion (CI/lint asserted
elsewhere in the contract); domain_gate passes iff ALL THREE hypotheses meet their
pre-registered thresholds. Status stays "open" either way -- closure is human-gated
(operator sign-off line in the contract), never auto-emitted here.
"""
import argparse
import datetime
import json
import traceback

from prabodha.config import load
from prabodha.contracts.closure import GateReport, GateSide
from prabodha.lens.adapter import LensAdapter, build_model
from prabodha.lens.e1_metrics import run_e1


def compose_gate(results: dict | None, contention: str, error: str | None = None) -> GateReport:
    """Assemble the dual-verdict GateReport. Contention (GPU shared-mode state at run time)
    is recorded in evidence; deviations auto-populate from the evaluators (R5 honesty)."""
    if error is not None:
        return GateReport(
            loop="L1", status="open",
            code_gate=GateSide(verdict="fail", evidence=f"E1 run crashed: {error}",
                               deviations=[]),
            domain_gate=GateSide(verdict="pending", evidence="no results (run crashed)"))
    hyps = {k: v for k, v in results.items() if k != "deviations"}
    summary = {k: {"value": v["value"], "threshold": v["threshold"], "pass": v["pass"]}
               for k, v in hyps.items()}
    evidence = json.dumps({"summary": summary, "contention": contention,
                           "detail": {k: v["evidence"] for k, v in hyps.items()}})
    return GateReport(
        loop="L1", status="open",
        code_gate=GateSide(
            verdict="pass",
            evidence=f"E1 evaluation completed without error; contention={contention}"),
        domain_gate=GateSide(
            verdict="pass" if all(v["pass"] for v in hyps.values()) else "fail",
            evidence=evidence, deviations=list(results["deviations"])))


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    for f in ("--model", "--lens-file", "--exp", "--out"):
        ap.add_argument(f, required=True)
    ap.add_argument("--journal", required=False)
    ap.add_argument("--contention", default="unknown",
                    help="GPU contention state at dispatch (scripts/dispatch/l1/run.sh)")
    a = ap.parse_args(argv)
    exp = load(a.exp, required=("hypotheses", "seeds"))
    try:
        hf, tok = build_model(load(a.model))
        adapter = LensAdapter("jacobian").load(a.lens_file)
        results = run_e1(hf, tok, adapter, exp)
        # Pre-registration deviations/amendments (e1.yaml) flow into the gate record too —
        # adversarial-review finding: an empty gate deviations list on an amended config
        # misreports the run (R5 honesty).
        results["deviations"] = list(exp.get("deviations", [])) + list(results["deviations"])
        report = compose_gate(results, a.contention)
    except Exception:
        report = compose_gate(None, a.contention, error=traceback.format_exc(limit=3))
    with open(a.out, "w") as f:
        f.write(report.model_dump_json(indent=2))
    if a.journal:
        with open(a.journal, "a") as f:
            f.write(f"\n- {datetime.date.today()} E1 gate written ({a.out}): "
                    f"code={report.code_gate.verdict} domain={report.domain_gate.verdict} "
                    f"contention={a.contention}\n")
    print(f"gate written: {a.out} "
          f"(code={report.code_gate.verdict}, domain={report.domain_gate.verdict})")


if __name__ == "__main__":
    main()
