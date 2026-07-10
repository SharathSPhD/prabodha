"use client";

import { useState } from "react";
import { createClient } from "@/lib/supabase/client";

export default function BYOKTheatre() {
  const [provider, setProvider] = useState("openrouter");
  const [apiKey, setApiKey] = useState("");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  async function saveKey() {
    setSaving(true);
    setMessage("");

    try {
      const supabase = createClient();
      if (!supabase) throw new Error("Supabase not configured");

      const { error } = await supabase
        .from("user_llm_credentials")
        .upsert({ provider, api_key: apiKey.trim() })
        .eq("provider", provider);

      if (error) throw error;
      setMessage("Credentials saved securely.");
      setApiKey("");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Failed to save.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="card p-6 space-y-4 max-w-md">
      <div className="space-y-2">
        <h3 className="text-lg font-semibold text-slate-100">Bring Your Own Key</h3>
        <p className="text-xs text-slate-500">
          Provide your API key to use your own LLM endpoint for steering.
        </p>
      </div>

      <div className="space-y-3">
        <div>
          <label className="label">Provider</label>
          <select
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
            className="input"
          >
            <option value="openrouter">OpenRouter</option>
            <option value="anthropic">Anthropic</option>
            <option value="openai">OpenAI</option>
            <option value="llamacpp">LlamaCpp</option>
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
        </div>

        <button
          onClick={saveKey}
          disabled={saving || !apiKey}
          className="btn-primary w-full justify-center"
        >
          {saving ? "Saving..." : "Save securely"}
        </button>
      </div>

      {message && (
        <p className="text-xs text-teal-300">{message}</p>
      )}
    </div>
  );
}
