#!/usr/bin/env bash
# L22 job pack — lens head-to-head: same writes (planned from the band lens, recipe
# point site 24 / alpha 0.3), stub readback decoded through (a) the band-targeted lens
# (prabodha-mode) and (b) the final-target lens (jSpace vendored default). Identical
# stubs, identical write commands; the ONLY varied factor is the decode instrument.
# Pre-registration lives in configs/experiments/e_l22_lens_headtohead.yaml (H_lens_gap,
# H_band_detects, falsifier) — written BEFORE this dispatch.
#
# Execution split (GB10 ops pattern): gpu_guard + HF lens pull + compose on the HOST;
# the two e4 runs inside prabodha/gb10:0.1 with THIS WORKTREE mounted at /repo and
# PYTHONPATH=/repo/src (worktree src overrides the image-baked src — the --readback-lens
# flag lives here). Integrity check: per-generation seeding is deterministic, so the
# generation arms must produce IDENTICAL lift in both runs; any drift = pipeline bug.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"; export PRABODHA_ROOT="$ROOT"
source "$ROOT/scripts/lib/gpu_guard.sh"
gpu_guard_check real "${L22_EST_MIN:-60}" L22
cd "$ROOT"
mkdir -p outputs/l10 gates

# Lenses from HF via host python (outputs/ is gitignored; fresh worktrees start empty)
python3 - <<'PY'
from huggingface_hub import hf_hub_download
import shutil, pathlib
for src, dst in [("lens_qwen3_mid30.pt", "outputs/l10/lens_qwen3_mid30.pt"),
                 ("lens_qwen3.pt",       "outputs/l10/lens_qwen3_final.pt")]:
    p = hf_hub_download("qbz506/prabodha-lenses", src)
    pathlib.Path(dst).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(p, dst)
    print("staged", dst)
PY

# NOTE: the image's ENTRYPOINT is bash, so commands must be passed as `-c "<string>"`
# (a bare `docker run image python3` becomes `bash python3` -> "cannot execute binary").
drun() {
  docker run --rm --gpus all \
    -v "${ROOT}:/repo" \
    -v /home/sharaths/.cache/huggingface:/workspace/hf_cache \
    -e HF_HOME=/workspace/hf_cache \
    -e PYTHONPATH=/repo/src \
    -w /repo \
    prabodha/gb10:0.1 -c "$1"
}

# Sanity inside the image: both lenses expose source layers covering (24,28]
drun "python3 scripts/tools/l22_sanity.py"

for RB in band final; do
  if [ "$RB" = band ]; then RBL="outputs/l10/lens_qwen3_mid30.pt"; else RBL="outputs/l10/lens_qwen3_final.pt"; fi
  OUT="gates/gate_L22_lens_${RB}.json"
  echo "=== L22 readback-lens=${RB} -> ${OUT} ==="
  drun "nice -n ${GUARD_NICE:-10} python3 -m prabodha.steering.e4_cli \
    --model configs/models/qwen3.yaml \
    --mid-lens outputs/l10/lens_qwen3_mid30.pt \
    --readback-lens ${RBL} \
    --exp configs/experiments/e_l22_lens_headtohead.yaml \
    --seed 42 \
    --record-readback \
    --loop L22 \
    --out ${OUT} \
    --contention ${GUARD_CONTENTION:-unknown}"
done

echo "=== integrity: gated lift must match exactly across runs (determinism) ==="
python3 - <<'PY'
import json
def lift(f):
    ev = json.loads(json.load(open(f))["domain_gate"]["evidence"])
    return ev["aggregates"]["entropy_gated"]["lift"]
a, b = lift("gates/gate_L22_lens_band.json"), lift("gates/gate_L22_lens_final.json")
print("gated lift band-run:", a, "| final-run:", b)
assert a == b, "DETERMINISM VIOLATION — generations differ between runs; investigate before composing"
PY

echo "=== compose ==="
python3 scripts/tools/compose_L22.py
echo "L22 complete — gates/gate_L22_lens_headtohead.json + gates/gate_L22_benchmark.json"
