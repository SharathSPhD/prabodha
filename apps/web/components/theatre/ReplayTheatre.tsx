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
        const res = await fetch("/data/replays/fixture-qwen3.json");
        if (!res.ok) throw new Error("Failed to load fixture traces");
        const data = await res.json();
        setTraces(Array.isArray(data) ? data : [data]);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    }

    loadTraces();
  }, []);

  if (loading) return <p className="text-sm text-slate-500">Loading traces...</p>;
  if (error) return <p className="text-sm text-red-300">{error}</p>;
  if (traces.length === 0) return <p className="text-sm text-slate-500">No traces available yet. Replays pending first export.</p>;

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
