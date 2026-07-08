"""writer — plan_write: k-sparse non-negative concept codes -> residual write vectors.
Concept: vimarśa-lekhana — inscribing content into the band in the band's OWN coordinates:
the direction that raises the concept's logit under the band-targeted lens, J_l^T u_c
(local-linear through the final norm; approximation disclosed in contract L3).
Source: SPEC §6 (k-sparse non-negative codes; svātantrya norm cap); jlens transport = h @ J^T.
Primitive: numpy core (host-testable) + WriteCommand carrier consumed by the injector.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


def concept_direction(J: np.ndarray, u_rows: np.ndarray,
                      weights: np.ndarray | None = None) -> np.ndarray:
    """Unit write direction at a source layer: non-negative combination of per-concept
    gradients g_i = J^T u_i. J: [d, d] lens Jacobian; u_rows: [k, d] unembedding rows of
    the concept token ids; weights: [k] non-negative code (uniform if None).
    Raises ValueError on negative weights (the doctrine is non-negative by construction)."""
    u_rows = np.atleast_2d(np.asarray(u_rows, dtype=np.float64))
    if weights is None:
        weights = np.ones(len(u_rows))
    weights = np.asarray(weights, dtype=np.float64)
    if (weights < 0).any():
        raise ValueError("svātantrya doctrine: non-negative concept codes only")
    g = (weights @ u_rows) @ np.asarray(J, dtype=np.float64)  # row-vector form of J^T u
    norm = float(np.linalg.norm(g))
    if norm == 0:
        raise ValueError("degenerate write direction (zero gradient)")
    return g / norm


def capped_delta(direction: np.ndarray, h_norm: float, alpha: float,
                 norm_cap_rel: float) -> np.ndarray:
    """Scale the unit direction: ||delta|| = min(alpha, norm_cap_rel) * ||h||.
    The cap is the svātantrya budget's first line — the write may never dominate the
    residual it enters (entropy cost is measured separately by the verifier)."""
    scale = min(float(alpha), float(norm_cap_rel)) * float(h_norm)
    return direction * scale


@dataclass(frozen=True)
class WriteCommand:
    """Replayable write (Command pattern): everything needed to reproduce one injection."""
    layer: int
    direction: np.ndarray            # unit vector, [d]
    alpha: float                     # requested relative strength
    norm_cap_rel: float              # svātantrya cap on ||delta||/||h||
    concept_ids: tuple[int, ...]
    positions: str = "last"          # 'last' | 'from_pos:<i>' | 'all'
    meta: dict[str, Any] = field(default_factory=dict)


def plan_write(J: np.ndarray, u_rows: np.ndarray, layer: int, concept_ids: list[int], *,
               alpha: float, norm_cap_rel: float,
               weights: np.ndarray | None = None,
               positions: str = "last") -> WriteCommand:
    return WriteCommand(layer=layer,
                        direction=concept_direction(J, u_rows, weights),
                        alpha=alpha, norm_cap_rel=norm_cap_rel,
                        concept_ids=tuple(int(c) for c in concept_ids),
                        positions=positions)
