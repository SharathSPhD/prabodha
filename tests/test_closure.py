import pytest
from prabodha.contracts.closure import GateReport, GateSide

def _side(v): return GateSide(verdict=v, evidence="e")

def test_dual_closure_enforced():
    with pytest.raises(ValueError):
        GateReport(loop="LX", status="closed", code_gate=_side("pass"), domain_gate=_side("fail"))

def test_pass_and_pruned_both_close():
    for dv in ("pass", "pruned"):
        g = GateReport(loop="LX", status="closed", code_gate=_side("pass"), domain_gate=_side(dv))
        assert g.status == "closed"

def test_open_allows_pending():
    g = GateReport(loop="L1", status="open", code_gate=_side("pending"), domain_gate=_side("pending"))
    assert g.signoff == "pending"
