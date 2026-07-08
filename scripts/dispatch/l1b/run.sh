#!/usr/bin/env bash
# L1b job pack — size-matched retry: Jacobian lens fit + E1b on Qwen3.6-27B (GB10, IDLE WINDOW).
# 27B bf16 ~54GB weights cannot co-reside with a live trainer on 121GB unified memory:
# min_free=80GiB makes the guard refuse unless the GPU is effectively idle.
# On the Spark:   cd ~/projects/prabodha && docker compose run l1b
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"; export PRABODHA_ROOT="$ROOT"
source "$ROOT/scripts/lib/gpu_guard.sh"
gpu_guard_check real "${L1B_EST_MIN:-240}" L1b 80
cd "$ROOT"
NICE="nice -n ${GUARD_NICE:-10}"
$NICE python -m prabodha.lens.fit_cli --model configs/models/qwen27b.yaml \
  --lens configs/lens/fit_default.yaml --out outputs/l1b/lens_qwen27b.pt --resume
$NICE python -m prabodha.lens.e1_cli --model configs/models/qwen27b.yaml \
  --lens-file outputs/l1b/lens_qwen27b.pt --exp configs/experiments/e1b.yaml \
  --loop L1b --out gates/gate_L1b.json --journal research/journal.md --contention "${GUARD_CONTENTION:-unknown}"
echo "L1b complete — gates/gate_L1b.json written. Compare vs gates/gate_L1.json per e1b.yaml decision rule."
