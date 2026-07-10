"""Evaluation infrastructure for prabodha — reusable for batch experiments + live app labs.

Concept: pariksha (test) — integrated evaluation suite for steering arms.

Submodules:
- benchmarks: Offline prompt loaders (AdvBench, TruthfulQA, RefusalPairs).
- behavioral: Text scorers (refusal_rate, ASR, truthfulness_proxy, off_target_delta).
- baselines: Logit-bias steering arm for head-to-head baseline comparison.
- compare: Comparison harness + GateReport gate composer.
"""
from prabodha.eval.benchmarks import (
    AdvBenchItem,
    TruthfulQAItem,
    RefusalPair,
    advbench,
    truthfulqa,
    refusal_pairs,
)
from prabodha.eval.behavioral import (
    refusal_rate,
    attack_success_rate,
    truthfulness_proxy,
    off_target_delta,
)
from prabodha.eval.baselines import (
    LogitBiasProcessor,
    make_logit_bias_arm,
    is_logit_bias_processor,
)
from prabodha.eval.compare import (
    ArmResult,
    ComparisonReport,
    run_arms_comparison,
    comparison_to_gate_report,
)

__all__ = [
    # benchmarks
    "AdvBenchItem",
    "TruthfulQAItem",
    "RefusalPair",
    "advbench",
    "truthfulqa",
    "refusal_pairs",
    # behavioral
    "refusal_rate",
    "attack_success_rate",
    "truthfulness_proxy",
    "off_target_delta",
    # baselines
    "LogitBiasProcessor",
    "make_logit_bias_arm",
    "is_logit_bias_processor",
    # compare
    "ArmResult",
    "ComparisonReport",
    "run_arms_comparison",
    "comparison_to_gate_report",
]
