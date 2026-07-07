"""vis CLI: python -m prabodha.lens.vis_cli --model <yaml> --lens-file <pt> --prompt "..." --out <html>
Concept: sākṣāt-darśana — direct seeing; the qualitative slice page that lets a human read
the lens's layer-by-layer account of a prompt before trusting any aggregate metric.
Source: vendor jlens.vis (compute_slice/build_page, embed mode = self-contained HTML);
contracts/L1_qwen_replication.md D5 (slice-vis sample page).
Primitive: load model + lens -> compute_slice -> single-file HTML page.
"""
import argparse
import logging
from pathlib import Path

from prabodha.config import load
from prabodha.lens.adapter import LensAdapter, build_model


def main(argv=None) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--lens-file", required=True)
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", default="prabodha slice sample")
    ap.add_argument("--last-n-tokens", type=int, default=None,
                    help="window the slice grid to the last N positions (long prompts)")
    a = ap.parse_args(argv)
    import jlens
    from jlens.vis import build_page, compute_slice
    hf, tok = build_model(load(a.model))
    adapter = LensAdapter("jacobian").load(a.lens_file)
    model = jlens.from_hf(hf, tok)
    kwargs = {"last_n_tokens": a.last_n_tokens} if a.last_n_tokens else {}
    sl = compute_slice(model, adapter._lens, a.prompt, **kwargs)
    page, _w, _h = build_page(sl, a.prompt, title=a.title,
                              description=f"model={load(a.model).get('hf_id', 'tiny')} "
                                          f"lens={Path(a.lens_file).name}", mode="embed")
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    print(f"slice page written: {out} ({out.stat().st_size // 1024} KiB)")


if __name__ == "__main__":
    main()
