"use client";

import { useEffect, useState } from "react";
import SteerTraceViz from "@/components/theatre/SteerTraceViz";

interface SteerTrace {
  label: string;
  tokens: string[];
  entropies: number[];
  writes: Array<{ position: number; amplitude: number }>;
  readback: { verdict: "accept" | "reject"; confidence: number } | null;
}

// Raw trace files are { tokens: [{t, token, entropy, gated, write_norm}], ... }.
// The viz needs { tokens: string[], entropies: number[], writes, readback }. Transform + guard.
function toSteerTrace(raw: any, fallbackLabel: string): SteerTrace | null {
  const rawTokens = Array.isArray(raw?.tokens) ? raw.tokens : null;
  if (!rawTokens || rawTokens.length === 0) return null;
  const label =
    [raw?.concept, raw?.arm, raw?.seed != null ? `seed ${raw.seed}` : ""].filter(Boolean).join(" · ") ||
    fallbackLabel;
  const rb = raw?.readback;
  return {
    label,
    tokens: rawTokens.map((t: any) => (typeof t === "string" ? t : t?.token ?? "")),
    entropies: rawTokens.map((t: any) => (typeof t?.entropy === "number" ? t.entropy : 0)),
    writes: rawTokens
      .map((t: any, i: number) => ({ gated: !!t?.gated, position: typeof t?.t === "number" ? t.t : i, amplitude: t?.write_norm ?? 0 }))
      .filter((w: any) => w.gated)
      .map((w: any) => ({ position: w.position, amplitude: w.amplitude })),
    readback:
      rb && typeof rb.verdict === "string"
        ? { verdict: rb.verdict === "accept" ? "accept" : "reject", confidence: typeof rb.confidence === "number" ? rb.confidence : 0 }
        : null,
  };
}

export default function ReplayTheatre() {
  const [traces, setTraces] = useState<SteerTrace[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedTrace, setSelectedTrace] = useState(0);

  useEffect(() => {
    async function loadTraces() {
      try {
        const res = await fetch("/data/replays/index.json");
        if (res.status === 404) {
          setTraces([]);
          setLoading(false);
          return;
        }
        if (!res.ok) throw new Error("Failed to load traces");
        const data = await res.json();
        // index.json is { replays: [{slug, ...}] } (metadata) or an array of raw traces.
        const list: any[] = Array.isArray(data) ? data : Array.isArray(data?.replays) ? data.replays : [];
        const built: SteerTrace[] = [];
        for (let i = 0; i < list.length; i++) {
          const item = list[i];
          // If the item already carries tokens, use it; otherwise fetch its slug file.
          let raw = item;
          if (item?.slug && !Array.isArray(item?.tokens)) {
            try {
              const tr = await fetch(`/data/replays/${item.slug}.json`);
              if (tr.ok) raw = await tr.json();
            } catch {
              /* skip unreachable trace */
            }
          }
          const st = toSteerTrace(raw, item?.slug || `Trace ${i + 1}`);
          if (st) built.push(st);
        }
        setTraces(built);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    }

    loadTraces();
  }, []);

  if (loading) return <p className="text-sm text-slate-500">Loading fixture traces...</p>;
  if (error) return <p className="text-sm text-red-300">{error}</p>;
  if (traces.length === 0) {
    return (
      <div className="card p-6 space-y-4">
        <h2 className="font-semibold text-slate-100">No runs yet</h2>
        <p className="text-sm text-slate-400">
          Results are generated from experiment gates (live steering runs or confirmed benchmarks) and made available in Replay mode. Fixture traces showcase pre-recorded episodes.
        </p>
        <p className="text-xs text-slate-500">
          To populate fixture traces locally, run:
        </p>
        <code className="block text-xs text-slate-400 bg-night-900 p-3 rounded font-mono">
          python scripts/tools/export_app_data.py --repo-root . --out-app apps/web/public/data
        </code>
        <p className="text-xs text-slate-500">
          See <a href="/glossary" className="text-indigo-400 hover:text-indigo-300">Glossary</a> and README for methodology. Live steering requires admin gateway. BYOK mode accepts your own model.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="card p-6 space-y-4">
        <h2 className="text-lg font-semibold text-slate-100">Fixture Traces (read-only)</h2>
        <p className="text-xs text-slate-500">
          Pre-recorded runs from L19 experiments. No auth required.
        </p>

        {traces.length > 1 && (
          <div className="flex gap-2 overflow-x-auto pb-2">
            {traces.map((t, i) => (
              <button
                key={i}
                onClick={() => setSelectedTrace(i)}
                className={`chip px-3 py-1 text-xs whitespace-nowrap ${
                  selectedTrace === i
                    ? "border-indigo-600/60 text-indigo-300"
                    : "hover:border-indigo-600/60"
                }`}
              >
                {t.label || `Trace ${i + 1}`}
              </button>
            ))}
          </div>
        )}
      </div>

      {traces[selectedTrace] ? <SteerTraceViz trace={traces[selectedTrace]} /> : null}
    </div>
  );
}
