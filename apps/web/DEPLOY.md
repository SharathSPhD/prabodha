# Deploying the prabodha app

The app is a Next.js 14 monorepo package at `apps/web`, backed by a live Supabase
project (`prabodha`, ref `ndeahzldqjdfquhvzznm`, region ap-south-1) whose schema is
already applied and advisor-hardened.

## Vercel (recommended: git-linked, ~2 minutes)

1. Vercel dashboard → **Add New → Project → Import** `SharathSPhD/prabodha`.
2. **Root Directory:** `apps/web`. Framework auto-detects as Next.js.
3. Environment variables — the two public Supabase vars are already committed in
   `apps/web/.env.production` (the anon key is public and RLS-protected, same pattern as
   the kundali app), so they inline at build time. Add only the server-side secret when
   the live steering gateway is deployed:
   - `STEER_GATEWAY_SECRET` — the bearer secret the GB10 gateway expects (server-side
     only; NOT `NEXT_PUBLIC_`). Leave unset until the gateway is up — the app runs fully
     in **Replay** mode (real GB10 fire-case traces) and **BYOK** mode without it.
4. Deploy. Subsequent pushes to `main` auto-deploy.

Alternatively, from a checkout: `cd apps/web && npx vercel --prod` (set root to this dir).

## Admin bootstrap (one-time, after first sign-in)

Sign in once at the deployed URL with `sharath.sathish@outlook.com`, then in the Supabase
SQL editor:

```sql
insert into public.user_tiers (user_id, tier)
select id, 'admin' from auth.users where email = 'sharath.sathish@outlook.com'
on conflict (user_id) do update set tier = 'admin';
```

## Live steering gateway (admin "Live" mode — operator-run on the GB10)

The **Live** theatre mode streams real lens read/write internals from the GB10. It is
**not auto-deployed**: running a GPU steering endpoint co-resident with the PSALM/prabhasa
jobs risks them, and exposing the DGX is an operator decision. When you want it:

```bash
cd /home/sharaths/projects/prabodha
source scripts/lib/gpu_guard.sh && gpu_guard_check real 30 gateway   # confirm idle
docker compose build steer-gateway && docker compose up -d steer-gateway
tailscale funnel --bg --https=8443 8100                              # exposes GET /health, POST /steer
```

Then set the gateway URL + secret from the app's **admin** page (writes to
`runtime_config` via the admin RPC), and add `STEER_GATEWAY_SECRET` to Vercel env.
Replay + BYOK modes need none of this.
