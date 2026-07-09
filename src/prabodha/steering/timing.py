"""timing — write-timing policies (Strategy): WHEN the injector may fire.
Concept: sphurattā — the flash where graded evidence snaps to committed identity. L3's
triple dissociation showed timing (not amplitude) drives both steering and freedom cost;
the doctrine's clause "write at sphurattā events only" (scoping §3) is implemented here as
UNCOMMITTED-moment gating: write during step t iff the entropy of the model's committed
state entering t (logits of step t-1) is high — nudge only where the plant is undecided.
Source: PWM CamatkaraReward.sphuratta_score (min-gap temporal hygiene ported; VFE/Hopfield
terms have no analogue on a bare plant — deviation disclosed in contract L4); L3 review #5.
Primitive: policy.observe(step_entropy) from a logits hook; policy.should_write(is_prefill)
read by the ResidualInjector each forward. Rate-matched EveryK is the alignment CONTROL:
same write budget, no event alignment.
"""
from __future__ import annotations


class TimingPolicy:
    """Base: observe() every decode step (entropy of the just-produced logits);
    should_write() consulted by the injector on the NEXT forward."""

    def observe(self, step_entropy: float) -> None:  # pragma: no cover - trivial
        pass

    def should_write(self, is_prefill: bool) -> bool:
        raise NotImplementedError

    @property
    def n_allowed(self) -> int:
        raise NotImplementedError


class Continuous(TimingPolicy):
    """L3 replication arm: every forward writes."""
    def __init__(self):
        self._n = 0

    def should_write(self, is_prefill: bool) -> bool:
        self._n += 1
        return True

    @property
    def n_allowed(self) -> int:
        return self._n


class PrefillOnly(TimingPolicy):
    def __init__(self):
        self._n = 0

    def should_write(self, is_prefill: bool) -> bool:
        if is_prefill:
            self._n += 1
            return True
        return False

    @property
    def n_allowed(self) -> int:
        return self._n


class EveryK(TimingPolicy):
    """Rate-matched control: writes on prefill and every k-th decode step —
    the same write BUDGET as an event policy with rate 1/k, but no event ALIGNMENT."""
    def __init__(self, k: int):
        if k < 1:
            raise ValueError("k >= 1")
        self.k = k
        self._decode_steps = 0
        self._n = 0

    def should_write(self, is_prefill: bool) -> bool:
        if is_prefill:
            self._n += 1
            return True
        self._decode_steps += 1
        if self._decode_steps % self.k == 0:
            self._n += 1
            return True
        return False

    @property
    def n_allowed(self) -> int:
        return self._n


class EntropyGated(TimingPolicy):
    """Sphurattā arm: write during step t iff entropy(logits_{t-1}) >= tau (the plant is
    uncommitted) and at least min_gap decode steps have passed since the last write
    (PWM's temporal hygiene). Prefill always writes (content must enter once)."""
    def __init__(self, tau: float, min_gap: int = 2):
        self.tau = float(tau)
        self.min_gap = int(min_gap)
        self._last_entropy: float | None = None
        self._steps_since_write = 10 ** 9
        self._n = 0
        self.write_events: list[tuple[int, float]] = []  # (decode_step, gate entropy)
        self._decode_step = 0

    def observe(self, step_entropy: float) -> None:
        self._last_entropy = float(step_entropy)

    def should_write(self, is_prefill: bool) -> bool:
        if is_prefill:
            self._n += 1
            return True
        self._decode_step += 1
        self._steps_since_write += 1
        e = self._last_entropy
        gate = (e is not None and e >= self.tau
                and self._steps_since_write >= self.min_gap)
        if gate:
            self._n += 1
            self._steps_since_write = 0
            self.write_events.append((self._decode_step, float(e)))
        return gate

    @property
    def n_allowed(self) -> int:
        return self._n


def make_policy(name: str, **kw) -> TimingPolicy:
    """Config-driven factory (Strategy registry)."""
    table = {"continuous": Continuous, "prefill_only": PrefillOnly,
             "every_k": EveryK, "entropy_gated": EntropyGated}
    if name not in table:
        raise ValueError(f"unknown timing policy: {name!r}")
    return table[name](**kw)
