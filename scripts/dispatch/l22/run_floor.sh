#!/usr/bin/env bash
# L22 amendment 1 — detection-floor sweep: alpha in {0.02, 0.05, 0.1} x {band, final}
# readback lenses on the same 80-pair grid. Registered in research/journal.md BEFORE
# this dispatch (H_floor_gap: some alpha with band-final gap >= 0.3, McNemar p < .05;
# falsifier: gap < 0.1 at all alphas kills the necessity claim at every dose).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"; export PRABODHA_ROOT="$ROOT"
source "$ROOT/scripts/lib/gpu_guard.sh"
gpu_guard_check real "${L22_EST_MIN:-35}" L22
cd "$ROOT"

drun() {
  docker run --rm --gpus all \
    -v "${ROOT}:/repo" \
    -v /home/sharaths/.cache/huggingface:/workspace/hf_cache \
    -e HF_HOME=/workspace/hf_cache \
    -e PYTHONPATH=/repo/src \
    -w /repo \
    prabodha/gb10:0.1 -c "$1"
}

for A in 0.02 0.05 0.1; do
  for RB in band final; do
    if [ "$RB" = band ]; then RBL="outputs/l10/lens_qwen3_mid30.pt"; else RBL="outputs/l10/lens_qwen3_final.pt"; fi
    OUT="gates/gate_L22_floor_a${A}_${RB}.json"
    echo "=== L22-floor alpha=${A} readback-lens=${RB} -> ${OUT} ==="
    drun "nice -n ${GUARD_NICE:-10} python3 -m prabodha.steering.e4_cli \
      --model configs/models/qwen3.yaml \
      --mid-lens outputs/l10/lens_qwen3_mid30.pt \
      --readback-lens ${RBL} \
      --exp configs/experiments/e_l22_floor.yaml \
      --alpha ${A} \
      --seed 42 \
      --record-readback \
      --loop L22 \
      --out ${OUT} \
      --contention ${GUARD_CONTENTION:-unknown}"
  done
done
echo "L22-floor sweep complete"
