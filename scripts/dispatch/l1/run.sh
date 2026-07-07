#!/usr/bin/env bash
# L1 job pack — fit + apply Jacobian lens on Qwen3 (GB10). Guard-wrapped, checkpoint-resume, pulsed.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"; export PRABODHA_ROOT="$ROOT"
source "$ROOT/scripts/lib/gpu_guard.sh"
gpu_guard_check real 90 L1
cd "$ROOT"
pip install -e . -q && pip install -e vendor/jacobian-lens -q
python -m prabodha.lens.fit_cli --model configs/models/qwen3.yaml \
  --lens configs/lens/fit_default.yaml --out outputs/l1/lens_qwen3.pt --resume
python -m prabodha.lens.e1_cli --model configs/models/qwen3.yaml \
  --lens-file outputs/l1/lens_qwen3.pt --exp configs/experiments/e1.yaml \
  --out gates/gate_L1.json --journal research/journal.md
echo "L1 job pack complete — review gates/gate_L1.json, then adversarial review + sign-off."
