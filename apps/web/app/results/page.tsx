"use client";

import { useEffect, useState } from "react";
import { BarChart, LineChart } from "@/components/charts";
import { BenchmarkPanel } from "@/components/BenchmarkPanel";

interface ResultsData {
  claims: Array<{
    id: string;
    title: string;
    tier: "confirm" | "screen";
    value: number;
    context: string;
  }>;
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

  if (loading) return <p className="text-sm text-slate-500">Loading...</p>;
  if (error) return <p className="text-sm text-red-300">{error}</p>;

  return (
    <main className="min-h-screen bg-gradient-to-b from-night-950 to-night-900 py-12 px-6">
      <div className="mx-auto max-w-6xl">
        <div className="mb-8 space-y-3">
          <h1 className="text-4xl font-serif font-bold text-gradient">Results</h1>
          <p className="text-sm text-slate-400">
            Confirmed claims (confirm tier) and screening results (screen tier).
            Every number is sourced from a gate JSON (see HANDOFF.md).
          </p>
        </div>

        {!data ? (
          <div className="card p-6">
            <p className="text-sm text-slate-500">
              No results available yet. Run the export tool to populate result data:
            </p>
            <code className="block text-xs text-slate-400 mt-2 bg-night-900 p-2 rounded">
              python scripts/tools/export_app_data.py --repo-root . --out-app apps/web/public/data
            </code>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {data.claims.map((claim) => (
                <div
                  key={claim.id}
                  className={`card p-6 space-y-3 border-l-4 ${
                    claim.tier === "confirm"
                      ? "border-teal-600"
                      : "border-saffron-600"
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1">
                      <p className="text-lg font-semibold text-slate-100">
                        {claim.title}
                      </p>
                    </div>
                    <span
                      className={`chip text-xs capitalize ${
                        claim.tier === "confirm"
                          ? "border-teal-600/60 text-teal-300"
                          : "border-saffron-600/60 text-saffron-300"
                      }`}
                    >
                      {claim.tier}
                    </span>
                  </div>

                  <p className="text-2xl font-bold text-indigo-300">
                    {claim.value.toFixed(2)}
                  </p>

                  <p className="text-xs text-slate-500">{claim.context}</p>
                </div>
              ))}
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
