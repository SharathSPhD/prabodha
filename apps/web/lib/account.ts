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

/** Goal type for alignment specifications. */
export interface Goal {
  id: string;
  name: string;
  description: string;
  positive_examples: string[];
  negative_examples: string[];
  mechanism: string;
  space: "prompt" | "activation";
  created_at: string;
  updated_at: string;
}

/** Save an alignment goal for the current user. */
export async function saveGoal(goal: Omit<Goal, "id" | "created_at" | "updated_at">) {
  const supabase = createBrowserClient();
  if (!supabase) {
    // Fallback to localStorage for guests
    const goals = JSON.parse(localStorage.getItem("prabodha:goals") || "[]");
    const newGoal: Goal = {
      id: Math.random().toString(36).slice(2),
      ...goal,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    goals.push(newGoal);
    localStorage.setItem("prabodha:goals", JSON.stringify(goals));
    return newGoal;
  }

  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) throw new Error("Not authenticated");

  const { data, error } = await supabase
    .from("alignment_goals")
    .insert({
      user_id: user.id,
      name: goal.name,
      description: goal.description,
      positive_examples: goal.positive_examples,
      negative_examples: goal.negative_examples,
      mechanism: goal.mechanism,
      space: goal.space,
    })
    .select()
    .single();

  if (error) throw error;
  return data as Goal;
}

/** List alignment goals for the current user. */
export async function listGoals(): Promise<Goal[]> {
  const supabase = createBrowserClient();
  if (!supabase) {
    // Fallback to localStorage for guests
    return JSON.parse(localStorage.getItem("prabodha:goals") || "[]");
  }

  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) return [];

  const { data, error } = await supabase
    .from("alignment_goals")
    .select("*")
    .eq("user_id", user.id)
    .order("created_at", { ascending: false });

  if (error) throw error;
  return (data || []) as Goal[];
}

/** Delete an alignment goal by ID. */
export async function deleteGoal(goalId: string) {
  const supabase = createBrowserClient();
  if (!supabase) {
    // Fallback to localStorage for guests
    const goals = JSON.parse(localStorage.getItem("prabodha:goals") || "[]");
    const filtered = goals.filter((g: Goal) => g.id !== goalId);
    localStorage.setItem("prabodha:goals", JSON.stringify(filtered));
    return;
  }

  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) throw new Error("Not authenticated");

  const { error } = await supabase
    .from("alignment_goals")
    .delete()
    .eq("id", goalId)
    .eq("user_id", user.id);

  if (error) throw error;
}
