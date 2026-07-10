"use client";

import { useEffect, useState } from "react";
import SteerTraceViz from "@/components/theatre/SteerTraceViz";

interface SteerTrace {
  tokens: string[];
  entropies: number[];
  writes: Array<{ position: number; amplitude: number }>;
  readback: { verdict: "accept" | "reject"; confidence: number };
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
        // 404 is expected when no data has been exported yet (empty-state)
        if (res.status === 404) {
          setTraces([]);
          setLoading(false);
          return;
        }
        if (!res.ok) throw new Error("Failed to load traces");
        const data = await res.json();
        setTraces(Array.isArray(data) ? data : [data]);
      } catch (err) {
        // Network errors show as error, 404 shows as empty-state
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    }

    loadTraces();
  }, []);

  if (loading) return <p className="text-sm text-slate-500">Loading traces...</p>;
  if (error) return <p className="text-sm text-red-300">{error}</p>;
  if (traces.length === 0) {
    return (
      <div className="card p-6">
        <p className="text-sm text-slate-500">
          No replays available yet. Run the export tool to populate trace data:
        </p>
        <code className="block text-xs text-slate-400 mt-2 bg-night-900 p-2 rounded">
          python scripts/tools/export_app_data.py --repo-root . --out-app apps/web/public/data
        </code>
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
            {traces.map((_, i) => (
              <button
                key={i}
                onClick={() => setSelectedTrace(i)}
                className={`chip px-3 py-1 text-xs ${
                  selectedTrace === i
                    ? "border-indigo-600/60 text-indigo-300"
                    : "hover:border-indigo-600/60"
                }`}
              >
                Trace {i + 1}
              </button>
            ))}
          </div>
        )}
      </div>

      <SteerTraceViz trace={traces[selectedTrace]} />
    </div>
  );
}
