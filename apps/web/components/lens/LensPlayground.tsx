"use client";

import { useState, useRef, useEffect } from "react";
import { Send, AlertCircle } from "lucide-react";

interface BandState {
  token: string;
  layer: number;
  activations: number[];
  verbalized: string;
}

export default function LensPlayground() {
  const [prompt, setPrompt] = useState("What is the capital of France?");
  const [loading, setLoading] = useState(false);
  const [selectedToken, setSelectedToken] = useState(0);
  const [bandData, setBandData] = useState<BandState[]>([]);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const handleVisualize = async () => {
    setLoading(true);
    setBandData([]);

    // Simulate band visualization
    // In reality, this would call /api/lens with the prompt
    await new Promise((resolve) => setTimeout(resolve, 500));

    // Mock band data for demonstration
    const mockBandData: BandState[] = [
      {
        token: "What",
        layer: 24,
        activations: [0.1, 0.2, 0.3, 0.4, 0.35, 0.25],
        verbalized: 'Interrogative: seeking information about something',
      },
      {
        token: "is",
        layer: 24,
        activations: [0.2, 0.3, 0.4, 0.5, 0.4, 0.3],
        verbalized: 'Relationship: establishing identity or equation',
      },
      {
        token: "the",
        layer: 24,
        activations: [0.15, 0.25, 0.35, 0.45, 0.35, 0.25],
        verbalized: 'Definiteness: referring to a specific entity',
      },
      {
        token: "capital",
        layer: 24,
        activations: [0.3, 0.4, 0.5, 0.6, 0.5, 0.4],
        verbalized: 'Geography/Politics: seat of government, urban center',
      },
      {
        token: "of",
        layer: 24,
        activations: [0.2, 0.3, 0.4, 0.5, 0.4, 0.3],
        verbalized: 'Possession: indicating ownership or association',
      },
      {
        token: "France",
        layer: 24,
        activations: [0.4, 0.5, 0.6, 0.7, 0.6, 0.5],
        verbalized: 'Country: nation-state in Western Europe',
      },
    ];

    setBandData(mockBandData);
    setLoading(false);
  };

  // Draw heatmap
  useEffect(() => {
    if (!bandData.length || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    canvas.width = canvas.offsetWidth;
    canvas.height = 200;

    const cellWidth = canvas.width / bandData[selectedToken].activations.length;
    const cellHeight = canvas.height;

    const activations = bandData[selectedToken].activations;

    activations.forEach((activation, i) => {
      // Normalize activation to 0-1
      const normalized = Math.min(Math.max(activation, 0), 1);

      // Color gradient from dark to bright (indigo/teal)
      const hue = 270 + (60 * (1 - normalized)); // Indigo to teal
      const lightness = 30 + normalized * 40; // Dark to light
      ctx.fillStyle = `hsl(${hue}, 70%, ${lightness}%)`;

      ctx.fillRect(i * cellWidth, 0, cellWidth, cellHeight);
    });

    // Draw grid
    ctx.strokeStyle = "rgba(255, 255, 255, 0.1)";
    ctx.lineWidth = 1;
    for (let i = 0; i <= bandData[selectedToken].activations.length; i++) {
      ctx.beginPath();
      ctx.moveTo(i * cellWidth, 0);
      ctx.lineTo(i * cellWidth, cellHeight);
      ctx.stroke();
    }
  }, [bandData, selectedToken]);

  return (
    <div className="space-y-6">
      {/* Info card */}
      <div className="card p-6 border-l-4 border-indigo-600 space-y-3">
        <div className="flex gap-3">
          <AlertCircle className="w-5 h-5 text-indigo-400 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-slate-300 space-y-2">
            <p className="font-semibold">Lens: Reading the Workspace Band</p>
            <p>
              The workspace band (J-space, global broadcast layer) is where the model's
              "inner thoughts" live. You can see token-by-token activations across the band
              dimensions and read interpretations of what the model is attending to.
            </p>
            <p className="text-xs text-slate-400">
              Live band-read is coming online with the next gateway update. For now, this
              playground shows pre-recorded band states.
            </p>
          </div>
        </div>
      </div>

      {/* Input */}
      <div className="card p-6 space-y-4">
        <h2 className="text-lg font-semibold text-slate-100">
          Read the Workspace Band
        </h2>

        <div className="space-y-2">
          <label className="label">Prompt</label>
          <div className="flex gap-2">
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              disabled={loading}
              className="input flex-1"
              placeholder="Enter a prompt to visualize its workspace band..."
            />
            <button
              onClick={handleVisualize}
              disabled={loading || !prompt.trim()}
              className="btn-primary px-4"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Visualization */}
      {bandData.length > 0 && (
        <div className="space-y-6">
          {/* Token selector */}
          <div className="card p-6 space-y-4">
            <h3 className="font-semibold text-slate-100">Tokens</h3>

            <div className="flex gap-2 flex-wrap">
              {bandData.map((state, i) => (
                <button
                  key={i}
                  onClick={() => setSelectedToken(i)}
                  className={`chip text-xs px-3 py-1.5 transition-colors ${
                    selectedToken === i
                      ? "border-indigo-600/60 text-indigo-300 bg-indigo-900/20"
                      : "hover:border-indigo-600/40"
                  }`}
                >
                  {state.token}
                </button>
              ))}
            </div>
          </div>

          {/* Heatmap */}
          <div className="card p-6 space-y-4">
            <h3 className="font-semibold text-slate-100">
              Band Activation Heatmap
            </h3>

            <p className="text-sm text-slate-400">
              Token: <span className="text-indigo-300 font-semibold">
                "{bandData[selectedToken].token}"
              </span>
            </p>

            <canvas
              ref={canvasRef}
              className="w-full border border-night-600 rounded-lg bg-night-900/30"
            />

            <div className="grid grid-cols-2 gap-4">
              <div className="text-xs text-slate-600">
                <p className="mb-1 font-semibold text-slate-400">Activation values</p>
                <div className="font-mono space-y-1">
                  {bandData[selectedToken].activations.map((v, i) => (
                    <p key={i}>Dim {i}: {v.toFixed(2)}</p>
                  ))}
                </div>
              </div>

              <div className="text-xs text-slate-600">
                <p className="mb-1 font-semibold text-slate-400">
                  Dimension interpretation
                </p>
                <p className="text-slate-400 leading-relaxed">
                  The band dimensions capture abstract features (syntax, semantics,
                  pragmatics, intent, etc.) that the model attends to when processing
                  this token.
                </p>
              </div>
            </div>
          </div>

          {/* Verbalization */}
          <div className="card p-6 border-l-4 border-teal-600 space-y-3">
            <h3 className="font-semibold text-teal-300">What the Band is "Thinking"</h3>

            <div className="bg-teal-900/20 p-4 rounded text-sm text-slate-300 leading-relaxed">
              <p>
                <span className="font-semibold text-teal-300">
                  "{bandData[selectedToken].token}"
                </span>{" "}
                — {bandData[selectedToken].verbalized}
              </p>
            </div>

            <p className="text-xs text-slate-600 pt-2 border-t border-night-600 mt-4 pt-4">
              This interpretation is derived from the band's activation profile.
              High-activation dimensions correspond to the semantic/pragmatic content
              the model is currently attending to.
            </p>
          </div>

          {/* Pinning guide */}
          <div className="card p-6 space-y-3">
            <h3 className="font-semibold text-slate-100">Explore</h3>
            <p className="text-sm text-slate-400">
              Click on different tokens above to see how the band's focus shifts
              as the model processes the prompt. Notice which dimensions activate
              strongly for different parts of speech and semantic roles.
            </p>
          </div>
        </div>
      )}

      {/* Empty state */}
      {bandData.length === 0 && (
        <div className="card p-12 text-center text-slate-500 text-sm">
          <p>Enter a prompt and click "Visualize" to explore the workspace band.</p>
        </div>
      )}
    </div>
  );
}
