"use client";

import { createBrowserClient } from "@supabase/ssr";
import type { SupabaseClient } from "@supabase/supabase-js";
import { SUPABASE_URL, SUPABASE_ANON_KEY, FORCE_LOCAL_MODE } from "../config";

const url = FORCE_LOCAL_MODE ? "" : SUPABASE_URL;
const anonKey = FORCE_LOCAL_MODE ? "" : SUPABASE_ANON_KEY;

export const supabaseConfigured = Boolean(url && anonKey);

let browserClient: SupabaseClient | null = null;

export function createClient(): SupabaseClient | null {
  if (!url || !anonKey) return null;
  if (!browserClient) {
    browserClient = createBrowserClient(url, anonKey);
  }
  return browserClient;
}
