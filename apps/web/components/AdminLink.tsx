"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Settings } from "lucide-react";
import { getMyTier } from "@/lib/account.server";

export function AdminLink() {
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const tier = await getMyTier();
        setIsAdmin(tier === "admin");
      } catch (err) {
        console.error("Failed to check admin status:", err);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading || !isAdmin) return null;

  return (
    <Link
      href="/dashboard/admin"
      className="text-xs text-slate-500 hover:text-indigo-400 transition flex items-center gap-1"
      title="Admin dashboard"
    >
      <Settings className="w-3 h-3" />
      Admin
    </Link>
  );
}
