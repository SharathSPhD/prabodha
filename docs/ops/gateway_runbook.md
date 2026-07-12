# Steer-gateway runbook — stop to free memory, restart on demand

The live app's "Live Steering Studio" runs on the GB10 **steer-gateway** container,
exposed to Vercel through a cloudflared tunnel. This doc covers stopping it to free
memory and bringing it back.

## What actually holds memory

| Thing | Memory | Auto-managed? |
|---|---|---|
| **Loaded models** (the big cost, ~5–12 GB GPU each) | 0 when idle | **Yes** — loaded only when the app triggers a run, evicted after `PRABODHA_MODEL_IDLE_TTL` (default 600 s). Reloads on the next run. |
| **Container base** (FastAPI + CUDA context) | ~4.4 GiB RAM, ~0 GPU | No — freed only by stopping the container. |

So **model memory needs no manual management** — it loads on an app run and releases on
idle. Stopping the container only reclaims the ~4.4 GiB idle base, and it does **not**
auto-start on an app run (only the systemd service starts it). That is why this doc exists.

## Stop (free the ~4.4 GiB + take the tunnel down)

```bash
export XDG_RUNTIME_DIR=/run/user/1000
# 1. Stop the self-healing service first (else it restarts the container in ~10 s)
systemctl --user stop prabodha-gateway-tunnel
systemctl --user disable prabodha-gateway-tunnel   # optional: also skip auto-start on reboot
# 2. Stop the container
docker stop steer-gateway
```

While stopped, the live app shows a non-blocking "Live gateway offline" banner; the
recorded replays, the BYOK path, and the Lens Playground (recorded slices) all keep working.

## Restart

```bash
export XDG_RUNTIME_DIR=/run/user/1000
systemctl --user enable prabodha-gateway-tunnel   # if you disabled it
systemctl --user start prabodha-gateway-tunnel
```

The service self-heals: it starts the `steer-gateway` container, opens a fresh cloudflared
quick-tunnel, and **re-registers the new tunnel URL to Vercel** (`NEXT_PUBLIC_STEER_GATEWAY_URL`
+ `STEER_GATEWAY_SECRET`) and redeploys, so the live app reconnects automatically. Models
then load on demand on the first steering run — no manual model management.

## Verify

```bash
# service + container up
export XDG_RUNTIME_DIR=/run/user/1000
systemctl --user is-active prabodha-gateway-tunnel
docker ps --filter name=steer-gateway
# gateway answers (no models loaded until a run)
curl -s http://localhost:8200/health        # -> {"ok":true,"loaded_models":[...]}
# live app sees it (allow ~1 min for the Vercel redeploy after a URL change)
curl -s https://prabodha-live.vercel.app/api/steer   # -> {"online":true}
```

## Notes

- **Only touch `steer-gateway`.** The co-resident `samsaadhanii` container and the
  PSALM-integration / prabhasa GPU processes belong to other projects — leave them alone.
- Current URL is written to `/tmp/gateway_tunnel_url.txt`; logs via
  `journalctl --user -u prabodha-gateway-tunnel`.
- Secret `VERCEL_TOKEN` lives in `~/.config/prabodha/gateway.env` (chmod 600, not committed).
- The service has `Linger=yes`, so once enabled it survives a reboot.
