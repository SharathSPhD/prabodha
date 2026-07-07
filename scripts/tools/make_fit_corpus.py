"""make_fit_corpus.py — generate the pre-registered pretraining-like fit corpus (L1 D2).
Concept: ābhāsa-sāmagrī — the stream of ordinary appearances the mirror is polished against;
the lens must be fit on unremarkable text so that what it reveals is the model, not the probe.
Source: jacobian-lens README (corpus guidance: pretraining-distribution prompts, quality
saturates ~100); configs/lens/fit_default.yaml (n_prompts pre-registered per R4).
Primitive: local HF-datasets arrow cache -> seeded non-overlapping word windows -> flat
one-prompt-per-line file consumed by prabodha.lens.adapter._prompts (corpus: pretraining_like).

Host-side, one-time, CPU-only. Example (on the Spark):
  python3 scripts/tools/make_fit_corpus.py \
    --arrow ~/.cache/huggingface/datasets/wikitext/wikitext-2-raw-v1/0.0.0/<hash>/wikitext-train.arrow \
    --out outputs/corpora/wikitext2_64x128.txt
"""
import argparse
import random
from pathlib import Path


def load_text_arrow(path: str) -> str:
    """Read the 'text' column of an HF-datasets arrow cache file (stream or file format)."""
    import pyarrow as pa
    with pa.memory_map(str(path)) as src:
        try:
            table = pa.ipc.open_stream(src).read_all()
        except pa.ArrowInvalid:
            table = pa.ipc.open_file(src).read_all()
    return "\n".join(t for t in table.column("text").to_pylist() if t and t.strip())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arrow", required=True, help="HF datasets .arrow cache file with 'text'")
    ap.add_argument("--out", required=True)
    ap.add_argument("--n-prompts", type=int, default=64)
    ap.add_argument("--window-words", type=int, default=128)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    words = load_text_arrow(a.arrow).split()
    n_windows = (len(words) - 1) // a.window_words
    if n_windows < a.n_prompts:
        raise SystemExit(f"corpus too small: {n_windows} windows < {a.n_prompts} prompts")
    rng = random.Random(a.seed)
    starts = sorted(rng.sample(range(n_windows), a.n_prompts))
    prompts = [" ".join(words[s * a.window_words:(s + 1) * a.window_words]) for s in starts]
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(prompts) + "\n", encoding="utf-8")
    print(f"wrote {len(prompts)} x {a.window_words}-word prompts "
          f"(seed={a.seed}, {len(words)} corpus words) -> {out}")


if __name__ == "__main__":
    main()
