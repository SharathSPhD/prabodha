"use client";

import { useEffect, useMemo, useState } from "react";

// The graded mechanism library, rendered from public/data/moat.json (real REGISTRY
// entries from prabodha.steering.mechanisms). Per-mechanism metrics appear ONLY where a
// real characterization gate measured them; otherwise no numbers are shown (no invention).
interface Mechanism {
  key: string;
  name: string;
  space: "prompt" | "activation";
  weights: "both" | "open";
  tier: number;
  summary: string;
  measured_profile: {
    model: string;
    asr_reduction: number | null;
    over_refusal_cost: number | null;
    coherence: number | null;
  } | null;
}

export default function MechanismSelector() {
  const [mechs, setMechs] = useState<Mechanism[]>([]);
  const [weights, setWeights] = useState<"all" | "open" | "closed">("all");

  useEffect(() => {
    fetch("/data/moat.json")
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => setMechs(d?.mechanisms ?? []))
      .catch(() => setMechs([]));
  }, []);

  const shown = useMemo(() => {
    if (weights === "closed") return mechs.filter((m) => m.weights === "both"); // prompt-space works on closed
    if (weights === "open") return mechs;
    return mechs;
  }, [mechs, weights]);

  if (!mechs.length) {
    return <div className="card p-6 text-sm text-slate-400">Mechanism library not loaded.</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3 flex-wrap">
        <span className="text-sm text-slate-400">Which model can you touch?</span>
        {(["all", "open", "closed"] as const).map((w) => (
          <button
            key={w}
            onClick={() => setWeights(w)}
            className={`text-xs px-3 py-1 rounded-full border transition ${
              weights === w ? "border-indigo-500 bg-indigo-600/30 text-white" : "border-night-600 text-slate-400"
            }`}
          >
            {w === "all" ? "All" : w === "open" ? "Open weights (self-host)" : "Closed / BYOK"}
          </button>
        ))}
        {weights === "closed" && (
          <span className="text-xs text-slate-500">
            Only prompt-space mechanisms apply to closed models — activation tiers need the weights.
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {shown
          .sort((a, b) => a.tier - b.tier)
          .map((m) => {
            const isMoat = m.key === "act_recognition_gated";
            return (
              <div
                key={m.key}
                className={`card p-4 space-y-2 ${isMoat ? "border-l-2 border-indigo-500" : ""}`}
              >
                <div className="flex items-center justify-between gap-2">
                  <div className="font-medium text-slate-200 text-sm">{m.name}</div>
                  <div className="flex gap-1">
                    <Badge>{m.space}</Badge>
                    <Badge>{m.weights === "both" ? "open+closed" : "open"}</Badge>
                    <Badge>tier {m.tier}</Badge>
                    {isMoat && <Badge tone="indigo">the moat</Badge>}
                  </div>
                </div>
                <p className="text-xs text-slate-400">{m.summary}</p>
                {m.measured_profile ? (
                  <div className="text-[11px] text-slate-500 font-mono border-t border-night-700/50 pt-2">
                    measured on {m.measured_profile.model}:{" "}
                    {m.measured_profile.asr_reduction != null && `ASR −${m.measured_profile.asr_reduction} `}
                    {m.measured_profile.over_refusal_cost != null &&
                      `· over-refusal ${m.measured_profile.over_refusal_cost} `}
                    {m.measured_profile.coherence != null && `· coherence ${m.measured_profile.coherence}`}
                  </div>
                ) : (
                  <div className="text-[11px] text-slate-600 italic border-t border-night-700/50 pt-2">
                    no per-model measurement yet (run a characterization to populate)
                  </div>
                )}
              </div>
            );
          })}
      </div>
    </div>
  );
}

function Badge({ children, tone = "slate" }: { children: React.ReactNode; tone?: "slate" | "indigo" }) {
  return (
    <span
      className={`text-[10px] px-1.5 py-0.5 rounded ${
        tone === "indigo" ? "bg-indigo-600/30 text-indigo-200" : "bg-night-700 text-slate-400"
      }`}
    >
      {children}
    </span>
  );
}
