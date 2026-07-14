"use client";

import { useEffect, useRef } from "react";
import Link from "next/link";
import { ArrowRight, Sparkles, Zap } from "lucide-react";
import { AdminLink } from "@/components/AdminLink";
import { ArchitecturePanel } from "@/components/ArchitecturePanel";

export default function LandingPage() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Set canvas size
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;

    // Animate J-space visualization: two rotating spirals
    let frame = 0;
    const animate = () => {
      ctx.fillStyle = "#050a14";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;
      const time = frame * 0.01;

      // Draw gradient circles (workspace bands)
      for (let i = 0; i < 3; i++) {
        const radius = 50 + i * 40;
        const alpha = 0.2 - i * 0.05;

        ctx.strokeStyle = `rgba(124, 77, 255, ${alpha})`;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
        ctx.stroke();
      }

      // Draw orbiting "sphuraṭṭā" (flash) points
      for (let i = 0; i < 6; i++) {
        const angle = (time + (i / 6) * Math.PI * 2) % (Math.PI * 2);
        const x = centerX + Math.cos(angle) * 120;
        const y = centerY + Math.sin(angle) * 120;

        // Pulsing dot
        const scale = Math.sin(time * 2 + i) * 0.5 + 1;
        ctx.fillStyle = "rgba(20, 220, 187, 0.6)";
        ctx.beginPath();
        ctx.arc(x, y, 3 * scale, 0, Math.PI * 2);
        ctx.fill();

        // Glow
        ctx.strokeStyle = `rgba(20, 220, 187, ${0.3 * (1 - scale * 0.5)})`;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.arc(x, y, 8 * scale, 0, Math.PI * 2);
        ctx.stroke();
      }

      frame++;
      requestAnimationFrame(animate);
    };

    animate();
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-b from-night-950 to-night-900">
      {/* Header Navigation */}
      <nav className="border-b border-night-600 bg-night-900/50 backdrop-blur-md sticky top-0 z-50">
        <div className="mx-auto max-w-7xl px-6 py-4 flex items-center justify-between">
          <div className="text-2xl font-serif font-bold text-gradient">
            prabodha
          </div>
          <div className="flex gap-6 items-center">
            <Link href="/studio" className="text-sm text-slate-400 hover:text-indigo-400 transition">
              Studio
            </Link>
            <Link href="/theatre" className="text-sm text-slate-400 hover:text-indigo-400 transition">
              Theatre
            </Link>
            <Link href="/results" className="text-sm text-slate-400 hover:text-indigo-400 transition">
              Results
            </Link>
            <Link href="/glossary" className="text-sm text-slate-400 hover:text-indigo-400 transition">
              Glossary
            </Link>
            <a
              href="https://www.preprints.org/frontend/manuscript/5b72d5c7d0e37f4f5b222acfab709652/download_pub"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-slate-400 hover:text-indigo-400 transition"
            >
              Paper ↗
            </a>
            <Link href="/login" className="btn-primary text-xs">
              Sign in
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative min-h-[70vh] flex flex-col items-center justify-center px-6 pt-20 pb-32">
        {/* Animated Canvas */}
        <div className="absolute inset-0 flex items-center justify-center opacity-60">
          <canvas
            ref={canvasRef}
            className="w-full h-full max-h-96"
            aria-label="J-space visualization"
          />
        </div>

        {/* Content */}
        <div className="relative z-10 max-w-3xl text-center space-y-8">
          {/* Plain-language value prop */}
          <div className="space-y-2">
            <p className="text-base md:text-lg text-teal-300 font-semibold">
              Harden any language model against jailbreaks — with a defense that lives <em>below</em> the prompt, where an attacker can&apos;t see, override, or strip it.
            </p>
          </div>

          <div className="space-y-4">
            <h1 className="text-5xl md:text-6xl font-serif font-bold leading-tight">
              <span className="text-gradient">Recognition</span>
              <br />
              as Defense
            </h1>
            <p className="text-lg text-slate-400 max-w-xl mx-auto">
              prabodha recognizes an input&apos;s harmful signature in the model&apos;s own activations, then
              reinforces refusal <strong>only</strong> for genuine attacks — cutting real jailbreaks in half at
              zero benign over-refusal on gemma-2-2b, where a brute-force defense refuses everything.
              A graded, per-model library built on the J-space × Pratyabhijñā steering research.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 items-center justify-center pt-6">
            <Link href="/jailbreak" className="btn-primary px-6 py-3">
              See the moat &amp; graded library
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link href="/dashboard/goals" className="btn-secondary px-6 py-3">
              Define a goal &amp; register a pack
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-12 max-w-2xl mx-auto">
            <div className="card p-6 space-y-3">
              <div className="flex items-center gap-2 text-teal-400">
                <Zap className="w-4 h-4" />
                <span className="text-sm font-semibold">Recognize</span>
              </div>
              <p className="text-xs text-slate-500">
                Read the input&apos;s harmful projection in the model&apos;s activations — below what the prompt can disguise.
              </p>
            </div>

            <div className="card p-6 space-y-3">
              <div className="flex items-center gap-2 text-indigo-400">
                <Sparkles className="w-4 h-4" />
                <span className="text-sm font-semibold">Harden — graded, not one switch</span>
              </div>
              <p className="text-xs text-slate-500">
                Pick from a tiered library: gentle→firm prompt wrappers (any model) up to the recognition-gated activation moat (open weights).
              </p>
            </div>

            <div className="card p-6 space-y-3">
              <div className="flex items-center gap-2 text-saffron-400">
                <Zap className="w-4 h-4" />
                <span className="text-sm font-semibold">Bring your model</span>
              </div>
              <p className="text-xs text-slate-500">
                Open weights on your own GPU, or any model via BYOK/OpenRouter. Characterize per-model, then register a hardening pack to your HF.
              </p>
            </div>
          </div>

          {/* Tools section */}
          <div className="pt-16 mt-16 border-t border-night-600 space-y-8">
            <div className="text-center space-y-3 pb-8">
              <h2 className="text-3xl font-serif font-bold text-gradient">
                Steering Tools
              </h2>
              <p className="text-slate-400 text-sm max-w-xl mx-auto">
                Explore, build, and evaluate steering in multiple modes
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-w-4xl mx-auto">
              <Link href="/studio" className="card p-6 hover:border-indigo-600/40 transition-colors group">
                <div className="space-y-2">
                  <h3 className="font-semibold text-slate-100 group-hover:text-indigo-300 transition">
                    Live Steering Studio
                  </h3>
                  <p className="text-xs text-slate-500">
                    Real-time steering with prompt, concept, amplitude, and timing control
                  </p>
                </div>
              </Link>

              <Link href="/build" className="card p-6 hover:border-teal-600/40 transition-colors group">
                <div className="space-y-2">
                  <h3 className="font-semibold text-slate-100 group-hover:text-teal-300 transition">
                    Steering Builder
                  </h3>
                  <p className="text-xs text-slate-500">
                    Create custom steering from concepts or contrastive examples, export as packs
                  </p>
                </div>
              </Link>

              <Link href="/jailbreak" className="card p-6 hover:border-red-600/40 transition-colors group">
                <div className="space-y-2">
                  <h3 className="font-semibold text-slate-100 group-hover:text-red-300 transition">
                    Jailbreak Lab
                  </h3>
                  <p className="text-xs text-slate-500">
                    Defensive research: test refusal steering on adversarial prompts
                  </p>
                </div>
              </Link>

              <Link href="/align" className="card p-6 hover:border-teal-600/40 transition-colors group">
                <div className="space-y-2">
                  <h3 className="font-semibold text-slate-100 group-hover:text-teal-300 transition">
                    Alignment Lab
                  </h3>
                  <p className="text-xs text-slate-500">
                    Test steering toward truthfulness on TruthfulQA-style questions
                  </p>
                </div>
              </Link>

              <Link href="/compare" className="card p-6 hover:border-indigo-600/40 transition-colors group">
                <div className="space-y-2">
                  <h3 className="font-semibold text-slate-100 group-hover:text-indigo-300 transition">
                    Arm Comparison
                  </h3>
                  <p className="text-xs text-slate-500">
                    Compare timing arms with effect sizes and metrics
                  </p>
                </div>
              </Link>

              <Link href="/lens" className="card p-6 hover:border-purple-600/40 transition-colors group">
                <div className="space-y-2">
                  <h3 className="font-semibold text-slate-100 group-hover:text-purple-300 transition">
                    Lens Playground
                  </h3>
                  <p className="text-xs text-slate-500">
                    Visualize and explore the workspace band activation
                  </p>
                </div>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Architecture */}
      <ArchitecturePanel />

      {/* Footer */}
      <footer className="border-t border-night-600 bg-night-900/50 py-8 px-6">
        <div className="max-w-7xl mx-auto flex items-center justify-center gap-6 text-xs text-slate-500">
          <p>
            prabodha is an open research project.{" "}
            <Link href="https://github.com/SharathSPhD/prabodha" className="text-indigo-400 hover:text-indigo-300">
              View on GitHub
            </Link>
            {" · "}
            <a
              href="https://www.preprints.org/frontend/manuscript/5b72d5c7d0e37f4f5b222acfab709652/download_pub"
              target="_blank"
              rel="noopener noreferrer"
              className="text-indigo-400 hover:text-indigo-300"
            >
              Read the paper
            </a>
          </p>
          <AdminLink />
        </div>
      </footer>
    </main>
  );
}
