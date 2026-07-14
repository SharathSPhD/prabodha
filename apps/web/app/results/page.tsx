"use client";

import { useEffect, useState } from "react";
import { BarChart, LineChart } from "@/components/charts";
import { BenchmarkPanel } from "@/components/BenchmarkPanel";
import { SiteNav } from "@/components/SiteNav";

// Matches the real shape emitted by scripts/tools/export_app_data.py:
// { claims: [{ id, text, tier, gates: string[], numbers: { value, threshold, pass } }] }
interface Claim {
  id: string;
  text?: string;
  title?: string; // tolerate either key
  tier?: string;
  gates?: string[];
  numbers?: { value?: number; threshold?: number; pass?: boolean };
  value?: number; // tolerate a flat value too
  context?: string;
}
interface ResultsData {
  claims: Claim[];
}

export default function ResultsPage() {
  const [data, setData] = useState<ResultsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadResults() {
      try {
        const res = await fetch("/data/results.json");
        // 404 is expected when no data has been exported yet (empty-state)
        if (res.status === 404) {
          setData(null);
          setLoading(false);
          return;
        }
        if (!res.ok) throw new Error("Failed to load results");
        const json = await res.json();
        setData(json);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    }

    loadResults();
  }, []);

  if (loading) return (
    <main className="min-h-screen bg-gradient-to-b from-night-950 to-night-900">
      <SiteNav />
      <div className="mx-auto max-w-6xl px-6 py-12">
        <div className="animate-pulse space-y-4">
          <div className="h-10 w-48 rounded-lg bg-night-700" />
          <div className="h-4 w-96 max-w-full rounded bg-night-700/70" />
          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-32 rounded-xl bg-night-800/60" />
            ))}
          </div>
        </div>
      </div>
    </main>
  );
  if (error) return (
    <main className="min-h-screen bg-gradient-to-b from-night-950 to-night-900">
      <SiteNav />
      <div className="mx-auto max-w-6xl px-6 py-12">
        <div className="rounded-xl border border-rose-400/30 bg-rose-400/10 p-6">
          <p className="text-sm text-rose-200">{error}</p>
        </div>
      </div>
    </main>
  );

  return (
    <main className="min-h-screen bg-gradient-to-b from-night-950 to-night-900">
      <SiteNav />
      <div className="mx-auto max-w-6xl px-6 py-12">
        <div className="mb-8 space-y-3">
          <h1 className="text-4xl font-serif font-bold text-gradient">Results</h1>
          <p className="text-sm text-slate-400">
            Confirmed claims (confirm tier) and screening results (screen tier).
            Every number is sourced from a gate JSON (see HANDOFF.md).
          </p>
        </div>

        {!data ? (
          <div className="card p-6 space-y-4">
            <h2 className="font-semibold text-slate-100">No results yet</h2>
            <p className="text-sm text-slate-400">
              Results are generated from experiment gates (gates/*.json) and displayed here after export. Results showcase confirmed claims (confirm tier) and screening results (screen tier).
            </p>
            <p className="text-xs text-slate-500">
              To populate results locally, run:
            </p>
            <code className="block text-xs text-slate-400 bg-night-900 p-3 rounded font-mono">
              python scripts/tools/export_app_data.py --repo-root . --out-app apps/web/public/data
            </code>
            <p className="text-xs text-slate-500">
              See <a href="/glossary" className="text-indigo-400 hover:text-indigo-300">Glossary</a> for term definitions and README for methodology.
            </p>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {(data.claims || []).map((claim, i) => {
                const title = claim.text || claim.title || claim.id || "claim";
                const value = claim.numbers?.value ?? claim.value;
                const threshold = claim.numbers?.threshold;
                const pass = claim.numbers?.pass;
                return (
                  <div
                    key={claim.id || i}
                    className={`card p-6 space-y-3 border-l-4 ${
                      claim.tier === "confirm" ? "border-teal-600" : "border-saffron-600"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <p className="text-lg font-semibold text-slate-100 flex-1 break-words">{title}</p>
                      {claim.tier && (
                        <span
                          className={`chip text-xs capitalize ${
                            claim.tier === "confirm"
                              ? "border-teal-600/60 text-teal-300"
                              : "border-saffron-600/60 text-saffron-300"
                          }`}
                        >
                          {claim.tier}
                        </span>
                      )}
                    </div>

                    <div className="flex items-baseline gap-3">
                      <p className="text-2xl font-bold text-indigo-300">
                        {typeof value === "number" ? value.toFixed(3) : "—"}
                      </p>
                      {typeof threshold === "number" && (
                        <span className="text-xs text-slate-500">threshold {threshold}</span>
                      )}
                      {typeof pass === "boolean" && (
                        <span
                          className={`text-xs px-1.5 py-0.5 rounded ${
                            pass ? "bg-teal-900/40 text-teal-300" : "bg-amber-900/40 text-amber-300"
                          }`}
                        >
                          {pass ? "pass" : "fail-on-margin / screen"}
                        </span>
                      )}
                    </div>

                    {(claim.gates?.length || claim.context) && (
                      <p className="text-xs text-slate-500 font-mono break-words">
                        {claim.context || claim.gates?.join(", ")}
                      </p>
                    )}
                  </div>
                );
              })}
            </div>

            <div className="mt-12 card p-6 space-y-3 bg-night-800/50">
              <h2 className="text-lg font-semibold text-slate-100">About the data</h2>
              <p className="text-sm text-slate-500">
                All results are exported directly from{" "}
                <code className="rounded bg-night-900 px-1.5 py-0.5 text-[11px] font-mono text-indigo-300">
                  gates/*.json
                </code>{" "}
                using{" "}
                <code className="rounded bg-night-900 px-1.5 py-0.5 text-[11px] font-mono text-indigo-300">
                  scripts/tools/compose_*.py
                </code>
                . No hand-written numbers. Commit the JSON generator (not the JSON) to the repo.
              </p>
            </div>
          </>
        )}

        {/* Benchmark Panel (always shown) */}
        <div className="mt-12">
          <BenchmarkPanel />
        </div>
      </div>
    </main>
  );
}
