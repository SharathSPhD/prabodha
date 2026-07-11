#!/usr/bin/env bash
# Self-healing gateway tunnel: keeps the steer-gateway + a cloudflared tunnel up, and
# auto-re-registers the tunnel URL into Vercel (env + redeploy) whenever it changes.
# This is the best-effort "permanent" tunnel without a cloudflare domain/named tunnel.
# Run:  VERCEL_TOKEN=... nohup bash scripts/ops/gateway_tunnel_service.sh >/tmp/gw_tunnel_service.log 2>&1 &
# For reboot survival, install as a systemd --user service + `loginctl enable-linger`.
set -u

CF="${CF:-$HOME/.local/bin/cloudflared}"
GATEWAY_LOCAL="http://localhost:8200"
VT="${VERCEL_TOKEN:?set VERCEL_TOKEN}"
PROJ="${VERCEL_PROJECT:-prj_atIFYtXDOkg6rmjMZnCA2SnaR2Oo}"
TEAM="${VERCEL_TEAM:-team_qIaQJRTK68ppKLeE9X3HL7jV}"
URL_FILE="/tmp/gateway_tunnel_url.txt"
LOG="/tmp/cf_tunnel.log"

log(){ echo "[$(date -u +%H:%M:%S)] $*"; }

ensure_gateway(){
  if ! curl -s -o /dev/null --max-time 8 "$GATEWAY_LOCAL/health"; then
    log "gateway down -> docker start steer-gateway"
    docker start steer-gateway >/dev/null 2>&1
    for _ in $(seq 1 20); do curl -s -o /dev/null --max-time 5 "$GATEWAY_LOCAL/health" && break; sleep 5; done
  fi
}

vercel_set(){  # $1=key $2=value
  local id
  id=$(curl -s "https://api.vercel.com/v9/projects/$PROJ/env?teamId=$TEAM" -H "Authorization: Bearer $VT" \
        | python3 -c "import sys,json;[print(e['id']) for e in json.load(sys.stdin).get('envs',[]) if e['key']=='$1']" 2>/dev/null | head -1)
  [ -n "$id" ] && curl -s -X DELETE "https://api.vercel.com/v9/projects/$PROJ/env/$id?teamId=$TEAM" -H "Authorization: Bearer $VT" -o /dev/null
  curl -s -X POST "https://api.vercel.com/v10/projects/$PROJ/env?teamId=$TEAM" -H "Authorization: Bearer $VT" \
    -H "Content-Type: application/json" -d "{\"key\":\"$1\",\"value\":\"$2\",\"type\":\"encrypted\",\"target\":[\"production\"]}" -o /dev/null
}

register_url(){  # $1=new url
  local secret; secret=$(docker exec steer-gateway printenv STEER_GATEWAY_SECRET 2>/dev/null)
  log "registering $1 into Vercel + redeploy"
  vercel_set NEXT_PUBLIC_STEER_GATEWAY_URL "$1"
  vercel_set STEER_GATEWAY_SECRET "$secret"
  local did; did=$(curl -s "https://api.vercel.com/v6/deployments?projectId=$PROJ&teamId=$TEAM&target=production&limit=1" -H "Authorization: Bearer $VT" \
        | python3 -c "import sys,json;print(json.load(sys.stdin)['deployments'][0]['uid'])" 2>/dev/null)
  curl -s -X POST "https://api.vercel.com/v13/deployments?teamId=$TEAM&forceNew=1" -H "Authorization: Bearer $VT" \
    -H "Content-Type: application/json" -d "{\"name\":\"prabodha-live\",\"deploymentId\":\"$did\",\"target\":\"production\"}" -o /dev/null
  echo "$1" > "$URL_FILE"
}

start_tunnel(){
  pkill -f "cloudflared tunnel --url $GATEWAY_LOCAL" 2>/dev/null
  : > "$LOG"
  nohup "$CF" tunnel --url "$GATEWAY_LOCAL" --no-autoupdate >"$LOG" 2>&1 &
  echo $! > /tmp/cf_tunnel.pid
  for _ in $(seq 1 30); do
    URL=$(grep -oE "https://[a-z0-9-]+\.trycloudflare\.com" "$LOG" | head -1)
    [ -n "$URL" ] && break; sleep 2
  done
  echo "${URL:-}"
}

log "gateway tunnel service starting"
CURRENT=""
while true; do
  ensure_gateway
  if [ -n "$CURRENT" ] && curl -s -o /dev/null --max-time 12 "$CURRENT/health"; then
    sleep 30; continue
  fi
  log "tunnel down/absent -> (re)starting"
  NEW=$(start_tunnel)
  if [ -z "$NEW" ]; then log "failed to get tunnel URL, retrying in 15s"; sleep 15; continue; fi
  ok=""; for _ in $(seq 1 8); do curl -s -o /dev/null --max-time 12 "$NEW/health" && { ok=1; break; }; sleep 3; done
  [ -z "$ok" ] && { log "new tunnel $NEW not reaching gateway, retrying"; sleep 10; continue; }
  if [ "$NEW" != "$CURRENT" ]; then register_url "$NEW"; CURRENT="$NEW"; log "active tunnel: $NEW"; fi
  sleep 30
done
