"""Tests for prabodha.steering.direction — CAA-style contrastive steering.

Concept: Unit tests for contrastive_direction and apply_direction_write (CPU-only, no model).

Discipline: All tests must pass on CPU with fake activations. No imports of torch or model-loading
code should be required. Tests exercise the core numpy logic and WriteCommand composition.
"""
import pytest
import numpy as np

from prabodha.steering.direction import contrastive_direction, apply_direction_write
from prabodha.steering.writer import WriteCommand


class TestContrastiveDirection:
    """Tests for contrastive_direction function."""

    def test_basic_direction_computation(self):
        """Test direction = normalize(mean(pos) - mean(neg))."""
        # Simple case: pos all ones, neg all zeros
        pos = np.array([[1.0, 0.0], [1.0, 0.0]], dtype=np.float64)
        neg = np.array([[0.0, 0.0], [0.0, 0.0]], dtype=np.float64)
        
        direction = contrastive_direction(pos, neg)
        
        # Direction should be [1, 0] normalized
        assert direction.shape == (2,)
        assert np.isclose(np.linalg.norm(direction), 1.0), "Direction should be unit norm"
        # [1, 0] normalized is [1, 0]
        assert np.allclose(direction, np.array([1.0, 0.0], dtype=np.float64), atol=1e-5)

    def test_direction_three_dimensional(self):
        """Test on 3D activations."""
        pos = np.array([[1.0, 0.0, 0.0], [1.0, 0.0, 0.0]], dtype=np.float64)
        neg = np.array([[-1.0, 0.0, 0.0], [-1.0, 0.0, 0.0]], dtype=np.float64)
        
        direction = contrastive_direction(pos, neg)
        
        assert direction.shape == (3,)
        assert np.isclose(np.linalg.norm(direction), 1.0)
        # Direction should be [1, 0, 0] (difference in first dimension)
        assert np.allclose(direction, np.array([1.0, 0.0, 0.0], dtype=np.float64), atol=1e-5)

    def test_direction_multiple_examples(self):
        """Test with multiple positive and negative examples."""
        np.random.seed(42)
        pos = np.random.randn(5, 10)
        neg = np.random.randn(5, 10)
        
        direction = contrastive_direction(pos, neg)
        
        assert direction.shape == (10,)
        assert np.isclose(np.linalg.norm(direction), 1.0)

    def test_no_normalization(self):
        """Test with normalize=False."""
        # Use inputs that produce non-unit norm difference
        pos = np.array([[3.0, 4.0], [3.0, 4.0]], dtype=np.float64)  # mean [3, 4], norm 5
        neg = np.array([[0.0, 0.0], [0.0, 0.0]], dtype=np.float64)   # mean [0, 0]

        direction = contrastive_direction(pos, neg, normalize=False)

        # Should be [3, 4] unnormalized (mean diff)
        expected = np.array([3.0, 4.0], dtype=np.float64)
        assert np.allclose(direction, expected)
        # Should NOT be unit norm (norm = 5)
        assert not np.isclose(np.linalg.norm(direction), 1.0)
        assert np.isclose(np.linalg.norm(direction), 5.0)

    def test_empty_activations_raises(self):
        """Test that empty activation arrays raise ValueError."""
        pos_empty = np.array([], dtype=np.float64).reshape(0, 5)
        neg = np.random.randn(3, 5)
        
        with pytest.raises(ValueError, match="non-empty"):
            contrastive_direction(pos_empty, neg)
        
        pos = np.random.randn(3, 5)
        neg_empty = np.array([], dtype=np.float64).reshape(0, 5)
        
        with pytest.raises(ValueError, match="non-empty"):
            contrastive_direction(pos, neg_empty)

    def test_dimension_mismatch_raises(self):
        """Test that mismatched dimensions raise ValueError."""
        pos = np.random.randn(3, 5)
        neg = np.random.randn(3, 7)  # Different dimension
        
        with pytest.raises(ValueError, match="dimension mismatch"):
            contrastive_direction(pos, neg)

    def test_wrong_shape_raises(self):
        """Test that non-2D arrays raise ValueError."""
        pos = np.random.randn(10)  # 1D
        neg = np.random.randn(3, 5)
        
        with pytest.raises(ValueError, match="2D"):
            contrastive_direction(pos, neg)

    def test_degenerate_direction_raises(self):
        """Test that pos == neg (zero difference) raises ValueError."""
        pos = np.array([[1.0, 2.0, 3.0]], dtype=np.float64)
        neg = np.array([[1.0, 2.0, 3.0]], dtype=np.float64)  # Same
        
        with pytest.raises(ValueError, match="degenerate"):
            contrastive_direction(pos, neg, normalize=True)

    def test_orthogonal_directions(self):
        """Test that orthogonal pos/neg produce expected perpendicularity."""
        # pos along [1, 0], neg along [0, 1]
        pos = np.array([[1.0, 0.0], [1.0, 0.0]], dtype=np.float64)
        neg = np.array([[0.0, 1.0], [0.0, 1.0]], dtype=np.float64)
        
        direction = contrastive_direction(pos, neg)
        
        # Difference is [1, -1], normalized
        expected = np.array([1.0, -1.0]) / np.sqrt(2.0)
        assert np.allclose(direction, expected, atol=1e-5)

    def test_dtype_conversion(self):
        """Test that float32 inputs are handled (converted to float64)."""
        pos = np.array([[1.0, 0.0], [1.0, 0.0]], dtype=np.float32)
        neg = np.array([[0.0, 0.0], [0.0, 0.0]], dtype=np.float32)
        
        direction = contrastive_direction(pos, neg)
        
        assert direction.dtype == np.float64
        assert np.isclose(np.linalg.norm(direction), 1.0)


class TestApplyDirectionWrite:
    """Tests for apply_direction_write function."""

    def test_basic_write_command_creation(self):
        """Test that apply_direction_write creates a valid WriteCommand."""
        direction = np.array([1.0, 0.0, 0.0], dtype=np.float64)
        direction /= np.linalg.norm(direction)  # Ensure unit norm
        
        cmd = apply_direction_write(
            direction=direction,
            layer=20,
            alpha=0.3,
            norm_cap_rel=1.0,
        )
        
        assert isinstance(cmd, WriteCommand)
        assert cmd.layer == 20
        assert cmd.alpha == 0.3
        assert cmd.norm_cap_rel == 1.0
        assert np.allclose(cmd.direction, direction)
        assert cmd.concept_ids == ()
        assert cmd.positions == "last"

    def test_direction_normalization(self):
        """Test that non-unit-norm directions are normalized."""
        direction_unnormalized = np.array([3.0, 4.0], dtype=np.float64)  # Norm = 5
        
        cmd = apply_direction_write(
            direction=direction_unnormalized,
            layer=15,
            alpha=0.1,
            norm_cap_rel=0.1,
        )
        
        # Should be normalized to [0.6, 0.8]
        expected = direction_unnormalized / 5.0
        assert np.allclose(cmd.direction, expected)
        assert np.isclose(np.linalg.norm(cmd.direction), 1.0)

    def test_metadata_propagation(self):
        """Test that metadata dict is carried through."""
        direction = np.array([1.0, 0.0], dtype=np.float64)
        meta = {"source": "refusal_pairs", "n_examples": 10}
        
        cmd = apply_direction_write(
            direction=direction,
            layer=20,
            alpha=0.3,
            norm_cap_rel=1.0,
            meta=meta,
        )
        
        assert "source" in cmd.meta
        assert cmd.meta["source"] == "refusal_pairs"
        assert cmd.meta["n_examples"] == 10
        assert cmd.meta["direction_type"] == "contrastive"

    def test_positions_parameter(self):
        """Test that positions parameter is set correctly."""
        direction = np.array([1.0, 0.0], dtype=np.float64)
        
        cmd_last = apply_direction_write(
            direction=direction,
            layer=20,
            alpha=0.3,
            norm_cap_rel=1.0,
            positions="last",
        )
        assert cmd_last.positions == "last"
        
        cmd_all = apply_direction_write(
            direction=direction,
            layer=20,
            alpha=0.3,
            norm_cap_rel=1.0,
            positions="all",
        )
        assert cmd_all.positions == "all"

    def test_zero_direction_raises(self):
        """Test that zero directions raise ValueError."""
        direction = np.array([0.0, 0.0, 0.0], dtype=np.float64)
        
        with pytest.raises(ValueError, match="zero norm"):
            apply_direction_write(
                direction=direction,
                layer=20,
                alpha=0.3,
                norm_cap_rel=1.0,
            )

    def test_list_input_converted(self):
        """Test that list inputs are converted to numpy arrays."""
        direction = [1.0, 0.0, 0.0]  # Python list, not numpy
        
        cmd = apply_direction_write(
            direction=direction,
            layer=20,
            alpha=0.3,
            norm_cap_rel=1.0,
        )
        
        assert isinstance(cmd.direction, np.ndarray)
        assert cmd.direction.dtype == np.float64

    def test_concept_ids_empty_for_contrastive(self):
        """Test that contrastive writes have empty concept_ids."""
        direction = np.array([1.0, 0.0], dtype=np.float64)
        
        cmd = apply_direction_write(
            direction=direction,
            layer=20,
            alpha=0.3,
            norm_cap_rel=1.0,
        )
        
        assert cmd.concept_ids == ()
        assert "direction_type" in cmd.meta
        assert cmd.meta["direction_type"] == "contrastive"


class TestIntegration:
    """Integration tests for contrastive_direction + apply_direction_write."""

    def test_full_pipeline(self):
        """Test complete pipeline: extract direction -> create write command."""
        # Simulate refusal vs harmful activations
        refusal_acts = np.array([
            [1.0, 2.0, 3.0],
            [1.1, 2.1, 3.1],
            [0.9, 1.9, 2.9],
        ], dtype=np.float64)
        
        harmful_acts = np.array([
            [-1.0, -2.0, -3.0],
            [-1.1, -2.1, -3.1],
            [-0.9, -1.9, -2.9],
        ], dtype=np.float64)
        
        # Extract direction
        direction = contrastive_direction(refusal_acts, harmful_acts)
        
        # Create write command
        cmd = apply_direction_write(
            direction=direction,
            layer=20,
            alpha=0.3,
            norm_cap_rel=1.0,
            meta={"experiment": "jailbreak_steering"},
        )
        
        # Verify
        assert cmd.layer == 20
        assert cmd.alpha == 0.3
        assert np.isclose(np.linalg.norm(cmd.direction), 1.0)
        assert cmd.meta["experiment"] == "jailbreak_steering"

    def test_direction_stability_across_extraction(self):
        """Test that direction extraction is stable (not stochastic)."""
        np.random.seed(42)
        pos = np.random.randn(10, 50)
        neg = np.random.randn(10, 50)
        
        direction1 = contrastive_direction(pos, neg)
        direction2 = contrastive_direction(pos, neg)
        
        # Should be identical (deterministic)
        assert np.allclose(direction1, direction2, atol=1e-10)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
