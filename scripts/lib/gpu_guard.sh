#!/usr/bin/env bash
# gpu_guard.sh — mandatory before any CUDA dispatch (RULES R2). Adapted from prabhasa-samskrutam.
# Usage: source gpu_guard.sh && gpu_guard_check <smoke|real> <est_minutes> [loop_id]
# Env: PRABODHA_ROOT (repo root), GUARD_SIMULATE=1 for dry-run testing.
gpu_guard_check() {
  local mode="${1:?smoke|real}" est_min="${2:?minutes}" loop="${3:-L1}"
  local root="${PRABODHA_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || echo .)}"
  [[ -f "$root/research/KILL_SWITCH" ]] && { echo "GUARD: kill switch present — refusing"; return 1; }
  if [[ "${GUARD_SIMULATE:-0}" == "1" ]]; then echo "GUARD(sim): $mode ${est_min}m ok"; return 0; fi
  command -v nvidia-smi >/dev/null || { echo "GUARD: no nvidia-smi — not a GPU host"; return 1; }
  # live trainer detection (prabhasa + PSALM + any big GPU-mem holder)
  if pgrep -f "[t]rain_130m" >/dev/null || pgrep -if "[p]salm" >/dev/null; then
    echo "GUARD: co-resident trainer live — refusing ($mode)"; return 1; fi
  local used total frac
  used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)
  total=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
  frac=$(( 100 * used / total ))
  if [[ "$mode" == "smoke" ]]; then
    (( est_min <= 5 )) || { echo "GUARD: smoke >5min — use real"; return 1; }
    (( frac < 10 )) || { echo "GUARD: GPU ${frac}% busy — refusing smoke"; return 1; }
  else
    (( frac < 10 )) || { echo "GUARD: GPU ${frac}% busy — real runs need idle device"; return 1; }
    # budget check (jq optional)
    if command -v jq >/dev/null && [[ -f "$root/research/state.json" ]]; then
      local spent cap
      spent=$(jq -r ".gpu_budget_hours.${loop}_spent // 0" "$root/research/state.json")
      cap=$(jq -r ".gpu_budget_hours.${loop}_cap // 0" "$root/research/state.json")
      awk -v s="$spent" -v c="$cap" -v m="$est_min" 'BEGIN{exit !(s + m/60.0 <= c)}' \
        || { echo "GUARD: budget exceeded for $loop (spent=$spent cap=$cap)"; return 1; }
    fi
  fi
  echo "GUARD: ok ($mode, ${est_min}m, gpu ${frac}% used)"; return 0
}
