"""E1 evaluation CLI (screen tier): report-ordering rho, CKA bands, modulation hit-rate.
Emits gates/gate_L1.json via GateReport. GB10 target; metrics per configs/experiments/e1.yaml (R4).
Status: metric implementations land in the L1 worktree; this CLI defines the contract surface.
"""
import argparse
import datetime
from prabodha.config import load
from prabodha.contracts.closure import GateReport, GateSide

def main() -> None:
    ap = argparse.ArgumentParser()
    for f in ("--model", "--lens-file", "--exp", "--out", "--journal"):
        ap.add_argument(f, required=(f != "--journal"))
    a = ap.parse_args()
    exp = load(a.exp)
    # TODO(L1 worktree): implement H_report / H_bands / H_modulation evaluators (see contract D1).
    report = GateReport(
        loop="L1", status="open",
        code_gate=GateSide(verdict="pending", evidence="awaiting GB10 run"),
        domain_gate=GateSide(verdict="pending", evidence=f"pre-registered: {list(exp['hypotheses'])}"),
    )
    with open(a.out, "w") as f:
        f.write(report.model_dump_json(indent=2))
    print(f"gate skeleton written: {a.out} ({datetime.date.today()})")

if __name__ == "__main__":
    main()
