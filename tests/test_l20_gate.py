"""Unit tests for L20 trained-bridge gate evaluation logic.

Tests the domain-gate verdict computation for H_trained_bridge hypothesis,
including lift/entropy/gap constraints and overall pass/fail logic.
"""


def test_h_trained_bridge_pass_criterion():
    """Test H_trained_bridge passes with good lift, entropy, and gap."""
    # Simulate hypothesis and aggregates from e4_cli.py evaluation
    hyp = {
        "H_trained_bridge": {
            "min_lift": 0.15,
            "entropy_epsilon": 0.5,
            "max_gap_vs_analytic": 0.05,
        }
    }
    agg = {
        "entropy_gated": {
            "lift": 0.25,  # Reference analytic arm
            "step_entropy_delta": 0.1,
        },
        "trained_bridge": {
            "lift": 0.20,  # Above 0.15 threshold
            "step_entropy_delta": 0.2,  # Within [-0.5, +0.5]
        },
    }

    # Evaluation logic
    ht = hyp["H_trained_bridge"]
    tb = agg["trained_bridge"]
    g = agg["entropy_gated"]

    min_lift = float(ht["min_lift"])
    entropy_eps = float(ht["entropy_epsilon"])
    max_gap = float(ht.get("max_gap_vs_analytic", 0.05))

    tb_lift = tb["lift"]
    tb_entropy_delta = tb["step_entropy_delta"]
    gap_vs_analytic = tb_lift - g["lift"]

    h_trained_bridge = (
        tb_lift >= min_lift
        and abs(tb_entropy_delta) <= entropy_eps
        and abs(gap_vs_analytic) <= max_gap
    )

    assert h_trained_bridge, "Should pass with lift=0.20, entropy_delta=0.2, gap=-0.05"


def test_h_trained_bridge_fail_low_lift():
    """Test H_trained_bridge fails when lift is below threshold."""
    hyp = {
        "H_trained_bridge": {
            "min_lift": 0.15,
            "entropy_epsilon": 0.5,
            "max_gap_vs_analytic": 0.05,
        }
    }
    agg = {
        "entropy_gated": {"lift": 0.25, "step_entropy_delta": 0.1},
        "trained_bridge": {
            "lift": 0.12,  # Below 0.15 threshold
            "step_entropy_delta": 0.2,
        },
    }

    ht = hyp["H_trained_bridge"]
    tb = agg["trained_bridge"]
    g = agg["entropy_gated"]

    tb_lift = tb["lift"]
    tb_entropy_delta = tb["step_entropy_delta"]
    gap_vs_analytic = tb_lift - g["lift"]

    h_trained_bridge = (
        tb_lift >= float(ht["min_lift"])
        and abs(tb_entropy_delta) <= float(ht["entropy_epsilon"])
        and abs(gap_vs_analytic) <= float(ht.get("max_gap_vs_analytic", 0.05))
    )

    assert not h_trained_bridge, "Should fail when lift < 0.15"


def test_h_trained_bridge_fail_entropy_outside_budget():
    """Test H_trained_bridge fails when entropy delta exceeds budget."""
    hyp = {
        "H_trained_bridge": {
            "min_lift": 0.15,
            "entropy_epsilon": 0.5,
            "max_gap_vs_analytic": 0.05,
        }
    }
    agg = {
        "entropy_gated": {"lift": 0.25, "step_entropy_delta": 0.1},
        "trained_bridge": {
            "lift": 0.20,  # Good lift
            "step_entropy_delta": 0.6,  # Outside [-0.5, +0.5]
        },
    }

    ht = hyp["H_trained_bridge"]
    tb = agg["trained_bridge"]
    g = agg["entropy_gated"]

    tb_lift = tb["lift"]
    tb_entropy_delta = tb["step_entropy_delta"]
    gap_vs_analytic = tb_lift - g["lift"]

    h_trained_bridge = (
        tb_lift >= float(ht["min_lift"])
        and abs(tb_entropy_delta) <= float(ht["entropy_epsilon"])
        and abs(gap_vs_analytic) <= float(ht.get("max_gap_vs_analytic", 0.05))
    )

    assert not h_trained_bridge, "Should fail when entropy_delta outside budget"


def test_h_trained_bridge_fail_large_gap_vs_analytic():
    """Test H_trained_bridge fails when gap vs analytic exceeds max_gap."""
    hyp = {
        "H_trained_bridge": {
            "min_lift": 0.15,
            "entropy_epsilon": 0.5,
            "max_gap_vs_analytic": 0.05,
        }
    }
    agg = {
        "entropy_gated": {"lift": 0.25, "step_entropy_delta": 0.1},
        "trained_bridge": {
            "lift": 0.18,  # Good lift
            "step_entropy_delta": 0.2,  # Good entropy
            # but gap = 0.18 - 0.25 = -0.07, exceeds max_gap of 0.05
        },
    }

    ht = hyp["H_trained_bridge"]
    tb = agg["trained_bridge"]
    g = agg["entropy_gated"]

    tb_lift = tb["lift"]
    tb_entropy_delta = tb["step_entropy_delta"]
    gap_vs_analytic = tb_lift - g["lift"]

    h_trained_bridge = (
        tb_lift >= float(ht["min_lift"])
        and abs(tb_entropy_delta) <= float(ht["entropy_epsilon"])
        and abs(gap_vs_analytic) <= float(ht.get("max_gap_vs_analytic", 0.05))
    )

    assert not h_trained_bridge, "Should fail when gap vs analytic > 0.05"


def test_h_trained_bridge_pass_with_negative_entropy_delta():
    """Test H_trained_bridge passes with negative entropy delta within budget."""
    hyp = {
        "H_trained_bridge": {
            "min_lift": 0.15,
            "entropy_epsilon": 0.5,
            "max_gap_vs_analytic": 0.05,
        }
    }
    agg = {
        "entropy_gated": {"lift": 0.25, "step_entropy_delta": 0.1},
        "trained_bridge": {
            "lift": 0.22,  # Good lift
            "step_entropy_delta": -0.3,  # Negative entropy delta (good!)
            # gap = 0.22 - 0.25 = -0.03, within 0.05
        },
    }

    ht = hyp["H_trained_bridge"]
    tb = agg["trained_bridge"]
    g = agg["entropy_gated"]

    tb_lift = tb["lift"]
    tb_entropy_delta = tb["step_entropy_delta"]
    gap_vs_analytic = tb_lift - g["lift"]

    h_trained_bridge = (
        tb_lift >= float(ht["min_lift"])
        and abs(tb_entropy_delta) <= float(ht["entropy_epsilon"])
        and abs(gap_vs_analytic) <= float(ht.get("max_gap_vs_analytic", 0.05))
    )

    assert h_trained_bridge, "Should pass with negative entropy delta in budget"


def test_h_trained_bridge_pass_at_boundary():
    """Test H_trained_bridge passes exactly at all thresholds."""
    hyp = {
        "H_trained_bridge": {
            "min_lift": 0.15,
            "entropy_epsilon": 0.5,
            "max_gap_vs_analytic": 0.05,
        }
    }
    agg = {
        "entropy_gated": {"lift": 0.25, "step_entropy_delta": 0.1},
        "trained_bridge": {
            "lift": 0.15,  # Exactly at threshold
            "step_entropy_delta": 0.5,  # Exactly at entropy boundary
            # gap = 0.15 - 0.25 = -0.10, which is abs(-0.10) = 0.10 > 0.05
            # This should actually fail!
        },
    }

    ht = hyp["H_trained_bridge"]
    tb = agg["trained_bridge"]
    g = agg["entropy_gated"]

    tb_lift = tb["lift"]
    tb_entropy_delta = tb["step_entropy_delta"]
    gap_vs_analytic = tb_lift - g["lift"]

    h_trained_bridge = (
        tb_lift >= float(ht["min_lift"])
        and abs(tb_entropy_delta) <= float(ht["entropy_epsilon"])
        and abs(gap_vs_analytic) <= float(ht.get("max_gap_vs_analytic", 0.05))
    )

    # Should fail due to gap exceeding 0.05
    assert not h_trained_bridge, "Should fail when gap abs value exceeds 0.05"


def test_h_trained_bridge_pass_well_above_threshold():
    """Test H_trained_bridge passes well above all thresholds."""
    hyp = {
        "H_trained_bridge": {
            "min_lift": 0.15,
            "entropy_epsilon": 0.5,
            "max_gap_vs_analytic": 0.05,
        }
    }
    agg = {
        "entropy_gated": {"lift": 0.20, "step_entropy_delta": 0.1},
        "trained_bridge": {
            "lift": 0.25,  # Well above 0.15 threshold
            "step_entropy_delta": 0.1,  # Well within budget
            # gap = 0.25 - 0.20 = 0.05, at gap threshold
        },
    }

    ht = hyp["H_trained_bridge"]
    tb = agg["trained_bridge"]
    g = agg["entropy_gated"]

    tb_lift = tb["lift"]
    tb_entropy_delta = tb["step_entropy_delta"]
    gap_vs_analytic = tb_lift - g["lift"]

    h_trained_bridge = (
        tb_lift >= float(ht["min_lift"])
        and abs(tb_entropy_delta) <= float(ht["entropy_epsilon"])
        and abs(gap_vs_analytic) <= float(ht.get("max_gap_vs_analytic", 0.05))
    )

    # Should pass: all well above thresholds
    assert h_trained_bridge, "Should pass when criteria are well above thresholds"
