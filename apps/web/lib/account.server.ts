"use server";

import { createClient as createServerClient } from "@/lib/supabase/server";

export type AccountTier = "guest" | "user" | "admin";
export const ACCOUNT_TIERS: AccountTier[] = ["guest", "user", "admin"];

/** Get the current user's tier (server-side). */
export async function getMyTier(): Promise<AccountTier | null> {
  const supabase = createServerClient();
  if (!supabase) return null;

  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) return null;

  const { data } = await supabase
    .from("user_tiers")
    .select("tier")
    .eq("user_id", user.id)
    .single();

  return (data?.tier || "guest") as AccountTier;
}

/** Look up a user by email and get their tier (admin only, server-side). */
export async function adminLookupUserByEmail(email: string) {
  const supabase = createServerClient();
  if (!supabase) return null;

  // Verify caller is admin
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) throw new Error("Not authenticated");

  const { data: tierData } = await supabase
    .from("user_tiers")
    .select("tier")
    .eq("user_id", user.id)
    .single();

  if (tierData?.tier !== "admin") {
    throw new Error("Admin access required");
  }

  // Look up user
  const { data: users } = await supabase.auth.admin.listUsers();
  const found = users?.users.find((u) => u.email === email);

  if (!found) return null;

  const { data: userTier } = await supabase
    .from("user_tiers")
    .select("tier")
    .eq("user_id", found.id)
    .single();

  return {
    email: found.email || "",
    tier: (userTier?.tier || "guest") as AccountTier,
  };
}

/** Set a user's tier (admin only). */
export async function adminSetTierByEmail(email: string, tier: AccountTier) {
  const supabase = createServerClient();
  if (!supabase) throw new Error("Supabase not configured");

  // Verify caller is admin
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) throw new Error("Not authenticated");

  const { data: tierData } = await supabase
    .from("user_tiers")
    .select("tier")
    .eq("user_id", user.id)
    .single();

  if (tierData?.tier !== "admin") {
    throw new Error("Admin access required");
  }

  // Look up user by email
  const { data: users } = await supabase.auth.admin.listUsers();
  const found = users?.users.find((u) => u.email === email);
  if (!found) throw new Error("User not found");

  // Upsert tier
  const { error } = await supabase
    .from("user_tiers")
    .upsert({ user_id: found.id, tier })
    .eq("user_id", found.id);

  if (error) throw error;
}
