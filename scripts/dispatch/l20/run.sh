#!/usr/bin/env bash
# L20 job pack — trained-bridge comparator: baseline / analytic entropy_gated / trained_bridge
# on Qwen3-4B band-exit (site 24). GB10. Runs each seed in L20_SEEDS (default "42").
# Screen tier = seed 42; confirm tier adds the existing clean-stream seeds 123 777.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"; export PRABODHA_ROOT="$ROOT"
source "$ROOT/scripts/lib/gpu_guard.sh"
gpu_guard_check real "${L20_EST_MIN:-90}" L20
cd "$ROOT"
NICE="nice -n ${GUARD_NICE:-10}"
mkdir -p outputs/L20 outputs/traces
for SEED in ${L20_SEEDS:-42}; do
  OUT_GATE="gates/gate_L20_s${SEED}.json"
  TRACE="outputs/traces/trained_bridge_qwen3_s${SEED}.json"
  echo "=== L20 seed ${SEED} -> ${OUT_GATE} ==="
  $NICE python -m prabodha.steering.e4_cli \
    --model configs/models/qwen3.yaml \
    --mid-lens outputs/l10/lens_qwen3_mid30.pt \
    --exp configs/experiments/e_l20_bridge.yaml \
    --seed "${SEED}" \
    --out "${OUT_GATE}" \
    --emit-trace "${TRACE}" \
    --contention "${GUARD_CONTENTION:-unknown}"
done
echo "L20 complete — per-seed gates gates/gate_L20_s*.json. Next: compose + determinism check + review #17."
