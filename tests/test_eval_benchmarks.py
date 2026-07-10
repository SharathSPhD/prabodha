"""Unit tests for eval.benchmarks — data loader tests (CPU only, no network)."""
from prabodha.eval.benchmarks import advbench, truthfulqa, refusal_pairs


class TestAdvBenchLoader:
    """Tests for AdvBench loader."""

    def test_advbench_loads_all(self):
        """AdvBench loader returns expected number of items."""
        items = advbench()
        assert len(items) > 0, "AdvBench should not be empty"
        assert all(hasattr(item, 'prompt') for item in items)

    def test_advbench_with_limit(self):
        """AdvBench loader respects limit parameter."""
        items_full = advbench()
        items_limited = advbench(n=5)
        assert len(items_limited) == min(5, len(items_full))

    def test_advbench_items_well_formed(self):
        """AdvBench items have non-empty prompts."""
        items = advbench(n=3)
        for item in items:
            assert len(item.prompt) > 0
            assert isinstance(item.prompt, str)


class TestTruthfulQALoader:
    """Tests for TruthfulQA loader."""

    def test_truthfulqa_loads_all(self):
        """TruthfulQA loader returns expected number of items."""
        items = truthfulqa()
        assert len(items) > 0, "TruthfulQA should not be empty"
        assert all(hasattr(item, 'question') for item in items)
        assert all(hasattr(item, 'correct') for item in items)
        assert all(hasattr(item, 'incorrect') for item in items)

    def test_truthfulqa_with_limit(self):
        """TruthfulQA loader respects limit parameter."""
        items_full = truthfulqa()
        items_limited = truthfulqa(n=5)
        assert len(items_limited) == min(5, len(items_full))

    def test_truthfulqa_items_well_formed(self):
        """TruthfulQA items have questions and answer options."""
        items = truthfulqa(n=2)
        for item in items:
            assert len(item.question) > 0
            assert len(item.correct) > 0
            assert len(item.incorrect) > 0
            assert isinstance(item.correct, list)
            assert isinstance(item.incorrect, list)


class TestRefusalPairsLoader:
    """Tests for RefusalPairs loader."""

    def test_refusal_pairs_loads_all(self):
        """Refusal pairs loader returns expected number of items."""
        items = refusal_pairs()
        assert len(items) > 0, "Refusal pairs should not be empty"
        assert all(hasattr(item, 'harmful_request') for item in items)
        assert all(hasattr(item, 'refusal_response') for item in items)

    def test_refusal_pairs_with_limit(self):
        """Refusal pairs loader respects limit parameter."""
        items_full = refusal_pairs()
        items_limited = refusal_pairs(n=3)
        assert len(items_limited) == min(3, len(items_full))

    def test_refusal_pairs_well_formed(self):
        """Refusal pairs have both request and response."""
        items = refusal_pairs(n=2)
        for item in items:
            assert len(item.harmful_request) > 0
            assert len(item.refusal_response) > 0
            # Sanity: refusal should be longer than request on average
            # (it explains why)
            assert len(item.refusal_response) >= 10
