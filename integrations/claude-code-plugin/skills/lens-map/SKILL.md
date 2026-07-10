---
name: lens-map
description: Fit a band-targeted Jacobian lens to any HuggingFace decoder LLM and map its workspace band (fit, evaluate, visualize). Use when the user wants to inspect what a model's mid-depth layers verbalize, or produce a lens slice visualization. Walks through prabodha lens-fit → lens-eval → lens-vis end-to-end.
---

# Fit a band-targeted workspace lens (operational)

Requires `pip install prabodha` (add `[lens]` for torch/transformers) and a CUDA device.
All commands are local; nothing leaves the machine.

## Workflow (invoke prabodha CLI end-to-end)

### Step 1: Prepare model and lens configs

First, identify your target model. We'll use Qwen3-4B as an example.

```bash
# Check that a model config exists, or create one:
test -f configs/models/Qwen3-4B.yaml || echo "Config not found; copy an existing model config and edit model_id"
```

Ensure `configs/models/<model>.yaml` has:
- `model_id`: the HF model ID (e.g., `Qwen/Qwen3-4B`)
- `torch_dtype`: dtype (e.g., `bfloat16`)

And `configs/lens.yaml` exists with:
- `target_layer`: band-exit layer (NOT final layer; measure via e1_metrics on healthy models)
- `rank`, `dtype`, etc.

**Calibration rule:** Band readback (the main use) requires `target_layer` to be the band-exit layer,
NOT the final layer — final-target lenses are blind to band content (measured result on e1_metrics).

### Step 2: Run the fit

This step trains the lens projection matrix. Duration scales with model size (minutes to hours).

```bash
prabodha lens-fit \
  --model configs/models/Qwen3-4B.yaml \
  --lens configs/lens.yaml \
  --out outputs/lens_Qwen3-4B.pt
```

Expected output: checkpoint written to `outputs/lens_Qwen3-4B.pt`.

**Checkpoint resume:** If interrupted, re-run the same command; fit resumes from checkpoint.

### Step 3: Evaluate lens correspondence

This step measures how well the lens reconstructs the workspace band.

```bash
prabodha lens-eval \
  --model configs/models/Qwen3-4B.yaml \
  --lens-file outputs/lens_Qwen3-4B.pt \
  --exp configs/experiments/e1.yaml \
  --out gates/lens_eval_Qwen3-4B.json
```

Expected output: gate JSON at `gates/lens_eval_Qwen3-4B.json` with:
- `per_layer_cka`: CKA correspondence by layer (rises with depth on healthy models)
- `band_structure`: three-band indicator (marks workspace band)

**Read the gate:** CKA rises from ~0.3 at shallow layers to ~0.7+ at band layers on healthy decoders.
Flat or inverted curves indicate modeling issues (pruning, quantization, etc.).

### Step 4: (Optional) Visualize the band for a prompt

Generate an interactive slice page showing the band readout for a specific input.

```bash
prabodha lens-vis \
  --model configs/models/Qwen3-4B.yaml \
  --lens-file outputs/lens_Qwen3-4B.pt \
  --prompt "Once upon a time in" \
  --out slice_Qwen3-4B.html
```

Open `slice_Qwen3-4B.html` in a browser. You'll see:
- Band CKA per token (heatmap)
- Token sequence
- Top-k band readout per token (the verbalizable workspace)

## Calibration & interpretation

- **Rank-correlation null floor:** −0.7 on permutation nulls; don't trust correlations above −0.4 without support.
- **Instructed-concept loadability:** scales with model size; collapses on pruned/distilled lineages.
- **Zero on distilled models:** can be genuine (the band is compressed away).

## Gate citation

The lens evaluation gate (`gates/lens_eval_Qwen3-4B.json`) records:
- Model, layer depths, lens rank, CKA structure
- See the gate file directly for exact numbers

**Default gate:** `gates/gate_L13_recipe.json` (band readback correspondence structure on healthy
models, Qwen3-4B arm).
