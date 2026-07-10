"""Baselines — logit_bias steering arm as H5b-style head-to-head comparator.

Concept: pratidvandva (rival) — a baseline steering arm that is orthogonal to the
concept-space arms (continuous, entropy_gated) in order to provide credible negative control.

Source: H5b protocol (PWM); paper Table 1 comparator requirement.

Primitive: LogitsProcessor subclass, invocable like e4_cli's arm signatures.
"""
from __future__ import annotations


class LogitBiasProcessor:
    """A simple logits processor that adds a fixed bias to target token logits.

    This processor mirrors the signature of e4_cli's timing-based arms but operates
    via logit manipulation instead of injected steering directions. It provides a
    head-to-head baseline: if concept steering (continuous/entropy_gated) beats logit_bias,
    the effect is not merely "increasing concept token probability" but specific to
    the steering method.

    LIMITATION: logit_bias is a crude lever — it affects ALL instances of the target tokens
    uniformly across the sequence, whereas concept steering is more nuanced (layer-specific,
    injected at chosen timing). This is intentional for a baseline.
    """

    def __init__(self, concept_token_ids: list[int], bias: float = 5.0):
        """Initialize the logit-bias processor.

        Args:
            concept_token_ids: List of token IDs to bias upward (e.g., concept tokens).
            bias: Logit bias value to ADD to scores of target tokens. Positive increases
                  their probability. Default 5.0 is roughly +exp(5) ≈ 150x ratio.
        """
        self.concept_token_ids = set(concept_token_ids)
        self.bias = float(bias)

    def __call__(self, input_ids, scores):
        """Apply logit bias: add bias to target tokens' logits.

        Args:
            input_ids: Tensor of shape [batch, seq_len] (ignored; we modify scores uniformly).
            scores: Tensor of shape [batch, vocab_size] (the next-token logits).

        Returns:
            Modified scores with bias applied.

        Note: This is a simple procedural processor. Integration with transformers'
        LogitsProcessorList requires wrapping in a torch.nn.Module or exposing __call__
        as a LogitsProcessor. See compare.py for usage context.
        """
        import torch

        # Clone to avoid in-place modification of input
        scores = scores.clone() if isinstance(scores, torch.Tensor) else scores

        # Add bias to concept token IDs (batch-wise: all examples get same bias)
        for tid in self.concept_token_ids:
            if tid < scores.shape[-1]:
                scores[:, tid] += self.bias

        return scores


def make_logit_bias_arm(concept_token_ids: list[int], bias: float = 5.0) -> LogitBiasProcessor:
    """Factory for a logit-bias steering arm.

    Args:
        concept_token_ids: Token IDs to bias.
        bias: Logit bias magnitude.

    Returns:
        A LogitBiasProcessor ready to pass to the generation pipeline.

    Usage:
        bias_arm = make_logit_bias_arm([1000, 2000], bias=5.0)
        # Then use in generation: logits_processor=LogitsProcessorList([bias_arm])
    """
    return LogitBiasProcessor(concept_token_ids, bias)


def is_logit_bias_processor(obj) -> bool:
    """Type check for LogitBiasProcessor."""
    return isinstance(obj, LogitBiasProcessor)
