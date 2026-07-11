"use client";

import { useEffect, useState } from "react";

// Renders ONLY the real numbers from public/data/moat.json (derived from
// gates/gate_L26_moat_proof.json by scripts/tools/export_moat_data.py). No invented metrics.
interface Defense {
  name: string;
  asr: number;
  over_refusal: number;
  note?: string;
  gate?: string;
  moat?: boolean;
}
interface MoatData {
  model: string;
  headline: string;
  defenses: Defense[];
  projection_separation: { benign_range: number[]; attack_range: number[]; note: string };
  caveats: string[];
  source: string;
}

export default function MoatProof() {
  const [d, setD] = useState<MoatData | null>(null);
  useEffect(() => {
    fetch("/data/moat.json")
      .then((r) => (r.ok ? r.json() : null))
      .then(setD)
      .catch(() => setD(null));
  }, []);

  if (!d) {
    return (
      <div className="card p-6 text-sm text-slate-400">
        Moat proof data not found. It is generated from <code>gates/gate_L26_moat_proof.json</code> by{" "}
        <code>scripts/tools/export_moat_data.py</code>.
      </div>
    );
  }

  const pct = (x: number) => `${Math.round(x * 100)}%`;

  return (
    <div className="space-y-6">
      <div className="card p-6 space-y-2">
        <h3 className="text-lg font-semibold text-gradient">The server-side moat, proven</h3>
        <p className="text-sm text-slate-300">{d.headline}</p>
        <p className="text-xs text-slate-500">
          Model: <span className="font-mono">{d.model}</span> · real jailbreak battery ·{" "}
          <span className="text-slate-400">{d.source}</span>
        </p>
      </div>

      <div className="card p-6 overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-slate-400 border-b border-night-600">
              <th className="py-2 pr-4">Defense</th>
              <th className="py-2 px-3">Attack ASR</th>
              <th className="py-2 px-3">Benign over-refusal</th>
              <th className="py-2 px-3">Gate</th>
            </tr>
          </thead>
          <tbody>
            {d.defenses.map((x) => (
              <tr key={x.name} className={`border-b border-night-700/50 ${x.moat ? "bg-indigo-950/40" : ""}`}>
                <td className="py-2 pr-4 font-medium text-slate-200">
                  {x.name}
                  {x.moat && (
                    <span className="ml-2 text-[10px] uppercase tracking-wide text-indigo-300">moat</span>
                  )}
                  {x.note && <div className="text-xs text-slate-500">{x.note}</div>}
                </td>
                <td className="py-2 px-3 font-mono text-slate-300">{pct(x.asr)}</td>
                <td
                  className={`py-2 px-3 font-mono ${
                    x.over_refusal === 0
                      ? "text-teal-400"
                      : x.over_refusal >= 0.9
                      ? "text-red-400"
                      : "text-amber-400"
                  }`}
                >
                  {pct(x.over_refusal)}
                </td>
                <td className="py-2 px-3 text-xs text-slate-500 font-mono">{x.gate || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="mt-3 text-xs text-slate-400">
          Brute-force hardening cuts jailbreaks as well as the moat but refuses <b>all</b> benign traffic.
          The recognition-gated defense achieves the <b>same</b> attack reduction at <b>zero</b> benign cost.
        </p>
      </div>

      <div className="card p-6 space-y-3">
        <h4 className="font-semibold text-slate-200">Why wrapping can’t evade it — activation-level detection</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div className="rounded-lg border border-teal-700/40 bg-teal-950/20 p-3">
            <div className="text-xs text-slate-400">Benign inputs project to</div>
            <div className="font-mono text-teal-300">[{d.projection_separation.benign_range.join(", ")}]</div>
          </div>
          <div className="rounded-lg border border-red-700/40 bg-red-950/20 p-3">
            <div className="text-xs text-slate-400">Attack inputs (incl. wrapped) project to</div>
            <div className="font-mono text-red-300">[{d.projection_separation.attack_range.join(", ")}]</div>
          </div>
        </div>
        <p className="text-xs text-slate-400">{d.projection_separation.note}</p>
      </div>

      <div className="card p-4 border border-amber-700/40 bg-amber-950/10">
        <div className="text-xs font-semibold text-amber-300 mb-1">Honest caveats</div>
        <ul className="text-xs text-slate-400 list-disc pl-5 space-y-0.5">
          {d.caveats.map((c) => (
            <li key={c}>{c}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
