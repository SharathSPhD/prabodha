#!/usr/bin/env bash
# ralph loop runner (Template Method): re-enterable, state in repo. Usage: loop.sh <LOOP_ID>
set -euo pipefail
LOOP="${1:?loop id}"; ROOT="$(cd "$(dirname "$0")/../.." && pwd)"; cd "$ROOT"
CARD=$(ls contracts/${LOOP}_*.md 2>/dev/null | head -1) || true
[[ -n "${CARD:-}" ]] || { echo "no contract card for $LOOP"; exit 1; }
echo "== ralph $LOOP: contract = $CARD"
echo "1/5 plan: read card + SPEC + research/state.json (agent step)"
echo "2/5 build: worktree loop/${LOOP,,} (agent step)"
echo "3/5 test: pytest -q"; python -m pytest -q || exit 1
echo "4/5 validate: run experiment / stats tier per card (GPU steps via scripts/dispatch/${LOOP,,}/run.sh on GB10)"
echo "5/5 close: emit gates/gate_${LOOP}.json (dual verdict), update SPEC/PRD evolution logs, journal, squash-merge"
echo "closure is NOT automatic: domain gate + adversarial review + sign-off required (RULES R1)."
