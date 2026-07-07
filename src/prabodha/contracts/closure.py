"""Dual-closure gate schema (RULES R1).
Concept: dvāra (gate) with ubhaya-siddhi — both accomplishments required.
Source: neo-fm five-point gate; prabhasa closure.py; scoping doc §7.
Primitive: pydantic model serialized to gates/gate_<loop>.json.
"""
from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, model_validator

Verdict = Literal["pass", "fail", "pruned", "pending"]

class GateSide(BaseModel):
    verdict: Verdict
    evidence: str
    deviations: list[str] = []

class GateReport(BaseModel):
    loop: str
    status: Literal["open", "closed"]
    closed_at: Optional[str] = None
    code_gate: GateSide
    domain_gate: GateSide
    signoff: str = "pending"

    @model_validator(mode="after")
    def _dual_closure(self) -> "GateReport":
        if self.status == "closed":
            ok = {"pass", "pruned"}
            if not (self.code_gate.verdict in ok and self.domain_gate.verdict in ok):
                raise ValueError("R1 violation: closed loop requires BOTH gates pass|pruned")
            if self.domain_gate.verdict == "pruned" and not self.domain_gate.evidence:
                raise ValueError("R5: pruned closure requires evidence (diagnosis)")
        return self
