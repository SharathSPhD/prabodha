"""Unit tests for eval.compare — comparison harness tests (CPU only)."""
import pytest

from prabodha.eval.compare import (
    ArmResult,
    ComparisonReport,
    run_arms_comparison,
    comparison_to_gate_report,
)


@pytest.fixture
def baseline_arm():
    """Baseline arm result."""
    return ArmResult(
        arm_name="baseline",
        concept_surface_rate=0.3,
        mean_entropy_delta=0.0,
        refusal_rate=0.2,
        attack_success_rate=0.8,
        truthfulness_score=0.6,
        off_target_delta=0.0,
        n_generations=100,
    )


@pytest.fixture
def test_arm():
    """Test arm result (steered)."""
    return ArmResult(
        arm_name="entropy_gated",
        concept_surface_rate=0.6,  # Higher concept surface
        mean_entropy_delta=-0.5,  # Lower entropy
        refusal_rate=0.5,  # Higher refusal (good for safety)
        attack_success_rate=0.5,  # Lower ASR
        truthfulness_score=0.7,  # Improved truthfulness
        off_target_delta=0.05,  # Slight capability drop
        n_generations=100,
    )


@pytest.fixture
def baseline_arm_logit():
    """Logit-bias baseline arm result."""
    return ArmResult(
        arm_name="logit_bias",
        concept_surface_rate=0.4,
        mean_entropy_delta=-0.2,
        refusal_rate=0.25,
        attack_success_rate=0.75,
        truthfulness_score=0.62,
        off_target_delta=0.02,
        n_generations=100,
    )


class TestArmResult:
    """Tests for ArmResult dataclass."""

    def test_arm_result_creation(self, baseline_arm):
        """ArmResult should be created successfully."""
        assert baseline_arm.arm_name == "baseline"
        assert baseline_arm.concept_surface_rate == 0.3
        assert baseline_arm.n_generations == 100


class TestComparisonReport:
    """Tests for ComparisonReport."""

    def test_comparison_report_creation(self, baseline_arm, test_arm):
        """ComparisonReport should be created successfully."""
        arms = {"baseline": baseline_arm, "entropy_gated": test_arm}
        report = ComparisonReport(
            loop="L21",
            corpus_name="advbench_jailbreak",
            baseline_arm="baseline",
            arms=arms,
        )
        assert report.loop == "L21"
        assert len(report.arms) == 2
        assert report.deviations == []


class TestRunArmsComparison:
    """Tests for run_arms_comparison orchestration."""

    def test_comparison_with_baseline(self, baseline_arm, test_arm, baseline_arm_logit):
        """Comparison should compute effect sizes."""
        arms = {
            "baseline": baseline_arm,
            "entropy_gated": test_arm,
            "logit_bias": baseline_arm_logit,
        }

        comparison = run_arms_comparison(
            loop="L21",
            corpus_name="advbench_test",
            arms_results=arms,
            baseline_arm_name="baseline",
        )

        assert comparison.loop == "L21"
        assert comparison.baseline_arm == "baseline"
        assert "entropy_gated" in comparison.effect_sizes
        assert "logit_bias" in comparison.effect_sizes

    def test_comparison_effect_sizes_computed(self, baseline_arm, test_arm):
        """Effect sizes should be computed for each non-baseline arm."""
        arms = {"baseline": baseline_arm, "entropy_gated": test_arm}
        comparison = run_arms_comparison(
            loop="L21",
            corpus_name="test_corpus",
            arms_results=arms,
            baseline_arm_name="baseline",
        )

        effects = comparison.effect_sizes["entropy_gated"]
        # Should have computed various effect sizes
        assert "concept_surface_delta" in effects
        assert "entropy_delta_magnitude" in effects
        assert "refusal_delta" in effects
        assert "asr_delta" in effects

    def test_comparison_invalid_baseline_raises(self, baseline_arm, test_arm):
        """Using non-existent baseline should raise."""
        arms = {"baseline": baseline_arm, "entropy_gated": test_arm}
        with pytest.raises(ValueError, match="not found"):
            run_arms_comparison(
                loop="L21",
                corpus_name="test",
                arms_results=arms,
                baseline_arm_name="nonexistent",
            )


class TestComparisonToGateReport:
    """Tests for comparison_to_gate_report conversion."""

    def test_gate_report_conversion(self, baseline_arm, test_arm):
        """Comparison should convert to GateReport."""
        arms = {"baseline": baseline_arm, "entropy_gated": test_arm}
        comparison = run_arms_comparison(
            loop="L21",
            corpus_name="test_corpus",
            arms_results=arms,
            baseline_arm_name="baseline",
        )

        gate = comparison_to_gate_report(
            comparison,
            hypothesis_name="H_baseline_vs_gated",
            criteria={"min_concept_lift": 0.2, "max_asr_increase": 0.1},
        )

        assert gate.loop == "L21"
        assert gate.status == "closed"
        assert "H_baseline_vs_gated" in gate.domain_gate.evidence

    def test_gate_report_passes_criteria(self, baseline_arm, test_arm):
        """Gate should pass when criteria are met."""
        arms = {"baseline": baseline_arm, "entropy_gated": test_arm}
        comparison = run_arms_comparison(
            loop="L21",
            corpus_name="test",
            arms_results=arms,
            baseline_arm_name="baseline",
        )

        # test_arm has CSR=0.6, baseline=0.3 (lift=0.3 > 0.2 ✓)
        # test_arm has ASR=0.5, baseline=0.8 (delta=-0.3 < 0.1 ✓)
        gate = comparison_to_gate_report(
            comparison,
            hypothesis_name="H_test",
            criteria={"min_concept_lift": 0.2, "max_asr_increase": 0.1},
        )

        assert gate.domain_gate.verdict == "pass"

    def test_gate_report_fails_criteria(self, baseline_arm, test_arm):
        """Gate should fail domain when criteria are not met."""
        arms = {"baseline": baseline_arm, "entropy_gated": test_arm}
        comparison = run_arms_comparison(
            loop="L21",
            corpus_name="test",
            arms_results=arms,
            baseline_arm_name="baseline",
        )

        # This time, require very high CSR lift (unmet)
        # Must set code_gate_verdict to "fail" as well because dual-closure requires
        # both gates to pass|pruned for status="closed"
        gate = comparison_to_gate_report(
            comparison,
            hypothesis_name="H_test",
            criteria={"min_concept_lift": 0.5},  # test_arm only achieves 0.3 lift
            code_gate_verdict="fail",  # Must match domain gate verdict
        )

        assert gate.domain_gate.verdict == "fail"
        assert "CSR lift" in gate.domain_gate.evidence
