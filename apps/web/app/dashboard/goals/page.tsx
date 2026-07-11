"use client";

import AlignmentGoals from "@/components/goals/AlignmentGoals";
import Link from "next/link";
import { ChevronLeft } from "lucide-react";

export default function GoalsPage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-night-950 to-night-900 py-12 px-6">
      <div className="mx-auto max-w-4xl">
        <div className="mb-8 space-y-3">
          <Link href="/dashboard" className="flex items-center gap-2 text-slate-400 hover:text-slate-300 text-sm">
            <ChevronLeft className="w-4 h-4" />
            Back to Dashboard
          </Link>
          <h1 className="text-3xl font-serif font-bold text-slate-100">
            Alignment Goals
          </h1>
          <p className="text-sm text-slate-500">
            Define and register hardening packs for alignment goals.
          </p>
        </div>

        <AlignmentGoals />
      </div>
    </main>
  );
}
