-- prabodha — Supabase schema
-- Run in the Supabase SQL editor after project creation.
-- RLS: admin-only for config/credentials; per-user for BYOK.

create extension if not exists pgcrypto;

-- ---------------------------------------------------------------------------
-- User account tiers
-- ---------------------------------------------------------------------------
create type public.account_tier as enum ('guest', 'user', 'admin');

create table if not exists public.user_tiers (
  user_id        uuid primary key references auth.users (id) on delete cascade,
  tier           public.account_tier not null default 'guest',
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now()
);

alter table public.user_tiers enable row level security;

drop policy if exists "user_tiers select self" on public.user_tiers;
create policy "user_tiers select self"
  on public.user_tiers for select
  using (auth.uid() = user_id);

-- Admin-only bootstrap RPC (run once via Supabase SQL editor):
-- select auth.uid() as id, email from auth.users where email = 'sharath.sathish@outlook.com';
-- then insert into public.user_tiers (user_id, tier) values ('<uid>', 'admin');

-- ---------------------------------------------------------------------------
-- User LLM credentials (BYOK — Bring Your Own Key)
-- ---------------------------------------------------------------------------
create table if not exists public.user_llm_credentials (
  id             uuid primary key default gen_random_uuid(),
  user_id        uuid not null references auth.users (id) on delete cascade,
  provider       text not null check (provider in ('openrouter', 'anthropic', 'openai', 'llamacpp')),
  api_key        text not null,
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now(),
  unique(user_id, provider)
);

create index if not exists user_llm_creds_user_idx on public.user_llm_credentials (user_id);

alter table public.user_llm_credentials enable row level security;

drop policy if exists "creds select own" on public.user_llm_credentials;
create policy "creds select own"
  on public.user_llm_credentials for select
  using (auth.uid() = user_id);

drop policy if exists "creds insert own" on public.user_llm_credentials;
create policy "creds insert own"
  on public.user_llm_credentials for insert
  with check (auth.uid() = user_id);

drop policy if exists "creds update own" on public.user_llm_credentials;
create policy "creds update own"
  on public.user_llm_credentials for update
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

drop policy if exists "creds delete own" on public.user_llm_credentials;
create policy "creds delete own"
  on public.user_llm_credentials for delete
  using (auth.uid() = user_id);

-- ---------------------------------------------------------------------------
-- Runtime configuration (admin-managed: gateway URLs, default models, etc.)
-- ---------------------------------------------------------------------------
create table if not exists public.runtime_config (
  key            text primary key,
  value          text not null,
  description    text,
  updated_at     timestamptz not null default now()
);

insert into public.runtime_config (key, description) values
  ('steer_gateway_url', 'Gateway SSE proxy URL (e.g., https://spark.tailnet.ts.net:8443)'),
  ('steer_gateway_secret', 'Bearer token for gateway auth'),
  ('default_model', 'Default LLM for Live mode (e.g., qwen2.5:14b)'),
  ('llamacpp_gateway_url', 'LlamaCpp inference server URL (alternative to steer_gateway_url)'),
  ('default_llamacpp_model', 'Default model on llamacpp gateway')
on conflict do nothing;

alter table public.runtime_config enable row level security;

drop policy if exists "config select public" on public.runtime_config;
create policy "config select public"
  on public.runtime_config for select
  using (true);

drop policy if exists "config update admin" on public.runtime_config;
create policy "config update admin"
  on public.runtime_config for update
  using (
    exists (
      select 1 from public.user_tiers ut
      where ut.user_id = auth.uid()
        and ut.tier = 'admin'
    )
  )
  with check (
    exists (
      select 1 from public.user_tiers ut
      where ut.user_id = auth.uid()
        and ut.tier = 'admin'
    )
  );

-- Admin RPC to update config (security definer, runs as postgres)
create or replace function admin_set_runtime_config(cfg_key text, cfg_value text)
returns void
language sql
security definer
set search_path = 'public'
as $$
  update public.runtime_config
  set value = cfg_value,
      updated_at = now()
  where key = cfg_key;
$$;

-- Verify admin status before allowing update
create or replace function check_is_admin()
returns boolean
language sql
security definer
set search_path = 'public'
as $$
  select tier = 'admin'
  from public.user_tiers
  where user_id = auth.uid();
$$;

-- ---------------------------------------------------------------------------
-- Exported data (results, traces, etc.)
-- Stored in apps/web/public/data/ as JSON files, NOT in the DB
-- But metadata about what's exported can live here for audit
-- ---------------------------------------------------------------------------
create table if not exists public.export_logs (
  id             uuid primary key default gen_random_uuid(),
  export_type    text not null,
  file_path      text not null,
  content_hash   text not null,
  exported_at    timestamptz not null default now()
);

create index if not exists export_logs_type_idx on public.export_logs (export_type);

alter table public.export_logs enable row level security;

drop policy if exists "export_logs select public" on public.export_logs;
create policy "export_logs select public"
  on public.export_logs for select
  using (true);
