"use client";

import Link from "next/link";
import { ArrowLeft, Shield, Lock } from "lucide-react";
import DepthToggle from "@/components/DepthToggle";
import JailbreakLab from "@/components/labs/JailbreakLab";
import MoatReplay from "@/components/labs/MoatReplay";
import MoatProof from "@/components/MoatProof";
import MechanismSelector from "@/components/MechanismSelector";
import { useState } from "react";

export default function JailbreakPage() {
  const [activeTab, setActiveTab] = useState<"lab" | "moat" | "mechanisms" | "replay">("moat");

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
                <Shield className="w-5 h-5" />
                Jailbreak Defense Lab
              </h1>
              <p className="text-xs text-slate-500 mt-1">
                Real moat proof + mechanism library + interactive steering tests
              </p>
            </div>
          </div>
          <DepthToggle />
        </div>
      </nav>

      {/* Tabs */}
      <div className="border-b border-night-600 bg-night-900/30 sticky top-16 z-40">
        <div className="mx-auto max-w-7xl px-6">
          <div className="flex gap-2">
            <button
              onClick={() => setActiveTab("moat")}
              className={`px-4 py-3 text-sm font-semibold border-b-2 transition ${
                activeTab === "moat"
                  ? "border-indigo-500 text-indigo-300"
                  : "border-transparent text-slate-500 hover:text-slate-300"
              }`}
            >
              <Lock className="w-4 h-4 inline mr-2" />
              Moat Proof
            </button>
            <button
              onClick={() => setActiveTab("mechanisms")}
              className={`px-4 py-3 text-sm font-semibold border-b-2 transition ${
                activeTab === "mechanisms"
                  ? "border-indigo-500 text-indigo-300"
                  : "border-transparent text-slate-500 hover:text-slate-300"
              }`}
            >
              <Shield className="w-4 h-4 inline mr-2" />
              Mechanisms
            </button>
            <button
              onClick={() => setActiveTab("replay")}
              className={`px-4 py-3 text-sm font-semibold border-b-2 transition ${
                activeTab === "replay"
                  ? "border-indigo-500 text-indigo-300"
                  : "border-transparent text-slate-500 hover:text-slate-300"
              }`}
            >
              <Lock className="w-4 h-4 inline mr-2" />
              Demo Replay
            </button>
            <button
              onClick={() => setActiveTab("lab")}
              className={`px-4 py-3 text-sm font-semibold border-b-2 transition ${
                activeTab === "lab"
                  ? "border-indigo-500 text-indigo-300"
                  : "border-transparent text-slate-500 hover:text-slate-300"
              }`}
            >
              Interactive Testing
            </button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="mx-auto max-w-7xl px-6 py-8">
        {activeTab === "moat" && <MoatProof />}
        {activeTab === "mechanisms" && <MechanismSelector />}
        {activeTab === "replay" && <MoatReplay />}
        {activeTab === "lab" && <JailbreakLab />}
      </div>
    </main>
  );
}
