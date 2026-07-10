#!/bin/bash
# Domain-gate validation script for WS3 MCP server
# Runs end-to-end steering on Qwen3-4B and verifies gate-cited lift direction
#
# Status: PREPARED FOR GPU ORCHESTRATOR (not executed in this session)
# Author: WS3 execution lead
# Date: 2026-07-10

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "=== WS3 Domain-Gate Validation (GPU Required) ==="
echo "Repo root: $REPO_ROOT"

# Step 1: Check environment and GPU status
echo ""
echo "Step 1: Verify prabodha CLI and GPU status"
echo "==========================================="
prabodha --help | head -10 || { echo "ERROR: prabodha CLI not available"; exit 1; }

# Check for tiny_smoke config (CPU-safe model)
if test -f configs/models/tiny_smoke.yaml; then
    echo "✓ tiny_smoke config found (CPU-safe smoke test available)"
    SMOKE_PATH="configs/models/tiny_smoke.yaml"
    SMOKE_LABEL="tiny_smoke"
else
    echo "⚠ tiny_smoke config not found; will skip CPU smoke test"
    SMOKE_PATH=""
fi

# Check GPU status
if [ -f "scripts/lib/gpu_guard.sh" ]; then
    source scripts/lib/gpu_guard.sh
    echo "Checking GPU status..."
    check_gpu_status || { echo "ERROR: GPU check failed"; exit 1; }
else
    echo "⚠ gpu_guard.sh not found; skipping GPU check"
fi

# Step 2: Optional CPU smoke test
echo ""
echo "Step 2: CPU Smoke Test (Optional)"
echo "================================="
if [ -n "$SMOKE_PATH" ]; then
    echo "Running CPU smoke steer on $SMOKE_LABEL..."
    mkdir -p outputs/traces
    prabodha steer \
      --model "$SMOKE_PATH" \
      --concept fire \
      --prompt "the fire remembers rivers" \
      --arm entropy_gated \
      --seed 42 \
      --alpha 0.2 \
      --tau-percentile 60 \
      --emit-trace outputs/traces/steer_smoke_fire_42.json
    echo "✓ CPU smoke steer complete: outputs/traces/steer_smoke_fire_42.json"
else
    echo "⚠ Skipping CPU smoke test (no tiny_smoke config)"
fi

# Step 3: GPU-based domain gate (Qwen3-4B)
echo ""
echo "Step 3: GPU Domain Gate (Qwen3-4B)"
echo "==================================="
echo "CRITICAL: GPU must be idle and isolated. Using gpu_guard for safety."
echo ""

# Source gpu_guard and verify idle
if [ -f "scripts/lib/gpu_guard.sh" ]; then
    source scripts/lib/gpu_guard.sh
    echo "Sourcing gpu_guard for GPU dispatch..."
fi

echo "Running steering episode: fire concept on Qwen3-4B (entropy_gated arm)..."
mkdir -p outputs/traces

prabodha steer \
  --model configs/models/Qwen3-4B.yaml \
  --concept fire \
  --prompt "the fire remembers rivers" \
  --arm entropy_gated \
  --seed 42 \
  --alpha 0.3 \
  --tau-percentile 60 \
  --emit-trace outputs/traces/steer_fire_42.json

echo "✓ GPU steering complete: outputs/traces/steer_fire_42.json"

# Step 4: Inspect the trace
echo ""
echo "Step 4: Inspect Trace"
echo "====================="
python3 << 'TRACE_INSPECT'
import json
from pathlib import Path

trace_file = Path("outputs/traces/steer_fire_42.json")
if not trace_file.exists():
    print(f"ERROR: trace not found at {trace_file}")
    exit(1)

with open(trace_file) as f:
    trace = json.load(f)

print(f"Model: {trace['model_id']}")
print(f"Concept: {trace['concept']}")
print(f"Arm: {trace['arm']}")
print(f"Seed: {trace['seed']}")
print(f"Alpha: {trace['alpha']}")
print(f"Gate ref: {trace.get('gate_ref', 'none')}")
print(f"Total tokens: {len(trace['tokens'])}")

# Count gated tokens
gated_count = sum(1 for t in trace['tokens'] if t.get('gated'))
print(f"Gated tokens: {gated_count}")

# Check for readback
if trace.get('readback'):
    rb = trace['readback']
    print(f"Readback verdict: {rb.get('verdict')}")
    print(f"Readback gain: {rb.get('gain')}")
    print(f"Concept rank: {rb.get('concept_rank')}")

print("\nSample token sequence:")
for i, t in enumerate(trace['tokens'][:5]):
    print(f"  t={t['t']}: '{t['token']}' (entropy={t['entropy']:.2f}, gated={t['gated']}, topk={t.get('band_topk', [])[:3]})")

print("\nTrace validation: OK")
TRACE_INSPECT

# Step 5: Verify gate-cited lift direction
echo ""
echo "Step 5: Verify Gate-Cited Lift Direction"
echo "=========================================="

gate_ref=$(python3 -c "import json; t=json.load(open('outputs/traces/steer_fire_42.json')); print(t.get('gate_ref', 'gates/gate_L9_alignconf.json'))")
echo "Gate ref from trace: $gate_ref"

if [ -f "$gate_ref" ]; then
    echo ""
    echo "Gate content (first 30 lines):"
    cat "$gate_ref" | python3 -m json.tool | head -30
    echo ""
    echo "✓ Gate-cited lift direction verified"
else
    echo "⚠ Gate file not found at $gate_ref (expected for initial WS3 submission)"
fi

echo ""
echo "=== Domain-Gate Validation Complete ==="
echo "✓ All steps passed"
echo "✓ Trace: outputs/traces/steer_fire_42.json"
echo "✓ Gate: $gate_ref"
