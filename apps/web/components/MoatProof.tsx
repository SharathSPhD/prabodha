"use client";

/**
 * MoatProof — Display the recognition-gated jailbreak defense moat.
 *
 * Concept: darśana (direct view) — show real jailbreak battery results + activation projection.
 * Source: gates/gate_L26_moat_proof.json
 * Primitive: render 3-defense table (none, system_prompt, recognition_gated) + projection chart
 *
 * Visualizes:
 * - Single-turn attack ASR comparison across 3 defenses
 * - Benign false refusal rates (over_refusal)
 * - 2D activation projection: benign vs attack regions
 * - Wrapping resilience (whether jailbreak wrapping evades the defense)
 */

import React, { useEffect, useState } from "react";
import { AlertCircle, CheckCircle, BarChart3 } from "lucide-react";

interface DefenseResult {
  defense: string;
  asr: number;
  refusal_rate: number;
  over_refusal_harmless: number;
  attack_count: number;
  mean_coherence: number;
  interpretation: string;
  attacks_blocked?: number;
  benign_allowed?: number;
}

interface ProjectionAnalysis {
  description: string;
  benign_region: {
    mean_projection: [number, number];
    bounds: [[number, number], [number, number]];
    std_dev: number;
    sample_count: number;
  };
  attack_region: {
    mean_projection: [number, number];
    bounds: [[number, number], [number, number]];
    std_dev: number;
    sample_count: number;
  };
  separation_margin: number;
  interpretation: string;
}

interface MoatData {
  headline: string;
  operating_point: string;
  model: string;
  results: {
    single_turn_attacks: DefenseResult[];
    projection_analysis: ProjectionAnalysis;
    jailbreak_wrapping_resilience: Record<string, any>;
  };
  honest_negatives: string[];
  product_implication: string;
}

export function MoatProof() {
  const [moatData, setMoatData] = useState<MoatData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadMoatData() {
      try {
        const res = await fetch("/data/moat.json");
        if (!res.ok) throw new Error(`Failed to load moat data: ${res.status}`);
        const data = await res.json();
        setMoatData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    }
    loadMoatData();
  }, []);

  if (loading) {
    return (
      <div className="rounded-lg border border-night-600 bg-night-800 p-6">
        <p className="text-slate-400">Loading moat proof data...</p>
      </div>
    );
  }

  if (error || !moatData) {
    return (
      <div className="rounded-lg border border-red-500/30 bg-red-950/20 p-6">
        <div className="flex gap-3">
          <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
          <p className="text-red-200 text-sm">{error || "Failed to load moat data"}</p>
        </div>
      </div>
    );
  }

  const results = moatData.results.single_turn_attacks;
  const projection = moatData.results.projection_analysis;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="rounded-lg border border-indigo-500/30 bg-gradient-to-r from-indigo-950/40 to-night-800 p-6">
        <div className="flex gap-3 items-start">
          <CheckCircle className="w-5 h-5 text-indigo-400 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-lg font-serif font-bold text-indigo-200 mb-1">
              {moatData.headline}
            </h3>
            <p className="text-sm text-slate-300 mb-3">
              {moatData.operating_point}
            </p>
            <p className="text-xs text-slate-400">
              Model: <span className="font-mono text-indigo-300">{moatData.model}</span>
            </p>
          </div>
        </div>
      </div>

      {/* Defense Comparison Table */}
      <div className="rounded-lg border border-night-600 bg-night-800/50 p-6 overflow-x-auto">
        <h4 className="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2">
          <BarChart3 className="w-4 h-4" />
          Single-Turn Attack Results
        </h4>

        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-night-600">
              <th className="text-left py-2 px-3 text-slate-400 font-semibold">Defense</th>
              <th className="text-center py-2 px-3 text-slate-400 font-semibold">
                ASR
                <div className="text-xs font-normal text-slate-500">Attack Success</div>
              </th>
              <th className="text-center py-2 px-3 text-slate-400 font-semibold">
                Over-Refusal
                <div className="text-xs font-normal text-slate-500">False Refusals</div>
              </th>
              <th className="text-center py-2 px-3 text-slate-400 font-semibold">
                Attacks Tested
              </th>
              <th className="text-left py-2 px-3 text-slate-400 font-semibold">
                Interpretation
              </th>
            </tr>
          </thead>
          <tbody>
            {results.map((result, idx) => {
              const isRecognitionGated = result.defense === "recognition_gated";
              const bgClass = isRecognitionGated ? "bg-indigo-950/30" : "";
              const asrColor = result.asr <= 0.25 ? "text-green-300" : "text-yellow-300";
              const overRefusalColor =
                result.over_refusal_harmless === 0 ? "text-green-300" : "text-red-300";

              return (
                <tr key={idx} className={`border-b border-night-600/50 ${bgClass}`}>
                  <td className="py-3 px-3 text-slate-200 font-mono">
                    {result.defense}
                    {isRecognitionGated && (
                      <span className="ml-2 text-xs bg-indigo-600/40 text-indigo-200 px-2 py-1 rounded">
                        Premium
                      </span>
                    )}
                  </td>
                  <td className={`text-center py-3 px-3 font-bold ${asrColor}`}>
                    {(result.asr * 100).toFixed(0)}%
                  </td>
                  <td className={`text-center py-3 px-3 font-bold ${overRefusalColor}`}>
                    {(result.over_refusal_harmless * 100).toFixed(0)}%
                  </td>
                  <td className="text-center py-3 px-3 text-slate-300">
                    {result.attacks_blocked ?? result.attack_count}/{result.attack_count}
                  </td>
                  <td className="py-3 px-3 text-slate-400 text-xs max-w-xs">
                    {result.interpretation}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        <p className="text-xs text-slate-500 mt-4">
          <strong>Key:</strong> ASR = Attack Success Rate (lower is better);
          Over-Refusal = False refusals on benign prompts (lower is better).
          Recognition-gated achieves the best tradeoff: detects jailbreaks while preserving benign queries.
        </p>
      </div>

      {/* Projection Gap */}
      <div className="rounded-lg border border-night-600 bg-night-800/50 p-6">
        <h4 className="text-sm font-bold text-slate-200 mb-4">
          Activation Projection Gap (Benign vs Attack)
        </h4>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="rounded bg-green-950/30 border border-green-600/30 p-4">
            <p className="text-xs text-green-400 font-semibold mb-2">Benign Prompts</p>
            <p className="text-sm font-mono text-green-200 mb-1">
              [{projection.benign_region.mean_projection[0].toFixed(1)},
              {projection.benign_region.mean_projection[1].toFixed(1)}]
            </p>
            <p className="text-xs text-green-400">
              n={projection.benign_region.sample_count}, σ={projection.benign_region.std_dev.toFixed(1)}
            </p>
          </div>

          <div className="rounded bg-red-950/30 border border-red-600/30 p-4">
            <p className="text-xs text-red-400 font-semibold mb-2">Attack Prompts</p>
            <p className="text-sm font-mono text-red-200 mb-1">
              [{projection.attack_region.mean_projection[0].toFixed(1)},
              {projection.attack_region.mean_projection[1].toFixed(1)}]
            </p>
            <p className="text-xs text-red-400">
              n={projection.attack_region.sample_count}, σ={projection.attack_region.std_dev.toFixed(1)}
            </p>
          </div>
        </div>

        <div className="rounded bg-indigo-950/20 border border-indigo-600/30 p-4">
          <p className="text-sm text-indigo-200 mb-2">
            <strong>Separation Margin:</strong> <span className="font-mono">{projection.separation_margin.toFixed(1)}σ</span>
          </p>
          <p className="text-xs text-slate-300">
            {projection.interpretation}
          </p>
        </div>
      </div>

      {/* Wrapping Resilience */}
      <div className="rounded-lg border border-night-600 bg-night-800/50 p-6">
        <h4 className="text-sm font-bold text-slate-200 mb-4">Jailbreak Wrapping Resilience</h4>

        <div className="space-y-3">
          {Object.entries(moatData.results.jailbreak_wrapping_resilience).map(
            ([key, value]: [string, any]) => {
              if (key === "conclusion") return null;

              const isWrappingName = key.includes("attack") || key.includes("encoded") || key.includes("roleplay");
              if (!isWrappingName) return null;

              const succeeded = value.wrapped_success === false;
              const statusBg = succeeded ? "bg-green-950/30 border-green-600/30" : "bg-red-950/30 border-red-600/30";
              const statusColor = succeeded ? "text-green-300" : "text-red-300";
              const statusLabel = succeeded ? "✓ Blocked" : "✗ Evaded";

              return (
                <div key={key} className={`rounded border p-3 ${statusBg}`}>
                  <div className="flex items-start gap-3">
                    <div className={`text-xs font-bold ${statusColor} mt-0.5`}>{statusLabel}</div>
                    <div className="flex-1">
                      <p className="text-sm text-slate-200 capitalize font-mono mb-1">
                        {key.replace(/_/g, " ")}
                      </p>
                      <p className="text-xs text-slate-400">{value.interpretation}</p>
                    </div>
                  </div>
                </div>
              );
            }
          )}
        </div>

        {moatData.results.jailbreak_wrapping_resilience.conclusion && (
          <p className="text-xs text-slate-300 mt-4 border-t border-night-600 pt-4">
            <strong>Conclusion:</strong> {moatData.results.jailbreak_wrapping_resilience.conclusion}
          </p>
        )}
      </div>

      {/* Honest Negatives / Caveats */}
      <div className="rounded-lg border border-amber-600/30 bg-amber-950/20 p-6">
        <h4 className="text-sm font-bold text-amber-300 mb-3">Honest Negatives (Caveats)</h4>
        <ul className="space-y-2">
          {moatData.honest_negatives.map((caveat, idx) => (
            <li key={idx} className="text-xs text-amber-200 flex gap-2">
              <span className="text-amber-400 flex-shrink-0">•</span>
              <span>{caveat}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Product Implication */}
      <div className="rounded-lg border border-indigo-600/30 bg-indigo-950/20 p-6">
        <h4 className="text-sm font-bold text-indigo-300 mb-2">Product Implication</h4>
        <p className="text-sm text-slate-300">{moatData.product_implication}</p>
      </div>
    </div>
  );
}

export default MoatProof;
