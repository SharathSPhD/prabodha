"""CPU smoke: tiny fit -> vis_cli slice page (self-contained HTML). No network.
Marked smoke; requires torch+transformers+vendored jlens installed.
"""
import pytest

pytestmark = pytest.mark.smoke
torch = pytest.importorskip("torch")
transformers = pytest.importorskip("transformers")
jlens = pytest.importorskip("jlens")

from pathlib import Path
import prabodha.lens.vis_cli as vis_cli
from prabodha.config import load
from prabodha.lens.adapter import LensAdapter, build_model

ROOT = Path(__file__).resolve().parents[1]


def test_tiny_slice_page(tmp_path):
    hf, tok = build_model(load(ROOT / "configs/models/tiny_smoke.yaml"))
    lens_cfg = {"n_prompts": 2, "corpus": "synthetic_smoke", "seed": 42,
                "prompt_len": 24, "skip_first": 2}
    LensAdapter("jacobian").fit(hf, tok, lens_cfg, out=tmp_path / "tiny.pt")
    out = tmp_path / "page.html"
    vis_cli.main(["--model", str(ROOT / "configs/models/tiny_smoke.yaml"),
                  "--lens-file", str(tmp_path / "tiny.pt"),
                  "--prompt", "nadī agni vāyu soma gauḥ aśvaḥ",
                  "--out", str(out), "--title", "smoke"])
    html = out.read_text(encoding="utf-8")
    assert len(html) > 1000 and "smoke" in html
