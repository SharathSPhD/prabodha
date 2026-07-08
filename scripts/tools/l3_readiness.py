"""l3_readiness.py — Selectivity@5 entry gate for L3 writes (adversarial review #4, L2 card).
Concept: yogyatā-parīkṣā — testing the site's fitness before writing to it; is the onset
layer already inside the representational funnel that decides the model's report?
Source: contracts/L2_pwm_stack.md "L3 ENTRY GATE"; review #4's decision thresholds.
Primitive: per prompt, |lens_top5(onset_layer) ∩ model_top5| / 5 at position -1, averaged;
verdict GO (>=0.75) / READBACK_GATED (0.60-0.75) / NO_GO (<0.60) -> gates/gate_L3_readiness.json.

Usage (inside the prabodha container):
  python scripts/tools/l3_readiness.py --model configs/models/nemotron4b.yaml \
    --lens-file outputs/l2/lens_nemotron4b.pt --lens-cfg configs/lens/fit_default.yaml \
    --layer 6 --out gates/gate_L3_readiness.json
"""
import argparse
import datetime
import json
from pathlib import Path

from prabodha.config import load
from prabodha.lens.adapter import LensAdapter, _prompts, build_model


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--lens-file", required=True)
    ap.add_argument("--lens-cfg", required=True, help="for the eval prompt list (corpus_file)")
    ap.add_argument("--layer", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--go", type=float, default=0.75)
    ap.add_argument("--no-go", type=float, default=0.60)
    a = ap.parse_args(argv)
    import torch
    hf, tok = build_model(load(a.model))
    adapter = LensAdapter("jacobian").load(a.lens_file)
    prompts = _prompts(load(a.lens_cfg))
    per_prompt = []
    for prompt in prompts:
        lens_logits, model_logits = adapter.read_with_model(
            hf, tok, prompt, positions=[-1], layers=[a.layer])
        lens_top = set(torch.topk(lens_logits[a.layer][0], k=5).indices.tolist())
        model_top = set(torch.topk(model_logits[0], k=5).indices.tolist())
        per_prompt.append(len(lens_top & model_top) / 5)
    value = sum(per_prompt) / len(per_prompt)
    verdict = ("GO" if value >= a.go else
               "NO_GO" if value < a.no_go else "READBACK_GATED")
    report = {"check": "selectivity_at5", "layer": a.layer, "value": round(value, 4),
              "per_prompt": [round(x, 2) for x in per_prompt],
              "thresholds": {"go": a.go, "no_go": a.no_go}, "verdict": verdict,
              "n_prompts": len(prompts), "date": str(datetime.date.today()),
              "lineage": "contracts/L2_pwm_stack.md L3 ENTRY GATE (review #4)"}
    Path(a.out).write_text(json.dumps(report, indent=2))
    print(f"L3 readiness: selectivity@5(layer {a.layer}) = {value:.3f} -> {verdict} ({a.out})")


if __name__ == "__main__":
    main()
