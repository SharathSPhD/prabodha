"use client";

import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/Tabs";
import { Download, Play, X } from "lucide-react";
import type { DirectionMode } from "@/lib/types/steering";

type BuildMode = "concept" | "contrastive";

interface ContrastiveExample {
  id: string;
  text: string;
}

export default function SteeringBuilder() {
  const [buildMode, setBuildMode] = useState<BuildMode>("concept");
  const [directionMode, setDirectionMode] = useState<DirectionMode>("concept");
  const [concept, setConcept] = useState("honesty");
  const [alpha, setAlpha] = useState(0.5);
  const [testPrompt, setTestPrompt] = useState("Is the sky blue?");

  // Contrastive mode
  const [posExamples, setPosExamples] = useState<ContrastiveExample[]>([
    { id: "p1", text: "The sky appears blue due to Rayleigh scattering." },
  ]);
  const [negExamples, setNegExamples] = useState<ContrastiveExample[]>([
    { id: "n1", text: "The sky is green and triangular." },
  ]);

  const [showExportDialog, setShowExportDialog] = useState(false);
  const [packName, setPackName] = useState("my-steering-pack");
  const [packDescription, setPackDescription] = useState("Custom steering pack");

  const handleAddPosExample = () => {
    setPosExamples([
      ...posExamples,
      { id: `p${Date.now()}`, text: "" },
    ]);
  };

  const handleAddNegExample = () => {
    setNegExamples([
      ...negExamples,
      { id: `n${Date.now()}`, text: "" },
    ]);
  };

  const handleRemovePosExample = (id: string) => {
    setPosExamples(posExamples.filter((e) => e.id !== id));
  };

  const handleRemoveNegExample = (id: string) => {
    setNegExamples(negExamples.filter((e) => e.id !== id));
  };

  const handleUpdatePosExample = (id: string, text: string) => {
    setPosExamples(
      posExamples.map((e) => (e.id === id ? { ...e, text } : e))
    );
  };

  const handleUpdateNegExample = (id: string, text: string) => {
    setNegExamples(
      negExamples.map((e) => (e.id === id ? { ...e, text } : e))
    );
  };

  const exportSteeringPack = () => {
    // Create the steering pack structure
    const pack = {
      name: packName,
      description: packDescription,
      version: "1.0.0",
      type: "concept-vector-steering",
      direction_spec: {
        mode: directionMode,
        concept: directionMode === "concept" ? concept : undefined,
        pos_texts: directionMode === "contrastive" ? posExamples.map(e => e.text).filter(t => t) : undefined,
        neg_texts: directionMode === "contrastive" ? negExamples.map(e => e.text).filter(t => t) : undefined,
      },
      default_config: {
        alpha,
        arm: "gated",
        site_layer: 24,
      },
      readme: `# ${packName}

${packDescription}

## What is this?

This is an **inference-time steering artifact** — a reproducible recipe for writing a direction vector into the model's global workspace band (J-space). This is NOT a modified model weight file.

## Why publish inference-time steering instead of modifying weights?

- **Reproducibility**: You can re-run the steering on any compatible model
- **Interpretability**: The direction is explicit and human-readable (or derivable from examples)
- **Autonomy preservation**: Steering respects the model's entropy budget (±0.5 nats freedom cost)
- **Auditability**: Every steer is logged with its exact parameters

## How to use this pack

### With prabodha

1. Go to https://prabodha.research.anthropic.com/build
2. Import this pack
3. Test and refine
4. Export your findings

### Programmatically

\`\`\`python
import json

# Load the pack
with open('steering_pack.json') as f:
    pack = json.load(f)

# The direction_spec tells you how to construct the direction vector
direction_spec = pack['direction_spec']
default_config = pack['default_config']

# Use with your steering gateway:
# POST /steer {
#   "prompt": "...",
#   "direction_spec": direction_spec,
#   "alpha": default_config['alpha'],
#   "arm": default_config['arm']
# }
\`\`\`

## Citation

If you use this steering pack in your research, please cite:

\`\`\`bibtex
@inproceedings{sphr2024,
  title={Steering Frozen Language Models via Recognition in J-Space},
  author={Sharath, S.},
  year={2024}
}
\`\`\`

---

**Created with prabodha** — steering via workspace recognition
`,
    };

    // Create JSON file
    const jsonBlob = new Blob([JSON.stringify(pack, null, 2)], {
      type: "application/json",
    });
    const jsonUrl = URL.createObjectURL(jsonBlob);
    const jsonLink = document.createElement("a");
    jsonLink.href = jsonUrl;
    jsonLink.download = `${packName}.json`;
    jsonLink.click();

    // Create README file
    const readmeBlob = new Blob([pack.readme], { type: "text/plain" });
    const readmeUrl = URL.createObjectURL(readmeBlob);
    const readmeLink = document.createElement("a");
    readmeLink.href = readmeUrl;
    readmeLink.download = `${packName}-README.md`;
    readmeLink.click();

    setShowExportDialog(false);
  };

  return (
    <div className="space-y-6">
      {/* Mode selector */}
      <div className="card p-6">
        <h2 className="text-lg font-semibold text-slate-100 mb-4">
          Direction Method
        </h2>

        <Tabs value={buildMode} onValueChange={(v) => setBuildMode(v as BuildMode)} className="space-y-4">
          <TabsList className="grid w-full grid-cols-2 max-w-md">
            <TabsTrigger value="concept">Concept Word</TabsTrigger>
            <TabsTrigger value="contrastive">Contrastive</TabsTrigger>
          </TabsList>

          <TabsContent value="concept" className="space-y-4">
            <p className="text-sm text-slate-400">
              Specify a single concept word. The gateway will embed it directly.
            </p>
            <div className="space-y-2">
              <label className="label">Concept</label>
              <input
                type="text"
                value={concept}
                onChange={(e) => {
                  setConcept(e.target.value);
                  setDirectionMode("concept");
                }}
                className="input"
                placeholder="e.g., honesty, creativity, caution..."
              />
            </div>
          </TabsContent>

          <TabsContent value="contrastive" className="space-y-4">
            <p className="text-sm text-slate-400">
              Provide positive (desired) and negative (undesired) examples.
              The direction is inferred via CAA-style contrastive activation analysis.
            </p>

            {/* Positive examples */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <label className="label">Positive Examples (Desired)</label>
                <button
                  onClick={handleAddPosExample}
                  className="btn-ghost text-xs px-2 py-1"
                >
                  + Add
                </button>
              </div>
              <div className="space-y-2">
                {posExamples.map((ex) => (
                  <div key={ex.id} className="flex gap-2">
                    <textarea
                      value={ex.text}
                      onChange={(e) =>
                        handleUpdatePosExample(ex.id, e.target.value)
                      }
                      className="input flex-1 h-20 resize-none"
                      placeholder="Example of desired behavior..."
                    />
                    {posExamples.length > 1 && (
                      <button
                        onClick={() => handleRemovePosExample(ex.id)}
                        className="btn-ghost text-red-400 hover:text-red-300 p-2"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Negative examples */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <label className="label">Negative Examples (Undesired)</label>
                <button
                  onClick={handleAddNegExample}
                  className="btn-ghost text-xs px-2 py-1"
                >
                  + Add
                </button>
              </div>
              <div className="space-y-2">
                {negExamples.map((ex) => (
                  <div key={ex.id} className="flex gap-2">
                    <textarea
                      value={ex.text}
                      onChange={(e) =>
                        handleUpdateNegExample(ex.id, e.target.value)
                      }
                      className="input flex-1 h-20 resize-none"
                      placeholder="Example of undesired behavior..."
                    />
                    {negExamples.length > 1 && (
                      <button
                        onClick={() => handleRemoveNegExample(ex.id)}
                        className="btn-ghost text-red-400 hover:text-red-300 p-2"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <div
              onClick={() => setDirectionMode("contrastive")}
              className="text-xs text-slate-600 cursor-default"
            >
              ✓ Ready for contrastive direction inference
            </div>
          </TabsContent>
        </Tabs>
      </div>

      {/* Configuration */}
      <div className="card p-6 space-y-4">
        <h2 className="text-lg font-semibold text-slate-100">Configuration</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="label">Default Amplitude (α)</label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={alpha}
              onChange={(e) => setAlpha(parseFloat(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-slate-500">
              <span>0</span>
              <span className="font-mono text-indigo-400">{alpha.toFixed(2)}</span>
              <span>1.0</span>
            </div>
          </div>

          <div className="space-y-2">
            <label className="label">Test Prompt</label>
            <input
              type="text"
              value={testPrompt}
              onChange={(e) => setTestPrompt(e.target.value)}
              className="input"
              placeholder="Enter a test prompt..."
            />
          </div>
        </div>
      </div>

      {/* Export button */}
      <button
        onClick={() => setShowExportDialog(true)}
        className="w-full bg-teal-600 hover:bg-teal-700 text-white py-3 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
      >
        <Download className="w-4 h-4" />
        Export as Steering Pack
      </button>

      {/* Export dialog */}
      {showExportDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="card p-6 max-w-md space-y-4">
            <h3 className="text-lg font-semibold text-slate-100">
              Export Steering Pack
            </h3>

            <div className="space-y-2">
              <label className="label">Pack Name</label>
              <input
                type="text"
                value={packName}
                onChange={(e) => setPackName(e.target.value)}
                className="input"
              />
            </div>

            <div className="space-y-2">
              <label className="label">Description</label>
              <textarea
                value={packDescription}
                onChange={(e) => setPackDescription(e.target.value)}
                className="input h-20 resize-none"
              />
            </div>

            <p className="text-xs text-slate-500">
              Your steering pack will be exported as a JSON configuration file
              with an accompanying README explaining how to use it.
            </p>

            <div className="flex gap-2 pt-2">
              <button
                onClick={() => setShowExportDialog(false)}
                className="flex-1 btn-ghost"
              >
                Cancel
              </button>
              <button
                onClick={exportSteeringPack}
                className="flex-1 bg-teal-600 hover:bg-teal-700 text-white py-2 rounded-lg font-medium transition-colors"
              >
                Export
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Info card */}
      <div className="card p-6 border-l-4 border-indigo-600 space-y-3">
        <h3 className="font-semibold text-indigo-300">What you're building</h3>
        <p className="text-sm text-slate-400">
          Steering packs are inference-time artifacts — recipes for writing direction vectors
          into the model's workspace band. They're not modified weights, so they're:
        </p>
        <ul className="text-sm text-slate-400 space-y-1">
          <li className="flex gap-2">
            <span className="text-teal-400">✓</span>
            <span>Reproducible across model instances</span>
          </li>
          <li className="flex gap-2">
            <span className="text-teal-400">✓</span>
            <span>Interpretable (the direction is explicit)</span>
          </li>
          <li className="flex gap-2">
            <span className="text-teal-400">✓</span>
            <span>Respects the model's autonomy budget</span>
          </li>
          <li className="flex gap-2">
            <span className="text-teal-400">✓</span>
            <span>Fully auditable and publishable</span>
          </li>
        </ul>
      </div>
    </div>
  );
}
