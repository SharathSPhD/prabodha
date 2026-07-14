"use client";

import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/Tabs";
import ReplayTheatre from "@/components/theatre/ReplayTheatre";
import LiveTheatre from "@/components/theatre/LiveTheatre";
import BYOKTheatre from "@/components/theatre/BYOKTheatre";
import { SiteNav } from "@/components/SiteNav";

export default function TheatrePage() {
  const [mode, setMode] = useState<"replay" | "live" | "byok">("replay");

  return (
    <main className="min-h-screen bg-gradient-to-b from-night-950 to-night-900">
      <SiteNav />
      <div className="mx-auto max-w-6xl px-6 py-12">
        <div className="mb-8 space-y-3">
          <h1 className="text-4xl font-serif font-bold text-gradient">
            J-space Theatre
          </h1>
          <p className="text-sm text-slate-400">
            Watch steering unfold: SteerTrace visualization, entropy gating, readback verdicts, and dose response.
          </p>
        </div>

        <Tabs value={mode} onValueChange={(v) => setMode(v as any)} className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 max-w-md">
            <TabsTrigger value="replay">Replay</TabsTrigger>
            <TabsTrigger value="live">Live (admin)</TabsTrigger>
            <TabsTrigger value="byok">BYOK</TabsTrigger>
          </TabsList>

          <TabsContent value="replay">
            <ReplayTheatre />
          </TabsContent>

          <TabsContent value="live">
            <LiveTheatre />
          </TabsContent>

          <TabsContent value="byok">
            <BYOKTheatre />
          </TabsContent>
        </Tabs>
      </div>
    </main>
  );
}
