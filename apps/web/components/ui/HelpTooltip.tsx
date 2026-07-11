"use client";

import { useState } from "react";
import { HelpCircle } from "lucide-react";

interface HelpTooltipProps {
  text: string;
  className?: string;
}

export function HelpTooltip({ text, className = "" }: HelpTooltipProps) {
  const [show, setShow] = useState(false);

  return (
    <div className="relative inline-block">
      <button
        type="button"
        onClick={() => setShow(!show)}
        onMouseEnter={() => setShow(true)}
        onMouseLeave={() => setShow(false)}
        className={`inline-flex items-center justify-center w-4 h-4 ml-1 text-slate-500 hover:text-indigo-400 transition ${className}`}
        aria-label="Help"
      >
        <HelpCircle className="w-4 h-4" />
      </button>

      {show && (
        <div
          className="absolute z-50 bottom-full left-0 mb-2 w-48 p-2 text-xs text-slate-300 bg-night-800 border border-night-600 rounded-lg shadow-lg"
          role="tooltip"
        >
          {text}
        </div>
      )}
    </div>
  );
}
