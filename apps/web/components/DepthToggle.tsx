"use client";

import { useEffect, useState } from "react";
import { getDepthMode, setDepthMode } from "@/lib/depth-toggle";
import type { DepthMode } from "@/lib/depth-toggle";

export default function DepthToggle() {
  const [mode, setMode] = useState<DepthMode>("explorer");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMode(getDepthMode());
    setMounted(true);
  }, []);

  const handleToggle = (newMode: DepthMode) => {
    setMode(newMode);
    setDepthMode(newMode);
  };

  if (!mounted) return null;

  return (
    <div className="flex items-center gap-2 text-xs">
      <span className="text-slate-500">View:</span>
      <button
        onClick={() => handleToggle("explorer")}
        className={`px-2 py-1 rounded transition-colors ${
          mode === "explorer"
            ? "bg-indigo-600/30 text-indigo-300"
            : "text-slate-500 hover:text-slate-400"
        }`}
        title="Plain-language explanations and examples"
      >
        Explorer
      </button>
      <button
        onClick={() => handleToggle("researcher")}
        className={`px-2 py-1 rounded transition-colors ${
          mode === "researcher"
            ? "bg-indigo-600/30 text-indigo-300"
            : "text-slate-500 hover:text-slate-400"
        }`}
        title="Deep mechanism, real math and methods"
      >
        Researcher
      </button>
    </div>
  );
}
