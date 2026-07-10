import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "prabodha — LLM steering via workspace recognition",
  description: "Verify the philosophical doctrine for steering frozen language models.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-night-950 text-slate-100">{children}</body>
    </html>
  );
}
