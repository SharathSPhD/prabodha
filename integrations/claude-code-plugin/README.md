# prabodha Claude Code Plugin

Workspace-band lens fitting, visualization, and recognition-gated steering for HuggingFace decoder LLMs.

## Installation

```bash
# Install the plugin via Claude Code
/plugin install path/to/integrations/claude-code-plugin
```

This makes available:
- **Skills** (Claude Code only): `lens-map`, `steer-verify` — operational workflows that guide you through the prabodha CLI
- **MCP Tools** (any MCP client):
  - Steering primitives: `lens_map`, `steer_generate`, `readback_verify`, `list_gates`
  - **Graded hardening library**: `list_mechanisms`, `recommend_mechanism`, `characterize_model`, `harden_prompt` — pick a defense by capability/tradeoff (prompt-space works on open *and* closed models; the activation moat needs open weights)

## Usage: Skills (Claude Code)

### lens-map

Fit and evaluate a band-targeted Jacobian lens:

```
/lens-map
```

Guides you through:
1. Fit the lens (`prabodha lens-fit`)
2. Evaluate correspondence (`prabodha lens-eval`)
3. (Optional) Visualize the band for a prompt (`prabodha lens-vis`)

Output: gate JSON + optional HTML slice page.

### steer-verify

Run a steering episode with readback verification:

```
/steer-verify
```

Guides you through:
1. Run the steering episode (`prabodha steer --emit-trace`)
2. Inspect the trace (per-token entropy, writes, band readout)
3. Run readback verification (`prabodha steer --readback`)

Output: SteerTrace JSON + readback verdict.

## End-to-End Walkthrough: lens-map → steer-verify

This walkthrough demonstrates a realistic workflow: fit a Jacobian lens to a model's workspace band, then run a steering episode with readback verification.

### Step 1: Fit and evaluate the lens (lens-map)

Run:
```bash
/lens-map
```

This guides you through fitting. The tool calls:
1. `prabodha lens-fit --config configs/lens/Qwen_default.yaml --model Qwen/Qwen3-4B --output-dir ./my-lens`
2. `prabodha lens-eval --gate-ref gates/gate_L13_recipe.json --output-dir ./my-lens`

**Sample output (eval gate):**
```json
{
  "schema_version": 1,
  "fit_config": "Qwen_default.yaml",
  "model_id": "Qwen/Qwen3-4B",
  "eval_layer": 13,
  "readback_correspondence": {
    "method": "top-m rank correlation",
    "top_m": 5,
    "mean_rank": 1.8,
    "median_rank": 2,
    "percentile_95": 4,
    "pass": true
  },
  "band_transport_strength": 0.92,
  "timestamp": "2026-07-11T15:23:45Z",
  "claim": "Layer 13 has strong workspace band correspondence (mean rank 1.8 on eval set). Writing to layer 13 is a sound target.",
  "caveat": "Single-seed eval; multi-seed sweeps at higher confidence."
}
```

**What to note:**
- `readback_correspondence.mean_rank = 1.8` → when you write a concept to the band, the readback finds it ranked #2 on average
- `band_transport_strength = 0.92` → the lens explains 92% of the workspace band dynamics (well-fitted)
- This gate is now your **target layer reference** for steering

### Step 2: Run a steering episode (steer-verify)

Run:
```bash
/steer-verify
```

The skill guides you through:

**2a. Steer with trace:**
```bash
prabodha steer \
  --model Qwen/Qwen3-4B \
  --prompt "What is fire?" \
  --concept fire \
  --alpha 0.3 \
  --arm gated \
  --gate-ref gates/gate_L13_recipe.json \
  --emit-trace \
  --output-dir ./my-steer
```

**Sample trace snippet (tokens array):**
```json
{
  "schema_version": 1,
  "model_id": "Qwen/Qwen3-4B",
  "prompt": "What is fire?",
  "concept": "fire",
  "alpha": 0.3,
  "arm": "entropy_gated",
  "seed": 42,
  "tokens": [
    {
      "t": 0,
      "token": " A",
      "entropy": 5.12,
      "gated": false,
      "band_topk": [" A", " The", " In"]
    },
    {
      "t": 1,
      "token": " chemical",
      "entropy": 2.31,
      "gated": true,
      "band_write_norm": 0.3,
      "band_topk": [" chemical", " physical", " natural"]
    },
    {
      "t": 2,
      "token": " reaction",
      "entropy": 1.89,
      "gated": false,
      "band_topk": [" reaction", " process", " phenomenon"]
    }
  ],
  "gate_ref": "gates/gate_L13_recipe.json"
}
```

**What to read:**
- `tokens[1].gated = true` → entropy at token 1 (2.31 nats) crossed the threshold (tau_percentile=60), so the write injected
- `tokens[1].band_topk` → after the write, the workspace band's top-5 concepts are ranked in this order
- `band_write_norm = 0.3` → the write magnitude was 0.3 (matches alpha)

**2b. Readback verification:**
```bash
prabodha steer \
  --readback \
  --trace-json my-steer/trace.json \
  --gate-ref gates/gate_L14_readback.json
```

**Sample readback verdict:**
```json
{
  "status": "ok",
  "verdict": "accepted",
  "top_m": 5,
  "concept": "fire",
  "concept_rank": 2,
  "gain": 0.0523,
  "caveat": "single-seed readback; multi-seed required for claims"
}
```

**Interpretation:**
- `verdict = "accepted"` → the concept "fire" was successfully written and verified
- `concept_rank = 2` → on readback, "fire" appeared in the top 5 workspace band concepts, ranked #2
- `gain = 0.0523` → steering improved the concept's prominence by 5.23 percentage points vs. baseline
- **Caveat:** one run is not confirmatory; commit multi-seed runs to `gates/` for publication

### Summary

This workflow demonstrates the full loop:
1. **Fit** a lens (band-targeted Jacobian; outputs gate with correspondence metrics)
2. **Write** a concept into the workspace at the entropy-gated moment (steering trace shows per-token entropy and band state)
3. **Verify** via readback that the write persisted (rank correlation + concept prominence gain)

Use the skill's guided walkthrough (`/lens-map` and `/steer-verify`) to run these end-to-end, or call the MCP tools directly for integration into other systems.

## Usage: MCP Tools (any MCP client)

The plugin registers an MCP server exposing four tools:

### lens_map

Fit and evaluate a band-targeted Jacobian lens.

**Input:**
- `model_config`: path to model config YAML (e.g., `configs/models/Qwen3-4B.yaml`)
- `lens_config`: path to lens config YAML
- `output_dir`: output directory for lens checkpoint and gate JSON
- `prompt` (optional): seed prompt for visualization

**Output:**
```json
{
  "status": "ok",
  "fit_status": "ok",
  "eval_gate": "path/to/gate_lens_eval.json",
  "vis_page": "path/to/slice.html",
  "default_gate": "gates/gate_L13_recipe.json"
}
```

**Default gate:** `gates/gate_L13_recipe.json` (band readback correspondence structure).

### steer_generate

Run a steering episode and return the full SteerTrace JSON.

**Input:**
- `model_config`: path to model config YAML
- `concept`: steering concept (e.g., "fire")
- `prompt`: seed prompt
- `arm` (optional): steering arm (default: `entropy_gated`)
- `seed` (optional): random seed (default: 42)
- `alpha` (optional): write amplitude (default: 0.3)
- `tau_percentile` (optional): entropy-gate threshold (default: 60)

**Output:**
```json
{
  "status": "ok",
  "trace": {
    "schema_version": 1,
    "model_id": "Qwen/Qwen3-4B",
    "prompt": "...",
    "concept": "fire",
    "arm": "entropy_gated",
    "seed": 42,
    "tokens": [
      {
        "t": 0,
        "token": " The",
        "entropy": 2.31,
        "gated": false,
        "band_topk": ["The", "the", "a"]
      },
      ...
    ],
    "readback": null,
    "gate_ref": "gates/gate_L9_alignconf.json"
  },
  "default_gate": "gates/gate_L9_alignconf.json"
}
```

**Default gate:** `gates/gate_L9_alignconf.json` (arm/seed/alpha semantics).

### readback_verify

Run readback verification on a completed steering trace.

**Input:**
- `trace_json_path`: path to SteerTrace JSON (output from `steer_generate`)

**Output:**
```json
{
  "status": "ok",
  "verdict": "accepted",
  "top_m": 5,
  "gain": 0.0123,
  "concept_rank": 2,
  "caveat": "readback is probabilistic and noisy; single runs not confirmatory"
}
```

**Caveat:** readback is a weak signal; multi-seed readback at the confirm tier (gates/) is required for claims.

**Default gate:** `gates/gate_L14_readback.json` (readback method + thresholds).

### list_gates

Enumerate all committed gates in `gates/*.json`.

**Input:**
- `filter_arm` (optional): filter by steering arm (e.g., "entropy_gated")
- `filter_concept` (optional): filter by concept (e.g., "fire")

**Output:**
```json
{
  "status": "ok",
  "gates": [
    {
      "path": "gates/gate_L9_alignconf.json",
      "name": "gate_L9_alignconf",
      "verdict": "pass",
      "arm": "entropy_gated",
      "concept": "fire"
    },
    ...
  ],
  "count": 42,
  "filtered_count": 5
}
```

## Graded hardening library (jailbreak resistance)

Rather than shipping a single "winner" defense, prabodha exposes a **graded library** of
hardening mechanisms so a deployer picks by capability and tradeoff. Prompt-space mechanisms
are portable to **any** model (open or closed, via BYOK/OpenRouter); activation-space mechanisms
are the prompt-untouchable server-side tier that needs open weights — culminating in the
**recognition-gated moat** (`act_recognition_gated`), which reinforces refusal only when the
input's activation-level harmful-signature crosses a threshold, so benign traffic is untouched
and jailbreak wrapping can't disguise the attack.

### list_mechanisms

List every mechanism in `prabodha.steering.mechanisms` REGISTRY. No arguments.

**Output:** `{ status, count, mechanisms: [{ key, name, space, weights, tier, summary, profiles }] }`
— graded tier 1 (gentle prompt wrapper) → tier 4 (recognition-gated activation moat). Per-model
`profiles` appear only where a real characterization measured them.

### recommend_mechanism

Recommend a graded menu filtered by deployment constraints.

**Input:**
- `weights` (optional): `open` (activation access) | `closed` (prompt-only, any model). Default `open`.
- `max_over_refusal` (optional): max tolerated benign over-refusal, 0–1. Default 0.3.
- `min_coherence` (optional): min tolerated output coherence, 0–1. Default 0.6.

**Output:** `{ status, recommended: [...], rationale, count }` — gentle→aggressive. With
`weights="closed"` only prompt-space mechanisms are returned.

### characterize_model

Describe (and, where measured, return) a model's steering/jailbreak susceptibility.

**Input:**
- `model_id`: HuggingFace model id (e.g., `Qwen/Qwen3-4B`)
- `mode` (optional): `prompt` (no-GPU BYOK/OpenRouter sweep) | `weight` (white-box GPU sweep) | `both`. Default `prompt`.

**Output:** `{ status, model, characterization_description, measured_data, data_source, caveat }`
— measured rows come from `gates/` with an honest single-seed caveat; unmeasured models return a plan.

### harden_prompt

Apply prompt-space hardening to a chat message list (works on open **and** closed models).

**Input:**
- `messages`: list of `{role, content}` dicts (standard chat format)
- `level` (optional): `gentle` | `firm` | `constitutional`. Default `firm`.

**Output:** `{ status, hardened_messages, level_applied, system_prompt, caveat }` — prepends a
graded refusal-reinforcing system message.

**Caveat:** prompt hardening alone does not stop all jailbreaks; combine with the activation
moat where the weights allow. The moat's proof (recognition-gated hardening cuts real jailbreaks
2× with zero benign over-refusal) is in `gates/gate_L26_moat_proof.json`.

## Calibration rules

- **Band readout target layer:** NOT the final layer; measure via `lens-eval` correspondence rise.
- **Write amplitude (alpha):** scales inversely with lens transport strength. Typical 0.1–0.5; tune per model/concept.
- **Entropy threshold (tau_percentile):** higher = more selective gating. Typical 50–80.
- **Readback caveat:** probabilistic and noisy; single runs not confirmatory. Multi-seed at confirm tier.

## Gate citations

Every tool/skill cites a default gate, recording the governing claim or measurement:

- `gates/gate_L13_recipe.json` — lens evaluation (band readback correspondence structure)
- `gates/gate_L9_alignconf.json` — steering arms/seeds/alpha semantics
- `gates/gate_L14_readback.json` — readback method and thresholds

The gates/ directory is the single source of truth for all publicly-facing numbers.

## Requirements

- Python 3.10+
- `prabodha` installed: `pip install prabodha[lens]` (includes torch, transformers, jacobian-lens)
- CUDA device (for steering; lens-eval works on CPU for small models)

## Reference

- **prabodha library:** https://github.com/SharathSPhD/prabodha
- **PyPI:** `pip install prabodha`
- **Paper:** forthcoming
- **J-space:** https://github.com/SharathSPhD/jacobian-lens (workspace band concepts)
