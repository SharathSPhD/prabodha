"""Tests for bridge_trained.py — CittaStore-based write direction computation."""

import numpy as np
import pytest

torch = pytest.importorskip("torch")  # skip when optional [lens] extra absent (CI [dev])

from prabodha.steering.bridge_trained import TrainedBridgeWriter  # noqa: E402
from prabodha.steering.writer import WriteCommand  # noqa: E402


class MockCittaStore:
    """Minimal CittaStore mock for unit testing."""
    def __init__(self, dim: int = 768):
        self.dim = dim
        self._query_returns: dict[str, torch.Tensor] = {}

    def recall(self, query: torch.Tensor, level: int = 0) -> torch.Tensor:
        """Return a fixed direction derived from query (for deterministic testing)."""
        # Deterministic but non-trivial: return a weighted sum of query and its reflection
        return 0.7 * query + 0.3 * torch.ones_like(query) * 0.1

    def hopfield_entropy(self, level: int = 0) -> float:
        """Mock entropy."""
        return 0.5


def test_trained_bridge_writer_init():
    """Test that TrainedBridgeWriter initializes with CittaStore."""
    citta = MockCittaStore(dim=768)
    writer = TrainedBridgeWriter(citta, write_layer=24, tau_percentile=60)
    assert writer.write_layer == 24
    assert writer.citta_store is citta


def test_trained_bridge_plan_write_returns_write_command():
    """Test that plan_write produces a WriteCommand conforming to the interface."""
    citta = MockCittaStore(dim=768)
    writer = TrainedBridgeWriter(citta, write_layer=24)

    # Mock unembedding rows (would normally be U[concept_ids] from model)
    u_rows = np.random.randn(3, 768).astype(np.float32)
    concept_ids = [1024, 2048, 4096]

    cmd = writer.plan_write(
        u_rows=u_rows,
        concept_ids=concept_ids,
        alpha=0.1,
        norm_cap_rel=1.0,
        weights=None,  # Uniform weighting
    )

    # Verify WriteCommand shape and properties
    assert isinstance(cmd, WriteCommand)
    assert cmd.layer == 24
    assert len(cmd.direction) == 768
    assert np.linalg.norm(cmd.direction) <= 1.01, "direction should be close to unit norm"
    assert cmd.alpha == 0.1
    assert cmd.norm_cap_rel == 1.0
    assert cmd.concept_ids == tuple(concept_ids)


def test_trained_bridge_rejects_negative_weights():
    """Test that negative weights are rejected (svātantrya doctrine)."""
    citta = MockCittaStore(dim=768)
    writer = TrainedBridgeWriter(citta, write_layer=24)
    u_rows = np.random.randn(3, 768).astype(np.float32)
    concept_ids = [1024, 2048, 4096]
    bad_weights = np.array([0.5, -0.1, 0.6])

    with pytest.raises(ValueError, match="non-negative"):
        writer.plan_write(
            u_rows=u_rows,
            concept_ids=concept_ids,
            alpha=0.1,
            norm_cap_rel=1.0,
            weights=bad_weights,
        )


def test_trained_bridge_direction_reproducibility():
    """Test that identical inputs produce identical direction (determinism check)."""
    citta = MockCittaStore(dim=768)
    writer = TrainedBridgeWriter(citta, write_layer=24)
    u_rows = np.random.randn(3, 768).astype(np.float32)
    concept_ids = [1024, 2048, 4096]

    cmd1 = writer.plan_write(u_rows, concept_ids, alpha=0.1, norm_cap_rel=1.0)
    cmd2 = writer.plan_write(u_rows, concept_ids, alpha=0.1, norm_cap_rel=1.0)

    np.testing.assert_array_almost_equal(cmd1.direction, cmd2.direction,
                                         err_msg="Identical inputs should produce identical directions")


def test_trained_bridge_zero_query_handling():
    """Test graceful handling when CittaStore returns zero or degenerate vectors."""

    class ZeroCittaStore(MockCittaStore):
        def recall(self, query, level=0):
            # Return a zero vector to test degenerate case
            return torch.zeros_like(query)

    citta = ZeroCittaStore(dim=768)
    writer = TrainedBridgeWriter(citta, write_layer=24)
    u_rows = np.random.randn(3, 768).astype(np.float32)
    concept_ids = [1024, 2048, 4096]

    # Should handle gracefully (either raise or fall back to a safe default)
    # Current expectation: raises ValueError on degenerate direction
    with pytest.raises(ValueError, match="degenerate"):
        writer.plan_write(u_rows, concept_ids, alpha=0.1, norm_cap_rel=1.0)
