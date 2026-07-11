"use client";

import { ChevronRight, Database, Zap, Shield } from "lucide-react";

export function ArchitecturePanel() {
  return (
    <section className="py-16 px-6 bg-gradient-to-b from-night-900 to-night-950 border-t border-night-600">
      <div className="max-w-6xl mx-auto space-y-12">
        <div className="text-center space-y-3">
          <h2 className="text-3xl font-serif font-bold text-gradient">
            System Architecture
          </h2>
          <p className="text-slate-400 text-sm max-w-2xl mx-auto">
            Three interlocking systems: steering pipeline (core control), research loop (dual-closure gates), and deployment topology (library → app → site → paper).
          </p>
        </div>

        {/* Steering Pipeline */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-slate-100">Steering Pipeline (Core)</h3>
          <div className="bg-night-800/50 border border-night-600 rounded-lg p-6 space-y-4">
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 text-sm text-slate-300">
              <div className="flex items-center gap-2 whitespace-nowrap">
                <span className="bg-indigo-600/20 px-3 py-1 rounded text-indigo-300 font-mono text-xs">Prompt</span>
                <ChevronRight className="w-4 h-4 text-slate-500" />
              </div>
              <div className="flex items-center gap-2 whitespace-nowrap">
                <span className="bg-purple-600/20 px-3 py-1 rounded text-purple-300 font-mono text-xs">e4_cli</span>
                <ChevronRight className="w-4 h-4 text-slate-500" />
              </div>
              <div className="flex items-center gap-2 whitespace-nowrap">
                <span className="bg-teal-600/20 px-3 py-1 rounded text-teal-300 font-mono text-xs">band_read</span>
                <ChevronRight className="w-4 h-4 text-slate-500" />
              </div>
              <div className="flex items-center gap-2 whitespace-nowrap">
                <span className="bg-orange-600/20 px-3 py-1 rounded text-orange-300 font-mono text-xs">sphuraṭṭā</span>
                <ChevronRight className="w-4 h-4 text-slate-500" />
              </div>
              <div className="flex items-center gap-2 whitespace-nowrap">
                <span className="bg-pink-600/20 px-3 py-1 rounded text-pink-300 font-mono text-xs">writer</span>
                <ChevronRight className="w-4 h-4 text-slate-500" />
              </div>
              <div className="flex items-center gap-2 whitespace-nowrap">
                <span className="bg-green-600/20 px-3 py-1 rounded text-green-300 font-mono text-xs">verifier</span>
                <ChevronRight className="w-4 h-4 text-slate-500" />
              </div>
              <div className="flex items-center gap-2 whitespace-nowrap">
                <span className="bg-cyan-600/20 px-3 py-1 rounded text-cyan-300 font-mono text-xs">Output</span>
              </div>
            </div>
            <div className="text-xs text-slate-500 font-mono space-y-1">
              <p><strong>Modules:</strong> steering/e4_cli • steering/writer.py (plan_write, capped_delta) • steering/verifier.py (readback_verdict, entropy) • contracts/trace.py (SteerTrace) • contracts/closure.py (GateReport)</p>
            </div>
          </div>
        </div>

        {/* Research Loop */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-slate-100">Research Loop (Dual Closure)</h3>
          <div className="bg-night-800/50 border border-night-600 rounded-lg p-6 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-sm">
              <div className="bg-gradient-to-br from-orange-600/20 to-orange-600/10 border border-orange-600/30 rounded p-3">
                <div className="text-orange-300 font-semibold text-xs mb-1">Smoke</div>
                <div className="text-slate-400 text-xs">1 seed, 5 min</div>
              </div>
              <div className="bg-gradient-to-br from-yellow-600/20 to-yellow-600/10 border border-yellow-600/30 rounded p-3">
                <div className="text-yellow-300 font-semibold text-xs mb-1">Screen</div>
                <div className="text-slate-400 text-xs">2–3 seeds</div>
              </div>
              <div className="bg-gradient-to-br from-green-600/20 to-green-600/10 border border-green-600/30 rounded p-3">
                <div className="text-green-300 font-semibold text-xs mb-1">Confirm</div>
                <div className="text-slate-400 text-xs">≥3 seeds, n≥120</div>
              </div>
              <div className="bg-gradient-to-br from-cyan-600/20 to-cyan-600/10 border border-cyan-600/30 rounded p-3">
                <div className="text-cyan-300 font-semibold text-xs mb-1">Dual Gate</div>
                <div className="text-slate-400 text-xs">code ∧ domain</div>
              </div>
            </div>
            <div className="text-xs text-slate-500 font-mono">
              <p><strong>Modules:</strong> eval/benchmarks.py (AdvBench, TruthfulQA) • eval/behavioral.py (metrics) • eval/compare.py (gate_report)</p>
            </div>
          </div>
        </div>

        {/* Deployment Map */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-slate-100">Deployment & Artifacts</h3>
          <div className="bg-night-800/50 border border-night-600 rounded-lg p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3 text-xs">
              {/* Repo */}
              <div className="bg-indigo-600/10 border border-indigo-600/30 rounded p-3">
                <div className="text-indigo-300 font-semibold mb-2 flex items-center gap-1">
                  <Database className="w-3 h-3" />
                  Repo
                </div>
                <div className="text-slate-400 space-y-1">
                  <div>src/prabodha</div>
                  <div>configs/</div>
                  <div>gates/*.json</div>
                </div>
              </div>

              {/* Distribution */}
              <div className="bg-purple-600/10 border border-purple-600/30 rounded p-3">
                <div className="text-purple-300 font-semibold mb-2 flex items-center gap-1">
                  <Zap className="w-3 h-3" />
                  Dist
                </div>
                <div className="text-slate-400 space-y-1">
                  <div>PyPI prabodha</div>
                  <div>HF qbz506/</div>
                  <div>prabodha-lenses</div>
                </div>
              </div>

              {/* Integration */}
              <div className="bg-teal-600/10 border border-teal-600/30 rounded p-3">
                <div className="text-teal-300 font-semibold mb-2 flex items-center gap-1">
                  <Shield className="w-3 h-3" />
                  Integration
                </div>
                <div className="text-slate-400 space-y-1">
                  <div>MCP Server</div>
                  <div>Claude Plugin</div>
                </div>
              </div>

              {/* Live Steering */}
              <div className="bg-orange-600/10 border border-orange-600/30 rounded p-3">
                <div className="text-orange-300 font-semibold mb-2 flex items-center gap-1">
                  <Zap className="w-3 h-3" />
                  GB10
                </div>
                <div className="text-slate-400 space-y-1">
                  <div>steer-gateway</div>
                  <div>FastAPI + SSE</div>
                  <div>HMAC Auth</div>
                </div>
              </div>

              {/* Frontend */}
              <div className="bg-cyan-600/10 border border-cyan-600/30 rounded p-3">
                <div className="text-cyan-300 font-semibold mb-2 flex items-center gap-1">
                  <Database className="w-3 h-3" />
                  Frontend
                </div>
                <div className="text-slate-400 space-y-1">
                  <div>Vercel App</div>
                  <div>Astro Pages</div>
                  <div>Paper PDF</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
