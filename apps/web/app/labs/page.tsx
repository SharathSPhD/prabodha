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

type LabTab = "jailbreak" | "alignment";

export default function LabsPage() {
  const [activeTab, setActiveTab] = useState<LabTab>("jailbreak");

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-4xl px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Steering Labs
          </h1>
          <p className="text-gray-600 text-lg">
            Interactive evaluation of model steering effects via real gateway
            results and behavioral scoring.
          </p>
        </div>

        {/* Tab navigation */}
        <div className="mb-6 flex space-x-2 border-b border-gray-200">
          <button
            onClick={() => setActiveTab("jailbreak")}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === "jailbreak"
                ? "border-b-2 border-blue-600 text-blue-600"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            Refusal Steering
          </button>
          <button
            onClick={() => setActiveTab("alignment")}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === "alignment"
                ? "border-b-2 border-blue-600 text-blue-600"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            Truthfulness Steering
          </button>
        </div>

        {/* Tab content */}
        <div className="rounded-lg bg-white shadow-sm p-6">
          {activeTab === "jailbreak" && <JailbreakLab />}
          {activeTab === "alignment" && <AlignmentLab />}
        </div>

        {/* Information footer */}
        <div className="mt-8 rounded-lg border border-blue-200 bg-blue-50 p-6">
          <h3 className="font-semibold text-blue-900 mb-2">About these labs</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>
              • <strong>Refusal Steering:</strong> Test steering via
              contrastive exemplars to increase model refusal on harmful
              requests. Real attack-success-rate scoring via heuristic refusal
              detection.
            </li>
            <li>
              • <strong>Truthfulness Steering:</strong> Test steering toward
              truthful responses on factual questions. Real truthfulness scoring
              via string overlap heuristic.
            </li>
            <li>
              • <strong>Behavioral metrics:</strong> All scoring uses Python
              prabodha.eval.behavioral ported to TypeScript. Proxy metrics
              designed for screening; semantic evaluation (LLM) stronger for
              production.
            </li>
            <li>
              • <strong>Gateway connectivity:</strong> Labs require the
              prabodha steer gateway. If offline, you'll see a clear "gateway
              offline" message.
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
