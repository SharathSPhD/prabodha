"""prabodha.hardening — L23 prayoga↔prabodha jailbreak→harden loop.

Concept: pratirodha (hardening/resistance). The jailbreak-refusal direction extracted
by prayoga is injected back into the residual stream by prabodha with entropy gating,
testing the hypothesis that gated hardening reduces jailbreak ASR comparably to naive
continuous addition while preserving freedom (lower over-refusal on benign prompts).

Primitive: fused loop (direction extraction → layer-wise ablation scan → entropy-gated
injection) using ONE underlying HF model, portable direction (numpy), and prabodha's
ResidualInjector with timing policies.

Source: L23 worklist; review #16 determinism discipline (fixed decoding, unit-direction).
"""

from prabodha.hardening.harden_loop import (
    run_hardening_loop,
    HardeningConfig,
    HardeningResult,
)

__all__ = [
    "run_hardening_loop",
    "HardeningConfig",
    "HardeningResult",
]
