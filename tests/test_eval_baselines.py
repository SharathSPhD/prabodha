"""Unit tests for eval.baselines — LogitBiasProcessor tests (CPU only)."""
import pytest

pytest.importorskip("torch")

import torch
from prabodha.eval.baselines import LogitBiasProcessor, make_logit_bias_arm, is_logit_bias_processor


class TestLogitBiasProcessor:
    """Tests for LogitBiasProcessor."""

    def test_logit_bias_shifts_target_tokens(self):
        """Bias should increase logits of target tokens."""
        target_ids = [100, 200]
        processor = LogitBiasProcessor(target_ids, bias=5.0)

        # Mock scores: batch_size=2, vocab_size=300
        scores = torch.randn(2, 300)
        original_scores = scores.clone()

        result = processor(None, scores)

        # Check that target token logits increased
        assert (result[:, 100] > original_scores[:, 100] + 4.5).all()
        assert (result[:, 200] > original_scores[:, 200] + 4.5).all()

    def test_logit_bias_preserves_other_tokens(self):
        """Bias should not affect non-target tokens."""
        target_ids = [100]
        processor = LogitBiasProcessor(target_ids, bias=5.0)

        scores = torch.randn(1, 300)
        original_scores = scores.clone()

        result = processor(None, scores)

        # Non-target tokens should be unchanged
        for i in range(300):
            if i != 100:
                assert torch.allclose(result[0, i], original_scores[0, i])

    def test_logit_bias_respects_bias_magnitude(self):
        """Bias magnitude should match the specified value."""
        target_ids = [50]
        bias_val = 7.5
        processor = LogitBiasProcessor(target_ids, bias=bias_val)

        scores = torch.zeros(1, 100)
        result = processor(None, scores)

        assert abs(float(result[0, 50]) - bias_val) < 1e-5

    def test_logit_bias_factory(self):
        """Factory function should create valid processor."""
        processor = make_logit_bias_arm([100, 200], bias=3.0)
        assert is_logit_bias_processor(processor)
        assert isinstance(processor, LogitBiasProcessor)

    def test_logit_bias_type_check(self):
        """Type check should identify LogitBiasProcessor correctly."""
        processor = LogitBiasProcessor([100], bias=5.0)
        assert is_logit_bias_processor(processor)
        assert not is_logit_bias_processor("not a processor")
        assert not is_logit_bias_processor(None)

    def test_logit_bias_empty_targets(self):
        """Empty target list should be handled gracefully."""
        processor = LogitBiasProcessor([], bias=5.0)
        scores = torch.randn(1, 100)
        result = processor(None, scores)
        # Should return scores unchanged
        assert torch.allclose(result, scores)

    def test_logit_bias_out_of_vocab_targets(self):
        """Out-of-vocab token IDs should be clamped."""
        processor = LogitBiasProcessor([999], bias=5.0)  # Out of vocab
        scores = torch.randn(1, 100)
        original = scores.clone()
        result = processor(None, scores)
        # Should not raise; out-of-vocab IDs are simply skipped
        assert result.shape == original.shape
