"""Test FastAPI gateway endpoints and SSE integration.

Concept: I3 interface verification — the gateway serves as an SSE proxy.
Tests verify the authentication, request/response contract, and SSE framing.
"""
import os
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
import pytest

from prabodha.contracts.trace import TraceToken, SteerTrace
from steer_gateway.schema import LiveEpisode


# Patch environment before importing main
os.environ["STEER_GATEWAY_SECRET"] = "test-secret"

from steer_gateway.main import app  # noqa: E402


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


def test_health_check(client):
    """GET /health returns model_id (no auth required)."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["ok"] is True
    # model_id may be "uninitialized" if runtime is not set


def test_steer_missing_bearer_token(client):
    """POST /steer without Bearer token returns 401."""
    response = client.post(
        "/steer",
        json={"prompt": "test", "concept": "fire"}
    )
    assert response.status_code == 401


def test_steer_invalid_bearer_token(client):
    """POST /steer with invalid token returns 403."""
    response = client.post(
        "/steer",
        json={"prompt": "test", "concept": "fire"},
        headers={"Authorization": "Bearer wrong-token"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_steer_stream_mock_runtime(client):
    """POST /steer with valid token streams SSE events."""
    # Mock the runtime to avoid GPU/model loading
    mock_runtime = AsyncMock()

    # Create mock episode
    tokens = [
        TraceToken(t=0, token=" The", entropy=2.1, gated=False),
        TraceToken(t=1, token=" fire", entropy=1.2, gated=True),
    ]
    trace = SteerTrace(
        model_id="mock/model",
        prompt="test",
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
        model_id="mock/model",
        prompt="test",
        concept="fire",
        arm="entropy_gated",
        site_layer=24,
        alpha=0.3,
        baseline_text="The fire burns",
        steered_text="The flame glows",
        trace=trace,
        created_at="2026-07-10T00:00:00Z",
    )

    # Mock steer_stream to yield tokens then episode
    async def mock_steer_stream(*args, **kwargs):
        for tok in tokens:
            yield tok
        yield episode

    mock_runtime.steer_stream = mock_steer_stream

    with patch("steer_gateway.main.runtime", mock_runtime):
        response = client.post(
            "/steer",
            json={"prompt": "test", "concept": "fire", "alpha": 0.3, "arm": "entropy_gated"},
            headers={"Authorization": "Bearer test-secret"}
        )

        # Check SSE response
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]

        # Parse SSE events
        events = response.text.split("\n\n")
        events = [e.strip() for e in events if e.strip()]

        # Expect 2 token events + 1 done event
        assert len(events) >= 3
        assert events[0].startswith("event: token")
        assert events[1].startswith("event: token")
        assert events[2].startswith("event: done")

        # Verify done event contains baseline_text and steered_text
        done_event = events[2]
        assert "baseline_text" in done_event
        assert "steered_text" in done_event
        assert "The fire burns" in done_event
        assert "The flame glows" in done_event


def test_steer_request_schema_validation(client):
    """POST /steer validates request schema."""
    # Missing required 'concept' field
    response = client.post(
        "/steer",
        json={"prompt": "test"},
        headers={"Authorization": "Bearer test-secret"}
    )
    assert response.status_code == 422  # Validation error


def test_steer_request_defaults(client):
    """SteerRequest uses default arm if not provided."""
    from steer_gateway.main import SteerRequest
    req = SteerRequest(prompt="test", concept="fire")
    assert req.arm == "entropy_gated"  # default
    assert req.alpha is None


def test_steer_request_custom_params(client):
    """SteerRequest accepts all parameters."""
    from steer_gateway.main import SteerRequest
    req = SteerRequest(
        prompt="test",
        concept="honesty",
        alpha=0.5,
        arm="continuous"
    )
    assert req.prompt == "test"
    assert req.concept == "honesty"
    assert req.alpha == 0.5
    assert req.arm == "continuous"
