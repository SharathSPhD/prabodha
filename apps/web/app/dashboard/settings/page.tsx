"use client";

import { useState } from "react";
import { saveCredentials, getMyCredentials } from "@/lib/account";

const PROVIDERS = [
  { id: "openrouter", label: "OpenRouter" },
  { id: "anthropic", label: "Anthropic" },
  { id: "openai", label: "OpenAI" },
  { id: "llamacpp", label: "LlamaCpp" },
  { id: "huggingface", label: "HuggingFace" },
];

export default function SettingsPage() {
  const [provider, setProvider] = useState("openrouter");
  const [apiKey, setApiKey] = useState("");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState<"success" | "error">("success");

  async function handleSave() {
    setSaving(true);
    setMessage("");

    try {
      await saveCredentials(provider, apiKey.trim());
      setMessage("Credentials saved securely.");
      setMessageType("success");
      setApiKey("");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Failed to save");
      setMessageType("error");
    } finally {
      setSaving(false);
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-night-950 to-night-900 py-12 px-6">
      <div className="mx-auto max-w-2xl">
        <h1 className="text-3xl font-serif font-bold text-slate-100 mb-8">
          Settings
        </h1>

        <div className="card p-6 space-y-6">
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-slate-100">
              LLM API Keys (BYOK)
            </h2>
            <p className="text-sm text-slate-500">
              Your API keys are encrypted at rest and in transit. They&apos;re never sent to our servers.
            </p>

            <div className="space-y-3">
              <div>
                <label className="label">Provider</label>
                <select
                  value={provider}
                  onChange={(e) => setProvider(e.target.value)}
                  className="input"
                >
                  {PROVIDERS.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="label">API Key</label>
                <input
                  type="password"
                  placeholder="sk-..."
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="input"
                />
                <p className="text-xs text-slate-600 mt-1">
                  For OpenRouter, find it at https://openrouter.ai/keys
                </p>
              </div>

              <button
                onClick={handleSave}
                disabled={saving || !apiKey.trim()}
                className="btn-primary w-full justify-center"
              >
                {saving ? "Saving..." : "Save API Key"}
              </button>
            </div>

            {message && (
              <p
                className={`text-sm ${
                  messageType === "success"
                    ? "text-teal-300"
                    : "text-red-300"
                }`}
              >
                {message}
              </p>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
