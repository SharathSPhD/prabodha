"""L22 pre-flight: both lenses must expose source layers covering the readback
window (24, 28] or the head-to-head is impossible.
Concept: pariksa (examination before the rite).
Source: e_l22_lens_headtohead.yaml pre-registration.
Primitive: load both checkpoints, assert non-empty readback window.
"""
from prabodha.lens.adapter import LensAdapter

for name in ("outputs/l10/lens_qwen3_mid30.pt", "outputs/l10/lens_qwen3_final.pt"):
    ad = LensAdapter("jacobian").load(name)
    win = [l for l in ad.source_layers if 24 < l <= 28]
    print(name, "source_layers window (24,28]:", win)
    assert win, f"{name}: empty readback window - head-to-head impossible"
print("sanity OK")
