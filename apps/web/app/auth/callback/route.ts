import { createServerClient, type CookieOptions } from "@supabase/ssr";
import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";
import { SUPABASE_URL, SUPABASE_ANON_KEY } from "@/lib/config";

type CookieToSet = { name: string; value: string; options?: CookieOptions };

function isValidRedirectPath(path: string): boolean {
  if (!path) return false;

  // Must be a relative path starting with /
  if (!path.startsWith("/")) return false;

  // Reject protocol-relative URLs (//host)
  if (path.startsWith("//")) return false;

  // Reject absolute URLs with protocol (http://, https://, etc.)
  if (/^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(path)) return false;

  return true;
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const code = searchParams.get("code");
  const nextParam = searchParams.get("next");

  // Validate redirect target: must be same-origin relative path
  const next = isValidRedirectPath(nextParam) ? nextParam : "/dashboard";

  if (!code) {
    return NextResponse.redirect(new URL("/login?error=no_code", request.url));
  }

  const cookieStore = cookies();
  const supabase = createServerClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
    cookies: {
      getAll() {
        return cookieStore.getAll();
      },
      setAll(cookiesToSet: CookieToSet[]) {
        cookiesToSet.forEach(({ name, value, options }) =>
          cookieStore.set(name, value, options)
        );
      },
    },
  });

  const { error } = await supabase.auth.exchangeCodeForSession(code);

  if (error) {
    return NextResponse.redirect(
      new URL(`/login?error=${error.message}`, request.url)
    );
  }

  return NextResponse.redirect(new URL(next, request.url));
}
