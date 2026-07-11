/**
 * POST /api/byok-run — run prompt-space hardening on the USER'S OWN model via OpenRouter (BYOK).
 *
 * This is the "any model, open or closed, no GPU" path: it calls OpenRouter chat/completions
 * twice for the same prompt — once raw (baseline) and once with the graded refusal-reinforcing
 * system prompt (hardened) — and returns both so the UI can show the real before/after.
 *
 * Key resolution (BYOK, never ours): body.apiKey, else the user's saved `openrouter` credential.
 */
import { NextRequest, NextResponse } from "next/server";
import { createClient as createServerClient } from "@/lib/supabase/server";
import { hardenMessages, REFUSAL_SYSTEM, type HardenLevel } from "@/lib/hardening-prompts";

async function resolveKey(bodyKey?: string): Promise<string | null> {
  if (bodyKey && bodyKey.trim()) return bodyKey.trim();
  try {
    const supabase = createServerClient();
    if (!supabase) return null;
    const {
      data: { user },
    } = await supabase.auth.getUser();
    if (!user) return null;
    const { data } = await supabase
      .from("user_llm_credentials")
      .select("api_key")
      .eq("user_id", user.id)
      .eq("provider", "openrouter")
      .maybeSingle();
    return data?.api_key || null;
  } catch {
    return null;
  }
}

async function callOpenRouter(
  key: string,
  model: string,
  messages: Array<{ role: string; content: string }>,
): Promise<{ text: string } | { error: string; status: number }> {
  let resp: Response;
  try {
    resp = await fetch("https://openrouter.ai/api/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${key}`,
        "Content-Type": "application/json",
        "HTTP-Referer": "https://prabodha-live.vercel.app",
        "X-Title": "prabodha",
      },
      body: JSON.stringify({ model, messages, max_tokens: 220, temperature: 0.7 }),
    });
  } catch (e) {
    return { error: `Network error reaching OpenRouter: ${(e as Error).message}`, status: 502 };
  }
  if (!resp.ok) {
    const detail = await resp.text().catch(() => "");
    return { error: `OpenRouter ${resp.status}: ${detail.slice(0, 200)}`, status: resp.status };
  }
  const json = await resp.json().catch(() => null);
  const text = json?.choices?.[0]?.message?.content;
  if (typeof text !== "string") return { error: "OpenRouter returned no completion", status: 502 };
  return { text };
}

export async function POST(request: NextRequest) {
  let body: { prompt?: string; model?: string; level?: HardenLevel; apiKey?: string };
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }
  const { prompt, model, level } = body;
  if (!prompt || !model) {
    return NextResponse.json({ error: "Missing prompt or model" }, { status: 400 });
  }
  const lvl: HardenLevel = level && REFUSAL_SYSTEM[level] ? level : "firm";

  const key = await resolveKey(body.apiKey);
  if (!key) {
    return NextResponse.json(
      {
        error:
          "No OpenRouter key. Save an 'openrouter' credential in Settings, or pass apiKey. " +
          "The key stays yours (BYOK) and is used only to run this comparison on your chosen model.",
      },
      { status: 401 },
    );
  }

  // Baseline: the raw prompt, no hardening. Hardened: graded refusal-reinforcing system prompt.
  const [baseline, hardened] = await Promise.all([
    callOpenRouter(key, model, [{ role: "user", content: prompt }]),
    callOpenRouter(key, model, hardenMessages(prompt, lvl)),
  ]);

  for (const r of [baseline, hardened]) {
    if ("error" in r) return NextResponse.json({ error: r.error }, { status: r.status });
  }

  return NextResponse.json({
    ok: true,
    model,
    level: lvl,
    system_prompt: REFUSAL_SYSTEM[lvl],
    baseline_text: (baseline as { text: string }).text,
    hardened_text: (hardened as { text: string }).text,
    caveat:
      "Prompt-space hardening works on any model but does not stop all jailbreaks; for open weights, " +
      "combine with the activation moat. This ran on YOUR OpenRouter model with YOUR key.",
  });
}
