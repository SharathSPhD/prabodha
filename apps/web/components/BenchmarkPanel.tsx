"use client";

import { TrendingUp, AlertCircle, CheckCircle, XCircle } from "lucide-react";

export function BenchmarkPanel() {
  return (
    <section className="py-16 px-6 bg-gradient-to-b from-night-900 to-night-950 border-t border-night-600">
      <div className="max-w-6xl mx-auto space-y-12">
        <div className="text-center space-y-3">
          <h2 className="text-3xl font-serif font-bold text-gradient">
            Benchmark: Efficiency and Lens Comparison
          </h2>
          <p className="text-slate-400 text-sm max-w-2xl mx-auto">
            L22 consolidation: gated steering delivers 2.32× lift-per-write vs continuous (6/6 sign-consistent). Lens detection improves at subtle doses but fails registered margin.
          </p>
        </div>

        {/* Efficiency Section */}
        <div className="space-y-6">
          <h3 className="text-lg font-semibold text-slate-100">Intervention Efficiency</h3>

          {/* Key Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* LPW Ratio */}
            <div className="bg-gradient-to-br from-green-600/20 to-green-600/10 border border-green-600/30 rounded-lg p-6">
              <div className="flex items-start justify-between mb-2">
                <div className="text-green-400 font-mono text-xs font-semibold">LPW RATIO</div>
                <TrendingUp className="w-5 h-5 text-green-400" />
              </div>
              <div className="text-4xl font-bold text-green-300 mb-1">2.32×</div>
              <p className="text-xs text-slate-400">
                Gated lift-per-write vs continuous (range 1.83–3.25, 6/6 cells)
              </p>
            </div>

            {/* Lift Fraction */}
            <div className="bg-gradient-to-br from-amber-600/20 to-amber-600/10 border border-amber-600/30 rounded-lg p-6">
              <div className="flex items-start justify-between mb-2">
                <div className="text-amber-400 font-mono text-xs font-semibold">LIFT RECOVERY</div>
                <CheckCircle className="w-5 h-5 text-amber-400" />
              </div>
              <div className="text-4xl font-bold text-amber-300 mb-1">66%</div>
              <p className="text-xs text-slate-400">
                Gated lift vs continuous at 29% write budget
              </p>
            </div>

            {/* Write Sparsity */}
            <div className="bg-gradient-to-br from-blue-600/20 to-blue-600/10 border border-blue-600/30 rounded-lg p-6">
              <div className="flex items-start justify-between mb-2">
                <div className="text-blue-400 font-mono text-xs font-semibold">WRITE SPARSITY</div>
                <AlertCircle className="w-5 h-5 text-blue-400" />
              </div>
              <div className="text-4xl font-bold text-blue-300 mb-1">29%</div>
              <p className="text-xs text-slate-400">
                Gated writes per timestep vs continuous
              </p>
            </div>
          </div>

          {/* Efficiency Table */}
          <div className="bg-night-800/30 border border-night-600 rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-night-600 bg-night-800/50">
                    <th className="px-4 py-3 text-left text-slate-300 font-mono">Seed</th>
                    <th className="px-4 py-3 text-center text-slate-300 font-mono">α</th>
                    <th className="px-4 py-3 text-right text-slate-300">Gated Lift</th>
                    <th className="px-4 py-3 text-right text-slate-300">Writes</th>
                    <th className="px-4 py-3 text-right text-slate-300">Cont. Lift</th>
                    <th className="px-4 py-3 text-right text-slate-300">Writes</th>
                    <th className="px-4 py-3 text-right text-green-400 font-semibold">LPW</th>
                    <th className="px-4 py-3 text-right text-green-400">Ratio</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-night-700">
                  {[
                    { seed: 42, alpha: "0.02", gl: 0.275, gw: 8.4, cl: 0.475, cw: 28.95, lpw: 0.0327, ratio: "1.99×" },
                    { seed: 42, alpha: "0.1", gl: 0.3, gw: 8.93, cl: 0.5, cw: 27.23, lpw: 0.0336, ratio: "1.83×" },
                    { seed: 123, alpha: "0.02", gl: 0.275, gw: 7.88, cl: 0.375, cw: 27.85, lpw: 0.0349, ratio: "2.59×" },
                    { seed: 123, alpha: "0.1", gl: 0.35, gw: 7.75, cl: 0.425, cw: 30.52, lpw: 0.0452, ratio: "3.25×" },
                    { seed: 777, alpha: "0.02", gl: 0.25, gw: 8.9, cl: 0.375, cw: 29.6, lpw: 0.0281, ratio: "2.21×" },
                    { seed: 777, alpha: "0.1", gl: 0.35, gw: 9.53, cl: 0.55, cw: 30.68, lpw: 0.0367, ratio: "2.05×" },
                  ].map((row, i) => (
                    <tr key={i} className="hover:bg-night-700/20">
                      <td className="px-4 py-2 text-slate-300 font-mono">{row.seed}</td>
                      <td className="px-4 py-2 text-center text-slate-300 font-mono">{row.alpha}</td>
                      <td className="px-4 py-2 text-right text-slate-300">{row.gl}</td>
                      <td className="px-4 py-2 text-right text-slate-300">{row.gw}</td>
                      <td className="px-4 py-2 text-right text-slate-300">{row.cl}</td>
                      <td className="px-4 py-2 text-right text-slate-300">{row.cw}</td>
                      <td className="px-4 py-2 text-right font-mono text-green-400">{row.lpw}</td>
                      <td className="px-4 py-2 text-right text-green-400 font-semibold">{row.ratio}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="px-4 py-2 bg-night-800/30 border-t border-night-700">
              <p className="text-xs text-slate-500">
                Source: <code className="text-slate-400">gates/gate_L22_benchmark.json</code> efficiency.cells (6 seed×alpha pairs from L18/L19 clean-stream data)
              </p>
            </div>
          </div>
        </div>

        {/* Lens Detection Section */}
        <div className="space-y-6">
          <h3 className="text-lg font-semibold text-slate-100">Lens Detection: Floor Sweep</h3>
          <p className="text-xs text-slate-400">
            The final-target (output) lens must detect steering writes for closed-loop control. Prabodha reads at the write site and amplifies; both compared across dose range (α = steering amplitude).
          </p>

          {/* Dose Response Table */}
          <div className="bg-night-800/30 border border-night-600 rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-night-600 bg-night-800/50">
                    <th className="px-4 py-3 text-center text-slate-300 font-mono">Dose (α)</th>
                    <th className="px-4 py-3 text-center text-slate-300">n_pairs</th>
                    <th className="px-4 py-3 text-right text-slate-300">Band Detect.</th>
                    <th className="px-4 py-3 text-right text-slate-300">Final Detect.</th>
                    <th className="px-4 py-3 text-right text-slate-300">Gap</th>
                    <th className="px-4 py-3 text-right text-slate-300">McNemar p</th>
                    <th className="px-4 py-3 text-left text-slate-300">Verdict</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-night-700">
                  {[
                    { alpha: "0.02", n: 80, band: 0.0, final: 0.0, gap: 0.0, p: 1.0, verdict: "Floor (both miss)", verdict_color: "text-slate-500" },
                    { alpha: "0.05", n: 80, band: 0.025, final: 0.025, gap: 0.0, p: 1.0, verdict: "Equivocal", verdict_color: "text-slate-500" },
                    { alpha: "0.1", n: 80, band: 0.475, final: 0.2375, gap: 0.2375, p: "2.1e-05", verdict: "FAIL-ON-MARGIN", verdict_color: "text-orange-400" },
                    { alpha: "0.3", n: 80, band: 1.0, final: 0.95, gap: 0.05, p: 0.125, verdict: "WITHDRAWN", verdict_color: "text-amber-400" },
                  ].map((row, i) => (
                    <tr key={i} className={row.alpha === "0.1" || row.alpha === "0.3" ? "bg-night-700/30 hover:bg-night-700/50" : "hover:bg-night-700/20"}>
                      <td className={`px-4 py-2 text-center font-mono font-semibold ${row.alpha === "0.1" || row.alpha === "0.3" ? "text-slate-100" : "text-slate-300"}`}>
                        {row.alpha}
                      </td>
                      <td className="px-4 py-2 text-center text-slate-300">{row.n}</td>
                      <td className={`px-4 py-2 text-right font-mono ${row.alpha === "0.1" ? "text-orange-400 font-semibold" : "text-slate-300"}`}>
                        {row.band}
                      </td>
                      <td className={`px-4 py-2 text-right font-mono ${row.alpha === "0.1" ? "text-orange-400 font-semibold" : "text-slate-300"}`}>
                        {row.final}
                      </td>
                      <td className={`px-4 py-2 text-right font-mono ${row.alpha === "0.1" || row.alpha === "0.3" ? row.alpha === "0.1" ? "text-orange-400 font-semibold" : "text-amber-400 font-semibold" : "text-slate-300"}`}>
                        +{row.gap}
                      </td>
                      <td className={`px-4 py-2 text-right font-mono ${row.alpha === "0.1" ? "text-orange-400" : "text-slate-400"}`}>
                        {row.p}
                      </td>
                      <td className={`px-4 py-2 text-left font-semibold text-xs ${row.verdict_color}`}>
                        {row.verdict}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="px-4 py-2 bg-night-800/30 border-t border-night-700">
              <p className="text-xs text-slate-500">
                Source: <code className="text-slate-400">gates/gate_L22_benchmark.json</code> lens_headtohead.floor_sweep_amendment1
              </p>
            </div>
          </div>

          {/* Interpretation */}
          <div className="bg-orange-600/10 border-l-4 border-orange-600 rounded p-4">
            <h4 className="text-sm font-semibold text-orange-300 mb-2">Honest Reading</h4>
            <ul className="text-xs text-orange-200/80 space-y-2 ml-2">
              <li>
                <strong>α=0.1 (subtle dose):</strong> Prabodha lens detects 2× more (0.475 vs 0.2375, p=2.1e-05, direction decisive). Gap +0.2375 misses the registered margin of 0.3. Verdict: <strong>FAIL-ON-MARGIN</strong>.
              </li>
              <li>
                <strong>α=0.3 (saturating):</strong> Both saturate (band 1.00 vs final 0.95, gap +0.05, p=0.125). The necessity claim is <strong>WITHDRAWN</strong> — the registered falsifier fired; saturation makes this dose uninformative (a null p is not evidence of equivalence).
              </li>
            </ul>
          </div>
        </div>

        {/* Capability Comparison */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-slate-100">Capability Table: jSpace vs Prabodha</h3>
          <div className="bg-night-800/30 border border-night-600 rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-night-600 bg-night-800/50">
                    <th className="px-4 py-3 text-left text-slate-300 min-w-48">Capability</th>
                    <th className="px-4 py-3 text-left text-slate-300">jSpace</th>
                    <th className="px-4 py-3 text-left text-slate-300">Prabodha</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-night-700">
                  <tr className="hover:bg-night-700/20">
                    <td className="px-4 py-2 text-slate-300">Read concepts from residual stream</td>
                    <td className="px-4 py-2 text-green-400 font-semibold">yes ✓</td>
                    <td className="px-4 py-2 text-green-400">yes (vendored)</td>
                  </tr>
                  <tr className="bg-orange-600/10 hover:bg-orange-600/20">
                    <td className="px-4 py-2 text-slate-200 font-semibold">Read steered write at site 24</td>
                    <td className="px-4 py-2 text-orange-300 text-xs">Detection 0.24 at α=0.1 (misses subtle)</td>
                    <td className="px-4 py-2 text-orange-300 text-xs"><strong>FAIL-ON-MARGIN:</strong> 0.47 at α=0.1 (2× better, p=2.1e-05, gap +0.24 vs 0.3 criterion)</td>
                  </tr>
                  <tr className="hover:bg-night-700/20">
                    <td className="px-4 py-2 text-slate-300">Steer behavior (write into band)</td>
                    <td className="px-4 py-2 text-red-400 font-semibold">no ✗</td>
                    <td className="px-4 py-2 text-green-400">yes: 0.30/0.35/0.35 (3 seeds)</td>
                  </tr>
                  <tr className="bg-green-600/10 hover:bg-green-600/20">
                    <td className="px-4 py-2 text-slate-200 font-semibold">Intervention efficiency (LPW)</td>
                    <td className="px-4 py-2 text-slate-400 text-xs">n/a (no writes)</td>
                    <td className="px-4 py-2 text-green-300"><strong>2.32×</strong> continuous (6/6 cells)</td>
                  </tr>
                  <tr className="hover:bg-night-700/20">
                    <td className="px-4 py-2 text-slate-300">Freedom budget (entropy bounded)</td>
                    <td className="px-4 py-2 text-slate-400">n/a</td>
                    <td className="px-4 py-2 text-green-400">yes: ±0.5 nats (6 seeds)</td>
                  </tr>
                  <tr className="hover:bg-night-700/20">
                    <td className="px-4 py-2 text-slate-300">Cross-model calibration recipe</td>
                    <td className="px-4 py-2 text-slate-400">n/a</td>
                    <td className="px-4 py-2 text-green-400">yes: amp ∝ 1/lens-strength (4/4)</td>
                  </tr>
                  <tr className="hover:bg-night-700/20">
                    <td className="px-4 py-2 text-slate-300">Write verification (readback)</td>
                    <td className="px-4 py-2 text-slate-400">n/a</td>
                    <td className="px-4 py-2 text-amber-400">weak: BA 0.59–0.68 (honest negative)</td>
                  </tr>
                  <tr className="hover:bg-night-700/20">
                    <td className="px-4 py-2 text-slate-300">Alignment gains from steering</td>
                    <td className="px-4 py-2 text-slate-400">n/a</td>
                    <td className="px-4 py-2 text-red-400"><strong>NONE:</strong> ASR 0.25→0.25 (transparency, not alignment)</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div className="px-4 py-2 bg-night-800/30 border-t border-night-700">
              <p className="text-xs text-slate-500">
                All rows derived from gates; no hand-entered numbers. Source: <code className="text-slate-400">gate_L22_benchmark.json</code>
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
