"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { createClient } from "@/lib/supabase/client";
import { getMyTier } from "@/lib/account.server";
import { Settings, LogOut, Shield } from "lucide-react";

export default function DashboardPage() {
  const [user, setUser] = useState<any>(null);
  const [tier, setTier] = useState<string | null>(null);

  useEffect(() => {
    const supabase = createClient();
    if (!supabase) return;

    supabase.auth.getUser().then(({ data: { user } }) => {
      setUser(user);
    });

    getMyTier().then(setTier);
  }, []);

  async function handleLogout() {
    const supabase = createClient();
    if (!supabase) return;
    await supabase.auth.signOut();
    window.location.href = "/";
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-night-950 to-night-900 py-12 px-6">
      <div className="mx-auto max-w-4xl">
        <div className="mb-8 space-y-3">
          <h1 className="text-3xl font-serif font-bold text-slate-100">
            Dashboard
          </h1>
          <p className="text-sm text-slate-500">Welcome, {user?.email}</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Link href="/dashboard/settings">
            <div className="card p-6 space-y-3 hover:border-indigo-600 transition cursor-pointer">
              <div className="flex items-center gap-2 text-indigo-300">
                <Settings className="w-5 h-5" />
                <span className="font-semibold">Settings</span>
              </div>
              <p className="text-xs text-slate-500">
                Manage your BYOK API keys and preferences.
              </p>
            </div>
          </Link>

          {tier === "admin" && (
            <Link href="/dashboard/admin">
              <div className="card p-6 space-y-3 hover:border-saffron-600 transition cursor-pointer border-l-4 border-saffron-600">
                <div className="flex items-center gap-2 text-saffron-300">
                  <Shield className="w-5 h-5" />
                  <span className="font-semibold">Admin</span>
                </div>
                <p className="text-xs text-slate-500">
                  Manage users, configure gateway, health checks.
                </p>
              </div>
            </Link>
          )}
        </div>

        <div className="mt-8">
          <button
            onClick={handleLogout}
            className="btn-secondary inline-flex gap-2"
          >
            <LogOut className="w-4 h-4" />
            Sign out
          </button>
        </div>
      </div>
    </main>
  );
}
