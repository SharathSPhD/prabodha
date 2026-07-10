// PLACEHOLDER — generated data pending export_app_data.py; do not publish
// Structural dummy for local development ONLY. Every number below is fake
// (shape-correct, value-meaningless); the deploy workflow refuses to publish
// while this marker line is present. The real file is produced by
// scripts/tools/export_app_data.py from gates/ and outputs/traces/.

window.PRABODHA = {
  results: {
    claims: [
      {
        id: "core_steering",
        text: "Event-gated writes steer within entropy budget (core claim)",
        tier: "confirm, 6 seeds",
        gates: ["gates/gate_L9_alignconf.json", "gates/gate_L11_finetune.json"],
        numbers: { "seeds": 6, "lift_mean": 0.047, "lift_p": 0.016 }
      },
      {
        id: "transfer",
        text: "Method transfers to a 2nd model via calibration recipe",
        tier: "confirm, 4 seeds",
        gates: ["gates/gate_L13_recipe.json", "gates/gate_L14-ms.json"],
        numbers: { "seeds": 4, "nemotron_lift": 0.031 }
      },
      {
        id: "amplitude",
        text: "Amplitude ∝ 1/lens-strength; dose monotone in active range",
        tier: "confirm (Qwen3) / screen (Nemotron)",
        gates: ["gates/gate_L14-amp.json", "gates/gate_L15-amp.json", "gates/gate_L16-fine.json"],
        numbers: { "qwen3_alpha_sweep": [0.05, 0.1, 0.2], "nemotron_screen": true }
      },
      {
        id: "readback",
        text: "Readback verdict is weak signal (BA ≈ 0.59 at n=120) — never acceptance gate alone",
        tier: "honest negative",
        gates: ["gates/gate_L14-readback.json", "gates/gate_L15-readback.json"],
        numbers: { "ba": 0.59, "n": 120 }
      }
    ]
  },
  replays: {
    fire: {
      slug: "fire",
      prompt: "the fire remembers rivers",
      concept: "fire",
      model_id: "Qwen/Qwen3-4B",
      description: "Flagship replay: entropy-gated write steers a fire-concept band write with real training data.",
      trace_ref: "outputs/traces/fire_case_L11_seed42.json"
    }
  }
};
