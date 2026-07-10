---
name: steer-verify
description: Run a complete steering episode (fit lens, apply recognition-gated writes, run readback verification) and interpret the results. Use when the user wants to steer a concept through a model with evidence of behavioral change. Walks through prabodha steer → readback verification end-to-end.
---

# Run a steering episode with readback verification (operational)

Requires `pip install prabodha[lens]` (torch, transformers, jacobian-lens) and a CUDA device.
All commands are local; nothing leaves the machine.

## Workflow (invoke prabodha CLI end-to-end)

### Step 1: Prepare model, concept, and steering config

First, choose:
- **Model:** e.g., Qwen3-4B (ensure `configs/models/Qwen3-4B.yaml` exists)
- **Concept:** e.g., "fire" (verbalizable concept, loaded via the workspace band)
- **Prompt:** seed text to steer, e.g., "the fire remembers rivers"
- **Arm:** steering strategy (default: `entropy_gated`)
- **Seed:** random seed (use 42, 123, or 777 for clean stream)

Ensure `configs/experiments/e4.yaml` exists with steering hyperparameters:
- `alpha`: write amplitude (calibrated inversely to lens transport strength; typical 0.1–0.5)
- `tau_percentile`: entropy-gate threshold (0–100; higher = more selective)
- `site_layer`: steering site (band-exit layer, measured via lens eval)

**Calibration rule:** Write amplitude `alpha` scales inversely with lens transport strength.
Measure via gate_L9_alignconf.json and tune for the model and concept.

### Step 2: Run the steering episode

This step:
1. Loads the model and lens (or fits if absent)
2. Runs the prompt through the model with recognition-gated concept writes applied
3. Emits a SteerTrace JSON with per-token entropy, write norms, band readout, and token sequence

```bash
prabodha steer \
  --model configs/models/Qwen3-4B.yaml \
  --concept fire \
  --prompt "the fire remembers rivers" \
  --arm entropy_gated \
  --seed 42 \
  --alpha 0.3 \
  --tau-percentile 60 \
  --emit-trace outputs/traces/steer_fire_42.json
```

Expected output:
- Trace JSON written to `outputs/traces/steer_fire_42.json`
- Console logs per token: entropy, whether gated, write norm, band readout top-k

### Step 3: Inspect the trace

The trace JSON (`outputs/traces/steer_fire_42.json`) contains:

```json
{
  "schema_version": 1,
  "model_id": "Qwen/Qwen3-4B",
  "prompt": "the fire remembers rivers",
  "concept": "fire",
  "arm": "entropy_gated",
  "seed": 42,
  "alpha": 0.3,
  "tau_percentile": 60,
  "tokens": [
    {
      "t": 0,
      "token": " The",
      "entropy": 2.31,
      "gated": false,
      "band_topk": ["The", "the", "a"]
    },
    {
      "t": 1,
      "token": " fire",
      "entropy": 1.02,
      "gated": true,
      "write_norm": 0.30,
      "band_topk": ["fire", "flame", "ember"]
    },
    ...
  ],
  "readback": null,
  "gate_ref": "gates/gate_L9_alignconf.json"
}
```

**Key fields:**
- `entropy`: predictive entropy pre-write (nats). High = uncertain, low = confident.
- `gated`: True if a sphuraṭṭā (event-gated) write was applied at this token.
- `write_norm`: L2 norm of the concept write vector (None if not gated).
- `band_topk`: top-k tokens in the workspace band readout at this step.

### Step 4: Run readback verification

Readback measures whether the steering left a detectable signal in the model's token logits.
**Caveat:** readback is probabilistic and noisy; single runs are not confirmatory.
Multi-seed readback at the confirm tier (gates/) is required for claims.

```bash
prabodha steer \
  --readback outputs/traces/steer_fire_42.json
```

Expected output (JSON or text):
```
{
  "verdict": "accepted",
  "top_m": 5,
  "gain": 0.0123,
  "concept_rank": 2
}
```

**Interpretation:**
- `verdict`: "accepted" | "rejected" (does the signal pass threshold?)
- `top_m`: readback rank threshold (how many top-k tokens were considered?)
- `gain`: entropy gain/loss in nats
- `concept_rank`: where the concept token ranked in the readout (lower is better)

### Step 5: Interpret the full episode

The combination of:
1. **Gating pattern:** entropy trace tells you when writes were triggered (high-entropy moments)
2. **Write norms:** tell you amplitude at each step (calibration sanity check)
3. **Band readout:** the verbalizable workspace, moment-by-moment
4. **Readback verdict:** probabilistic weak-signal evidence of behavioral change

**Common patterns:**
- **High entropy early, low later:** entropy naturally drops during generation; gating is selective.
- **Write norm amplifies concept token:** the write is pushing the band readout toward the concept.
- **Readback accepted:** the band reorganization is detectable (weak signal; not confirmatory alone).
- **Readback rejected:** signal didn't pass threshold (can be noisy; re-run with different seed).

## Calibration & troubleshooting

- **No gates triggered (gated=false everywhere):** entropy threshold (tau_percentile) is too low; raise it or lower tau_percentile.
- **Writes too large (write_norm > 1.0):** alpha is too high; reduce it (start at 0.1, tune up).
- **Readback always rejected:** either the concept is not in the band, or alpha is too small.

**Tune via:** `gates/gate_L9_alignconf.json` (arm/seed/alpha/concept baseline) and the lens
evaluation gate for the model.

## Gate citation

**Default gate:** `gates/gate_L9_alignconf.json` (arm/seed/alpha semantics for Qwen3-4B, entropy_gated arm).
**Readback gate:** `gates/gate_L14_readback.json` (readback method + thresholds).

The trace's `gate_ref` field points to the governing gate for that run.
