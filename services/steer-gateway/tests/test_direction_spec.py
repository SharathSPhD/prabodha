"""Test DirectionSpec and direction_source schema.

Concept: verify the gateway's direction_spec contract for contrastive and vector steering.
"""
import pytest
from steer_gateway.schema import DirectionSpec, LiveEpisode
from prabodha.contracts.trace import TraceToken, SteerTrace


def test_direction_spec_concept_mode():
    """DirectionSpec with mode='concept' is valid."""
    spec = DirectionSpec(mode="concept", concept="fire")
    assert spec.mode == "concept"
    assert spec.concept == "fire"
    assert spec.pos_texts is None
    assert spec.neg_texts is None
    assert spec.vector is None


def test_direction_spec_contrastive_mode():
    """DirectionSpec with mode='contrastive' requires pos_texts and neg_texts."""
    spec = DirectionSpec(
        mode="contrastive",
        pos_texts=["Refusal text 1", "Refusal text 2"],
        neg_texts=["Harmful compliance 1", "Harmful compliance 2"],
    )
    assert spec.mode == "contrastive"
    assert len(spec.pos_texts) == 2
    assert len(spec.neg_texts) == 2


def test_direction_spec_vector_mode():
    """DirectionSpec with mode='vector' requires a vector."""
    spec = DirectionSpec(
        mode="vector",
        vector=[0.1, 0.2, 0.3, 0.4],
    )
    assert spec.mode == "vector"
    assert len(spec.vector) == 4


def test_live_episode_with_direction_source():
    """LiveEpisode direction_source field is optional and properly serialized."""
    tokens = [TraceToken(t=0, token=" test", entropy=1.5, gated=False)]
    trace = SteerTrace(
        model_id="test/model",
        prompt="prompt",
        concept="refusal",
        arm="entropy_gated",
        seed=0,
        alpha=0.3,
        tau_percentile=60,
        site_layer=24,
        tokens=tokens,
        created_at="2026-07-10T00:00:00Z",
    )

    # Test with direction_source set
    episode = LiveEpisode(
        model_id="test/model",
        prompt="prompt",
        concept="refusal",
        arm="entropy_gated",
        site_layer=24,
        alpha=0.3,
        baseline_text="I can help with that",
        steered_text="I cannot help with that",
        trace=trace,
        direction_source="contrastive:refusal(5+/5-)",
        created_at="2026-07-10T00:00:00Z",
    )
    assert episode.direction_source == "contrastive:refusal(5+/5-)"

    # Test without direction_source (should default to None)
    episode2 = LiveEpisode(
        model_id="test/model",
        prompt="prompt",
        concept="fire",
        arm="baseline",
        site_layer=24,
        alpha=0.3,
        baseline_text="The fire burns",
        steered_text="The fire burns",
        trace=trace,
        created_at="2026-07-10T00:00:00Z",
    )
    assert episode2.direction_source is None


def test_live_episode_direction_source_serialization():
    """LiveEpisode with direction_source is JSON-serializable."""
    tokens = [TraceToken(t=0, token=" x", entropy=1.0, gated=False)]
    trace = SteerTrace(
        model_id="m", prompt="p", concept="c", arm="a", seed=0, alpha=0.1,
        tau_percentile=50, site_layer=10, tokens=tokens, created_at="2026-01-01T00:00:00Z"
    )
    episode = LiveEpisode(
        model_id="m", prompt="p", concept="c", arm="a", site_layer=10, alpha=0.1,
        baseline_text="b", steered_text="s", trace=trace,
        direction_source="vector", created_at="2026-01-01T00:00:00Z"
    )
    json_str = episode.model_dump_json()
    assert isinstance(json_str, str)
    assert "direction_source" in json_str
    assert "vector" in json_str
