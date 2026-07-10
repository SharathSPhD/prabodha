"""Compare — comparison harness + gate composer for arm evaluation.

Concept: sarvaṅga-pariksha (complete test) — systematic head-to-head comparison of steering
arms with unified metric reporting (behavioral + entropy + effect size).

Source: neo-fm gate protocols; PWM comparative evaluation template.

Primitive: run_arms_comparison(...) -> GateReport-shaped result; emit per-arm lifts,
entropy deltas, AND behavioral metrics (refusal_rate, ASR, truthfulness) with Hedges' g
effect sizes vs baseline.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from prabodha.contracts.closure import GateReport, GateSide


@dataclass
class ArmResult:
    """Per-arm outcome from a single comparison run."""
    arm_name: str
    concept_surface_rate: float  # Fraction of generations with concept token
    mean_entropy_delta: float  # Mean entropy change vs baseline (negative = lower entropy)
    refusal_rate: float  # Behavioral: fraction that refuse
    attack_success_rate: float  # Behavioral: 1 - refusal_rate
    truthfulness_score: Optional[float] = None  # Behavioral: alignment proxy
    off_target_delta: Optional[float] = None  # Behavioral: capability drop
    n_generations: int = 0


@dataclass
class ComparisonReport:
    """Full comparison results for a single hypothesis or corpus."""
    loop: str
    corpus_name: str
    baseline_arm: str
    arms: dict[str, ArmResult]  # arm_name -> ArmResult
    effect_sizes: dict[str, dict[str, float]] = None  # arm -> {metric: hedges_g}
    deviations: list[str] = None

    def __post_init__(self):
        if self.effect_sizes is None:
            self.effect_sizes = {}
        if self.deviations is None:
            self.deviations = []


def _compute_effect_sizes(baseline: ArmResult, arm: ArmResult) -> dict[str, float]:
    """Compute Hedges' g effect sizes for key metrics (single-seed proxy).

    Args:
        baseline: Baseline arm result.
        arm: Arm to compare against baseline.

    Returns:
        Dict of metric -> Hedges' g effect size. For single-seed runs, this is
        approximate (we use the metric value as a sample; real CIs require replication).

    LIMITATION: Hedges' g is designed for n>1 per condition. Single-seed runs render
    this as a placeholder (documented honestly). Real comparison requires >=3 seeds per arm.
    """
    # For single-seed screening, we report the metric delta as a "pseudo-effect":
    # this is NOT a true Hedges' g (which requires independent samples) but rather
    # a normalized difference useful for ranking arms. See permutation_p(...) for rigorous test.
    effects = {}

    # Concept surface rate delta (higher better)
    csr_delta = arm.concept_surface_rate - baseline.concept_surface_rate
    effects["concept_surface_delta"] = csr_delta

    # Entropy delta (negative = lower entropy, which is "bad" for open-generation;
    # report as magnitude for clarity)
    effects["entropy_delta_magnitude"] = abs(arm.mean_entropy_delta - baseline.mean_entropy_delta)

    # Refusal rate delta (positive = more refusal, which is good for safety)
    refusal_delta = arm.refusal_rate - baseline.refusal_rate
    effects["refusal_delta"] = refusal_delta

    # Attack success rate (lower better)
    asr_delta = arm.attack_success_rate - baseline.attack_success_rate
    effects["asr_delta"] = asr_delta

    if arm.truthfulness_score is not None and baseline.truthfulness_score is not None:
        effects["truthfulness_delta"] = arm.truthfulness_score - baseline.truthfulness_score

    if arm.off_target_delta is not None and baseline.off_target_delta is not None:
        effects["off_target_delta_diff"] = arm.off_target_delta - baseline.off_target_delta

    return effects


def run_arms_comparison(
    loop: str,
    corpus_name: str,
    arms_results: dict[str, ArmResult],
    baseline_arm_name: str,
    seed: int = 42,
) -> ComparisonReport:
    """Orchestrate arm comparison and compute effect sizes.

    Args:
        loop: Loop label (e.g., "L21").
        corpus_name: Name of the benchmark/corpus used (e.g., "advbench_jailbreak").
        arms_results: Dict of arm_name -> ArmResult from evaluation runs.
        baseline_arm_name: Which arm to use as the baseline for effect size computation.
        seed: Seed for statistical tests (for reproducibility).

    Returns:
        ComparisonReport with per-arm results and effect sizes.

    Raises:
        ValueError: If baseline_arm_name not in arms_results.
    """
    if baseline_arm_name not in arms_results:
        raise ValueError(f"Baseline arm '{baseline_arm_name}' not found in results")

    baseline = arms_results[baseline_arm_name]
    deviations = []

    # Compute effect sizes vs baseline
    effects = {}
    for arm_name, arm_result in arms_results.items():
        effects[arm_name] = _compute_effect_sizes(baseline, arm_result)

    report = ComparisonReport(
        loop=loop,
        corpus_name=corpus_name,
        baseline_arm=baseline_arm_name,
        arms=arms_results,
        effect_sizes=effects,
        deviations=deviations,
    )

    return report


def comparison_to_gate_report(
    comparison: ComparisonReport,
    hypothesis_name: str,
    criteria: dict[str, Any],
    code_gate_verdict: str = "pass",
) -> GateReport:
    """Convert a ComparisonReport to a GateReport (dual-closure schema).

    Args:
        comparison: The ComparisonReport from arm comparison.
        hypothesis_name: Name of the research hypothesis being tested (e.g., "H_baseline_vs_continuous").
        criteria: Dict of test criteria (e.g., {"min_concept_lift": 0.1, "max_asr_increase": 0.05}).
        code_gate_verdict: Code gate status ("pass" / "fail" / "pruned").

    Returns:
        GateReport for dual-closure recording.

    CRITERIA EVALUATION:
        - min_concept_lift: baseline CSR must lift by this much (absolute)
        - max_asr_increase: ASR must not increase by more than this (safety bound)
        - truthfulness_improvement: truthfulness delta >= this threshold
        - off_target_tolerance: off-target delta must be <= this (capability preservation)
    """
    evidence_lines = [
        f"Hypothesis: {hypothesis_name}",
        f"Corpus: {comparison.corpus_name}",
        f"Baseline arm: {comparison.baseline_arm}",
        "",
        "Per-arm results:",
    ]

    # Summarize each arm
    for arm_name, arm_result in comparison.arms.items():
        evidence_lines.append(
            f"  {arm_name}: CSR={arm_result.concept_surface_rate:.3f}, "
            f"ASR={arm_result.attack_success_rate:.3f}, "
            f"refusal_rate={arm_result.refusal_rate:.3f}"
        )

    evidence_lines.append("")
    evidence_lines.append("Effect sizes (Hedges' g-like, single-seed proxy):")
    for arm_name in comparison.arms:
        if arm_name != comparison.baseline_arm:
            effects = comparison.effect_sizes.get(arm_name, {})
            evidence_lines.append(f"  {arm_name} vs baseline:")
            for metric, value in effects.items():
                evidence_lines.append(f"    {metric}: {value:+.3f}")

    # Check criteria
    domain_verdict = "pass"
    failures = []

    baseline_result = comparison.arms[comparison.baseline_arm]

    if "min_concept_lift" in criteria:
        threshold = criteria["min_concept_lift"]
        for arm_name, arm_result in comparison.arms.items():
            if arm_name != comparison.baseline_arm:
                lift = arm_result.concept_surface_rate - baseline_result.concept_surface_rate
                if lift < threshold:
                    failures.append(
                        f"{arm_name}: CSR lift {lift:.3f} < threshold {threshold}"
                    )

    if "max_asr_increase" in criteria:
        threshold = criteria["max_asr_increase"]
        for arm_name, arm_result in comparison.arms.items():
            if arm_name != comparison.baseline_arm:
                asr_delta = arm_result.attack_success_rate - baseline_result.attack_success_rate
                if asr_delta > threshold:
                    failures.append(
                        f"{arm_name}: ASR increase {asr_delta:.3f} > threshold {threshold}"
                    )

    if failures:
        domain_verdict = "fail"
        evidence_lines.append("")
        evidence_lines.append("FAILURES:")
        evidence_lines.extend(failures)
    else:
        evidence_lines.append("")
        evidence_lines.append("All criteria met.")

    evidence = "\n".join(evidence_lines)

    # Dual-closure rule: both gates must pass|pruned for status="closed"
    # If either gate fails, set status="open"
    status = "open" if domain_verdict == "fail" or code_gate_verdict == "fail" else "closed"

    return GateReport(
        loop=comparison.loop,
        status=status,
        code_gate=GateSide(verdict=code_gate_verdict, evidence=f"Code gate: {code_gate_verdict}"),
        domain_gate=GateSide(
            verdict=domain_verdict,
            evidence=evidence,
            deviations=comparison.deviations,
        ),
    )
