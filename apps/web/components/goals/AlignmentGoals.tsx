"use client";

import { useState, useEffect } from "react";
import { saveGoal, listGoals, deleteGoal, type Goal } from "@/lib/account";
import { getMyCredentials } from "@/lib/account";
import { Trash2, Plus } from "lucide-react";

interface Mechanism {
  key: string;
  name: string;
  space: "prompt" | "activation";
  tier: number;
  summary: string;
}

interface MoatData {
  mechanisms: Mechanism[];
}

interface MoatReplayData {
  model: string;
  read_layer: number;
  tau: number;
  projection_separation: { benign_range: number[]; attack_range: number[] };
  arms: Record<string, { attack_asr: number; benign_over_refusal: number }>;
}

export default function AlignmentGoals() {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [mechanisms, setMechanisms] = useState<Mechanism[]>([]);
  const [moatReplay, setMoatReplay] = useState<MoatReplayData | null>(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState<"success" | "error">("success");

  // Form state
  const [formOpen, setFormOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    positiveExamplesText: "",
    negativeExamplesText: "",
    mechanism: "",
  });

  // Register state
  const [registeringGoalId, setRegisteringGoalId] = useState<string | null>(null);
  const [registerData, setRegisterData] = useState<Record<string, {
    baseModel: string;
    hfToken: string;
    useMoat: boolean;
    registering: boolean;
    result: { ok: boolean; url?: string; error?: string } | null;
  }>>({});

  useEffect(() => {
    Promise.all([listGoals(), fetchMechanisms(), fetchMoatReplay()])
      .then(([g, _, __]) => {
        setGoals(g);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load data:", err);
        setLoading(false);
      });
  }, []);

  async function fetchMechanisms() {
    try {
      const res = await fetch("/data/moat.json");
      const data: MoatData = await res.json();
      setMechanisms(data.mechanisms);
    } catch (err) {
      console.error("Failed to fetch mechanisms:", err);
    }
  }

  async function fetchMoatReplay() {
    try {
      const res = await fetch("/data/moat_replay.json");
      const data: MoatReplayData = await res.json();
      setMoatReplay(data);
    } catch (err) {
      console.error("Failed to fetch moat replay:", err);
    }
  }

  async function handleCreateGoal(e: React.FormEvent) {
    e.preventDefault();
    setMessage("");

    if (!formData.name.trim()) {
      setMessage("Goal name is required");
      setMessageType("error");
      return;
    }

    if (!formData.mechanism) {
      setMessage("Mechanism is required");
      setMessageType("error");
      return;
    }

    try {
      const selectedMech = mechanisms.find(m => m.key === formData.mechanism);
      if (!selectedMech) {
        throw new Error("Invalid mechanism selected");
      }

      const newGoal = await saveGoal({
        name: formData.name.trim(),
        description: formData.description.trim(),
        positive_examples: formData.positiveExamplesText
          .split("\n")
          .map(s => s.trim())
          .filter(Boolean),
        negative_examples: formData.negativeExamplesText
          .split("\n")
          .map(s => s.trim())
          .filter(Boolean),
        mechanism: formData.mechanism,
        space: selectedMech.space,
      });

      setGoals([newGoal, ...goals]);
      setFormData({
        name: "",
        description: "",
        positiveExamplesText: "",
        negativeExamplesText: "",
        mechanism: "",
      });
      setFormOpen(false);
      setMessage("Goal created successfully");
      setMessageType("success");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Failed to create goal");
      setMessageType("error");
    }
  }

  async function handleDeleteGoal(goalId: string) {
    try {
      await deleteGoal(goalId);
      setGoals(goals.filter(g => g.id !== goalId));
      setMessage("Goal deleted");
      setMessageType("success");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Failed to delete goal");
      setMessageType("error");
    }
  }

  async function handleRegisterPack(goal: Goal) {
    const key = goal.id;
    const state = registerData[key] || {
      baseModel: "google/gemma-2-2b-it",
      hfToken: "",
      useMoat: false,
      registering: false,
      result: null,
    };

    if (!state.registering && !state.result) {
      // Show form
      setRegisterData({
        ...registerData,
        [key]: state,
      });
      setRegisteringGoalId(key);

      // Preload HF token from settings
      try {
        const token = await getMyCredentials("huggingface");
        if (token) {
          setRegisterData(prev => ({
            ...prev,
            [key]: { ...prev[key], hfToken: token },
          }));
        }
      } catch (err) {
        console.error("Failed to load HF token:", err);
      }
      return;
    }

    if (state.result) {
      setRegisteringGoalId(null);
      setRegisterData({
        ...registerData,
        [key]: { ...state, result: null },
      });
      return;
    }

    // Perform registration
    setRegisterData({
      ...registerData,
      [key]: { ...state, registering: true },
    });

    try {
      const measured = state.useMoat && moatReplay && moatReplay.model === state.baseModel
        ? {
            model: moatReplay.model,
            read_layer: moatReplay.read_layer,
            tau: moatReplay.tau,
            projection_separation: moatReplay.projection_separation,
            arms: moatReplay.arms,
          }
        : null;

      const res = await fetch("/api/register-pack", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          goal,
          baseModel: state.baseModel,
          measured,
          hfToken: state.hfToken || undefined,
        }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || "Registration failed");
      }

      setRegisterData({
        ...registerData,
        [key]: {
          ...state,
          registering: false,
          result: { ok: true, url: data.url },
        },
      });
    } catch (err) {
      setRegisterData({
        ...registerData,
        [key]: {
          ...state,
          registering: false,
          result: { ok: false, error: err instanceof Error ? err.message : "Unknown error" },
        },
      });
    }
  }

  if (loading) {
    return (
      <div className="text-center text-slate-400">
        <p>Loading...</p>
      </div>
    );
  }

  const selectedMech = formData.mechanism ? mechanisms.find(m => m.key === formData.mechanism) : null;

  return (
    <div className="space-y-8">
      {/* Create Goal Form */}
      <div className="card p-6 space-y-4">
        {!formOpen ? (
          <button
            onClick={() => setFormOpen(true)}
            className="btn-primary w-full justify-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Create Alignment Goal
          </button>
        ) : (
          <form onSubmit={handleCreateGoal} className="space-y-4">
            <div>
              <label className="label">Goal Name</label>
              <input
                type="text"
                placeholder="e.g., Refuse jailbreak attempts"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                className="input"
              />
            </div>

            <div>
              <label className="label">Description (plain-language policy)</label>
              <textarea
                placeholder="What behavior are you trying to enforce?"
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                className="input min-h-20"
              />
            </div>

            <div>
              <label className="label">Mechanism</label>
              <select
                value={formData.mechanism}
                onChange={(e) =>
                  setFormData({ ...formData, mechanism: e.target.value })
                }
                className="input"
              >
                <option value="">Select a mechanism...</option>
                {mechanisms.map((m) => (
                  <option key={m.key} value={m.key}>
                    {m.name} (Tier {m.tier}, {m.space})
                  </option>
                ))}
              </select>
              {selectedMech && (
                <p className="text-xs text-slate-500 mt-2">{selectedMech.summary}</p>
              )}
            </div>

            <div>
              <label className="label">Positive Examples (desired behaviors, one per line)</label>
              <textarea
                placeholder="Example: Don't help with illegal activities&#10;Example: Refuse to impersonate me"
                value={formData.positiveExamplesText}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    positiveExamplesText: e.target.value,
                  })
                }
                className="input min-h-24 font-mono text-xs"
              />
            </div>

            <div>
              <label className="label">Negative Examples (undesired behaviors, one per line)</label>
              <textarea
                placeholder="Example: Helping create malware&#10;Example: Pretending to be an unrestricted AI"
                value={formData.negativeExamplesText}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    negativeExamplesText: e.target.value,
                  })
                }
                className="input min-h-24 font-mono text-xs"
              />
            </div>

            <div className="flex gap-2">
              <button type="submit" className="btn-primary flex-1">
                Create
              </button>
              <button
                type="button"
                onClick={() => setFormOpen(false)}
                className="btn-secondary flex-1"
              >
                Cancel
              </button>
            </div>
          </form>
        )}
      </div>

      {message && (
        <div
          className={`p-3 rounded text-sm ${
            messageType === "success"
              ? "bg-teal-900/30 text-teal-300 border border-teal-700/50"
              : "bg-red-900/30 text-red-300 border border-red-700/50"
          }`}
        >
          {message}
        </div>
      )}

      {/* Goals List */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-slate-100">Your Goals ({goals.length})</h2>

        {goals.length === 0 ? (
          <div className="card p-6 text-center text-slate-500">
            <p>No alignment goals yet. Create one to get started.</p>
          </div>
        ) : (
          goals.map((goal) => {
            const regState = registerData[goal.id] || { baseModel: "google/gemma-2-2b-it", hfToken: "", useMoat: false, registering: false, result: null };
            const isMoatEligible = moatReplay && regState.baseModel === moatReplay.model;

            return (
              <div key={goal.id} className="card p-6 space-y-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-slate-100">{goal.name}</h3>
                    <p className="text-sm text-slate-400 mt-1">{goal.description}</p>
                    <div className="flex gap-4 mt-3 text-xs text-slate-500">
                      <span>
                        <strong>{goal.positive_examples.length}</strong> positive examples
                      </span>
                      <span>
                        <strong>{goal.negative_examples.length}</strong> negative examples
                      </span>
                      <span>
                        Mechanism: <strong>{goal.mechanism}</strong> ({goal.space})
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDeleteGoal(goal.id)}
                    className="text-slate-500 hover:text-red-400 transition"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>

                {/* Register Pack Section */}
                <div className="border-t border-slate-700/50 pt-4 space-y-3">
                  <h4 className="font-semibold text-slate-200 text-sm">Register Hardening Pack to HuggingFace</h4>
                  <p className="text-xs text-slate-500">
                    This registers a hardening PACK (spec + model card + loader) to your HuggingFace account — not modified weights.
                  </p>

                  {registeringGoalId === goal.id && !regState.result ? (
                    <div className="space-y-3 bg-slate-900/30 p-3 rounded">
                      <div>
                        <label className="label">Base Model</label>
                        <input
                          type="text"
                          placeholder="e.g., google/gemma-2-2b-it"
                          value={regState.baseModel}
                          onChange={(e) =>
                            setRegisterData({
                              ...registerData,
                              [goal.id]: { ...regState, baseModel: e.target.value },
                            })
                          }
                          className="input text-sm"
                        />
                      </div>

                      <div>
                        <label className="label">HuggingFace Token</label>
                        <input
                          type="password"
                          placeholder="Leave blank to use your saved Settings token"
                          value={regState.hfToken}
                          onChange={(e) =>
                            setRegisterData({
                              ...registerData,
                              [goal.id]: { ...regState, hfToken: e.target.value },
                            })
                          }
                          className="input text-sm"
                        />
                      </div>

                      {isMoatEligible && (
                        <label className="flex items-center gap-2 text-sm cursor-pointer">
                          <input
                            type="checkbox"
                            checked={regState.useMoat}
                            onChange={(e) =>
                              setRegisterData({
                                ...registerData,
                                [goal.id]: { ...regState, useMoat: e.target.checked },
                              })
                            }
                          />
                          <span className="text-slate-300">
                            Attach proven gemma-2-2b moat as measured results
                          </span>
                        </label>
                      )}

                      {isMoatEligible && (
                        <p className="text-xs text-slate-400">
                          See the real before/after transcripts this pack is measured on in the{" "}
                          <a href="/jailbreak" className="text-indigo-400 underline">
                            Jailbreak Defense Lab → Demo Replay
                          </a>
                          . For a custom goal on your own base model, effect is measured at serve time —
                          this pack ships as an unmeasured recipe until you run <code>prabodha characterize</code>.
                        </p>
                      )}

                      <div className="flex gap-2">
                        <button
                          onClick={() => handleRegisterPack(goal)}
                          disabled={regState.registering}
                          className="btn-primary flex-1 text-sm"
                        >
                          {regState.registering ? "Registering..." : "Register"}
                        </button>
                        <button
                          onClick={() => setRegisteringGoalId(null)}
                          className="btn-secondary flex-1 text-sm"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : regState.result ? (
                    <div
                      className={`p-3 rounded text-sm space-y-2 ${
                        regState.result.ok
                          ? "bg-teal-900/30 text-teal-300 border border-teal-700/50"
                          : "bg-red-900/30 text-red-300 border border-red-700/50"
                      }`}
                    >
                      {regState.result.ok ? (
                        <>
                          <p className="font-semibold">Registration successful!</p>
                          <a
                            href={regState.result.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="underline hover:opacity-80"
                          >
                            View on HuggingFace
                          </a>
                        </>
                      ) : (
                        <>
                          <p className="font-semibold">Registration failed</p>
                          <p>{regState.result.error}</p>
                        </>
                      )}
                      <button
                        onClick={() => handleRegisterPack(goal)}
                        className="btn-secondary text-sm w-full mt-2"
                      >
                        Close
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => handleRegisterPack(goal)}
                      className="btn-primary w-full text-sm"
                    >
                      Register Pack
                    </button>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
