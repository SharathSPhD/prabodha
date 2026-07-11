/**
 * POST /api/register-pack — register a prabodha hardening pack to the USER'S OWN HuggingFace account.
 *
 * BYOK: the user's HF token is used (never ours). Token resolution order:
 *   1. body.hfToken (explicit, e.g. pasted at registration time)
 *   2. the user's saved `huggingface` credential in user_llm_credentials (Supabase, RLS own-only)
 *
 * Honest artifact: we publish a hardening PACK (spec + model card + loader), not fake weights —
 * activation hardening is a runtime hook. See lib/hardening-pack.ts.
 */
import { NextRequest, NextResponse } from "next/server";
import { createRepo, uploadFiles, whoAmI, repoExists } from "@huggingface/hub";
import { createClient as createServerClient } from "@/lib/supabase/server";
import { buildHardeningPack, type PackInput } from "@/lib/hardening-pack";

async function resolveHfToken(bodyToken?: string): Promise<string | null> {
  if (bodyToken && bodyToken.trim()) return bodyToken.trim();
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
    .eq("provider", "huggingface")
    .single();
  return data?.api_key || null;
}

export async function POST(request: NextRequest) {
  let body: Partial<PackInput> & { hfToken?: string };
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  const { goal, baseModel, measured, hfToken } = body;
  if (!goal || !goal.name || !goal.mechanism || !goal.space) {
    return NextResponse.json(
      { error: "Missing goal (need name, mechanism, space)" },
      { status: 400 }
    );
  }
  if (!baseModel) {
    return NextResponse.json({ error: "Missing baseModel" }, { status: 400 });
  }

  const token = await resolveHfToken(hfToken);
  if (!token) {
    return NextResponse.json(
      {
        error:
          "No HuggingFace token. Save a 'huggingface' credential in Settings, or pass hfToken. " +
          "The token must have repo write permission and stays yours (BYOK).",
      },
      { status: 401 }
    );
  }

  // Verify the token and get the namespace we can write under.
  let namespace: string;
  try {
    const me = await whoAmI({ accessToken: token });
    namespace = me.name;
  } catch (e) {
    return NextResponse.json(
      { error: `HuggingFace token rejected: ${(e as Error).message}` },
      { status: 401 }
    );
  }

  const base = (baseModel.split("/").pop() || baseModel).toLowerCase().replace(/[^a-z0-9]+/g, "-");
  const goalSlug = goal.name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 40) || "goal";
  const repoName = `${namespace}/prabodha-hardening-${base}-${goalSlug}`.slice(0, 96);
  const repo = { type: "model" as const, name: repoName };

  const files = buildHardeningPack({
    goal: {
      name: goal.name,
      description: goal.description || "",
      positive_examples: goal.positive_examples || [],
      negative_examples: goal.negative_examples || [],
      mechanism: goal.mechanism,
      space: goal.space,
    },
    baseModel,
    measured: measured || null,
    prabodhaVersion: body.prabodhaVersion || "1.0",
  });

  try {
    const exists = await repoExists({ repo, accessToken: token }).catch(() => false);
    if (!exists) {
      await createRepo({ repo, accessToken: token, license: "apache-2.0" });
    }
    await uploadFiles({
      repo,
      accessToken: token,
      files: files.map((f) => ({
        path: f.path,
        content: new Blob([f.content], { type: "text/plain" }),
      })),
      commitTitle: `prabodha hardening pack: ${goal.name}`,
    });
  } catch (e) {
    return NextResponse.json(
      { error: `HuggingFace registration failed: ${(e as Error).message}` },
      { status: 502 }
    );
  }

  return NextResponse.json({
    ok: true,
    repo: repoName,
    url: `https://huggingface.co/${repoName}`,
    namespace,
    files: files.map((f) => f.path),
    kind: measured ? "measured" : "recipe",
  });
}
