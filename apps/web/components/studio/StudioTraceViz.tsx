"use client";

import { useEffect, useState, useRef } from "react";
import { Play, Pause } from "lucide-react";
import type { TraceToken } from "@/lib/types/steering";

interface StudioTraceVizProps {
  tokens: TraceToken[];
  done: boolean;
}

export default function StudioTraceViz({ tokens, done }: StudioTraceVizProps) {
  const [playing, setPlaying] = useState(false);
  const [position, setPosition] = useState(0);
  const svgRef = useRef<SVGSVGElement>(null);

  // Auto-advance when playing
  useEffect(() => {
    if (!playing || !done || position >= tokens.length - 1) return;

    const interval = setInterval(() => {
      setPosition((p) => Math.min(p + 1, tokens.length - 1));
    }, 100);

    return () => clearInterval(interval);
  }, [playing, tokens.length, done]);

  if (tokens.length === 0) return null;

  const currentToken = tokens[position];
  const maxEntropy = Math.max(...tokens.map((t) => t.entropy));
  const width = 1000;
  const height = 300;
  const padding = 40;
  const graphWidth = width - padding * 2;
  const graphHeight = height - padding * 2;

  const xScale = (i: number) =>
    padding + (i / Math.max(tokens.length - 1, 1)) * graphWidth;
  const yScale = (entropy: number) =>
    height - padding - (entropy / maxEntropy) * graphHeight;

  // Calculate write events (gated moments)
  const writeEvents = tokens.filter((t) => t.gated);

  return (
    <div className="card space-y-4 p-6">
      <div className="space-y-3">
        <h3 className="text-lg font-semibold text-slate-100">
          SteerTrace Visualization
        </h3>

        {/* Controls */}
        <div className="flex gap-2 items-center">
          <button
            onClick={() => setPlaying(!playing)}
            className="btn-ghost px-3 py-1.5"
            disabled={!done}
          >
            {playing ? (
              <>
                <Pause className="w-4 h-4" />
                Pause
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Play
              </>
            )}
          </button>

          <input
            type="range"
            min="0"
            max={tokens.length - 1}
            value={position}
            onChange={(e) => {
              setPosition(parseInt(e.target.value));
              setPlaying(false);
            }}
            className="flex-1 h-1.5 rounded-lg bg-night-700 cursor-pointer accent-indigo-600"
          />

          <span className="text-xs text-slate-500 font-mono">
            {position + 1} / {tokens.length}
          </span>
        </div>
      </div>

      {/* SVG Visualization */}
      <svg
        ref={svgRef}
        width={width}
        height={height}
        className="w-full border border-night-600 rounded-lg bg-night-900/30"
      >
        {/* Grid background */}
        <defs>
          <pattern
            id="studio-grid"
            width="50"
            height="50"
            patternUnits="userSpaceOnUse"
          >
            <path
              d="M 50 0 L 0 0 0 50"
              fill="none"
              stroke="rgba(52, 57, 90, 0.2)"
              strokeWidth="1"
            />
          </pattern>
          <linearGradient id="entropy-grad" x1="0%" y1="0%" x2="100%">
            <stop offset="0%" stopColor="rgba(124, 77, 255, 0.8)" />
            <stop offset="100%" stopColor="rgba(20, 220, 187, 0.8)" />
          </linearGradient>
        </defs>
        <rect width={width} height={height} fill="url(#studio-grid)" />

        {/* Axes */}
        <line
          x1={padding}
          y1={height - padding}
          x2={width - padding}
          y2={height - padding}
          stroke="rgba(148, 163, 184, 0.3)"
          strokeWidth="1"
        />
        <line
          x1={padding}
          y1={padding}
          x2={padding}
          y2={height - padding}
          stroke="rgba(148, 163, 184, 0.3)"
          strokeWidth="1"
        />

        {/* Entropy polyline */}
        <polyline
          points={tokens.map((t, i) => `${xScale(i)},${yScale(t.entropy)}`).join(" ")}
          fill="none"
          stroke="url(#entropy-grad)"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* Gated moments (sphuraṭṭā flashes) */}
        {writeEvents.map((write, i) => {
          const idx = tokens.indexOf(write);
          return (
            <g key={i}>
              {/* Ring effect */}
              <circle
                cx={xScale(idx)}
                cy={yScale(write.entropy)}
                r={5 + write.write_norm * 3}
                fill="none"
                stroke="rgba(255, 193, 7, 0.4)"
                strokeWidth="1"
              />
              {/* Center dot */}
              <circle
                cx={xScale(idx)}
                cy={yScale(write.entropy)}
                r={2.5}
                fill="rgba(255, 193, 7, 0.8)"
              />
            </g>
          );
        })}

        {/* Current position marker */}
        <line
          x1={xScale(position)}
          y1={padding}
          x2={xScale(position)}
          y2={height - padding}
          stroke="rgba(124, 77, 255, 0.5)"
          strokeWidth="2"
          strokeDasharray="4"
        />
        <circle
          cx={xScale(position)}
          cy={yScale(currentToken.entropy)}
          r="4"
          fill="rgba(124, 77, 255, 1)"
        />
      </svg>

      {/* Current token info */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card p-4">
          <p className="text-xs text-slate-500 mb-1">Token</p>
          <p className="font-mono text-sm text-indigo-300 break-words">
            "{currentToken.token}"
          </p>
        </div>

        <div className="card p-4">
          <p className="text-xs text-slate-500 mb-1">Entropy</p>
          <p className="font-mono text-sm text-teal-300">
            {currentToken.entropy.toFixed(3)}
          </p>
        </div>

        <div className="card p-4">
          <p className="text-xs text-slate-500 mb-1">Gated</p>
          <p className="font-mono text-sm text-saffron-300">
            {currentToken.gated ? "Yes" : "No"}
          </p>
        </div>

        <div className="card p-4">
          <p className="text-xs text-slate-500 mb-1">Write Norm</p>
          <p className="font-mono text-sm text-slate-300">
            {currentToken.write_norm.toFixed(4)}
          </p>
        </div>
      </div>

      {/* Band topk (the model's inner words) */}
      {currentToken.band_topk.length > 0 && (
        <div className="card p-4 space-y-2">
          <p className="text-xs text-slate-500 font-semibold">
            Band Top-K (Inner Words)
          </p>
          <div className="flex flex-wrap gap-2">
            {currentToken.band_topk.map((word, i) => (
              <span
                key={i}
                className="chip text-xs px-2 py-1 text-indigo-300 border-indigo-600/40"
              >
                {word}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
