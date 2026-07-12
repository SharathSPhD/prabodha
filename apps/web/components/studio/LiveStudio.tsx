"use client";

import { useState, useEffect } from "react";
import { useSSESteer } from "@/lib/hooks/useSSESteer";
import { getDepthMode } from "@/lib/depth-toggle";
import type { SteeringArm } from "@/lib/types/steering";
import { Play, Pause, Send, AlertCircle } from "lucide-react";
import { HelpTooltip } from "@/components/ui/HelpTooltip";
import StudioTraceViz from "./StudioTraceViz";
import { CONCEPT_CATEGORIES } from "@/lib/concept-presets";

export default function LiveStudio() {
  const [prompt, setPrompt] = useState(
    "It is a beautiful day and the temperature outside is"
  );
  const [concept, setConcept] = useState("fire");
  const [model, setModel] = useState("Qwen/Qwen3-4B-Instruct-2507");
  const [alpha, setAlpha] = useState(0.5);
  const [arm, setArm] = useState<SteeringArm>("gated");
  const [siteLayer, setSiteLayer] = useState(24);
  const [isOffline, setIsOffline] = useState(false);
  const [depth] = useState(getDepthMode());

  const { loading, error, tokens, episode, done, steer, cancel } =
    useSSESteer();

  // Check if the gateway is available on mount via the lightweight GET health probe
  // (no more POSTing an invalid empty request that returned a spurious 400).
  useEffect(() => {
    const checkGateway = async () => {
      try {
        const res = await fetch("/api/steer", { method: "GET" });
        const data = await res.json().catch(() => ({ online: false }));
        setIsOffline(!data.online);
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
      model: model.trim(),
      alpha: parseFloat(alpha.toString()),
      arm,
    });
  };

  return (
    <div className="space-y-6">
      {/* Non-blocking offline banner — the interface stays fully explorable even
          when the admin GB10 gateway is down; only the live Run is disabled. */}
      {isOffline && (
        <div className="card p-4 border-l-4 border-saffron-500 bg-saffron-500/5">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-saffron-400 mt-0.5 shrink-0" />
            <div>
              <h3 className="font-semibold text-saffron-300 mb-1">
                Live gateway offline
              </h3>
              <p className="text-sm text-slate-400 mb-3">
                The admin-run GB10 gateway isn&apos;t answering right now, so a live
                run is paused. You can still build a steering config below, browse the
                concept presets, and see exactly what would run — or watch recorded
                runs and bring your own model.
              </p>
              <div className="flex flex-wrap gap-2">
                <a href="/theatre" className="btn-secondary text-sm">
                  Watch recorded runs
                </a>
                <a href="/theatre?tab=byok" className="btn-secondary text-sm">
                  Bring your own model
                </a>
              </div>
            </div>
          </div>
        </div>
      )}

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

        {/* Model selector — the gateway loads whichever model you pick, on demand */}
        <div className="space-y-2">
          <label className="label">
            Model
            {depth === "researcher" && (
              <span className="text-xs text-slate-500 font-normal ml-2">
                — loaded on demand on the GB10 gateway; released when idle
              </span>
            )}
          </label>
          <input
            list="studio-models"
            value={model}
            onChange={(e) => setModel(e.target.value)}
            disabled={loading}
            placeholder="HuggingFace model id (e.g. google/gemma-2-2b-it)"
            className="input w-full text-sm font-mono"
          />
          <datalist id="studio-models">
            <option value="Qwen/Qwen3-4B-Instruct-2507" />
            <option value="google/gemma-2-2b-it" />
            <option value="meta-llama/Llama-3.2-1B-Instruct" />
            <option value="Qwen/Qwen2.5-1.5B-Instruct" />
            <option value="HuggingFaceTB/SmolLM2-1.7B-Instruct" />
            <option value="nvidia/Nemotron-Mini-4B-Instruct" />
          </datalist>
          <p className="text-xs text-slate-600">
            All six listed models ship a real fitted Jacobian lens and steer via the lens; any other HF
            model still works via real contrastive-direction steering. Lens steering may need a higher
            amplitude (α≈1–3) than Qwen3-4B (α≈0.3).
          </p>
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
          <p className="text-xs text-slate-600 mb-2">Click a preset or enter a custom concept — any word works</p>
          <div className="space-y-2 mb-2" role="radiogroup" aria-label="Concept presets">
            {CONCEPT_CATEGORIES.map((cat) => (
              <div key={cat.id}>
                <p className="text-[10px] uppercase tracking-wide text-slate-500 mb-1" title={cat.hint}>
                  {cat.title}
                </p>
                <div className="flex flex-wrap gap-2">
                  {cat.concepts.map((preset) => (
                    <button
                      key={preset.value}
                      onClick={() => setConcept(preset.value)}
                      disabled={loading}
                      role="radio"
                      aria-checked={concept === preset.value}
                      title={preset.blurb}
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
              </div>
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
          disabled={(!loading && isOffline) || !prompt.trim() || !concept.trim()}
          title={isOffline ? "Live gateway is offline — watch a recorded run instead" : undefined}
          className={`w-full py-3 rounded-lg font-medium transition-all flex items-center justify-center gap-2 shadow-glow disabled:opacity-50 disabled:shadow-none disabled:cursor-not-allowed ${
            loading
              ? "bg-rose-600 hover:bg-rose-500 text-white"
              : "bg-indigo-600 hover:bg-indigo-500 text-white hover:shadow-[0_0_28px_rgba(168,85,247,0.5)]"
          }`}
        >
          {loading ? (
            <>
              <Pause className="w-4 h-4" />
              Cancel
            </>
          ) : isOffline ? (
            <>
              <AlertCircle className="w-4 h-4" />
              Gateway offline — live run paused
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
                  {typeof episode.alpha === "number" ? episode.alpha.toFixed(3) : "—"}
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
