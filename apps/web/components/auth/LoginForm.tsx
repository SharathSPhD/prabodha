"use client";

import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { createClient } from "@/lib/supabase/client";

export default function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const next = searchParams.get("next") || "/dashboard";
  const errorParam = searchParams.get("error");

  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(errorParam || "");
  const [message, setMessage] = useState("");

  async function handleSignIn(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    setMessage("");

    const supabase = createClient();
    if (!supabase) {
      setError("Supabase not configured. Use local mode for development.");
      setLoading(false);
      return;
    }

    const { error: signInError } = await supabase.auth.signInWithOtp({
      email: email.trim(),
      options: {
        emailRedirectTo: `${window.location.origin}/auth/callback?next=${encodeURIComponent(next)}`,
      },
    });

    if (signInError) {
      setError(signInError.message);
    } else {
      setMessage(`Check your email for a magic link.`);
    }

    setLoading(false);
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-night-950 to-night-900 flex items-center justify-center px-6">
      <div className="w-full max-w-sm space-y-8">
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-serif font-bold text-gradient">prabodha</h1>
          <p className="text-sm text-slate-400">Sign in to save runs and access admin features</p>
        </div>

        <form onSubmit={handleSignIn} className="card space-y-4 p-6">
          {error && (
            <div className="rounded-lg border border-red-600/30 bg-red-900/10 p-3 text-sm text-red-300">
              {error}
            </div>
          )}

          {message && (
            <div className="rounded-lg border border-teal-600/30 bg-teal-900/10 p-3 text-sm text-teal-300">
              {message}
            </div>
          )}

          <div className="space-y-2">
            <label htmlFor="email" className="label">
              Email address
            </label>
            <input
              id="email"
              type="email"
              placeholder="your@email.com"
              className="input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            className="btn-primary w-full justify-center py-2.5"
            disabled={loading || !email}
          >
            {loading ? "Sending link..." : "Send magic link"}
          </button>

          <p className="text-xs text-center text-slate-500 pt-2">
            We&apos;ll send you a secure link. No password needed.
          </p>
        </form>
      </div>
    </main>
  );
}
