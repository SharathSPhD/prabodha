#!/usr/bin/env bash
# L2 job pack — E2+E7: lens fit + band map + articulation gradient on the PWM-stack twin
# (nvidia/Nemotron-Mini-4B-Instruct). GB10, shared-mode courtesy (4B fits beside trainers).
# On the Spark:   cd ~/projects/prabodha && docker compose run l2
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"; export PRABODHA_ROOT="$ROOT"
source "$ROOT/scripts/lib/gpu_guard.sh"
gpu_guard_check real "${L2_EST_MIN:-90}" L2
cd "$ROOT"
NICE="nice -n ${GUARD_NICE:-10}"
$NICE python -m prabodha.lens.fit_cli --model configs/models/nemotron4b.yaml \
  --lens configs/lens/fit_default.yaml --out outputs/l2/lens_nemotron4b.pt --resume
$NICE python -m prabodha.lens.e1_cli --model configs/models/nemotron4b.yaml \
  --lens-file outputs/l2/lens_nemotron4b.pt --exp configs/experiments/e2.yaml \
  --loop L2 --out gates/gate_L2.json --journal research/journal.md --contention "${GUARD_CONTENTION:-unknown}"
$NICE python -m prabodha.lens.vis_cli --model configs/models/nemotron4b.yaml \
  --lens-file outputs/l2/lens_nemotron4b.pt \
  --prompt "Think about fire. The weather today is" \
  --out outputs/l2/slice_sample.html --title "L2 sample: PWM-stack twin (fire)"
echo "L2 complete — gates/gate_L2.json + band map + slice page. Next: adversarial review."
