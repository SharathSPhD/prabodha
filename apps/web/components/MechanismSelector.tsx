"use client";

/**
 * MechanismSelector — Interactive mechanism library filter and explorer.
 *
 * Concept: samūha (collection) — show the 7 graded steering mechanisms with
 * filtering, tradeoffs, and recommendations.
 *
 * Source: gates/gate_L26_moat_proof.json mechanism_registry
 * Primitive: render mechanism cards with tier badges, filtering, recommendation engine
 *
 * Filters by:
 * - Tier: open, closed, premium
 * - Space: prompt, activation, mixed
 * - Weights: open, closed, mixed
 */

import React, { useState, useMemo, useEffect } from "react";
import { Filter, Zap, Lock, Globe } from "lucide-react";

interface Mechanism {
  id: string;
  name: string;
  tier: string;
  space: string;
  weights: string;
  tradeoff: string;
  asr: number;
  over_refusal: number;
  note?: string;
}

interface MoatData {
  mechanisms: Mechanism[];
}

type TierValue = "open" | "closed" | "premium";
type SpaceValue = "prompt" | "activation" | "mixed";
type WeightsValue = "open" | "closed" | "mixed";

export function MechanismSelector() {
  const [moatData, setMoatData] = useState<MoatData | null>(null);
  const [loading, setLoading] = useState(true);

  const [tierFilter, setTierFilter] = useState<TierValue | "all">("all");
  const [weightsFilter, setWeightsFilter] = useState<WeightsValue | "all">("all");
  const [spaceFilter, setSpaceFilter] = useState<SpaceValue | "all">("all");

  useEffect(() => {
    async function loadMoatData() {
      try {
        const res = await fetch("/data/moat.json");
        if (!res.ok) throw new Error(`Failed to load moat data`);
        const data = await res.json();
        setMoatData(data);
      } catch (err) {
        console.error("Failed to load moat data:", err);
      } finally {
        setLoading(false);
      }
    }
    loadMoatData();
  }, []);

  const filteredMechanisms = useMemo(() => {
    if (!moatData) return [];

    return moatData.mechanisms.filter((m: Mechanism) => {
      if (tierFilter !== "all" && m.tier !== tierFilter) return false;
      if (weightsFilter !== "all" && m.weights !== weightsFilter) return false;
      if (spaceFilter !== "all" && m.space !== spaceFilter) return false;
      return true;
    });
  }, [moatData, tierFilter, weightsFilter, spaceFilter]);

  const getTierBadge = (tier: string) => {
    const tiers: Record<string, { bg: string; text: string; icon: React.ReactNode }> = {
      open: {
        bg: "bg-green-950/40 border-green-600/40",
        text: "text-green-300",
        icon: <Globe className="w-3 h-3" />,
      },
      closed: {
        bg: "bg-purple-950/40 border-purple-600/40",
        text: "text-purple-300",
        icon: <Lock className="w-3 h-3" />,
      },
      premium: {
        bg: "bg-indigo-950/40 border-indigo-600/40",
        text: "text-indigo-300",
        icon: <Zap className="w-3 h-3" />,
      },
    };

    const style = tiers[tier] || tiers.open;
    return { ...style };
  };

  const getSpaceBadge = (space: string) => {
    const spaces: Record<string, string> = {
      prompt: "Prompt-space",
      activation: "Activation-space",
      mixed: "Hybrid",
    };
    return spaces[space] || space;
  };

  if (loading) {
    return (
      <div className="rounded-lg border border-night-600 bg-night-800 p-6">
        <p className="text-slate-400">Loading mechanisms...</p>
      </div>
    );
  }

  if (!moatData || moatData.mechanisms.length === 0) {
    return (
      <div className="rounded-lg border border-night-600 bg-night-800 p-6">
        <p className="text-slate-400">No mechanisms available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h3 className="text-lg font-serif font-bold text-slate-200 mb-2 flex items-center gap-2">
          <Zap className="w-5 h-5 text-indigo-400" />
          Graded Steering Mechanism Library
        </h3>
        <p className="text-sm text-slate-400">
          {moatData.mechanisms.length} mechanisms across 3 tiers (open/closed/premium) and 2 spaces
          (prompt/activation). Filter by deployment model.
        </p>
      </div>

      {/* Filters */}
      <div className="rounded-lg border border-night-600 bg-night-800/50 p-4">
        <div className="flex items-center gap-2 mb-3">
          <Filter className="w-4 h-4 text-slate-400" />
          <p className="text-sm font-semibold text-slate-300">Filter</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Tier filter */}
          <div>
            <label className="text-xs font-semibold text-slate-400 mb-2 block">Tier</label>
            <div className="flex flex-wrap gap-2">
              {["all", "open", "closed", "premium"].map((t) => (
                <button
                  key={t}
                  onClick={() => setTierFilter(t as TierValue | "all")}
                  className={`text-xs px-3 py-1 rounded border transition ${
                    tierFilter === t
                      ? "bg-indigo-600/40 border-indigo-500 text-indigo-200"
                      : "bg-night-700 border-night-600 text-slate-400 hover:border-night-500"
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          {/* Space filter */}
          <div>
            <label className="text-xs font-semibold text-slate-400 mb-2 block">Space</label>
            <div className="flex flex-wrap gap-2">
              {["all", "prompt", "activation", "mixed"].map((s) => (
                <button
                  key={s}
                  onClick={() => setSpaceFilter(s as SpaceValue | "all")}
                  className={`text-xs px-3 py-1 rounded border transition ${
                    spaceFilter === s
                      ? "bg-indigo-600/40 border-indigo-500 text-indigo-200"
                      : "bg-night-700 border-night-600 text-slate-400 hover:border-night-500"
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          {/* Weights filter */}
          <div>
            <label className="text-xs font-semibold text-slate-400 mb-2 block">Weights</label>
            <div className="flex flex-wrap gap-2">
              {["all", "open", "closed", "mixed"].map((w) => (
                <button
                  key={w}
                  onClick={() => setWeightsFilter(w as WeightsValue | "all")}
                  className={`text-xs px-3 py-1 rounded border transition ${
                    weightsFilter === w
                      ? "bg-indigo-600/40 border-indigo-500 text-indigo-200"
                      : "bg-night-700 border-night-600 text-slate-400 hover:border-night-500"
                  }`}
                >
                  {w}
                </button>
              ))}
            </div>
          </div>
        </div>

        <p className="text-xs text-slate-500 mt-3">
          Showing {filteredMechanisms.length} of {moatData.mechanisms.length} mechanisms
        </p>
      </div>

      {/* Mechanism Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredMechanisms.map((mechanism: Mechanism) => {
          const tierStyle = getTierBadge(mechanism.tier);
          const spaceName = getSpaceBadge(mechanism.space);

          return (
            <div
              key={mechanism.id}
              className="rounded-lg border border-night-600 bg-night-800/50 p-5 hover:border-night-500 transition"
            >
              <div className="flex items-start justify-between mb-3">
                <h4 className="text-sm font-bold text-slate-200 flex-1">{mechanism.name}</h4>
                <div
                  className={`flex items-center gap-1 text-xs px-2 py-1 rounded border ${tierStyle.bg} ${tierStyle.text}`}
                >
                  {tierStyle.icon}
                  <span className="capitalize">{mechanism.tier}</span>
                </div>
              </div>

              <p className="text-xs text-slate-400 mb-3">{mechanism.tradeoff}</p>

              {mechanism.note && (
                <p className="text-xs text-indigo-300 bg-indigo-950/30 rounded px-2 py-1 mb-3">
                  {mechanism.note}
                </p>
              )}

              <div className="grid grid-cols-3 gap-2 mb-3 text-xs">
                <div className="bg-night-700/50 rounded p-2">
                  <p className="text-slate-500 mb-1">Space</p>
                  <p className="text-slate-200 font-mono">{spaceName}</p>
                </div>
                <div className="bg-night-700/50 rounded p-2">
                  <p className="text-slate-500 mb-1">Weights</p>
                  <p className="text-slate-200 font-mono capitalize">{mechanism.weights}</p>
                </div>
                <div className="bg-night-700/50 rounded p-2">
                  <p className="text-slate-500 mb-1">ASR/O-Refusal</p>
                  <p className="text-slate-200 font-mono">
                    {(mechanism.asr * 100).toFixed(0)}% / {(mechanism.over_refusal * 100).toFixed(0)}%
                  </p>
                </div>
              </div>

              <div className="flex gap-2 text-xs">
                <div className="flex-1 bg-slate-950/50 rounded p-2">
                  <p className="text-slate-500 mb-1">ASR (Lower Better)</p>
                  <div className="w-full bg-night-700 rounded-full h-1.5 overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-green-500 to-red-500"
                      style={{ width: `${Math.max(5, Math.min(95, mechanism.asr * 100))}%` }}
                    />
                  </div>
                </div>
                <div className="flex-1 bg-slate-950/50 rounded p-2">
                  <p className="text-slate-500 mb-1">Over-Refusal (Lower Better)</p>
                  <div className="w-full bg-night-700 rounded-full h-1.5 overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-green-500 to-red-500"
                      style={{ width: `${Math.max(5, Math.min(95, mechanism.over_refusal * 100))}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {filteredMechanisms.length === 0 && (
        <div className="rounded-lg border border-night-600 bg-night-800/50 p-6 text-center">
          <p className="text-slate-400 text-sm">No mechanisms match the selected filters.</p>
        </div>
      )}
    </div>
  );
}

export default MechanismSelector;
