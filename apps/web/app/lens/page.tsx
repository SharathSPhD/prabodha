"use client";

import Link from "next/link";
import { ArrowLeft, Eye } from "lucide-react";
import DepthToggle from "@/components/DepthToggle";
import LensPlayground from "@/components/lens/LensPlayground";

export default function LensPage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-night-950 to-night-900">
      {/* Header */}
      <nav className="border-b border-night-600 bg-night-900/50 backdrop-blur-md sticky top-0 z-50">
        <div className="mx-auto max-w-7xl px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/" className="btn-ghost px-2 py-1">
              <ArrowLeft className="w-4 h-4" />
            </Link>
            <div>
              <h1 className="text-2xl font-serif font-bold text-gradient flex items-center gap-2">
                <Eye className="w-5 h-5" />
                Lens Playground
              </h1>
              <p className="text-xs text-slate-500 mt-1">
                Explore the workspace band: interactive slice visualization and verbalization
              </p>
            </div>
          </div>
          <DepthToggle />
        </div>
      </nav>

      {/* Main content */}
      <div className="mx-auto max-w-7xl px-6 py-8">
        <LensPlayground />
      </div>
    </main>
  );
}
