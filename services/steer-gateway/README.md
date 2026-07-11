# Prabodha Steer Gateway

Real steering runtime proxy for the prabodha web app. Supports three steering modes:
concept-based (legacy), contrastive (CAA-style), and explicit vector steering.

## Configuration

Set environment variables (see `.env.example`):

```bash
STEER_GATEWAY_SECRET=your-secret-key-here  # Bearer token for auth
PRABODHA_MODEL_CONFIG=configs/models/qwen3.yaml
PRABODHA_LENS_FILE=outputs/l10/lens_qwen3_mid30.pt
PRABODHA_SITE=24  # Layer for steering writes
PRABODHA_MAX_NEW_TOKENS=100
PRABODHA_MIN_GAP=2  # Min gap between gated writes
PRABODHA_TAU_PERCENTILE=60  # Entropy percentile for gating
```

## Building & Running (Docker)

```bash
# Build the gateway image (includes prabodha + dependencies)
docker build -t prabodha-gateway .

# Run the gateway
docker run -e STEER_GATEWAY_SECRET=your-secret \
  -e PRABODHA_MODEL_CONFIG=configs/models/qwen3.yaml \
  -e PRABODHA_LENS_FILE=outputs/l10/lens_qwen3_mid30.pt \
  -p 8100:8100 \
  -v $(pwd):/repo:ro \
  prabodha-gateway
```

The gateway mounts `/repo` as read-only; changes to code in `services/steer-gateway` are
picked up automatically via Python module reloading.

## API: POST /steer

Stream a steering episode via Server-Sent Events (SSE).

### Request

```json
{
  "prompt": "user prompt text",
  "concept": "steering concept (used for identification)",
  "alpha": 0.3,
  "arm": "entropy_gated",
  "direction_spec": {
    "mode": "concept|contrastive|vector",
    "concept": "optional (concept mode only)",
    "pos_texts": ["positive exemplar 1", "..."],
    "neg_texts": ["negative exemplar 1", "..."],
    "vector": [0.1, 0.2, ...]
  }
}
```

### Steering Modes

1. **concept** (legacy, default if no direction_spec):
   - Resolves `concept` string to token IDs via lens-fitted concept vocabulary
   - Plans write command using concept-token steering (plan_write)
   - Works for arbitrary concept tokens learned during lens fitting

2. **contrastive** (CAA-style via activation differentials):
   - Extracts residual-stream activations at `site_layer` for positive exemplars
   - Extracts residual-stream activations for negative exemplars
   - Computes direction via `contrastive_direction(mean(pos) - mean(neg))`
   - Injects direction using `apply_direction_write` (unit-norm, alpha-scaled)
   - Enables "refusal" and "truthfulness" steering without concept tokens

3. **vector** (explicit direction):
   - Accepts pre-computed unit-norm direction vector
   - Injects via `apply_direction_write` with alpha scaling
   - Useful for externally optimized directions or SAE features

### Response

Server-Sent Events stream with two event types:

1. **token** events (per decode step):
   ```json
   {
     "t": 0,
     "token": " The",
     "entropy": 2.1,
     "gated": false
   }
   ```

2. **done** event (complete episode):
   ```json
   {
     "model_id": "Qwen/Qwen3-4B",
     "prompt": "...",
     "concept": "refusal",
     "arm": "entropy_gated",
     "site_layer": 24,
     "alpha": 0.3,
     "baseline_text": "...",
     "steered_text": "...",
     "direction_source": "contrastive:refusal(5+/5-)",
     "trace": { ... },
     "created_at": "2026-07-11T..Z"
   }
   ```

## Concepts

**Concept: pratisaṃvit (discrimination)**
Steering via direction derived from contrastive activations or explicit vectors,
extending beyond concept-token steering.

**Source:**
- Rimsky et al. (2024) "Steering Conversational AI by its Values" (CAA)
- prabodha.steering.direction (contrastive_direction, apply_direction_write)
- prabodha.steering.writer (plan_write, WriteCommand)

## Testing

Unit tests (CPU, no GPU required):
```bash
pytest services/steer-gateway/tests/test_schema.py -v
pytest services/steer-gateway/tests/test_direction_spec.py -v
```

Integration tests require the full model + lens (GPU):
```bash
# On GB10 with GPU available
pytest services/steer-gateway/tests/test_main.py -v -m smoke
```

## Limitations (Honestly Disclosed)

- Contrastive activations are collected via forward passes; single-direction approximation
- Refusal/truthfulness steering effect depends on layer choice (empirical selection required)
- Scalability of direction computation limited by memory (batch activation extraction)
- Residual-stream layer assumed to be the site_layer; layer dependency not validated at runtime
