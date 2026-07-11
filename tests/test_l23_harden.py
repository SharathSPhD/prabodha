"""test_l23_harden — unit + smoke tests for L23 hardening loop.

Concept: pratirodha (hardening/resistance). Tests verify:
  1. Pure logic (corpus split, metric aggregation, hypothesis composition) via stubs/fakes.
  2. Mechanism (injector fires, policy gates correctly) via CPU smoke with tiny model.

Unit tests: no torch model load, no prayoga dependency. Smoke test (CPU): loads
sshleifer/tiny-gpt2, runs 1-2 prompts per arm, verifies execution and injector behavior.

Source: L23 worklist; smoke marked @pytest.mark.smoke to allow `pytest -m "not smoke"`.
"""
import json

import numpy as np
import pytest

from prabodha.hardening.harden_loop import (
    HardeningConfig,
    ArmResult,
    HardeningResult,
    _refusal_rate,
    _asr,
    _split_corpus,
    result_to_gate_json,
)


# ============= UNIT TESTS (no torch/prayoga) ============


class TestRefusalMetrics:
    """Test refusal detection and ASR computation."""

    def test_refusal_rate_with_refusals(self):
        texts = [
            "I cannot help with that.",
            "I can't assist you.",
            "I appreciate the question.",  # no refusal
        ]
        rate = _refusal_rate(texts)
        assert rate == pytest.approx(2.0 / 3.0, abs=0.01)

    def test_refusal_rate_empty(self):
        assert _refusal_rate([]) == 0.0

    def test_asr_compliant(self):
        texts = [
            "Sure, here's how to do it.",  # compliant
            "I cannot help with that.",  # refusal
        ]
        asr = _asr(texts)
        assert asr == pytest.approx(0.5, abs=0.01)

    def test_refusal_head_chars(self):
        long_text = "I cannot " + "x" * 500
        texts = [long_text]
        rate = _refusal_rate(texts, head_chars=200)
        assert rate > 0.0  # refusal should be in head


class TestCorpusSplit:
    """Test train/test corpus splitting."""

    def test_split_corpus_size(self):
        texts = [f"text_{i}" for i in range(100)]
        train, test = _split_corpus(texts, train_frac=0.8, seed=42)
        assert len(train) == 80
        assert len(test) == 20
        assert len(set(train) & set(test)) == 0  # no overlap

    def test_split_corpus_reproducibility(self):
        texts = [f"text_{i}" for i in range(100)]
        train1, test1 = _split_corpus(texts, train_frac=0.8, seed=42)
        train2, test2 = _split_corpus(texts, train_frac=0.8, seed=42)
        assert train1 == train2
        assert test1 == test2

    def test_split_corpus_different_seeds(self):
        texts = [f"text_{i}" for i in range(100)]
        train1, _ = _split_corpus(texts, train_frac=0.8, seed=42)
        train2, _ = _split_corpus(texts, train_frac=0.8, seed=43)
        assert train1 != train2  # different seeds give different splits


class TestArmResult:
    """Test ArmResult dataclass."""

    def test_arm_result_creation(self):
        arm = ArmResult(
            arm="baseline",
            asr_jailbreak=0.5,
            over_refusal_benign=0.1,
            mean_step_entropy=1.5,
            mean_writes_per_gen=0.0,
            texts_sample={"jailbreak": ["text1"], "benign": ["text2"]},
        )
        assert arm.arm == "baseline"
        assert arm.asr_jailbreak == 0.5


class TestHardeningResult:
    """Test HardeningResult and gate JSON conversion."""

    def test_result_to_gate_json_pass(self):
        arms = {
            "baseline": ArmResult(
                arm="baseline", asr_jailbreak=0.5, over_refusal_benign=0.1,
                mean_step_entropy=1.5, mean_writes_per_gen=0.0,
                texts_sample={"jailbreak": ["t1"], "benign": ["t2"]},
            ),
        }
        result = HardeningResult(
            arms=arms,
            tau=1.5,
            hypotheses_verdicts={
                "H_test": {"value": 1.0, "threshold": 0.5, "pass": True}
            },
            deviations=[],
        )
        gate_json = result_to_gate_json(result)
        assert gate_json["loop"] == "L23"
        assert gate_json["domain_gate"]["verdict"] == "pass"
        evidence = json.loads(gate_json["domain_gate"]["evidence"])
        assert evidence["tau"] == 1.5

    def test_result_to_gate_json_fail(self):
        arms = {
            "baseline": ArmResult(
                arm="baseline", asr_jailbreak=0.5, over_refusal_benign=0.1,
                mean_step_entropy=1.5, mean_writes_per_gen=0.0,
                texts_sample={"jailbreak": ["t1"], "benign": ["t2"]},
            ),
        }
        result = HardeningResult(
            arms=arms,
            tau=1.5,
            hypotheses_verdicts={
                "H_test": {"value": 0.2, "threshold": 0.5, "pass": False}
            },
            deviations=[],
        )
        gate_json = result_to_gate_json(result)
        assert gate_json["domain_gate"]["verdict"] == "fail"


class TestHardeningConfig:
    """Test HardeningConfig dataclass."""

    def test_config_creation(self):
        config = HardeningConfig(
            model_id="test/model",
            harmful_texts=["harm1"],
            harmless_texts=["safe1"],
            test_harmful_texts=["test_harm"],
            test_harmless_texts=["test_safe"],
            candidate_layers=[10, 12],
            write_layer=12,
            coeff=1.0,
            tau_percentile=50.0,
        )
        assert config.model_id == "test/model"
        assert config.write_layer == 12


# ============= CPU SMOKE TESTS (torch + prayoga required) ============


@pytest.mark.smoke
class TestHardeningLoopSmoke:
    """CPU smoke tests: verify execution paths with tiny model."""

    @pytest.fixture(autouse=True)
    def setup_tiny_model(self):
        """Load tiny-gpt2 for CPU smoke."""
        import importlib.util
        if importlib.util.find_spec("prayoga") is None:
            pytest.skip("prayoga not installed; skipping smoke")

        self.tiny_model_id = "sshleifer/tiny-gpt2"
        self.model = None  # lazy-load to avoid memory on non-smoke runs
        yield
        if self.model is not None:
            del self.model

    def test_smoke_hf_model_loads(self):
        """Verify HFModel loads (prayoga interface)."""
        try:
            from prayoga.lm.hf_model import HFModel
        except ImportError:
            pytest.skip("prayoga not installed")

        model = HFModel(self.tiny_model_id, device="cpu")
        assert model.n_layers > 0
        assert model.d_model > 0
        self.model = model

    def test_smoke_direction_extraction(self):
        """Verify direction extraction from tiny prompts."""
        try:
            from prayoga.lm.hf_model import HFModel
            from prayoga.axis_a.direction_extraction import directions_all_layers
        except ImportError:
            pytest.skip("prayoga not installed")

        model = HFModel(self.tiny_model_id, device="cpu")
        self.model = model

        harmful = ["bad prompt 1", "bad prompt 2"]
        harmless = ["good prompt 1", "good prompt 2"]

        directions = directions_all_layers(model, harmful, harmless)
        assert directions.shape[0] == model.n_layers
        assert directions.shape[1] == model.d_model
        # Verify unit normalization
        norms = np.linalg.norm(directions, axis=1)
        assert np.allclose(norms, 1.0, atol=1e-5)

    def test_smoke_intervention_engine(self):
        """Verify InterventionEngine baseline generation."""
        try:
            from prayoga.lm.hf_model import HFModel
            from prayoga.axis_a.intervention_engine import InterventionEngine
        except ImportError:
            pytest.skip("prayoga not installed")

        model = HFModel(self.tiny_model_id, device="cpu")
        self.model = model
        engine = InterventionEngine(model)

        prompts = ["Hello"]
        texts = engine.baseline_generate(prompts, max_new_tokens=5)
        assert len(texts) == 1
        assert isinstance(texts[0], str)
        assert len(texts[0]) > 0

    def test_smoke_residual_injector_no_policy(self):
        """Verify ResidualInjector fires without policy."""
        try:
            from prayoga.lm.hf_model import HFModel
            from prabodha.steering.injector import ResidualInjector
            from prabodha.steering.writer import WriteCommand
        except ImportError:
            pytest.skip("prayoga or prabodha dependencies not installed")

        import torch

        model = HFModel(self.tiny_model_id, device="cpu")
        self.model = model

        layer_module = model.layers[0]
        direction = np.ones(model.d_model, dtype=np.float32)
        direction /= np.linalg.norm(direction)

        cmd = WriteCommand(
            layer=0, direction=direction, alpha=0.1, norm_cap_rel=1.0,
            concept_ids=(0,), positions="last",
        )

        injector = ResidualInjector(layer_module, cmd, policy=None)
        assert injector.n_applications == 0

        # Simulate a forward pass hook (the hook increments n_applications)
        injector._hook(layer_module, None, torch.randn(1, 10, model.d_model))
        assert injector.n_applications == 1

    def test_smoke_entropy_gated_policy(self):
        """Verify EntropyGated policy gates correctly."""
        from prabodha.steering.timing import make_policy

        policy = make_policy("entropy_gated", tau=1.5, min_gap=2)

        # Prefill should always write
        assert policy.should_write(is_prefill=True) is True
        assert policy.n_allowed == 1

        # Low entropy (below tau) should not write
        policy.observe(1.0)  # entropy < tau
        assert policy.should_write(is_prefill=False) is False

        # High entropy (above tau) with sufficient gap should write
        policy.observe(2.0)  # entropy >= tau
        assert policy.should_write(is_prefill=False) is True
        assert policy.n_allowed == 2

    def test_smoke_continuous_policy(self):
        """Verify Continuous policy always writes."""
        from prabodha.steering.timing import make_policy

        policy = make_policy("continuous")

        for i in range(5):
            assert policy.should_write(is_prefill=False) is True
        assert policy.n_allowed == 5

    def test_smoke_end_to_end_config(self):
        """Verify HardeningConfig can be instantiated for E2E run."""
        config = HardeningConfig(
            model_id="sshleifer/tiny-gpt2",  # tiny model for smoke
            harmful_texts=["do bad thing"],
            harmless_texts=["do good thing"],
            test_harmful_texts=["test bad"],
            test_harmless_texts=["test good"],
            candidate_layers=[0, 1],
            write_layer=0,
            coeff=0.1,
            tau_percentile=50.0,
            max_new_tokens=5,
            seed=42,
            hypotheses={
                "H_attack": {"threshold": 0.3},
                "H_harden_gated": {"threshold": 0.5},
                "H_freedom": {"threshold": 0.0},
            },
        )
        assert config.model_id == "sshleifer/tiny-gpt2"
        assert len(config.candidate_layers) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
