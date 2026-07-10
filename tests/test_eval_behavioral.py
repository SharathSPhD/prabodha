"""Unit tests for eval.behavioral — text scorer tests (CPU only)."""
import pytest

from prabodha.eval.behavioral import (
    refusal_rate,
    attack_success_rate,
    truthfulness_proxy,
    off_target_delta,
)


class TestRefusalRate:
    """Tests for refusal_rate heuristic scorer."""

    def test_refusal_rate_all_refuse(self):
        """All refusing texts should yield refusal_rate ≈ 1.0."""
        texts = [
            "I can't help with that.",
            "I cannot assist.",
            "I'm not able to do this.",
        ]
        rate = refusal_rate(texts)
        assert rate > 0.9, f"Expected high refusal rate, got {rate}"

    def test_refusal_rate_none_refuse(self):
        """No refusing texts should yield refusal_rate ≈ 0.0."""
        texts = [
            "Here is the answer to your question.",
            "The capital of France is Paris.",
            "Yes, I can help you with that.",
        ]
        rate = refusal_rate(texts)
        assert rate < 0.1, f"Expected low refusal rate, got {rate}"

    def test_refusal_rate_mixed(self):
        """Mixed texts should yield refusal_rate between 0 and 1."""
        texts = [
            "I can't help with that.",
            "The capital of France is Paris.",
            "I cannot assist.",
        ]
        rate = refusal_rate(texts)
        assert 0.4 < rate < 0.8, f"Expected mid-range refusal rate, got {rate}"

    def test_refusal_rate_empty(self):
        """Empty text list should return 0."""
        rate = refusal_rate([])
        assert rate == 0.0

    def test_refusal_rate_case_insensitive(self):
        """Refusal patterns should be case-insensitive."""
        texts = [
            "I CAN'T HELP WITH THAT.",
            "I Cannot assist.",
        ]
        rate = refusal_rate(texts)
        assert rate > 0.8, f"Expected high refusal rate (case-insensitive), got {rate}"

    def test_refusal_rate_with_llm_judge(self):
        """Can override with custom LLM judge."""
        def custom_judge(text):
            return "refused" in text.lower()

        texts = [
            "I refused to help.",
            "Here is the answer.",
        ]
        rate = refusal_rate(texts, llm_judge=custom_judge)
        assert rate == 0.5


class TestAttackSuccessRate:
    """Tests for attack_success_rate (inverse of refusal_rate)."""

    def test_asr_is_inverse_of_refusal(self):
        """ASR should be 1 - refusal_rate."""
        texts = [
            "I can't help with that.",
            "The capital is Paris.",
        ]
        ref_rate = refusal_rate(texts)
        asr = attack_success_rate(texts)
        assert abs(asr - (1 - ref_rate)) < 1e-6


class TestTruthfulnessProxy:
    """Tests for truthfulness_proxy (string overlap heuristic)."""

    def test_truthfulness_exact_correct_match(self):
        """Exact match to correct should score high."""
        score = truthfulness_proxy(
            question="What is 2+2?",
            answer_text="The answer is 4.",
            correct_options=["4", "four"],
            incorrect_options=["5", "3"],
        )
        assert score > 0.7, f"Expected high score for correct match, got {score}"

    def test_truthfulness_incorrect_match(self):
        """Exact match to incorrect should score low."""
        score = truthfulness_proxy(
            question="What is 2+2?",
            answer_text="The answer is 5.",
            correct_options=["4", "four"],
            incorrect_options=["5", "3"],
        )
        assert score < 0.3, f"Expected low score for incorrect match, got {score}"

    def test_truthfulness_no_match(self):
        """No match to either should score neutral."""
        score = truthfulness_proxy(
            question="What is 2+2?",
            answer_text="I don't know the answer.",
            correct_options=["4", "four"],
            incorrect_options=["5", "3"],
        )
        # Should be in the middle or somewhat neutral
        assert 0.2 < score < 0.8, f"Expected neutral score, got {score}"

    def test_truthfulness_substring_match(self):
        """Substring matches should count."""
        score = truthfulness_proxy(
            question="Capitals?",
            answer_text="Paris is capital of France.",
            correct_options=["Paris", "France"],
            incorrect_options=["London", "Berlin"],
        )
        assert score > 0.5, f"Expected mid-high score for substring matches, got {score}"

    def test_truthfulness_with_semantic_scorer(self):
        """Can override with semantic similarity function."""
        def mock_semantic(text, option):
            # Mock: return 1.0 if substring match, 0.0 otherwise
            return 1.0 if option.lower() in text.lower() else 0.0

        score = truthfulness_proxy(
            question="Capital?",
            answer_text="Paris",
            correct_options=["Paris"],
            incorrect_options=["London"],
            semantic_scorer=mock_semantic,
        )
        assert score > 0.8, f"Expected high semantic score, got {score}"


class TestOffTargetDelta:
    """Tests for off_target_delta (capability drop metric)."""

    def test_off_target_delta_no_drop(self):
        """No capability drop should be 0."""
        delta = off_target_delta(baseline_acc=0.8, steered_acc=0.8)
        assert delta == 0.0

    def test_off_target_delta_full_loss(self):
        """Complete loss should be 1.0."""
        delta = off_target_delta(baseline_acc=0.8, steered_acc=0.0)
        assert delta == 1.0

    def test_off_target_delta_partial_loss(self):
        """Partial loss should be between 0 and 1."""
        delta = off_target_delta(baseline_acc=1.0, steered_acc=0.5)
        assert abs(delta - 0.5) < 1e-6, f"Expected 0.5, got {delta}"

    def test_off_target_delta_improvement_ok(self):
        """Improvement (steered_acc > baseline) should clip to 0."""
        delta = off_target_delta(baseline_acc=0.6, steered_acc=0.8)
        assert delta == 0.0, "Improvement should not penalize"

    def test_off_target_delta_zero_baseline(self):
        """Zero baseline should not divide by zero."""
        delta = off_target_delta(baseline_acc=0.0, steered_acc=0.5)
        assert delta == 0.0, "Zero baseline should return 0"

    def test_off_target_delta_negative_raises(self):
        """Negative accuracies should raise."""
        with pytest.raises(ValueError):
            off_target_delta(baseline_acc=-0.1, steered_acc=0.5)
