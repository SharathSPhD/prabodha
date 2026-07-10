"""bridge_trained — CittaStore-based write direction computation.

Concept: śakti-līlā (play of power) extended to trained association: instead of
deriving write direction from the lens's Jacobian (analytical), retrieve it from
a learned Hopfield store of past successful write events.

Source: PWM/pwm/memory/citta_store.py (Hopfield recall); paper §trained-bridge;
L20 menu item (comparator: trained vs. analytic, matched entropy budget).

Primitive: CittaStore.recall(query) returns a retrieved vector; we normalize it
and treat it as the write direction, consuming the same WriteCommand interface
as the analytic writer.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import torch
import torch.nn.functional as F


class TrainedBridgeWriter:
    """Produces WriteCommand using CittaStore-retrieved directions.

    The CittaStore is initialized with past successful activations (episodic mode).
    At steering time, a query (composed from unembedding rows + current hidden state
    context) is presented; CittaStore.recall() returns an attractor state. This
    becomes the unit direction, following the same svātantrya and WriteCommand
    protocols as the analytic J^T u writer.
    """

    def __init__(self, citta_store: Any, write_layer: int, tau_percentile: int = 60):
        """Initialize trained-bridge writer.

        Args:
            citta_store: PWM CittaStore instance (or mock with recall/hopfield_entropy methods)
            write_layer: layer index where writes are applied
            tau_percentile: entropy percentile for gating (unused here; kept for API compatibility)
        """
        self.citta_store = citta_store
        self.write_layer = write_layer
        self.tau_percentile = tau_percentile

    def plan_write(
        self,
        u_rows: np.ndarray,
        concept_ids: list[int],
        *,
        alpha: float,
        norm_cap_rel: float,
        weights: np.ndarray | None = None,
        positions: str = "last",
    ) -> WriteCommand:
        """Plan a write using CittaStore-retrieved direction.

        Args:
            u_rows: [k, d] unembedding rows for concept tokens (from model.get_output_embeddings())
            concept_ids: token IDs (length k)
            alpha: requested relative write strength (svātantrya amplitude parameter)
            norm_cap_rel: relative norm cap (svātantrya budget constraint)
            weights: [k] non-negative concept code (uniform if None)
            positions: "last" | "all" (where in the sequence to write)

        Returns:
            WriteCommand: replayable write specification

        Raises:
            ValueError: if weights contain negatives (svātantrya doctrine) or if
                       CittaStore produces a degenerate direction
        """
        from prabodha.steering.writer import WriteCommand

        u_rows = np.atleast_2d(np.asarray(u_rows, dtype=np.float64))
        if weights is None:
            weights = np.ones(len(u_rows))
        weights = np.asarray(weights, dtype=np.float64)

        if (weights < 0).any():
            raise ValueError("svātantrya doctrine: non-negative concept codes only")

        # Compose query: weighted sum of unembedding rows (concept signature)
        # This vector is fed to CittaStore.recall() as the memory query.
        query = (weights @ u_rows).astype(np.float32)  # [d]

        # Convert to torch for CittaStore interface
        query_t = torch.from_numpy(query).unsqueeze(0).float()  # [1, d]

        # Retrieve direction from CittaStore (episodic mode: sharp recall)
        retrieved = self.citta_store.recall(query_t, level=0)  # [1, d]
        direction_np = retrieved[0].detach().cpu().numpy().astype(np.float64)

        # Normalize to unit vector (same contract as analytic writer)
        norm = float(np.linalg.norm(direction_np))
        if norm == 0 or np.isnan(norm):
            raise ValueError(
                f"degenerate write direction from CittaStore (norm={norm}); "
                "retrieved vector is zero or malformed"
            )

        direction = direction_np / norm

        return WriteCommand(
            layer=self.write_layer,
            direction=direction,
            alpha=alpha,
            norm_cap_rel=norm_cap_rel,
            concept_ids=tuple(int(c) for c in concept_ids),
            positions=positions,
            meta={"bridge_type": "trained", "retrieval_norm": norm},
        )


# Backward compatibility: allow plan_write to be called as a module function
# (signature mirrors steering/writer.py for drop-in replacement)
def plan_write(
    citta_store: Any,
    u_rows: np.ndarray,
    write_layer: int,
    concept_ids: list[int],
    *,
    alpha: float,
    norm_cap_rel: float,
    weights: np.ndarray | None = None,
    positions: str = "last",
) -> WriteCommand:
    """Convenience function: create a TrainedBridgeWriter and plan write.

    Mirrors the steering/writer.plan_write signature but takes citta_store
    as first argument instead of Jacobian J.
    """
    writer = TrainedBridgeWriter(citta_store, write_layer)
    return writer.plan_write(
        u_rows=u_rows,
        concept_ids=concept_ids,
        alpha=alpha,
        norm_cap_rel=norm_cap_rel,
        weights=weights,
        positions=positions,
    )


# Import WriteCommand for module exports
from prabodha.steering.writer import WriteCommand
