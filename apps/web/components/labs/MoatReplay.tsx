"use client";

/**
 * Moat Replay — offline replay of REAL gemma-2-2b jailbreak→harden results.
 *
 * Concept: pratyabhijñā (recognition) — recognize the harmful signature, then respond.
 * Source: scripts/experiments/l26_moat_replay.py → public/data/moat_replay.json
 *         (every response below is a real captured generation; gate_L26_moat_proof.json).
 *
 * This needs NO live compute: it replays transcripts captured on GB10. The three arms are
 * none (baseline), unconditional (brute-force hardening), and recognition_gated (the moat).
 */
import React, { useEffect, useState } from "react";

type Arm = "none" | "unconditional" | "recognition_gated";

interface Row {
  id: string;
  kind: "attack" | "benign";
  prompt: string;
  projection: number;
  recognized_as_attack: boolean;
  responses: Record<Arm, string>;
  refused: Record<Arm, boolean>;
}

interface Replay {
  model: string;
  read_layer: number;
  tau: number;
  projection_separation: { benign_range: number[]; attack_range: number[] };
  arms: Record<Arm, { attack_asr: number; benign_over_refusal: number }>;
  attacks: Row[];
  benign: Row[];
  caveats: string[];
}

const ARM_LABEL: Record<Arm, string> = {
  none: "Baseline (no defense)",
  unconditional: "Brute-force hardening",
  recognition_gated: "Recognition-gated (the moat)",
};

interface ModelRow {
  model: string;
  read_layer: number;
  tau: number;
  clean_projection_gap: boolean;
  benign_range: number[];
  attack_range: number[];
  arms: Record<Arm, { attack_asr: number; benign_over_refusal: number }>;
  moat_works: boolean;
}
interface Models {
  finding: string;
  models: ModelRow[];
  caveats: string[];
}

export default function MoatReplay() {
  const [d, setD] = useState<Replay | null>(null);
  const [models, setModels] = useState<Models | null>(null);
  const [view, setView] = useState<"attack" | "benign">("attack");
  const [sel, setSel] = useState(0);

  useEffect(() => {
    fetch("/data/moat_replay.json")
      .then((r) => (r.ok ? r.json() : null))
      .then(setD)
      .catch(() => setD(null));
    fetch("/data/moat_models.json")
      .then((r) => (r.ok ? r.json() : null))
      .then(setModels)
      .catch(() => setModels(null));
  }, []);

  if (!d) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-6 text-sm text-gray-500">
        Replay data not found. It is captured by{" "}
        <code>scripts/experiments/l26_moat_replay.py</code> on GB10 and written to{" "}
        <code>public/data/moat_replay.json</code>. Every transcript is a real model generation — nothing is
        shown here until that real capture exists.
      </div>
    );
  }

  const rows = view === "attack" ? d.attacks : d.benign;
  const row = rows[Math.min(sel, rows.length - 1)];
  const pct = (x: number) => `${Math.round(x * 100)}%`;

  return (
    <div className="space-y-6">
      <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        <h2 className="text-2xl font-bold mb-1">Recognition-gated moat — replay of real results</h2>
        <p className="text-gray-600 text-sm">
          Real jailbreak→harden transcripts captured on <code>{d.model}</code> (read-layer {d.read_layer},
          gate threshold τ={d.tau}). No live compute — this replays what actually happened. The moat
          reinforces refusal <em>only</em> when the input's activation-level harmful signature crosses τ,
          so benign traffic is untouched and wrapping can't disguise the attack.
        </p>

        {/* Arm summary */}
        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="py-2 pr-4">Defense</th>
                <th className="py-2 px-3">Attack ASR</th>
                <th className="py-2 px-3">Benign over-refusal</th>
              </tr>
            </thead>
            <tbody>
              {(Object.keys(d.arms) as Arm[]).map((a) => (
                <tr key={a} className={a === "recognition_gated" ? "font-medium bg-indigo-50" : ""}>
                  <td className="py-2 pr-4">{ARM_LABEL[a]}</td>
                  <td className="py-2 px-3 font-mono">{pct(d.arms[a].attack_asr)}</td>
                  <td
                    className={`py-2 px-3 font-mono ${
                      d.arms[a].benign_over_refusal === 0
                        ? "text-teal-600"
                        : d.arms[a].benign_over_refusal >= 0.9
                        ? "text-red-600"
                        : "text-amber-600"
                    }`}
                  >
                    {pct(d.arms[a].benign_over_refusal)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* view toggle */}
      <div className="flex gap-2">
        {(["attack", "benign"] as const).map((v) => (
          <button
            key={v}
            onClick={() => {
              setView(v);
              setSel(0);
            }}
            className={`text-xs px-3 py-1.5 rounded-full border ${
              view === v ? "border-indigo-500 bg-indigo-600 text-white" : "border-gray-300 text-gray-600"
            }`}
          >
            {v === "attack" ? `Attacks (${d.attacks.length})` : `Benign (${d.benign.length})`}
          </button>
        ))}
        <span className="text-xs text-gray-500 self-center">
          {view === "attack"
            ? "wrapped jailbreaks — the moat should catch these"
            : "ordinary requests — the moat should leave these alone"}
        </span>
      </div>

      {/* row selector */}
      <div className="flex flex-wrap gap-1">
        {rows.map((r, i) => (
          <button
            key={r.id}
            onClick={() => setSel(i)}
            className={`text-xs px-2 py-1 rounded border ${
              i === sel ? "border-indigo-500 bg-indigo-100" : "border-gray-200"
            }`}
            title={r.id}
          >
            {i + 1}
          </button>
        ))}
      </div>

      {/* transcript */}
      <div className="rounded-lg border border-gray-200 bg-white p-4 space-y-4">
        <div>
          <p className="font-semibold text-gray-900 mb-1">Prompt <span className="text-xs text-gray-400">({row.id})</span></p>
          <p className="text-sm text-gray-700">{row.prompt}</p>
          <div className="mt-2 flex items-center gap-3 text-xs">
            <span className="font-mono">
              harmful projection = {row.projection}{" "}
              <span className="text-gray-400">(τ={d.tau})</span>
            </span>
            <span
              className={`px-2 py-0.5 rounded ${
                row.recognized_as_attack ? "bg-red-100 text-red-800" : "bg-teal-100 text-teal-800"
              }`}
            >
              {row.recognized_as_attack ? "recognized as attack → defense fires" : "not recognized → left untouched"}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {(Object.keys(ARM_LABEL) as Arm[]).map((a) => (
            <div
              key={a}
              className={`rounded border p-3 ${a === "recognition_gated" ? "border-indigo-400" : "border-gray-200"}`}
            >
              <div className="flex items-center justify-between mb-1">
                <p className="text-xs font-semibold text-gray-700">{ARM_LABEL[a]}</p>
                <span
                  className={`text-[10px] px-1.5 py-0.5 rounded ${
                    row.refused[a] ? "bg-teal-100 text-teal-800" : "bg-red-100 text-red-800"
                  }`}
                >
                  {row.refused[a] ? "Refused" : "Complied"}
                </span>
              </div>
              <p className="text-xs text-gray-600 whitespace-pre-wrap">{row.responses[a] || "—"}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Generality — model-dependent, honest */}
      {models && models.models.length > 1 && (
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <h3 className="font-semibold text-gray-900 mb-1">Does it generalize? (honest: model-dependent)</h3>
          <p className="text-xs text-gray-600 mb-3">{models.finding}</p>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b">
                  <th className="py-1 pr-3">Model</th>
                  <th className="py-1 px-2">Clean gap?</th>
                  <th className="py-1 px-2">Benign proj</th>
                  <th className="py-1 px-2">Attack proj</th>
                  <th className="py-1 px-2">Gated ASR</th>
                  <th className="py-1 px-2">Gated over-refusal</th>
                  <th className="py-1 px-2">Moat works?</th>
                </tr>
              </thead>
              <tbody>
                {models.models.map((m) => (
                  <tr key={m.model} className="border-b border-gray-100">
                    <td className="py-1 pr-3 font-mono text-xs">{m.model}</td>
                    <td className="py-1 px-2">{m.clean_projection_gap ? "yes" : "no (overlap)"}</td>
                    <td className="py-1 px-2 font-mono text-xs">[{m.benign_range.join(", ")}]</td>
                    <td className="py-1 px-2 font-mono text-xs">[{m.attack_range.join(", ")}]</td>
                    <td className="py-1 px-2 font-mono">{pct(m.arms.recognition_gated.attack_asr)}</td>
                    <td className="py-1 px-2 font-mono">{pct(m.arms.recognition_gated.benign_over_refusal)}</td>
                    <td className={`py-1 px-2 font-semibold ${m.moat_works ? "text-teal-600" : "text-red-600"}`}>
                      {m.moat_works ? "✓" : "✗"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            The moat needs a clean activation-level projection gap. Where the harmful signature isn't linearly
            separable at the read layer, the gate can't discriminate — so we report it, we don't hide it. Gate:{" "}
            <code>gates/gate_L26_moat_qwen.json</code>.
          </p>
        </div>
      )}

      <div className="rounded-lg border border-amber-200 bg-amber-50 p-4">
        <p className="text-xs font-semibold text-amber-800 mb-1">Honest caveats</p>
        <ul className="text-xs text-amber-800 list-disc pl-5 space-y-0.5">
          {d.caveats.map((c) => (
            <li key={c}>{c}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
