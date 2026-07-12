"use client";

import { useState, useEffect } from "react";
import { Eye, Info } from "lucide-react";

interface Slice {
  id: string;
  label: string;
  prompt: string;
  file: string;
}
interface Manifest {
  model: string;
  lens: string;
  note: string;
  slices: Slice[];
}

export default function LensPlayground() {
  const [manifest, setManifest] = useState<Manifest | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/lens/manifest.json")
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then((m: Manifest) => {
        setManifest(m);
        setSelected(m.slices[0]?.id ?? null);
      })
      .catch((e) => setError(e.message));
  }, []);

  const current = manifest?.slices.find((s) => s.id === selected) ?? null;

  return (
    <div className="space-y-6">
      {/* Info card */}
      <div className="card p-6 border-l-4 border-indigo-500 space-y-3">
        <div className="flex gap-3">
          <Info className="w-5 h-5 text-indigo-400 mt-0.5 flex-shrink-0" />
          <div className="text-sm text-slate-300 space-y-2">
            <p className="font-semibold">Reading the workspace band</p>
            <p>
              The workspace band (J-space, the late broadcast layers) is where a model&apos;s
              representations become verbalizable. A fitted Jacobian lens reads that band and
              shows, for every token and every layer, the top tokens the band is broadcasting —
              the model&apos;s account of what it is representing at that point.
            </p>
            <p className="text-xs text-slate-400">
              These are <span className="text-teal-300 font-medium">real recorded read-outs</span>
              {manifest && (
                <>
                  {" "}from <span className="font-mono text-slate-300">{manifest.model}</span> via
                  the fitted <span className="font-mono text-slate-300">{manifest.lens}</span>
                </>
              )}{" "}
              (vendor <span className="font-mono">jlens</span> slice, not fabricated). Live
              per-prompt reads run on the admin GB10 GPU and are admin-gated; these recorded
              slices are readable by anyone.
            </p>
          </div>
        </div>
      </div>

      {/* Prompt selector */}
      <div className="card p-6 space-y-4">
        <h2 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
          <Eye className="w-5 h-5 text-teal-400" />
          Pick a recorded read
        </h2>
        {error && (
          <p className="pill-reject">Couldn&apos;t load slices: {error}</p>
        )}
        {!manifest && !error && (
          <p className="text-sm text-slate-500">Loading recorded slices…</p>
        )}
        <div className="flex flex-wrap gap-2">
          {manifest?.slices.map((s) => (
            <button
              key={s.id}
              onClick={() => setSelected(s.id)}
              className={`chip text-xs transition-colors ${
                selected === s.id
                  ? "border-teal-400/60 text-teal-300 bg-teal-400/10"
                  : "hover:border-teal-400/40"
              }`}
              title={s.prompt}
            >
              {s.label}
            </button>
          ))}
        </div>
        {current && (
          <p className="text-sm text-slate-400">
            Prompt:{" "}
            <span className="font-mono text-slate-200">&ldquo;{current.prompt}&rdquo;</span>
          </p>
        )}
      </div>

      {/* Real slice, rendered in a framed instrument panel */}
      {current && (
        <div className="card-glow p-3 space-y-3">
          <div className="flex items-center justify-between px-2 pt-1">
            <h3 className="font-semibold text-slate-100 text-sm">
              Lens slice — layer × position grid
            </h3>
            <a
              href={`/lens/${current.file}`}
              target="_blank"
              rel="noreferrer"
              className="btn-ghost text-xs"
            >
              Open full page ↗
            </a>
          </div>
          <iframe
            key={current.id}
            src={`/lens/${current.file}`}
            title={`Lens slice — ${current.label}`}
            className="w-full rounded-lg border border-night-600 bg-white"
            style={{ height: "640px" }}
          />
          <p className="text-xs text-slate-500 px-2 pb-1">
            Each cell is the top-10 lens tokens at that (layer, position). Hover a cell, or
            use ←→ to move across tokens and ↑↓ to move through layers. Watch how the band&apos;s
            content resolves toward the answer in the later layers.
          </p>
        </div>
      )}
    </div>
  );
}
