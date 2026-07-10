"""Test LiveEpisode schema.

Concept: sākṣāt-darśana — verify the gateway's response schema carries
all required fields for the app to visualize steering effects.
"""
from prabodha.contracts.trace import TraceToken, SteerTrace
from steer_gateway.schema import LiveEpisode


def test_live_episode_valid():
    """LiveEpisode schema accepts valid data."""
    tokens = [
        TraceToken(t=0, token=" The", entropy=2.1, gated=False),
        TraceToken(t=1, token=" fire", entropy=1.2, gated=True),
    ]
    trace = SteerTrace(
        model_id="test/model",
        prompt="test prompt",
        concept="fire",
        arm="entropy_gated",
        seed=42,
        alpha=0.3,
        tau_percentile=60,
        site_layer=24,
        tokens=tokens,
        created_at="2026-07-10T00:00:00Z",
    )
    episode = LiveEpisode(
        model_id="test/model",
        prompt="test prompt",
        concept="fire",
        arm="entropy_gated",
        site_layer=24,
        alpha=0.3,
        baseline_text="The fire burns bright",
        steered_text="The flame glows softly",
        trace=trace,
        created_at="2026-07-10T00:00:00Z",
    )
    assert episode.model_id == "test/model"
    assert episode.baseline_text == "The fire burns bright"
    assert episode.steered_text == "The flame glows softly"
    assert len(episode.trace.tokens) == 2


def test_live_episode_json_serializable():
    """LiveEpisode is JSON-serializable (for SSE)."""
    tokens = [TraceToken(t=0, token=" test", entropy=1.5, gated=False)]
    trace = SteerTrace(
        model_id="test/model",
        prompt="prompt",
        concept="test",
        arm="baseline",
        seed=0,
        alpha=0.1,
        tau_percentile=50,
        site_layer=12,
        tokens=tokens,
        created_at="2026-07-10T00:00:00Z",
    )
    episode = LiveEpisode(
        model_id="test/model",
        prompt="prompt",
        concept="test",
        arm="baseline",
        site_layer=12,
        alpha=0.1,
        baseline_text="test",
        steered_text="test",
        trace=trace,
        created_at="2026-07-10T00:00:00Z",
    )
    json_str = episode.model_dump_json()
    assert isinstance(json_str, str)
    assert "test/model" in json_str
    assert "baseline_text" in json_str
    assert "steered_text" in json_str


def test_live_episode_optional_fields():
    """LiveEpisode optional fields (readback, behavioral_hit) default to None."""
    tokens = [TraceToken(t=0, token="x", entropy=1.0, gated=False)]
    trace = SteerTrace(
        model_id="m", prompt="p", concept="c", arm="a", seed=0, alpha=0.1,
        tau_percentile=50, site_layer=10, tokens=tokens, created_at="2026-01-01T00:00:00Z"
    )
    episode = LiveEpisode(
        model_id="m", prompt="p", concept="c", arm="a", site_layer=10, alpha=0.1,
        baseline_text="b", steered_text="s", trace=trace, created_at="2026-01-01T00:00:00Z"
    )
    assert episode.readback is None
    assert episode.behavioral_hit is None
