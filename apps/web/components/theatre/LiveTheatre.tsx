"use client";

import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase/client";
import { getMyTier } from "@/lib/account.server";

export default function LiveTheatre() {
  const [tier, setTier] = useState<string | null>(null);

  useEffect(() => {
    getMyTier().then(setTier);
  }, []);

  if (tier !== "admin") {
    return (
      <div className="card p-6">
        <p className="text-sm text-red-300">
          Live mode is restricted to admin accounts.
        </p>
      </div>
    );
  }

  return (
    <div className="card p-6">
      <h2 className="text-lg font-semibold text-slate-100 mb-3">Live Steering (Coming soon)</h2>
      <p className="text-sm text-slate-500">
        Admin users can trigger live steering runs via the gateway and watch the trace in real-time.
      </p>
    </div>
  );
}
