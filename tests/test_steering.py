"""Unit tests for the L3 steering core (CPU, numpy — no torch/GPU)."""
import numpy as np
import pytest

from prabodha.steering.verifier import Uptake, entropy, readback_verdict
from prabodha.steering.writer import capped_delta, concept_direction, plan_write


def test_concept_direction_raises_target_logit():
    """The planned direction must raise the concept's lens logit faster than random
    directions: lens logit = u_c . (J h); moving h along J^T u_c maximizes d(logit)."""
    rng = np.random.default_rng(0)
    d, vocab = 32, 100
    J = rng.normal(size=(d, d))
    U = rng.normal(size=(vocab, d))
    c = 7
    g = concept_direction(J, U[c])
    h = rng.normal(size=d)
    def logit(hv):
        return float(U[c] @ (J @ hv))
    base = logit(h)
    gain_planned = logit(h + 0.1 * g) - base
    gains_random = [logit(h + 0.1 * rng.normal(size=d) / np.sqrt(d)) - base
                    for _ in range(50)]
    assert gain_planned > 0
    assert gain_planned > max(gains_random)


def test_concept_direction_nonneg_code_enforced():
    rng = np.random.default_rng(1)
    J = rng.normal(size=(8, 8))
    U = rng.normal(size=(3, 8))
    with pytest.raises(ValueError, match="non-negative"):
        concept_direction(J, U, weights=np.array([1.0, -0.5, 0.2]))
    g = concept_direction(J, U, weights=np.array([1.0, 0.0, 2.0]))
    assert np.linalg.norm(g) == pytest.approx(1.0)


def test_capped_delta_respects_svatantrya_cap():
    g = np.zeros(16)
    g[0] = 1.0
    d = capped_delta(g, h_norm=10.0, alpha=0.5, norm_cap_rel=0.1)
    assert np.linalg.norm(d) == pytest.approx(1.0)  # 0.1 * 10, cap binds below alpha
    d2 = capped_delta(g, h_norm=10.0, alpha=0.05, norm_cap_rel=0.1)
    assert np.linalg.norm(d2) == pytest.approx(0.5)  # alpha binds below cap


def test_plan_write_command_carries_provenance():
    rng = np.random.default_rng(2)
    cmd = plan_write(rng.normal(size=(8, 8)), rng.normal(size=(1, 8)), layer=6,
                     concept_ids=[42], alpha=0.2, norm_cap_rel=0.1)
    assert cmd.layer == 6 and cmd.concept_ids == (42,)
    assert np.linalg.norm(cmd.direction) == pytest.approx(1.0)


def test_entropy_uniform_is_log_n():
    assert entropy(np.zeros(64)) == pytest.approx(np.log(64))


def _verdict(pre, ranks, e_before=3.0, e_after=3.05):
    return readback_verdict(pre, ranks, top_m=5, min_rank_gain=50,
                            entropy_before=e_before, entropy_after=e_after, epsilon=0.2)


def test_uptake_ok_path():
    v = _verdict(400, [20, 4, 3])
    assert v == Uptake(ok=True, loaded=True, amplified=True, persistent=True, mala=None,
                       best_rank=3, pre_rank=400, entropy_delta=v.entropy_delta,
                       within_budget=True)


def test_malas_taxonomy():
    assert _verdict(400, [300, 250, 200]).mala == "anava"       # never loaded
    assert _verdict(30, [10, 5, 4]).mala == "mayiya"            # loaded, gain 26 < 50
    assert _verdict(400, [3, 4, 90]).mala == "karma"            # loaded then faded
    v = readback_verdict(400, [20, 4, 3], top_m=5, min_rank_gain=50,
                         entropy_before=3.0, entropy_after=4.0, epsilon=0.2)
    assert v.mala == "svatantrya" and not v.within_budget       # uptake fine, budget blown


def test_camatk_text_port_matches_pwm_shape():
    from prabodha.steering.scoring import concept_surface_rate, score_camatk_text
    assert score_camatk_text("") == 0.0
    poem = "\n".join(["the fire remembers rivers", "gold under frost and slate",
                      "a moon of bread rising", "iron sings to snow"] * 5)
    assert 0.8 < score_camatk_text(poem) <= 1.0
    flat = "word " * 100  # long but zero diversity, one line
    assert score_camatk_text(flat) < 0.6
    assert concept_surface_rate(["the fire is bright", "no match here"], "fire") == 0.5
    assert concept_surface_rate(["Fire!"], "fire") == 1.0


def test_timing_policies_budget_and_alignment():
    from prabodha.steering.timing import EntropyGated, EveryK, make_policy
    ek = EveryK(k=4)
    fires = [ek.should_write(False) for _ in range(12)]
    assert sum(fires) == 3 and ek.should_write(True) and ek.n_allowed == 4
    eg = EntropyGated(tau=2.0, min_gap=2)
    assert eg.should_write(True)  # prefill always writes
    entropies = [0.5, 2.5, 2.6, 0.1, 3.0, 2.9, 0.2]
    fired = []
    for e in entropies:
        eg.observe(e)
        fired.append(eg.should_write(False))
    # writes only when observed entropy >= tau AND min_gap honored:
    # steps: 0.5 no; 2.5 yes; 2.6 no (gap); 0.1 no; 3.0 yes; 2.9 no (gap); 0.2 no
    assert fired == [False, True, False, False, True, False, False]
    assert [round(e, 1) for _, e in eg.write_events] == [2.5, 3.0]
    assert make_policy("prefill_only").should_write(True)
    import pytest as _pt
    with _pt.raises(ValueError):
        make_policy("nope")


def test_gated_injector_respects_policy_cpu():
    """Injector + policy contract without torch: a policy that refuses decode steps
    must leave the hook a no-op on 1-token forwards (checked via should_write calls)."""
    from prabodha.steering.timing import PrefillOnly
    p = PrefillOnly()
    assert p.should_write(True) is True
    assert p.should_write(False) is False
    assert p.n_allowed == 1
