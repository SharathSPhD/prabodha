"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { getMyTier } from "@/lib/account.server";

export default function LiveTheatre() {
  const [tier, setTier] = useState<string | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    getMyTier()
      .then(setTier)
      .finally(() => setLoaded(true));
  }, []);

  if (!loaded) {
    return (
      <div className="card p-6">
        <div className="h-4 w-40 animate-pulse rounded bg-night-700" />
      </div>
    );
  }

  if (tier !== "admin") {
    return (
      <div className="card p-6">
        <h2 className="mb-2 text-lg font-semibold text-slate-100">Live steering is admin-only</h2>
        <p className="mb-4 text-sm text-slate-400">
          Live runs execute on the admin's GB10 GPU, so they're restricted to admin accounts.
          You can still watch real recorded runs in <strong className="text-slate-200">Replay</strong>,
          or run steering on your own model with a key in <strong className="text-slate-200">BYOK</strong>.
        </p>
      </div>
    );
  }

  return (
    <div className="card p-6">
      <h2 className="mb-2 text-lg font-semibold text-slate-100">Live steering</h2>
      <p className="mb-5 text-sm text-slate-400">
        Full live steering — write concepts into the workspace band in real time, watch the
        SteerTrace unfold, and inspect entropy gating and readback verdicts — runs in the
        Live Steering Studio, which streams token-by-token from the gateway.
      </p>
      <Link href="/studio" className="btn-primary">
        Open the Live Studio
        <ArrowRight className="h-4 w-4" />
      </Link>
    </div>
  );
}
