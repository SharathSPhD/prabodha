"""End-to-end CPU smoke: tiny random decoder -> jlens fit -> read. No network (R: sandbox-safe).
Marked smoke; requires torch+transformers+vendored jlens installed.
"""
import pytest

pytestmark = pytest.mark.smoke
torch = pytest.importorskip("torch")
transformers = pytest.importorskip("transformers")
jlens = pytest.importorskip("jlens")

from pathlib import Path
from prabodha.config import load
from prabodha.lens.adapter import LensAdapter, build_model

ROOT = Path(__file__).resolve().parents[1]

def test_tiny_fit_and_read(tmp_path):
    hf, tok = build_model(load(ROOT / "configs/models/tiny_smoke.yaml"))
    lens_cfg = {"n_prompts": 2, "corpus": "synthetic_smoke", "seed": 42}
    ad = LensAdapter("jacobian").fit(hf, tok, lens_cfg, out=tmp_path / "tiny.pt")
    out = ad.read(hf, tok, "nadī agni vāyu soma", positions=[-1])
    assert isinstance(out, dict) and len(out) > 0
    layer0 = sorted(out)[0]
    assert out[layer0].shape[-1] == hf.config.vocab_size
