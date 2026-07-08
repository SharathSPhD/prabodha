"""scoring — text-only camatkāra + behavioral concept-surface rate for E3 arms.
Concept: camatkāra (aesthetic flash) as a QUALITY GUARD on steering — a write that gets the
concept said but flattens the saying has failed the doctrine.
Source: PWM pwm/eval/h5_ablation.py score_camatk_text (ported verbatim in spirit, weights
0.40 structure / 0.35 length / 0.25 imagery; VFE term omitted by design there — no WM
energy reading in LLM-only comparisons; port pre-authorized by operator, HANDOFF §5 mid).
Primitive: pure python, host-testable.
"""
from __future__ import annotations


def score_camatk_text(text: str) -> float:
    """Text-only camatkāra in [0, 1] (PWM H5b protocol; weights preserved for
    comparability with PWM's published H5b numbers)."""
    words = text.split()
    wc = len(words)
    r_length = min(1.0, wc / 80.0)
    unique = len({w.lower() for w in words})
    r_imagery = min(1.0, (unique / max(1, wc)) * 1.8)
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    r_structure = min(1.0, len(lines) / 4.0)
    return min(1.0, 0.40 * r_structure + 0.35 * r_length + 0.25 * r_imagery)


def concept_surface_rate(texts: list[str], concept: str) -> float:
    """Fraction of generations in which the concept word surfaces (case-insensitive,
    substring-on-word-boundary via simple token match). The E3 behavioral outcome."""
    c = concept.lower()
    hits = sum(any(w.strip('.,;:!?"()').lower() == c for w in t.split()) for t in texts)
    return hits / len(texts) if texts else 0.0
