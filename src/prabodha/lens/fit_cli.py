"""fit CLI: python -m prabodha.lens.fit_cli --model <yaml> --lens <yaml> --out <pt> [--resume]"""
import argparse
import logging
from pathlib import Path
from prabodha.config import load
from prabodha.lens.adapter import LensAdapter, build_model

def main() -> None:
    # Surface vendor jlens fit progress (logger.info per checkpoint) — hours-long GPU
    # fits must not run silent.
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--lens", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--resume", action="store_true")
    a = ap.parse_args()
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    hf, tok = build_model(load(a.model))
    LensAdapter("jacobian").fit(hf, tok, load(a.lens), out=a.out)
    print(f"lens saved: {a.out}")

if __name__ == "__main__":
    main()
