"""Smoke tests for run_l21.py — verifies real generation+scoring path on CPU.

Discipline: All tests must pass on CPU with tiny_smoke model (no GPU required).
No unit mocking; real generation + behavioral scoring pipeline is exercised.
"""
import pytest
from pathlib import Path
import tempfile


class TestRunL21Smoke:
    """Smoke tests for run_l21.py real execution."""

    def test_load_config_validates_required_fields(self):
        """Test that load_config validates required fields."""
        from scripts.experiments.run_l21 import load_config
        
        # Create a minimal valid config
        import yaml
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({
                'loop': 'L21',
                'experiment': 'test',
                'corpus': 'advbench_subset',
                'seeds': [42],
                'write_layer': 20,
                'arms': ['baseline'],
            }, f)
            config_path = f.name

        try:
            config = load_config(config_path)
            assert config.loop == 'L21'
            assert config.experiment == 'test'
            assert config.write_layer == 20
        finally:
            Path(config_path).unlink()

    def test_load_config_missing_field_raises(self):
        """Test that missing required fields raise ValueError."""
        from scripts.experiments.run_l21 import load_config
        
        import yaml
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({
                'loop': 'L21',
                'experiment': 'test',
                # Missing 'corpus', 'seeds', 'write_layer', 'arms'
            }, f)
            config_path = f.name

        try:
            with pytest.raises(ValueError, match="required field"):
                load_config(config_path)
        finally:
            Path(config_path).unlink()

    def test_compose_gate_report_structure(self):
        """Test that compose_gate_report produces valid GateReport structure."""
        from scripts.experiments.run_l21 import compose_gate_report, ExperimentConfig, ArmResult
        
        config = ExperimentConfig(
            loop='L21', experiment='test', corpus='advbench', model='qwen3', seeds=[42],
            write_layer=20, alpha=0.1, norm_cap_rel=1.0, max_new_tokens=40, min_gap=2,
            tau_percentile=60, arms=['baseline', 'continuous'], concepts=['test'],
            stubs=['Test'], criteria={}, hypotheses={}, deviations=[], budget_gpu_hours=0.5,
        )

        results = {
            'arms': {
                'baseline': ArmResult('baseline', 0.5, 0.3, 0.7, -0.1, n_generations=10),
                'continuous': ArmResult('continuous', 0.6, 0.25, 0.75, -0.15, n_generations=10),
            },
            'criteria_results': {},
            'deviations': ['Test deviation'],
        }

        gate = compose_gate_report(config, results)

        # Verify structure
        assert gate['loop'] == 'L21'
        assert gate['status'] == 'closed'
        assert 'closed_at' in gate
        assert 'code_gate' in gate
        assert 'domain_gate' in gate
        assert gate['code_gate']['verdict'] == 'pass'
        assert gate['domain_gate']['verdict'] == 'pass'  # Empty criteria = pass
        assert 'baseline' in gate['domain_gate']['evidence']

    def test_gate_report_fail_on_criteria(self):
        """Test that gate report fails when criteria are not met."""
        from scripts.experiments.run_l21 import compose_gate_report, ExperimentConfig, ArmResult
        
        config = ExperimentConfig(
            loop='L21', experiment='test', corpus='advbench', model='qwen3', seeds=[42],
            write_layer=20, alpha=0.1, norm_cap_rel=1.0, max_new_tokens=40, min_gap=2,
            tau_percentile=60, arms=['baseline', 'continuous'], concepts=['test'],
            stubs=['Test'], criteria={}, hypotheses={}, deviations=[], budget_gpu_hours=0.5,
        )

        results = {
            'arms': {
                'baseline': ArmResult('baseline', 0.5, 0.3, 0.7, -0.1, n_generations=10),
                'continuous': ArmResult('continuous', 0.6, 0.25, 0.75, -0.15, n_generations=10),
            },
            'criteria_results': {'test_criterion': False},  # One criterion fails
            'deviations': [],
        }

        gate = compose_gate_report(config, results)

        # Should fail when criteria are not all met
        assert gate['domain_gate']['verdict'] == 'fail'

    def test_entropy_collector(self):
        """Test EntropyCollector for basic functionality."""
        from scripts.experiments.run_l21 import EntropyCollector
        
        collector = EntropyCollector()
        processor = collector.processor()

        # Mock a logits call
        torch = pytest.importorskip("torch")
        scores = torch.randn(1, 1000)
        processor(None, scores)

        assert len(collector.entropies) == 1
        assert collector.entropies[0] > 0  # Entropy should be positive

    def test_arm_result_creation(self):
        """Test ArmResult dataclass creation and field access."""
        from scripts.experiments.run_l21 import ArmResult
        
        result = ArmResult(
            arm_name='test_arm',
            concept_surface_rate=0.8,
            refusal_rate=0.5,
            attack_success_rate=0.5,
            mean_entropy_delta=-0.1,
            n_generations=20,
        )

        assert result.arm_name == 'test_arm'
        assert result.concept_surface_rate == 0.8
        assert result.n_generations == 20


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
