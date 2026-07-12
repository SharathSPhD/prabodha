"""Generate REAL recorded lens-slice visualizations for the app's Lens Playground.

No fabrication: loads the real Qwen3-4B model + its real fitted band-exit lens
(lens_qwen3_mid30) once, then for each fixed prompt computes the vendor jlens
slice (compute_slice) and renders the self-contained slice page (build_page,
embed mode). These static HTML pages are the genuine layer-by-layer lens read-out
— the same instrument the paper's qualitative "direct seeing" pages use — and are
served as recorded artifacts so anyone (not just admins) can read a real band.

Run inside the gb10 container (repo at /repo, lens at /lens):
  docker exec steer-gateway sh -c \
    "cd /repo && LENS_FILE=/lens/l10/lens_qwen3_mid30.pt python3 scripts/experiments/generate_lens_slices.py"
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, "/repo/src")

from prabodha.config import load
from prabodha.lens.adapter import LensAdapter, build_model

MODEL_YAML = os.environ.get("MODEL_YAML", "/repo/configs/models/qwen3.yaml")
LENS_FILE = os.environ.get("LENS_FILE", "/lens/l10/lens_qwen3_mid30.pt")
OUT_DIR = Path(os.environ.get("OUT_DIR", "/repo/outputs/lens_slices"))

# Fixed prompts that show the band doing recognisable work: a fact, the confirmed
# sensory concept, and an alignment/truth statement.
PROMPTS = [
    {"id": "capital", "label": "A factual question", "prompt": "What is the capital of France?"},
    {"id": "fire", "label": "The confirmed sensory concept", "prompt": "It is a beautiful day and the temperature outside is"},
    {"id": "promise", "label": "An alignment / truth statement", "prompt": "I promise I will always tell you the truth."},
]


def main() -> None:
    import jlens
    from jlens.vis import build_page, compute_slice

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cfg = load(MODEL_YAML)
    print(f"[slices] loading {cfg.get('hf_id')} + lens {Path(LENS_FILE).name}", flush=True)
    hf, tok = build_model(cfg)
    adapter = LensAdapter("jacobian").load(LENS_FILE)
    model = jlens.from_hf(hf, tok)

    manifest = []
    for spec in PROMPTS:
        print(f"[slices] computing '{spec['prompt']}'", flush=True)
        sl = compute_slice(model, adapter._lens, spec["prompt"])
        page, w, h = build_page(
            sl, spec["prompt"], title=f"prabodha lens slice — {spec['label']}",
            description=f"model={cfg.get('hf_id')} lens={Path(LENS_FILE).name} (real recorded read)",
            mode="embed",
        )
        out = OUT_DIR / f"slice_{spec['id']}.html"
        out.write_text(page, encoding="utf-8")
        print(f"[slices] wrote {out} ({out.stat().st_size // 1024} KiB, {w}x{h})", flush=True)
        manifest.append({
            "id": spec["id"], "label": spec["label"], "prompt": spec["prompt"],
            "file": f"slice_{spec['id']}.html", "width": w, "height": h,
        })

    (OUT_DIR / "manifest.json").write_text(json.dumps({
        "model": cfg.get("hf_id"),
        "lens": Path(LENS_FILE).name,
        "note": "Real recorded lens-slice read-outs (vendor jlens compute_slice). Not fabricated.",
        "slices": manifest,
    }, indent=2))
    print(f"[slices] manifest written; {len(manifest)} slices", flush=True)


if __name__ == "__main__":
    main()
