#!/usr/bin/env bash
# L3 job pack — E3 H5b redo: v2 (mouth) vs v3 (band) writes on the PWM twin. GB10 shared-mode.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"; export PRABODHA_ROOT="$ROOT"
source "$ROOT/scripts/lib/gpu_guard.sh"
gpu_guard_check real "${L3_EST_MIN:-60}" L3
cd "$ROOT"
NICE="nice -n ${GUARD_NICE:-10}"
# mid-target lens is a prerequisite (fit in L2b; resume makes this a no-op when present)
$NICE python -m prabodha.lens.fit_cli --model configs/models/nemotron4b.yaml \
  --lens configs/lens/fit_mid26.yaml --out outputs/l2b/lens_nemotron4b_mid26.pt --resume
$NICE python -m prabodha.steering.e3_cli --model configs/models/nemotron4b.yaml \
  --mid-lens outputs/l2b/lens_nemotron4b_mid26.pt --exp configs/experiments/e3.yaml \
  --out gates/gate_L3.json --contention "${GUARD_CONTENTION:-unknown}"
echo "L3 complete — gates/gate_L3.json. Next: adversarial review."
