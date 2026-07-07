#!/usr/bin/env bash
# gpu_guard.sh v2 — GB10 SHARED MODE (RULES R2 as amended; TRIZ C3).
# v1 refused when a trainer was live; operator instruction (2026-07-07) sublated that:
# we now SHARE — proceed at low priority with contention recorded — refusing only on
# kill-switch or insufficient free memory. Usage:
#   source gpu_guard.sh && gpu_guard_check <smoke|real> <est_minutes> [loop_id]
# Exports: GUARD_CONTENTION ("none" | comma-list of co-resident trainer patterns) for gate JSON.
gpu_guard_check() {
  local mode="${1:?smoke|real}" est_min="${2:?minutes}" loop="${3:-L1}"
  local root="${PRABODHA_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || echo .)}"
  export GUARD_CONTENTION="none"
  [[ -f "$root/research/KILL_SWITCH" ]] && { echo "GUARD: kill switch present — refusing"; return 1; }
  if [[ "${GUARD_SIMULATE:-0}" == "1" ]]; then echo "GUARD(sim): $mode ${est_min}m ok"; return 0; fi
  command -v nvidia-smi >/dev/null || { echo "GUARD: no nvidia-smi — not a GPU host"; return 1; }
  local live=()
  pgrep -f "[t]rain_130m" >/dev/null && live+=("prabhasa:train_130m")
  pgrep -if "[p]salm" >/dev/null && live+=("psalm")
  if ((${#live[@]})); then
    GUARD_CONTENTION=$(IFS=,; echo "${live[*]}")
    echo "GUARD: shared mode — co-resident: $GUARD_CONTENTION (proceeding, nice=10, contention will be reported)"
  fi
  local used total free_gib
  used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)
  total=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
  free_gib=$(( (total - used) / 1024 ))
  local min_free=24
  (( free_gib >= min_free )) || { echo "GUARD: only ${free_gib}GiB free (<${min_free}) — refusing to crowd co-residents"; return 1; }
  if [[ "$mode" == "real" ]] && command -v jq >/dev/null && [[ -f "$root/research/state.json" ]]; then
    local spent cap
    spent=$(jq -r ".gpu_budget_hours.${loop}_spent // 0" "$root/research/state.json")
    cap=$(jq -r ".gpu_budget_hours.${loop}_cap // 0" "$root/research/state.json")
    awk -v s="$spent" -v c="$cap" -v m="$est_min" 'BEGIN{exit !(s + m/60.0 <= c)}' \
      || { echo "GUARD: budget exceeded for $loop (spent=$spent cap=$cap)"; return 1; }
  fi
  echo "GUARD: ok ($mode, ${est_min}m, ${free_gib}GiB free, contention=$GUARD_CONTENTION)"; return 0
}
