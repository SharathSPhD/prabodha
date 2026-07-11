#!/bin/bash
# L23: prayoga↔prabodha jailbreak→harden loop — GB10 dispatch
#
# Concept: pratirodha (hardening/resistance). Runs the fused hardening loop:
#   1. Extracts refusal direction via prayoga (difference-in-means).
#   2. Scans layers for ablation effectiveness.
#   3. Runs four arms: baseline, attack (ablation), harden_naive, harden_gated.
#   4. Verifies registered hypotheses (H_attack, H_harden_gated, H_freedom).
#   5. Emits gate report: gates/gate_L23_harden.json.
#
# GPU: GB10 only (5090 not available). Bandwidth-bound; use idle windows.
# Budget: Add "L23": 1.0 to research/state.json before dispatch.
# Reproducibility: Fixed decoding, per-generation seeding (review #16).
#
# Usage (from prabodha root):
#   bash scripts/dispatch/l23/run.sh
#
# Environment (docker entrypoint will set):
#   - PYTHONPATH=/repo/src:/prayoga/src
#   - Mount: worktree -> /repo, prayoga clone -> /prayoga
#   - Image: prabodha/gb10:0.1

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
DISPATCH_DIR="${REPO_ROOT}/scripts/dispatch/l23"

echo "[L23] Prayoga↔prabodha hardening loop — GB10 dispatch"
echo "[L23] Repo root: ${REPO_ROOT}"

# ============ GPU Guard & Budget Check ============
if [[ ! -f "${REPO_ROOT}/scripts/lib/gpu_guard.sh" ]]; then
    echo "[L23] ERROR: gpu_guard.sh not found at scripts/lib/gpu_guard.sh"
    exit 1
fi

source "${REPO_ROOT}/scripts/lib/gpu_guard.sh"

echo "[L23] Checking GPU availability and budget..."
gpu_guard_check real 60 L23

# ============ Prepare Prayoga Clone ============
PRAYOGA_PATH="${REPO_ROOT}/../prayoga"
if [[ ! -d "${PRAYOGA_PATH}" ]]; then
    echo "[L23] Prayoga not found at ${PRAYOGA_PATH}; cloning..."
    mkdir -p "$(dirname "${PRAYOGA_PATH}")"
    cd "$(dirname "${PRAYOGA_PATH}")"
    git clone https://github.com/SharathSPhD/prayoga.git prayoga || {
        echo "[L23] ERROR: Failed to clone prayoga"
        exit 1
    }
    cd "${REPO_ROOT}"
fi

echo "[L23] Prayoga at: ${PRAYOGA_PATH}"

# ============ Build Docker Image ============
echo "[L23] Building docker image prabodha/gb10:0.1..."
docker build \
    --tag prabodha/gb10:0.1 \
    --file "${REPO_ROOT}/Dockerfile" \
    "${REPO_ROOT}" || {
    echo "[L23] ERROR: Docker build failed"
    exit 1
}

# ============ Prepare Output Directory ============
GATES_DIR="${REPO_ROOT}/gates"
mkdir -p "${GATES_DIR}"
GATE_OUTPUT="${GATES_DIR}/gate_L23_harden.json"

# ============ Run Hardening Loop in Container ============
echo "[L23] Running hardening loop in container..."
docker run --rm \
    --gpus all \
    --mount type=bind,source="${REPO_ROOT}",target=/repo \
    --mount type=bind,source="${PRAYOGA_PATH}",target=/prayoga \
    --mount type=bind,source="${HOME}/.cache/huggingface",target=/root/.cache/huggingface \
    --env PYTHONPATH=/repo/src:/prayoga/src \
    --env CUDA_VISIBLE_DEVICES=0 \
    prabodha/gb10:0.1 \
    bash -c "
    set -euo pipefail
    cd /repo
    python -m prabodha.hardening.cli \
        --model Qwen/Qwen3-4B-Instruct-2507 \
        --config configs/experiments/e_l23_harden.yaml \
        --prayoga-path /prayoga \
        --out ${GATE_OUTPUT}
    " || {
    echo "[L23] ERROR: Container execution failed"
    exit 1
}

# ============ Verify Gate Output ============
if [[ ! -f "${GATE_OUTPUT}" ]]; then
    echo "[L23] ERROR: Gate output not found at ${GATE_OUTPUT}"
    exit 1
fi

echo "[L23] Gate written: ${GATE_OUTPUT}"
cat "${GATE_OUTPUT}" | jq '.' || echo "[L23] Warning: Could not pretty-print gate JSON"

echo "[L23] Dispatch complete ✓"
