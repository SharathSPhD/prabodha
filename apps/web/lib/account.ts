"use client";

import { createClient as createBrowserClient } from "@/lib/supabase/client";

export type AccountTier = "guest" | "user" | "admin";
export const ACCOUNT_TIERS: AccountTier[] = ["guest", "user", "admin"];

/** Get BYOK credentials for the current user (browser-side). */
export async function getMyCredentials(provider: string) {
  const supabase = createBrowserClient();
  if (!supabase) return null;

  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) return null;

  const { data } = await supabase
    .from("user_llm_credentials")
    .select("api_key")
    .eq("user_id", user.id)
    .eq("provider", provider)
    .single();

  return data?.api_key || null;
}

/** Save BYOK credentials for the current user. */
export async function saveCredentials(provider: string, apiKey: string) {
  const supabase = createBrowserClient();
  if (!supabase) throw new Error("Supabase not configured");

  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) throw new Error("Not authenticated");

  const { error } = await supabase
    .from("user_llm_credentials")
    .upsert({
      user_id: user.id,
      provider,
      api_key: apiKey,
    })
    .eq("user_id", user.id)
    .eq("provider", provider);

  if (error) throw error;
}
