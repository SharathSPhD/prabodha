---
name: lens-map
description: Fit a band-targeted Jacobian lens to a HuggingFace decoder LLM and map its workspace band (fit, evaluate, visualize). Use when the user wants to inspect what a model's mid-depth layers verbalize, fit a lens, or produce a lens slice page.
---

# Lens fit + band map

Requires `pip install prabodha` (add `[hybrid]` for linear-attention architectures) and
a CUDA device. All commands are local; nothing leaves the machine.

## Workflow

1. **Fit** a lens for the model (checkpoint-resumable; takes minutes to hours by size):
   ```bash
   prabodha lens-fit --model configs/models/<model>.yaml --lens configs/lens.yaml \
     --out outputs/lens_<model>.pt
   ```
   For band readback (the main use), set the lens config's `target_layer` to the
   band-exit layer, NOT the final layer — final-target lenses are blind to band
   content (this is a measured result, not a preference).

2. **Evaluate** report-correspondence and band structure:
   ```bash
   prabodha lens-eval --model <model>.yaml --lens-file outputs/lens_<model>.pt \
     --exp configs/experiments/e1.yaml --out gates/lens_eval.json
   ```
   Read the gate JSON: `per_layer` correspondence rises with depth on healthy decoders;
   three-band CKA structure marks the workspace band.

3. **Visualize** a slice page for a prompt:
   ```bash
   prabodha lens-vis --model <model>.yaml --lens-file outputs/lens_<model>.pt \
     --prompt "..." --out slice.html
   ```

## Calibration rules (measured, not folklore)
- Rank-correlation metrics on the union of top-K supports have a structural null floor
  near −0.7; use model-top-K support and permutation nulls.
- Instructed-concept loadability scales with model size and collapses on
  pruned/distilled lineages — a zero on a distilled model can be genuine.
