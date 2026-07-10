"""Benchmarks — offline prompt set loaders for evaluation (BUNDLED, no network at runtime).

Concept: pramāṇa (valid knowledge source) — benchmarks are authoritative prompts that pin
behavior; bundled offline so evaluation runs are deterministic and reproducible.

Source: AdvBench (Zou et al. 2023), TruthfulQA (Lin et al. 2022).

Primitive: loaders return typed dataclass/pydantic lists; data bundled under src/prabodha/eval/data/
as compact JSON, clearly cited, and small (~20-40 items each for research subsets).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class AdvBenchItem:
    """A harmful instruction prompt for jailbreak-resistance testing."""
    prompt: str


@dataclass
class TruthfulQAItem:
    """A QA pair with correct/incorrect options for truthfulness evaluation."""
    question: str
    correct: list[str]  # One or more correct answers
    incorrect: list[str]  # Common misconception answers


@dataclass
class RefusalPair:
    """Contrastive pair: harmful request + corresponding refusal response."""
    harmful_request: str
    refusal_response: str


def _get_data_dir() -> Path:
    """Locate the bundled data directory."""
    return Path(__file__).parent / "data"


def advbench(n: Optional[int] = None) -> list[AdvBenchItem]:
    """Load AdvBench harmful-instruction prompts.

    Args:
        n: If provided, return first n items; otherwise return all.

    Returns:
        List of AdvBenchItem prompts ready for jailbreak-resistance testing.

    Raises:
        FileNotFoundError: If bundled data file is missing.

    Citation: Zou, A., Wang, S., Norelli, A., Sap, M., Saxe, A., & Gabriel, I. (2023).
    Representation Engineering Mistral-7B Instruct. arXiv:2312.06961
    """
    data_path = _get_data_dir() / "advbench_subset.json"
    if not data_path.exists():
        raise FileNotFoundError(f"AdvBench data not found at {data_path}")

    with open(data_path) as f:
        data = json.load(f)

    items = [AdvBenchItem(prompt=p) for p in data["prompts"]]
    return items[:n] if n is not None else items


def truthfulqa(n: Optional[int] = None) -> list[TruthfulQAItem]:
    """Load TruthfulQA question + answer options.

    Args:
        n: If provided, return first n items; otherwise return all.

    Returns:
        List of TruthfulQAItem with questions and correct/incorrect answers.

    Raises:
        FileNotFoundError: If bundled data file is missing.

    Citation: Lin, S., Hilton, J., & Evans, O. (2022). TruthfulQA: Measuring how models
    mimic human falsehoods. In Proceedings of the 60th Annual Meeting of the Association
    for Computational Linguistics (pp. 3027-3051).
    """
    data_path = _get_data_dir() / "truthfulqa_subset.json"
    if not data_path.exists():
        raise FileNotFoundError(f"TruthfulQA data not found at {data_path}")

    with open(data_path) as f:
        data = json.load(f)

    items = [
        TruthfulQAItem(
            question=item["question"],
            correct=item["correct"],
            incorrect=item["incorrect"]
        )
        for item in data["items"]
    ]
    return items[:n] if n is not None else items


def refusal_pairs(n: Optional[int] = None) -> list[RefusalPair]:
    """Load contrastive refusal pairs for building harmlessness steering directions.

    Args:
        n: If provided, return first n pairs; otherwise return all.

    Returns:
        List of RefusalPair (harmful_request, refusal_response) tuples.

    Raises:
        FileNotFoundError: If bundled data file is missing.
    """
    data_path = _get_data_dir() / "refusal_pairs.json"
    if not data_path.exists():
        raise FileNotFoundError(f"Refusal pairs data not found at {data_path}")

    with open(data_path) as f:
        data = json.load(f)

    items = [
        RefusalPair(
            harmful_request=pair["harmful_request"],
            refusal_response=pair["refusal_response"]
        )
        for pair in data["pairs"]
    ]
    return items[:n] if n is not None else items
