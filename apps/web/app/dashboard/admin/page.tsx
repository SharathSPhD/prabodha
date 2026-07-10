"use client";

import { useEffect, useState } from "react";
import { Search, Users, Zap } from "lucide-react";
import {
  getMyTier,
  adminLookupUserByEmail,
  adminSetTierByEmail,
  type AccountTier,
} from "@/lib/account.server";
import { createClient } from "@/lib/supabase/client";

const ACCOUNT_TIERS: AccountTier[] = ["guest", "user", "admin"];

export default function AdminPage() {
  const [myTier, setMyTier] = useState<AccountTier | null>(null);
  const [loading, setLoading] = useState(true);
  const [email, setEmail] = useState("");
  const [looking, setLooking] = useState(false);
  const [found, setFound] = useState<{ email: string; tier: AccountTier } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [updating, setUpdating] = useState(false);

  // Gateway config
  const [gatewayUrl, setGatewayUrl] = useState("");
  const [gatewayLoading, setGatewayLoading] = useState(true);
  const [gatewayError, setGatewayError] = useState<string | null>(null);
  const [gatewayNotice, setGatewayNotice] = useState<string | null>(null);
  const [gatewaySaving, setGatewaySaving] = useState(false);
  const [gatewayHealthy, setGatewayHealthy] = useState<boolean | null>(null);
  const [gatewayTesting, setGatewayTesting] = useState(false);

  useEffect(() => {
    (async () => {
      const tier = await getMyTier();
      setMyTier(tier);
      setLoading(false);

      if (tier === "admin") {
        const supabase = createClient();
        if (supabase) {
          try {
            const { data } = await supabase
              .from("runtime_config")
              .select("key,value");

            if (data) {
              const urlCfg = data.find((r) => r.key === "steer_gateway_url");
              setGatewayUrl(urlCfg?.value ?? "");
            }
          } catch (err) {
            console.error("Failed to load config:", err);
          }
          setGatewayLoading(false);
        }
      }
    })();
  }, []);

  async function lookup() {
    setLooking(true);
    setError(null);
    try {
      const result = await adminLookupUserByEmail(email.trim());
      if (!result) setError("No user found with that email.");
      else setFound({ email: result.email, tier: result.tier });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Lookup failed.");
    } finally {
      setLooking(false);
    }
  }

  async function setTier(tier: AccountTier) {
    if (!found) return;
    setUpdating(true);
    setError(null);
    try {
      await adminSetTierByEmail(found.email, tier);
      setFound({ ...found, tier });
      setNotice(`${found.email} is now ${tier}.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update tier.");
    } finally {
      setUpdating(false);
    }
  }

  async function saveGatewayUrl() {
    setGatewaySaving(true);
    setGatewayError(null);
    setGatewayNotice(null);

    try {
      const supabase = createClient();
      if (!supabase) throw new Error("Supabase not configured");

      const { error } = await supabase.rpc(
        "admin_set_runtime_config",
        {
          cfg_key: "steer_gateway_url",
          cfg_value: gatewayUrl.trim() || null,
        }
      );

      if (error) throw error;
      setGatewayNotice("Gateway URL saved.");
    } catch (err) {
      setGatewayError(err instanceof Error ? err.message : "Failed to save.");
    } finally {
      setGatewaySaving(false);
    }
  }

  async function testGatewayHealth() {
    if (!gatewayUrl.trim()) {
      setGatewayError("Please enter a gateway URL first.");
      return;
    }

    setGatewayTesting(true);
    setGatewayError(null);
    setGatewayHealthy(null);

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);

    try {
      const res = await fetch(`${gatewayUrl.trim()}/health`, {
        mode: "no-cors",
        signal: controller.signal,
      });
      setGatewayHealthy(res.ok || res.status < 500);
    } catch (err) {
      setGatewayHealthy(false);
    } finally {
      clearTimeout(timeout);
      setGatewayTesting(false);
    }
  }

  if (loading) return <p className="text-sm text-slate-500">Loading...</p>;

  if (myTier !== "admin") {
    return (
      <main className="min-h-screen bg-gradient-to-b from-night-950 to-night-900 py-12 px-6">
        <div className="mx-auto max-w-2xl card p-6">
          <p className="text-sm text-red-300">
            This page is restricted to admin accounts.
          </p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-night-950 to-night-900 py-12 px-6">
      <div className="mx-auto max-w-4xl space-y-8">
        <h1 className="text-4xl font-serif font-bold text-gradient">Admin</h1>

        {/* User Management */}
        <div className="card p-6 space-y-6">
          <div className="space-y-2">
            <h2 className="flex items-center gap-2 text-lg font-semibold text-slate-100">
              <Users className="w-5 h-5" />
              User Management
            </h2>
            <p className="text-xs text-slate-500">
              Look up users by email and manage their tier.
            </p>
          </div>

          <div className="space-y-3">
            <div className="flex gap-2">
              <input
                type="email"
                placeholder="user@example.com"
                className="input flex-1"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && lookup()}
              />
              <button
                onClick={lookup}
                disabled={looking || !email.trim()}
                className="btn-primary"
              >
                <Search className="w-4 h-4" />
              </button>
            </div>

            {error && <p className="text-sm text-red-300">{error}</p>}
            {notice && <p className="text-sm text-teal-300">{notice}</p>}

            {found && (
              <div className="rounded-lg border border-night-600 p-4 space-y-3">
                <p className="text-sm text-slate-300">
                  <span className="font-semibold">{found.email}</span> — tier:{" "}
                  <span className="capitalize text-indigo-300 font-semibold">
                    {found.tier}
                  </span>
                </p>
                <div className="flex flex-wrap gap-2">
                  {ACCOUNT_TIERS.map((t) => (
                    <button
                      key={t}
                      onClick={() => setTier(t)}
                      disabled={updating || t === found.tier}
                      className={`chip ${
                        t === found.tier
                          ? "border-indigo-600 text-indigo-300"
                          : ""
                      }`}
                    >
                      {t}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Gateway Configuration */}
        <div className="card p-6 space-y-6">
          <div className="space-y-2">
            <h2 className="flex items-center gap-2 text-lg font-semibold text-slate-100">
              <Zap className="w-5 h-5" />
              Steer Gateway
            </h2>
            <p className="text-xs text-slate-500">
              Configure the prabodha steering gateway endpoint (GB10).
            </p>
          </div>

          {!gatewayLoading && (
            <div className="space-y-3">
              <div>
                <label className="label">Gateway URL</label>
                <div className="flex gap-2">
                  <input
                    type="url"
                    placeholder="https://spark-5208.tailnet.ts.net:8443"
                    className="input flex-1"
                    value={gatewayUrl}
                    onChange={(e) => setGatewayUrl(e.target.value)}
                    disabled={gatewaySaving}
                  />
                  <button
                    onClick={saveGatewayUrl}
                    disabled={gatewaySaving}
                    className="btn-primary"
                  >
                    {gatewaySaving ? "Saving..." : "Save"}
                  </button>
                </div>
              </div>

              <button
                onClick={testGatewayHealth}
                disabled={gatewayTesting || !gatewayUrl.trim()}
                className="btn-secondary text-sm"
              >
                {gatewayTesting ? "Testing..." : "Test health"}
              </button>

              {gatewayHealthy !== null && (
                <span
                  className={`chip ${
                    gatewayHealthy
                      ? "border-teal-600 text-teal-300"
                      : "border-red-600 text-red-300"
                  }`}
                >
                  {gatewayHealthy ? "Healthy" : "Unreachable"}
                </span>
              )}

              {gatewayError && (
                <p className="text-sm text-red-300">{gatewayError}</p>
              )}
              {gatewayNotice && (
                <p className="text-sm text-teal-300">{gatewayNotice}</p>
              )}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
