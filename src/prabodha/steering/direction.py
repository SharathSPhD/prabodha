"""direction — CAA-style contrastive steering via activation differentials.

Concept: pratisaṃvit (discrimination) — steering via a direction derived from contrastive
activations (positive vs negative) rather than through concept codes. This operationalizes
Rimsky et al.'s "Activation Addition" (CAA) and enables alignment/jailbreak direction steering
without a lens-derived basis.

Source: Rimsky et al. (2024) "Steering Conversational AI by its Values"; L21 contract §2
(jailbreak steering, refusal direction extraction); PWM bridge comparator archetype.

Primitive: contrastive_direction (numpy-based, CPU-testable) + apply_direction_write
(WriteCommand-compatible injection). Both interoperate with e4_cli's existing arm machinery.

LIMITATIONS (honestly disclosed):
- Positive/negative activations are collected via forward passes; no guarantee that a single
  direction captures all relevant steering structure (one-dimensional approximation).
- Refusal direction is computed from human-labeled pairs; scalability beyond ~20 pairs untested.
- Effect of direction depends on the layer; layer selection is empirical (e4 port required).
"""
from __future__ import annotations

from typing import Optional
import numpy as np

from prabodha.steering.writer import WriteCommand


def contrastive_direction(
    activations_pos: np.ndarray,
    activations_neg: np.ndarray,
    normalize: bool = True,
) -> np.ndarray:
    """Compute a steering direction from contrastive activations (CAA style).

    Args:
        activations_pos: Array of shape [n_pos, d] — activations for positive exemplars
                         (e.g., harmless instructions, truthful answers).
        activations_neg: Array of shape [n_neg, d] — activations for negative exemplars
                         (e.g., harmful instructions, falsehoods).
        normalize: If True, return unit-norm direction; else return raw difference.

    Returns:
        Direction vector of shape [d] (unit norm if normalize=True).

    Raises:
        ValueError: If shapes are incompatible or activations are empty.
        ValueError: If resulting direction is degenerate (zero after normalization).

    MECHANISM: direction = mean(act[pos]) - mean(act[neg]). Under layer-wise interpretation,
    higher values along this direction correlate with positive behavior (refusal, truthfulness).
    Unit norm enables amplitude-controlled injection via WriteCommand.alpha.

    CITE: Rimsky, N., Scheurer, J., Mishra, R. G., Andreoli, M., Chen, W., & Gabriel, I.
    (2024). Steering Conversational AI by its Values. arXiv:2405.20717.
    """
    activations_pos = np.asarray(activations_pos, dtype=np.float64)
    activations_neg = np.asarray(activations_neg, dtype=np.float64)

    if activations_pos.size == 0 or activations_neg.size == 0:
        raise ValueError("contrastive_direction: positive and negative activations must be non-empty")

    if len(activations_pos.shape) != 2 or len(activations_neg.shape) != 2:
        raise ValueError(f"activations must be 2D [n, d], got {activations_pos.shape} and {activations_neg.shape}")

    d_pos = activations_pos.shape[1]
    d_neg = activations_neg.shape[1]
    if d_pos != d_neg:
        raise ValueError(f"dimension mismatch: pos {d_pos} vs neg {d_neg}")

    mean_pos = np.mean(activations_pos, axis=0)
    mean_neg = np.mean(activations_neg, axis=0)
    direction = mean_pos - mean_neg

    if normalize:
        norm = float(np.linalg.norm(direction))
        if norm == 0:
            raise ValueError("degenerate direction: mean(pos) == mean(neg)")
        direction = direction / norm

    return direction


def apply_direction_write(
    direction: np.ndarray,
    layer: int,
    alpha: float,
    norm_cap_rel: float,
    positions: str = "last",
    meta: Optional[dict] = None,
) -> WriteCommand:
    """Create a WriteCommand from a supplied (unit) direction vector.

    This is the injection-side interface for contrastive steering. It bridges the
    CAA-computed direction into the existing e4_cli WriteCommand machinery, reusing
    the ResidualInjector + timing infrastructure.

    Args:
        direction: Unit-norm direction vector of shape [d]. Can be output of contrastive_direction
                   or any externally computed direction (e.g., via SAE features, explicit optimization).
        layer: Target layer for injection (must match hidden dimension d).
        alpha: Injection strength (relative amplitude). Capped by norm_cap_rel per svātantrya.
        norm_cap_rel: Norm capping ratio — write amplitude ≤ min(alpha, norm_cap_rel) * ||h||.
        positions: 'last' (only final position), 'all' (every position), or 'from_pos:<i>' (prefix).
        meta: Optional metadata dict (e.g., {"direction_source": "refusal_pairs", "n_examples": 20}).

    Returns:
        WriteCommand ready for ResidualInjector context manager.

    INVARIANT: The returned WriteCommand has direction normalized (unit norm). The injector
    applies capped_delta scaling at runtime based on residual norm.

    USAGE:
        direction = contrastive_direction(pos_acts, neg_acts)
        cmd = apply_direction_write(direction, layer=20, alpha=0.3, norm_cap_rel=1.0)
        with ResidualInjector(layer_module, cmd) as inj:
            # generate text with steering applied
    """
    if not isinstance(direction, np.ndarray):
        direction = np.asarray(direction, dtype=np.float64)

    direction = np.asarray(direction, dtype=np.float64)
    direction_norm = float(np.linalg.norm(direction))

    if direction_norm == 0:
        raise ValueError("apply_direction_write: direction has zero norm")

    # Normalize if not already
    if not np.isclose(direction_norm, 1.0, rtol=1e-5):
        direction = direction / direction_norm

    if meta is None:
        meta = {}

    # WriteCommand has no concept_ids for contrastive directions
    # (they are computed from activations, not concept tokens)
    return WriteCommand(
        layer=int(layer),
        direction=direction,
        alpha=float(alpha),
        norm_cap_rel=float(norm_cap_rel),
        concept_ids=(),  # Empty for contrastive directions
        positions=positions,
        meta={**meta, "direction_type": "contrastive"},
    )
