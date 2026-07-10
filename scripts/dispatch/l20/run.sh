#!/usr/bin/env bash
# L20 job pack — trained-bridge comparator: baseline / analytic entropy_gated / trained_bridge
# on Qwen3-4B band-exit (site 24). GB10. Screen tier (seed 42) by default; pass SEEDS to extend.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"; export PRABODHA_ROOT="$ROOT"
source "$ROOT/scripts/lib/gpu_guard.sh"
gpu_guard_check real "${L20_EST_MIN:-90}" L20
cd "$ROOT"
NICE="nice -n ${GUARD_NICE:-10}"
OUT_GATE="${L20_OUT:-gates/gate_L20_screen.json}"
TRACE="${L20_TRACE:-outputs/traces/trained_bridge_qwen3.json}"
mkdir -p outputs/L20 outputs/traces
$NICE python -m prabodha.steering.e4_cli \
  --model configs/models/qwen3.yaml \
  --mid-lens outputs/l10/lens_qwen3_mid30.pt \
  --exp configs/experiments/e_l20_bridge.yaml \
  --out "$OUT_GATE" \
  --emit-trace "$TRACE" \
  --contention "${GUARD_CONTENTION:-unknown}"
echo "L20 complete — $OUT_GATE ; trace $TRACE. Next: determinism check + adversarial review #17."
