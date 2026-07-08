"""CPU smoke: tiny fit -> plan_write -> ResidualInjector -> lens rank moves. No network.
The round-trip the E3 run depends on: a write along the lens concept direction must
improve that concept's lens rank downstream of the write layer.
"""
import pytest

pytestmark = pytest.mark.smoke
torch = pytest.importorskip("torch")
transformers = pytest.importorskip("transformers")
jlens = pytest.importorskip("jlens")

from pathlib import Path


from prabodha.config import load
from prabodha.lens.adapter import LensAdapter, build_model
from prabodha.steering.injector import ResidualInjector, logit_bias_processor
from prabodha.steering.writer import plan_write

ROOT = Path(__file__).resolve().parents[1]


def _rank(logits_row, token_id):
    return int((logits_row > logits_row[token_id]).sum().item())


def test_band_write_moves_lens_rank(tmp_path):
    hf, tok = build_model(load(ROOT / "configs/models/tiny_smoke.yaml"))
    lens_cfg = {"n_prompts": 2, "corpus": "synthetic_smoke", "seed": 42,
                "prompt_len": 24, "skip_first": 2}
    ad = LensAdapter("jacobian").fit(hf, tok, lens_cfg, out=tmp_path / "tiny.pt")
    lm = jlens.from_hf(hf, tok)
    wl = ad.source_layers[0]
    rb = [layer for layer in ad.source_layers if layer > wl] or [wl]
    concept_id = 5
    J = ad._lens.jacobians[wl].float().cpu().numpy()
    U = hf.get_output_embeddings().weight.detach().float().cpu().numpy()
    prompt = "nadī agni vāyu soma gauḥ aśvaḥ"
    clean = ad.read(hf, tok, prompt, positions=[-1], layers=rb)
    pre = min(_rank(clean[layer][0], concept_id) for layer in rb)
    # strong smoke-scale write so the tiny random model shows an unambiguous move
    cmd = plan_write(J, U[[concept_id]], wl, [concept_id], alpha=2.0, norm_cap_rel=2.0)
    with ResidualInjector(lm.layers[wl], cmd) as inj:
        written = ad.read(hf, tok, prompt, positions=[-1], layers=rb)
    assert inj.n_applications >= 1
    post = min(_rank(written[layer][0], concept_id) for layer in rb)
    assert post < pre, f"write did not improve lens rank ({pre} -> {post})"
    # hook is removed on exit: a fresh read matches the clean read
    again = ad.read(hf, tok, prompt, positions=[-1], layers=rb)
    assert min(_rank(again[layer][0], concept_id) for layer in rb) == pre


def test_logit_bias_processor_shifts_scores():
    scores = torch.zeros(1, 50)
    proc = logit_bias_processor([7, 9], 4.0)
    out = proc(None, scores)
    assert out[0, 7] == 4.0 and out[0, 9] == 4.0 and out[0, 0] == 0.0
