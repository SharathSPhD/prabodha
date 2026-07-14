/**
 * Labs page — interactive steering evaluation interface.
 *
 * Concept: sākṣī-śakti (witness power) — make visible the effects of steering
 * through interactive labs that use real gateway results and real behavioral scoring.
 */
"use client";

import React, { useState } from "react";
import { JailbreakLab } from "@/components/labs/JailbreakLab";
import { AlignmentLab } from "@/components/labs/AlignmentLab";
import { SiteNav } from "@/components/SiteNav";

type LabTab = "jailbreak" | "alignment";

export default function LabsPage() {
  const [activeTab, setActiveTab] = useState<LabTab>("jailbreak");

  return (
    <main className="min-h-screen bg-gradient-to-b from-night-950 to-night-900">
      <SiteNav />
      <div className="mx-auto max-w-4xl px-6 py-12">
        <div className="mb-8">
          <h1 className="mb-2 font-serif text-4xl font-bold text-gradient">
            Steering Labs
          </h1>
          <p className="text-lg text-slate-400">
            Interactive evaluation of model steering effects via real gateway
            results and behavioral scoring.
          </p>
        </div>

        {/* Tab navigation */}
        <div className="mb-6 flex gap-2 border-b border-night-600">
          <button
            onClick={() => setActiveTab("jailbreak")}
            className={`-mb-px border-b-2 px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === "jailbreak"
                ? "border-indigo-400 text-indigo-300"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            Refusal Steering
          </button>
          <button
            onClick={() => setActiveTab("alignment")}
            className={`-mb-px border-b-2 px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === "alignment"
                ? "border-indigo-400 text-indigo-300"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            Truthfulness Steering
          </button>
        </div>

        {/* Tab content */}
        <div className="card p-6">
          {activeTab === "jailbreak" && <JailbreakLab />}
          {activeTab === "alignment" && <AlignmentLab />}
        </div>

        {/* Information footer */}
        <div className="mt-8 rounded-xl border border-indigo-500/25 bg-indigo-500/5 p-6">
          <h3 className="mb-2 font-semibold text-indigo-200">About these labs</h3>
          <ul className="space-y-1 text-sm text-slate-400">
            <li>
              • <strong className="text-slate-200">Refusal Steering:</strong> Test steering via
              contrastive exemplars to increase model refusal on harmful
              requests. Real attack-success-rate scoring via heuristic refusal
              detection.
            </li>
            <li>
              • <strong className="text-slate-200">Truthfulness Steering:</strong> Test steering toward
              truthful responses on factual questions. Real truthfulness scoring
              via string overlap heuristic.
            </li>
            <li>
              • <strong className="text-slate-200">Behavioral metrics:</strong> All scoring uses Python
              prabodha.eval.behavioral ported to TypeScript. Proxy metrics
              designed for screening; semantic evaluation (LLM) stronger for
              production.
            </li>
            <li>
              • <strong className="text-slate-200">Gateway connectivity:</strong> Labs require the
              prabodha steer gateway. If offline, you'll see a clear "gateway
              offline" message.
            </li>
          </ul>
        </div>
      </div>
    </main>
  );
}
