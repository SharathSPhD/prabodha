# prabodha Claude Code Plugin

Workspace-band lens fitting, visualization, and recognition-gated steering for HuggingFace decoder LLMs.

## Installation

```bash
# Install the plugin via Claude Code
/plugin install path/to/integrations/claude-code-plugin
```

This makes available:
- **Skills** (Claude Code only): `lens-map`, `steer-verify` — operational workflows that guide you through the prabodha CLI
- **MCP Tools** (any MCP client): `lens_map`, `steer_generate`, `readback_verify`, `list_gates` — programmatic access to steering tools

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

**Default gate:** `gates/gate_L9_readback.json` (readback method + thresholds).

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

## Calibration rules

- **Band readout target layer:** NOT the final layer; measure via `lens-eval` correspondence rise.
- **Write amplitude (alpha):** scales inversely with lens transport strength. Typical 0.1–0.5; tune per model/concept.
- **Entropy threshold (tau_percentile):** higher = more selective gating. Typical 50–80.
- **Readback caveat:** probabilistic and noisy; single runs not confirmatory. Multi-seed at confirm tier.

## Gate citations

Every tool/skill cites a default gate, recording the governing claim or measurement:

- `gates/gate_L13_recipe.json` — lens evaluation (band readback correspondence structure)
- `gates/gate_L9_alignconf.json` — steering arms/seeds/alpha semantics
- `gates/gate_L9_readback.json` — readback method and thresholds

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
