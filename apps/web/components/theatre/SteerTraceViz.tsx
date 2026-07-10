"use client";

import { useEffect, useRef, useState } from "react";
import { Play, Pause } from "lucide-react";

interface SteerTrace {
  tokens: string[];
  entropies: number[];
  writes: Array<{ position: number; amplitude: number }>;
  readback: { verdict: "accept" | "reject"; confidence: number };
}

export default function SteerTraceViz({ trace }: { trace: SteerTrace }) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [playing, setPlaying] = useState(false);
  const [position, setPosition] = useState(0);
  const maxEntropy = Math.max(...trace.entropies);

  useEffect(() => {
    if (!playing) return;

    const interval = setInterval(() => {
      setPosition((p) => (p + 1) % (trace.tokens.length || 1));
    }, 200);

    return () => clearInterval(interval);
  }, [playing, trace.tokens.length]);

  const width = 1000;
  const height = 400;
  const padding = 40;
  const graphWidth = width - padding * 2;
  const graphHeight = height - padding * 2;

  const xScale = (i: number) => padding + (i / (trace.tokens.length - 1)) * graphWidth;
  const yScale = (entropy: number) => height - padding - (entropy / maxEntropy) * graphHeight;

  return (
    <div className="card space-y-4 p-6">
      <div className="space-y-3">
        <h3 className="text-lg font-semibold text-slate-100">SteerTrace Visualization</h3>

        {/* Controls */}
        <div className="flex gap-2 items-center">
          <button
            onClick={() => setPlaying(!playing)}
            className="btn-ghost px-3 py-1.5"
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
            max={trace.tokens.length - 1}
            value={position}
            onChange={(e) => setPosition(parseInt(e.target.value))}
            className="flex-1 h-1.5 rounded-lg bg-night-700 cursor-pointer accent-indigo-600"
          />

          <span className="text-xs text-slate-500">
            {position + 1} / {trace.tokens.length}
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
        {/* Background grid */}
        <defs>
          <pattern
            id="grid"
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
        </defs>
        <rect width={width} height={height} fill="url(#grid)" />

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

        {/* Entropy sparkline */}
        <polyline
          points={trace.entropies
            .map((e, i) => `${xScale(i)},${yScale(e)}`)
            .join(" ")}
          fill="none"
          stroke="url(#entropyGradient)"
          strokeWidth="2"
        />

        <defs>
          <linearGradient id="entropyGradient" x1="0%" y1="0%" x2="100%">
            <stop offset="0%" stopColor="rgba(124, 77, 255, 0.8)" />
            <stop offset="100%" stopColor="rgba(20, 220, 187, 0.8)" />
          </linearGradient>
        </defs>

        {/* Write events (sphuraṭṭā flashes) */}
        {trace.writes.map((write, i) => (
          <g key={i}>
            <circle
              cx={xScale(write.position)}
              cy={yScale(trace.entropies[write.position] || 0)}
              r={3 + write.amplitude * 2}
              fill="rgba(255, 193, 7, 0.6)"
              stroke="rgba(255, 193, 7, 0.8)"
              strokeWidth="2"
            />
          </g>
        ))}

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
          cy={yScale(trace.entropies[position] || 0)}
          r="4"
          fill="rgba(124, 77, 255, 1)"
        />
      </svg>

      {/* Current token info */}
      <div className="grid grid-cols-2 gap-4 pt-2">
        <div className="card p-4">
          <p className="text-xs text-slate-500 mb-1">Current token</p>
          <p className="font-mono text-sm text-indigo-300 break-words">
            {trace.tokens[position]}
          </p>
        </div>

        <div className="card p-4">
          <p className="text-xs text-slate-500 mb-1">Entropy</p>
          <p className="font-mono text-sm text-teal-300">
            {trace.entropies[position]?.toFixed(3)}
          </p>
        </div>
      </div>

      {/* Readback verdict (at end of trace) */}
      {position === trace.tokens.length - 1 && (
        <div
          className={`card p-4 border-l-4 ${
            trace.readback.verdict === "accept"
              ? "border-teal-600 bg-teal-900/10"
              : "border-red-600 bg-red-900/10"
          }`}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-400">Readback verdict</p>
              <p
                className={`text-lg font-bold capitalize ${
                  trace.readback.verdict === "accept"
                    ? "text-teal-300"
                    : "text-red-300"
                }`}
              >
                {trace.readback.verdict}
              </p>
            </div>
            <div className="text-right">
              <p className="text-xs text-slate-500">Confidence</p>
              <p className="text-lg font-bold text-slate-300">
                {(trace.readback.confidence * 100).toFixed(0)}%
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
