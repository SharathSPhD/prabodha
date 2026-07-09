#!/usr/bin/env bash
# L4 job pack — E4 sphurattā-gated timing: 5 arms on the PWM twin. GB10.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"; export PRABODHA_ROOT="$ROOT"
source "$ROOT/scripts/lib/gpu_guard.sh"
gpu_guard_check real "${L4_EST_MIN:-45}" L4
cd "$ROOT"
NICE="nice -n ${GUARD_NICE:-10}"
$NICE python -m prabodha.lens.fit_cli --model configs/models/nemotron4b.yaml \
  --lens configs/lens/fit_mid26.yaml --out outputs/l2b/lens_nemotron4b_mid26.pt --resume
$NICE python -m prabodha.steering.e4_cli --model configs/models/nemotron4b.yaml \
  --mid-lens outputs/l2b/lens_nemotron4b_mid26.pt --exp configs/experiments/e4.yaml \
  --out gates/gate_L4.json --contention "${GUARD_CONTENTION:-unknown}"
echo "L4 complete — gates/gate_L4.json. Next: adversarial review."
