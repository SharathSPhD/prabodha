#!/usr/bin/env bash
# L1 job pack — Jacobian lens fit + E1 evaluation on Qwen3 (GB10, shared mode, docker-first).
# On the Spark:   cd ~/projects/prabodha && docker compose run l1        (preferred)
# Bare-metal:     scripts/dispatch/l1/run.sh                              (inside any env with deps)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"; export PRABODHA_ROOT="$ROOT"
source "$ROOT/scripts/lib/gpu_guard.sh"
gpu_guard_check real "${L1_EST_MIN:-90}" L1
cd "$ROOT"
NICE="nice -n ${GUARD_NICE:-10}"
$NICE python -m prabodha.lens.fit_cli --model configs/models/qwen3.yaml \
  --lens configs/lens/fit_default.yaml --out outputs/l1/lens_qwen3.pt --resume
$NICE python -m prabodha.lens.e1_cli --model configs/models/qwen3.yaml \
  --lens-file outputs/l1/lens_qwen3.pt --exp configs/experiments/e1.yaml \
  --out gates/gate_L1.json --journal research/journal.md --contention "${GUARD_CONTENTION:-unknown}"
echo "L1 complete — gates/gate_L1.json written. Next: adversarial review + operator sign-off (AGENTS.md pt5)."
