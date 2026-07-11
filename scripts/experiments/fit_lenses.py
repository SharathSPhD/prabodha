"""Fit a REAL Jacobian lens for a chosen model on GB10.

No shortcuts: uses the same fitting pipeline and pre-registered config as the committed Qwen3
lens (n_prompts=16, seq_len=128, pretraining-like wikitext corpus, all layers up to the model's
depth). Saves outputs/lenses/<slug>.pt for the gateway to load. One model per invocation
(MODEL env) so a single GPU fits them sequentially.

Usage (in the gb10 container):
  MODEL=google/gemma-2-2b-it LENS_OUT=/repo/outputs/lenses/gemma-2-2b-it.pt python3 scripts/experiments/fit_lenses.py
"""
import os
import sys
import time
sys.path.insert(0, "/repo/src")

from prabodha.lens.adapter import LensAdapter, build_model

CORPUS = os.environ.get("FIT_CORPUS", "/repo/outputs/corpora/wikitext2_64x128.txt")


def ensure_corpus(path: str, n: int = 64, window: int = 128, seed: int = 42) -> None:
    if os.path.exists(path):
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    print(f"[corpus] generating {path} from wikitext-2-raw-v1 ({n}x{window} words)", flush=True)
    import subprocess
    try:
        import datasets  # noqa
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "datasets"], check=True)
        import datasets  # noqa
    from datasets import load_dataset
    # Salesforce/wikitext is the maintained parquet mirror ("wikitext" script dataset is deprecated).
    ds = load_dataset("Salesforce/wikitext", "wikitext-2-raw-v1", split="train")
    words = " ".join(t for t in ds["text"] if t and t.strip()).split()
    import random
    rng = random.Random(seed)
    n_windows = (len(words) - 1) // window
    if n_windows < n:
        raise SystemExit(f"corpus too small: {n_windows} windows < {n}")
    starts = sorted(rng.sample(range(n_windows), n))
    lines = [" ".join(words[s * window:(s + 1) * window]) for s in starts]
    open(path, "w").write("\n".join(lines) + "\n")
    print(f"[corpus] wrote {len(lines)} windows to {path}", flush=True)


def fit_one(model_id: str) -> None:
    out = f"/repo/outputs/lenses/{model_id.split('/')[-1].lower()}.pt"
    if os.path.exists(out):
        print(f"[fit] SKIP {model_id} (lens already exists at {out})", flush=True)
        return
    print(f"[fit] loading {model_id}", flush=True)
    cfg = {"hf_id": model_id, "dtype": "bf16", "device": "cuda", "trust_remote_code": False}
    hf, tok = build_model(cfg)
    n_layers = int(hf.config.num_hidden_layers)
    # Fit jacobians across the full depth so any band site_layer is covered. target_layer is the
    # read target; the lens produces per-layer jacobians for layers [0, target_layer).
    target_layer = n_layers - 1  # read target must be a valid layer index (< n_layers)
    lens_cfg = {
        "n_prompts": int(os.environ.get("FIT_N_PROMPTS", "16")),
        "seq_len": 128,
        "corpus": "pretraining_like",
        "corpus_file": CORPUS,
        "target_layer": target_layer,
        "checkpoint_every": 8,
        "seed": 42,
    }
    site_layer = int(0.62 * n_layers)
    print(f"[fit] {model_id}: n_layers={n_layers} target_layer={target_layer} site_layer={site_layer} "
          f"n_prompts={lens_cfg['n_prompts']}", flush=True)
    t0 = time.time()
    os.makedirs(os.path.dirname(out), exist_ok=True)
    try:
        LensAdapter("jacobian").fit(hf, tok, lens_cfg, out=out)
    finally:
        import torch
        del hf
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    dt = time.time() - t0
    size = os.path.getsize(out) if os.path.exists(out) else 0
    print(f"[fit] DONE {model_id} -> {out} ({size/1e6:.1f} MB) in {dt/60:.1f} min "
          f"(recommended site_layer={site_layer})", flush=True)


def main() -> None:
    ensure_corpus(CORPUS)
    models = os.environ.get("MODELS")
    ids = [m.strip() for m in models.split(",") if m.strip()] if models else [os.environ["MODEL"]]
    for mid in ids:
        try:
            fit_one(mid)
        except Exception as e:  # keep going so one bad model doesn't block the batch
            print(f"[fit] FAILED {mid}: {e}", flush=True)


if __name__ == "__main__":
    main()
