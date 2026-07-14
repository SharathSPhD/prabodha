"use client";

/**
 * Lightweight dependency-free SVG charts, themed for the neuro-lab palette.
 * Previously LineChart was a "coming soon" placeholder; both are now real.
 */

export function BarChart({
  data,
  color = "#a855f7",
  format = (v: number) => v.toFixed(2),
}: {
  data: Array<{ label: string; value: number }>;
  color?: string;
  format?: (v: number) => string;
}) {
  if (!data.length) return null;
  const max = Math.max(...data.map((d) => d.value), 0.0001);
  return (
    <div className="flex h-64 items-end gap-2">
      {data.map((d, i) => (
        <div key={i} className="flex flex-1 flex-col items-center gap-2">
          <span className="font-mono text-xs text-slate-400">{format(d.value)}</span>
          <div
            className="w-full rounded-t transition-all"
            style={{
              height: `${Math.max((d.value / max) * 100, 2)}%`,
              background: `linear-gradient(to top, ${color}, ${color}aa)`,
              boxShadow: `0 0 16px ${color}44`,
            }}
          />
          <p className="text-center text-xs text-slate-500">{d.label}</p>
        </div>
      ))}
    </div>
  );
}

export function LineChart({
  data,
  color = "#22d3ee",
  height = 256,
  yLabel,
  xLabel,
}: {
  data: Array<{ x: number; y: number }>;
  color?: string;
  height?: number;
  yLabel?: string;
  xLabel?: string;
}) {
  if (!data || data.length < 2) {
    return (
      <div
        className="flex items-center justify-center rounded-lg border border-night-600 bg-night-800/60 text-sm text-slate-500"
        style={{ height }}
      >
        Not enough data to plot
      </div>
    );
  }

  const W = 640;
  const H = height;
  const pad = { t: 16, r: 16, b: 28, l: 44 };
  const xs = data.map((d) => d.x);
  const ys = data.map((d) => d.y);
  const xMin = Math.min(...xs);
  const xMax = Math.max(...xs);
  const yMin = Math.min(...ys, 0);
  const yMax = Math.max(...ys);
  const sx = (x: number) =>
    pad.l + ((x - xMin) / (xMax - xMin || 1)) * (W - pad.l - pad.r);
  const sy = (y: number) =>
    H - pad.b - ((y - yMin) / (yMax - yMin || 1)) * (H - pad.t - pad.b);

  const linePath = data
    .map((d, i) => `${i === 0 ? "M" : "L"} ${sx(d.x).toFixed(1)} ${sy(d.y).toFixed(1)}`)
    .join(" ");
  const areaPath = `${linePath} L ${sx(xMax).toFixed(1)} ${(H - pad.b).toFixed(
    1
  )} L ${sx(xMin).toFixed(1)} ${(H - pad.b).toFixed(1)} Z`;

  const yTicks = 4;
  const ticks = Array.from(
    { length: yTicks + 1 },
    (_, i) => yMin + ((yMax - yMin) * i) / yTicks
  );

  return (
    <svg
      viewBox={`0 0 ${W} ${H}`}
      className="w-full"
      style={{ height }}
      role="img"
      aria-label="line chart"
    >
      <defs>
        <linearGradient id="lc-fill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.28" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>

      {ticks.map((t, i) => (
        <g key={i}>
          <line
            x1={pad.l}
            x2={W - pad.r}
            y1={sy(t)}
            y2={sy(t)}
            stroke="#1d2839"
            strokeWidth="1"
          />
          <text x={pad.l - 6} y={sy(t) + 3} textAnchor="end" fontSize="10" fill="#6b7688">
            {t.toFixed(2)}
          </text>
        </g>
      ))}

      <path d={areaPath} fill="url(#lc-fill)" />
      <path d={linePath} fill="none" stroke={color} strokeWidth="2" />

      {data.map((d, i) => (
        <circle key={i} cx={sx(d.x)} cy={sy(d.y)} r="3" fill={color} />
      ))}

      {yLabel && (
        <text
          x={12}
          y={pad.t}
          fontSize="10"
          fill="#8b98ac"
          transform={`rotate(-90 12 ${pad.t})`}
        >
          {yLabel}
        </text>
      )}
      {xLabel && (
        <text x={W / 2} y={H - 4} textAnchor="middle" fontSize="10" fill="#8b98ac">
          {xLabel}
        </text>
      )}
    </svg>
  );
}
