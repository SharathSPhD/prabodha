"use client";

import { useState, useEffect } from "react";
import { useSSESteer } from "@/lib/hooks/useSSESteer";
import { getDepthMode } from "@/lib/depth-toggle";
import type { SteeringArm } from "@/lib/types/steering";
import { Play, Pause, Send, AlertCircle } from "lucide-react";
import { HelpTooltip } from "@/components/ui/HelpTooltip";
import StudioTraceViz from "./StudioTraceViz";

const CONCEPT_PRESETS = [
  { label: "Honesty", value: "truthfulness" },
  { label: "Refusal", value: "harmlessness" },
  { label: "Creativity", value: "novelty" },
  { label: "Caution", value: "uncertainty" },
  { label: "Engagement", value: "conversational" },
];

export default function LiveStudio() {
  const [prompt, setPrompt] = useState(
    "Explain how to make a paper airplane."
  );
  const [concept, setConcept] = useState("honesty");
  const [alpha, setAlpha] = useState(0.5);
  const [arm, setArm] = useState<SteeringArm>("gated");
  const [siteLayer, setSiteLayer] = useState(24);
  const [isOffline, setIsOffline] = useState(false);
  const [depth] = useState(getDepthMode());

  const { loading, error, tokens, episode, done, steer, cancel } =
    useSSESteer();

  // Check if gateway is available on mount
  useEffect(() => {
    const checkGateway = async () => {
      try {
        const res = await fetch("/api/steer", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            prompt: "",
            concept: "",
            alpha: 0,
            arm: "baseline",
          }),
        });
        if (res.status === 503) {
          setIsOffline(true);
        }
      } catch {
        setIsOffline(true);
      }
    };
    checkGateway();
  }, []);

  const handleSteer = async () => {
    if (!prompt.trim() || !concept.trim()) {
      alert("Please enter both a prompt and a concept");
      return;
    }

    await steer({
      prompt: prompt.trim(),
      concept: concept.trim(),
      alpha: parseFloat(alpha.toString()),
      arm,
    });
  };

  if (isOffline) {
    return (
      <div className="card p-8 border-l-4 border-yellow-600 bg-yellow-900/10 space-y-4">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-yellow-400 mt-0.5" />
          <div>
            <h3 className="font-semibold text-yellow-300 mb-2">
              Gateway Offline
            </h3>
            <p className="text-sm text-slate-400 mb-4">
              Live steering is unavailable (admin-run GB10 gateway is offline). You can still explore the studio interface, replay pre-recorded runs, or bring your own model (BYOK). Live steering steering updates are available once the gateway comes back online.
            </p>
            <div className="flex flex-wrap gap-2">
              <a
                href="/theatre"
                className="btn-secondary text-sm"
              >
                View Recorded Runs
              </a>
              <a
                href="/theatre?tab=byok"
                className="btn-secondary text-sm"
              >
                Try BYOK Mode
              </a>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Control Panel */}
      <div className="card p-6 space-y-6">
        <h2 className="text-lg font-semibold text-slate-100">
          {depth === "explorer" ? "Steer Your Prompt" : "Steering Configuration"}
        </h2>

        {/* Prompt Input */}
        <div className="space-y-2">
          <label className="label">
            Prompt
            {depth === "researcher" && (
              <span className="text-xs text-slate-500 font-normal ml-2">
                — input to the model
              </span>
            )}
          </label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            disabled={loading}
            className="input font-mono text-xs h-24 resize-none"
            placeholder="Enter the prompt you want to steer..."
          />
          {depth === "researcher" && (
            <p className="text-xs text-slate-600">
              The model will process this with the steering direction applied.
            </p>
          )}
        </div>

        {/* Concept Input + Presets */}
        <div className="space-y-2">
          <label className="label">
            Select one concept
            {depth === "researcher" && (
              <span className="text-xs text-slate-500 font-normal ml-2">
                — direction vector in workspace band
              </span>
            )}
          </label>
          <p className="text-xs text-slate-600 mb-2">Click a preset or enter a custom concept</p>
          <div className="flex gap-2 mb-2" role="radiogroup" aria-label="Concept presets">
            {CONCEPT_PRESETS.map((preset) => (
              <button
                key={preset.value}
                onClick={() => setConcept(preset.value)}
                disabled={loading}
                role="radio"
                aria-checked={concept === preset.value}
                className={`chip text-xs transition-colors ${
                  concept === preset.value
                    ? "border-indigo-600/60 text-indigo-300 bg-indigo-900/20"
                    : "hover:border-indigo-600/40"
                }`}
              >
                {preset.label}
              </button>
            ))}
          </div>
          <input
            type="text"
            value={concept}
            onChange={(e) => {
              // Clear preset selection when custom text is entered
              const inputValue = e.target.value;
              setConcept(inputValue);
            }}
            disabled={loading}
            className="input text-sm"
            placeholder="Or enter a custom concept..."
          />
          {depth === "researcher" && (
            <p className="text-xs text-slate-600">
              The concept is tokenized and embedded into the workspace band at
              the gated moment.
            </p>
          )}
        </div>

        {/* Controls Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Amplitude slider */}
          <div className="space-y-2">
            <label className="label">
              Amplitude (α)
              <HelpTooltip text="Controls the strength of the steering write. Higher values = stronger direction influence, bounded by entropy budget ±0.5 nats. Typical range: 0.1–0.5." />
              {depth === "researcher" && (
                <span className="text-xs text-slate-500 font-normal ml-2">
                  — write norm
                </span>
              )}
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={alpha}
              onChange={(e) => setAlpha(parseFloat(e.target.value))}
              disabled={loading}
              className="w-full h-2 rounded-lg bg-night-700 cursor-pointer accent-indigo-600"
            />
            <div className="flex justify-between text-xs text-slate-500">
              <span>0</span>
              <span className="font-mono text-indigo-400">
                {alpha.toFixed(2)}
              </span>
              <span>1.0</span>
            </div>
            {depth === "researcher" && (
              <p className="text-xs text-slate-600 mt-2">
                Standardized effect: higher α = stronger direction influence,
                subject to entropy budget ±0.5 nats.
              </p>
            )}
          </div>

          {/* Timing arm */}
          <div className="space-y-2">
            <label className="label">
              Timing Arm
              <HelpTooltip text="Baseline: no steering. Gated: injects at sphuraṭṭā (entropy-gated moments). Continuous: every step. Logit-bias: output layer only." />
            </label>
            <select
              value={arm}
              onChange={(e) => setArm(e.target.value as SteeringArm)}
              disabled={loading}
              className="input text-sm"
            >
              <option value="baseline">Baseline (none)</option>
              <option value="gated">Gated (entropy)</option>
              <option value="continuous">Continuous</option>
              <option value="logit-bias">Logit bias</option>
            </select>
            {depth === "researcher" && (
              <p className="text-xs text-slate-600 mt-2">
                Baseline: no steering. Gated: inject at sphuraṭṭā (attention
                unified). Continuous: every step. Logit-bias: output layer only.
              </p>
            )}
          </div>

          {/* Site layer */}
          <div className="space-y-2">
            <label className="label">
              Site Layer
              <HelpTooltip text="The workspace band layer where the write occurs. Qwen3: 6–30 (default 24); Nemotron: 6–26 (default 24). Higher layers = closer to output, stronger behavioral coupling." />
              {depth === "researcher" && (
                <span className="text-xs text-slate-500 font-normal ml-2">
                  — workspace band depth
                </span>
              )}
            </label>
            <input
              type="number"
              min="1"
              max="32"
              value={siteLayer}
              onChange={(e) => setSiteLayer(parseInt(e.target.value))}
              disabled={loading}
              className="input text-sm"
            />
            {depth === "researcher" && (
              <p className="text-xs text-slate-600 mt-2">
                Global workspace layer (typically 24-26 for Qwen/Nemotron).
              </p>
            )}
          </div>
        </div>

        {/* Error display */}
        {error && (
          <div className="card p-3 border-l-4 border-red-600 bg-red-900/10">
            <p className="text-sm text-red-300">{error}</p>
          </div>
        )}

        {/* Run button */}
        <button
          onClick={loading ? cancel : handleSteer}
          disabled={!prompt.trim() || !concept.trim()}
          className={`w-full py-3 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 ${
            loading
              ? "bg-red-600 hover:bg-red-700 text-white"
              : "bg-indigo-600 hover:bg-indigo-700 text-white"
          }`}
        >
          {loading ? (
            <>
              <Pause className="w-4 h-4" />
              Cancel
            </>
          ) : (
            <>
              <Send className="w-4 h-4" />
              Steer
            </>
          )}
        </button>
      </div>

      {/* Results */}
      {(tokens.length > 0 || done) && (
        <div className="space-y-6">
          {/* Visualization */}
          {tokens.length > 0 && (
            <StudioTraceViz tokens={tokens} done={done} />
          )}

          {/* Side-by-side comparison */}
          {episode && (
            <div className="grid grid-cols-2 gap-4">
              <div className="card p-6 space-y-3">
                <h3 className="text-sm font-semibold text-slate-300">
                  Baseline
                </h3>
                <div className="bg-night-900/50 p-4 rounded border border-night-600 text-sm text-slate-300 leading-relaxed whitespace-pre-wrap font-mono text-xs">
                  {episode.baseline_text}
                </div>
              </div>

              <div className="card p-6 space-y-3 border-l-4 border-teal-600">
                <h3 className="text-sm font-semibold text-teal-300">Steered</h3>
                <div className="bg-night-900/50 p-4 rounded border border-night-600 text-sm text-slate-300 leading-relaxed whitespace-pre-wrap font-mono text-xs">
                  {episode.steered_text}
                </div>
              </div>
            </div>
          )}

          {/* Episode metadata */}
          {episode && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="card p-4">
                <p className="text-xs text-slate-500 mb-1">Model</p>
                <p className="font-mono text-sm text-indigo-300">
                  {episode.model_id}
                </p>
              </div>
              <div className="card p-4">
                <p className="text-xs text-slate-500 mb-1">Site Layer</p>
                <p className="font-mono text-sm text-teal-300">
                  {episode.site_layer}
                </p>
              </div>
              <div className="card p-4">
                <p className="text-xs text-slate-500 mb-1">Amplitude</p>
                <p className="font-mono text-sm text-saffron-300">
                  {episode.alpha.toFixed(3)}
                </p>
              </div>
              <div className="card p-4">
                <p className="text-xs text-slate-500 mb-1">Arm</p>
                <p className="font-mono text-sm text-slate-300 capitalize">
                  {episode.arm}
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Empty state */}
      {!tokens.length && !done && (
        <div className="card p-12 text-center space-y-4">
          <div className="text-slate-500">
            <p className="text-sm">
              Configure your steering parameters above and click "Steer" to
              begin.
            </p>
            {depth === "researcher" && (
              <p className="text-xs mt-2">
                The studio writes your concept into the workspace band at the
                gated moment, constraining the entropy budget within ±0.5 nats.
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
