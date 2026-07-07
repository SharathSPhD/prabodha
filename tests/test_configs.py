from pathlib import Path
from prabodha.config import load

ROOT = Path(__file__).resolve().parents[1]

def test_all_configs_parse_and_required_keys():
    assert load(ROOT / "configs/gpu/gb10_guard.yaml", ("trainer_patterns", "budgets_hours"))
    assert load(ROOT / "configs/models/qwen3.yaml", ("hf_id",))
    assert load(ROOT / "configs/models/tiny_smoke.yaml", ("builder", "n_layers"))
    e1 = load(ROOT / "configs/experiments/e1.yaml", ("hypotheses", "seeds", "budget_gpu_hours"))
    assert {"H_report", "H_bands", "H_modulation"} <= set(e1["hypotheses"])  # pre-registration (R4)

def test_e1_thresholds_declared_before_run():
    e1 = load(ROOT / "configs/experiments/e1.yaml")
    for h in e1["hypotheses"].values():
        assert any(k.startswith("threshold") for k in h), "R4: thresholds must be pre-registered"
