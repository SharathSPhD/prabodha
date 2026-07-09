"""Analytic Expected-Free-Energy selector over experiment candidates.
Concept: iccha-jnana-kriya as auto-research — wanting (pragmatic preference), knowing
(epistemic information gain), doing (the proposed action) balanced per GPU-hour.
Source: PORTED from prabhasa application/efe/agent.py (docs/efe_port_plan.md; likelihood
matrix, entropy, normalise, and all EFESelector methods preserved EXACTLY — only the
observation tier field names are generalized: bpb_tier->primary_tier, frt_tier->
secondary_tier, since prabodha's observations are gate outcomes, not token-efficiency).
Primitive: Candidate/Action/Observation/Proposal + EFESelector (belief/update/score/
select/rank). Stdlib only.

Original prabhasa docstring (design rationale) follows:
Analytic Expected-Free-Energy selector over experiment candidates.

State / observation discretisation
----------------------------------
Each candidate carries a belief over a latent **value** factor with four levels
(``negligible, low, moderate, high``) — "how much does running this config help
the product?". Observations are discretised tiers of the measured improvement
over the matched baseline:

  * ``bpb`` tier in 0..3 (token-efficiency gain),
  * ``frt`` tier in 0..3 (round-trip / probe gain; optional).

Actions modulate cost vs information resolution (separation by action, mirroring
the source agent's B-matrix entropy design):

  * ``smoke``   — cheap, low-information (explore),
  * ``partial`` — moderate,
  * ``full``    — expensive, high-information (confirm / exploit).

EFE
---
For a candidate ``c`` and action ``a`` the Expected Free Energy is

    G(c, a) = -( w_epi * epistemic(c, a) + w_prag * pragmatic(c) )

* ``epistemic`` = expected information gain ~ belief entropy * action resolution,
  divided by action cost (information per GPU-hour);
* ``pragmatic`` = expected preference satisfaction E_b[U(value)] minus a cost
  penalty.

The selector returns the ``(candidate, action)`` minimising ``G`` (equivalently
maximising the negative-EFE the source agent reports). EXPLORE->CONFIRM emerges:
high-entropy candidates pull a cheap ``smoke``; high-belief candidates pull a
``full`` run.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field

VALUE_LEVELS = 4
VALUE_LABELS = ("negligible", "low", "moderate", "high")
# Utility of each value level (pragmatic preference; prefer high value).
_UTILITY = (-1.0, 0.0, 1.0, 2.0)


@dataclass(frozen=True)
class Action:
    """A way to run a candidate: cost (GPU-hours) and information resolution."""

    name: str
    gpu_hours: float
    resolution: float  # 0..1; how much of the candidate's uncertainty it resolves


# Default action set (cheap-smoke -> full-run); EXPLORE..CONFIRM spectrum.
SMOKE = Action("smoke", gpu_hours=0.1, resolution=0.25)
PARTIAL = Action("partial", gpu_hours=1.0, resolution=0.6)
FULL = Action("full", gpu_hours=5.0, resolution=0.95)
DEFAULT_ACTIONS: tuple[Action, ...] = (SMOKE, PARTIAL, FULL)


@dataclass(frozen=True)
class Candidate:
    """One experiment candidate: a knob/config change to evaluate."""

    id: str
    description: str
    knobs: dict[str, object] = field(default_factory=dict)
    # Optional prior nudge in 0..3 (e.g. strong prior it is "moderate" value).
    prior_value_hint: int | None = None


@dataclass(frozen=True)
class Observation:
    """Discretised measured outcome of a trial (tiers in 0..3)."""

    primary_tier: int
    secondary_tier: int | None = None

    def __post_init__(self) -> None:
        for name, v in (("primary_tier", self.primary_tier), ("secondary_tier", self.secondary_tier)):
            if v is not None and not 0 <= v <= 3:
                raise ValueError(f"{name} must be in 0..3, got {v}")


@dataclass(frozen=True)
class Proposal:
    """The selector's recommendation for the next micro-experiment."""

    candidate: Candidate
    action: Action
    efe: float
    epistemic: float
    pragmatic: float
    belief: tuple[float, ...]


def _normalise(weights: Sequence[float]) -> list[float]:
    total = sum(weights)
    if total <= 0:
        n = len(weights)
        return [1.0 / n] * n
    return [w / total for w in weights]


def _entropy(belief: Sequence[float]) -> float:
    return -sum(p * math.log(p + 1e-12) for p in belief if p > 0)


# Likelihood P(observed tier | latent value level). Higher value -> higher tiers.
# Rows index latent value level (0..3), columns the observed tier (0..3).
_LIKELIHOOD: tuple[tuple[float, ...], ...] = (
    (0.70, 0.20, 0.07, 0.03),  # negligible
    (0.30, 0.45, 0.20, 0.05),  # low
    (0.07, 0.23, 0.45, 0.25),  # moderate
    (0.03, 0.07, 0.30, 0.60),  # high
)


class EFESelector:
    """Expected-Free-Energy selector over a fixed candidate set.

    Beliefs are categorical over the four latent value levels, one belief per
    candidate id, updated by Bayes rule from each observation's tiers.
    """

    def __init__(
        self,
        *,
        epistemic_weight: float = 1.0,
        pragmatic_weight: float = 1.0,
        cost_penalty: float = 0.15,
        actions: Sequence[Action] = DEFAULT_ACTIONS,
    ) -> None:
        self.epistemic_weight = float(epistemic_weight)
        self.pragmatic_weight = float(pragmatic_weight)
        self.cost_penalty = float(cost_penalty)
        self.actions = tuple(actions)
        self._beliefs: dict[str, list[float]] = {}

    # -- belief management --------------------------------------------------
    def _prior(self, candidate: Candidate) -> list[float]:
        # Default prior: most configs are low value; nudge if a hint is given.
        base = [0.40, 0.30, 0.20, 0.10]
        if candidate.prior_value_hint is not None:
            hint = max(0, min(3, candidate.prior_value_hint))
            base = [0.1, 0.1, 0.1, 0.1]
            base[hint] = 0.7
        return _normalise(base)

    def belief(self, candidate: Candidate) -> list[float]:
        return list(self._beliefs.get(candidate.id, self._prior(candidate)))

    def posterior(self, candidate_id: str) -> list[float] | None:
        """The updated belief for a candidate id, or ``None`` if never observed."""
        belief = self._beliefs.get(candidate_id)
        return list(belief) if belief is not None else None

    def update(
        self, candidate_id: str, obs: Observation, prior: list[float] | None = None
    ) -> list[float]:
        """Bayesian belief update for a candidate from one observation."""
        if prior is not None:
            belief = prior
        else:
            belief = self._beliefs.get(candidate_id, [0.40, 0.30, 0.20, 0.10])
        tiers = [obs.primary_tier] + ([obs.secondary_tier] if obs.secondary_tier is not None else [])
        post = list(belief)
        for tier in tiers:
            post = [post[v] * _LIKELIHOOD[v][tier] for v in range(VALUE_LEVELS)]
            post = _normalise(post)
        self._beliefs[candidate_id] = post
        return post

    # -- EFE scoring --------------------------------------------------------
    def _epistemic(self, belief: Sequence[float], action: Action) -> float:
        """Expected info gain per GPU-hour: belief entropy * resolution / cost."""
        return _entropy(belief) * action.resolution / max(action.gpu_hours, 1e-6)

    def _pragmatic(self, belief: Sequence[float], action: Action) -> float:
        """Expected preference satisfaction minus a cost penalty."""
        utility = sum(p * u for p, u in zip(belief, _UTILITY, strict=True))
        return utility - self.cost_penalty * action.gpu_hours

    def score(self, candidate: Candidate, action: Action) -> Proposal:
        belief = self.belief(candidate)
        epi = self._epistemic(belief, action)
        prag = self._pragmatic(belief, action)
        efe = -(self.epistemic_weight * epi + self.pragmatic_weight * prag)
        return Proposal(
            candidate=candidate,
            action=action,
            efe=efe,
            epistemic=epi,
            pragmatic=prag,
            belief=tuple(belief),
        )

    def select(
        self,
        candidates: Sequence[Candidate],
        *,
        budget_gpu_hours: float = float("inf"),
        exclude: Sequence[str] = (),
    ) -> Proposal:
        """Pick the ``(candidate, action)`` minimising EFE within budget."""
        if not candidates:
            raise ValueError("no candidates to select from")
        excluded = set(exclude)
        best: Proposal | None = None
        for cand in candidates:
            if cand.id in excluded:
                continue
            for action in self.actions:
                if action.gpu_hours > budget_gpu_hours:
                    continue
                prop = self.score(cand, action)
                if best is None or prop.efe < best.efe:
                    best = prop
        if best is None:
            raise ValueError("no (candidate, action) fits the GPU-hour budget")
        return best

    def rank(self, candidates: Sequence[Candidate]) -> list[Proposal]:
        """Best action per candidate, sorted by ascending EFE (best first)."""
        out = []
        for cand in candidates:
            props = [self.score(cand, a) for a in self.actions]
            out.append(min(props, key=lambda p: p.efe))
        out.sort(key=lambda p: p.efe)
        return out
