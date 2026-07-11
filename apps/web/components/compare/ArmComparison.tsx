"use client";

import { useState } from "react";
import { Play } from "lucide-react";
import type { SteeringArm } from "@/lib/types/steering";

const ARMS: { value: SteeringArm; label: string; description: string }[] = [
  {
    value: "baseline",
    label: "Baseline",
    description: "No steering (control)",
  },
  {
    value: "gated",
    label: "Gated",
    description: "Entropy-gated (sphuraṭṭā moment)",
  },
  {
    value: "continuous",
    label: "Continuous",
    description: "Every token generation step",
  },
  {
    value: "logit-bias",
    label: "Logit Bias",
    description: "Output layer only",
  },
];

interface ArmResult {
  arm: SteeringArm;
  output: string;
  entropy: number;
  effectSize: number;
  tokens: number;
}

export default function ArmComparison() {
  const [prompt, setPrompt] = useState(
    "Explain the benefits and risks of AI in healthcare."
  );
  const [concept, setConcept] = useState("balanced");
  const [alpha, setAlpha] = useState(0.5);
  const [running, setRunning] = useState(false);
  const [results, setResults] = useState<ArmResult[]>([]);

  const handleRun = async () => {
    setRunning(true);
    setResults([]);

    // Simulate running all arms sequentially
    for (const arm of ARMS) {
      await new Promise((resolve) => setTimeout(resolve, 500));

      const baselineLength = 200 + Math.floor(Math.random() * 100);
      const armLength =
        arm.value === "baseline"
          ? baselineLength
          : baselineLength + Math.floor((Math.random() - 0.5) * 50);

      // Calculate effect size (Hedges' g approximation)
      const effectSize =
        Math.abs(armLength - baselineLength) / Math.sqrt(baselineLength);

      setResults((prev) => [
        ...prev,
        {
          arm: arm.value,
          output: `[Sample output for ${arm.label} arm]\n\nThis is a simulated response...`,
          entropy: 4.5 + Math.random() * 2,
          effectSize: arm.value === "baseline" ? 0 : effectSize,
          tokens: armLength,
        },
      ]);
    }

    setRunning(false);
  };

  return (
    <div className="space-y-6">
      {/* Configuration */}
      <div className="card p-6 space-y-6">
        <h2 className="text-lg font-semibold text-slate-100">
          Comparison Setup
        </h2>

        <div className="space-y-2">
          <label className="label">Prompt</label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            disabled={running}
            className="input h-20 resize-none"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="label">Concept</label>
            <input
              type="text"
              value={concept}
              onChange={(e) => setConcept(e.target.value)}
              disabled={running}
              className="input"
            />
          </div>

          <div className="space-y-2">
            <label className="label">Amplitude (α)</label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={alpha}
              onChange={(e) => setAlpha(parseFloat(e.target.value))}
              disabled={running}
              className="w-full"
            />
            <div className="text-xs text-slate-500 font-mono text-center">
              {alpha.toFixed(2)}
            </div>
          </div>
        </div>

        <button
          onClick={handleRun}
          disabled={running || !prompt.trim() || !concept.trim()}
          className={`w-full py-3 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 ${
            running
              ? "bg-slate-700 text-slate-300 cursor-not-allowed"
              : "bg-indigo-600 hover:bg-indigo-700 text-white"
          }`}
        >
          <Play className="w-4 h-4" />
          {running ? "Running comparisons..." : "Run Comparison"}
        </button>
      </div>

      {/* Arm descriptions */}
      {results.length === 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {ARMS.map((arm) => (
            <div key={arm.value} className="card p-4 space-y-2">
              <h3 className="font-semibold text-slate-200">{arm.label}</h3>
              <p className="text-sm text-slate-400">{arm.description}</p>
            </div>
          ))}
        </div>
      )}

      {/* Results */}
      {results.length > 0 && (
        <div className="space-y-6">
          {/* Summary metrics */}
          <div className="card p-6 space-y-4">
            <h3 className="font-semibold text-slate-100">Effect Sizes</h3>

            <div className="space-y-3">
              {results.map((result) => {
                const arm = ARMS.find((a) => a.value === result.arm);
                if (!arm) return null;

                // Interpret effect size
                let effectLabel = "negligible";
                let effectColor = "text-slate-400";
                if (result.effectSize > 0.2 && result.effectSize <= 0.5) {
                  effectLabel = "small";
                  effectColor = "text-yellow-400";
                } else if (result.effectSize > 0.5 && result.effectSize <= 0.8) {
                  effectLabel = "medium";
                  effectColor = "text-orange-400";
                } else if (result.effectSize > 0.8) {
                  effectLabel = "large";
                  effectColor = "text-red-400";
                }

                return (
                  <div
                    key={result.arm}
                    className="flex items-center justify-between p-4 rounded border border-night-600"
                  >
                    <div>
                      <p className="font-semibold text-slate-200">
                        {arm.label}
                      </p>
                      <p className="text-xs text-slate-500">{arm.description}</p>
                    </div>
                    <div className="text-right">
                      <div className="flex items-baseline gap-2">
                        <span className={`text-2xl font-bold ${effectColor}`}>
                          {result.effectSize.toFixed(2)}
                        </span>
                        <span className="text-xs text-slate-500">
                          {" "}{effectLabel}
                        </span>
                      </div>
                      <p className="text-xs text-slate-600 mt-1">
                        {result.tokens} tokens
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="text-xs text-slate-600 pt-2 border-t border-night-600 mt-4 pt-4">
              <p>
                <span className="font-semibold">Hedges' g:</span> Effect size
                standardized for small samples. Baseline arm is the control
                (effect size = 0).
              </p>
            </div>
          </div>

          {/* Detailed outputs */}
          <div className="space-y-4">
            <h3 className="font-semibold text-slate-100">Outputs</h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {results.map((result) => {
                const arm = ARMS.find((a) => a.value === result.arm);
                if (!arm) return null;

                return (
                  <div key={result.arm} className="card p-4 space-y-3">
                    <div>
                      <h4 className="font-semibold text-slate-200">
                        {arm.label}
                      </h4>
                      <p className="text-xs text-slate-600">{arm.description}</p>
                    </div>

                    <div className="bg-night-900/50 p-3 rounded text-xs text-slate-400 font-mono max-h-32 overflow-y-auto">
                      {result.output}
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="bg-night-800/30 p-2 rounded">
                        <p className="text-slate-600">Entropy</p>
                        <p className="font-mono text-slate-300">
                          {result.entropy.toFixed(2)}
                        </p>
                      </div>
                      <div className="bg-night-800/30 p-2 rounded">
                        <p className="text-slate-600">Effect Size</p>
                        <p className="font-mono text-slate-300">
                          {result.effectSize.toFixed(3)}
                        </p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Interpretation */}
          <div className="card p-6 border-l-4 border-teal-600 space-y-3">
            <h3 className="font-semibold text-teal-300">Interpretation</h3>
            <div className="text-sm text-slate-400 space-y-2">
              <p>
                <span className="text-teal-300 font-semibold">Baseline:</span>{" "}
                Control (no steering). All other arms' effect sizes are relative
                to this.
              </p>
              <p>
                <span className="text-teal-300 font-semibold">Gated:</span>{" "}
                Steers at the sphuraṭṭā moment (when attention unifies). Most
                efficient use of entropy budget.
              </p>
              <p>
                <span className="text-teal-300 font-semibold">Continuous:</span>{" "}
                Steers every step. Higher cost but potentially more influence.
              </p>
              <p>
                <span className="text-teal-300 font-semibold">Logit Bias:</span>{" "}
                Output layer only. Lowest cost but lowest steering impact.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Empty state */}
      {results.length === 0 && (
        <div className="card p-12 text-center text-slate-500 text-sm">
          <p>Configure the comparison above and click "Run Comparison" to start.</p>
        </div>
      )}
    </div>
  );
}
