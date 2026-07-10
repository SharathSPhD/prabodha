---
name: steer-verify
description: Apply a budgeted, event-gated concept write to a decoder LLM's workspace band and verify uptake by band-lens readback. Use when the user wants to steer generation toward a concept, test steering timing schedules, or check whether a write was actually taken up.
---

# Steer + verify

Requires a fitted band-targeted lens (see the lens-map skill) and a CUDA device.

## Workflow

Run the steering experiment CLI (arms: baseline, prefill-only, entropy-gated,
rate-matched control):
```bash
prabodha steer --model configs/models/<model>.yaml --mid-lens outputs/lens_<model>.pt \
  --exp configs/experiments/<exp>.yaml --loop <tag> --out gates/steer.json \
  [--alpha A --norm-cap-rel A] [--seed S] [--record-readback]
```
Read the gate JSON's `aggregates`: per-arm `lift` (concept surfacing over baseline),
`step_entropy_delta` (the freedom budget spend), `writes_per_gen`.

## Defaults that are findings, not preferences
- **Sampling decoding required.** Greedy argmax mechanically masks all decode-time
  writes (identical outputs across schedules). The exp config must set
  `decoding: {do_sample: true, temperature: ...}`.
- **Entropy-gated timing** writes at uncommitted moments (step entropy above a
  self-calibrated τ = P60 of the baseline's own entropies). It matches continuous
  steering at ~1/4 the writes and beats commitment-flash gating.
- **Amplitude must be calibrated per model**: working amplitude scales inversely with
  the lens's transport strength (weak Jacobians ⇒ larger α). Sweep α with
  `--alpha A --norm-cap-rel A` (BOTH — the cap silently binds otherwise) and expect a
  monotone dose response within the entropy budget.
- **Budget is reported on every run** (trajectory-mean entropy delta under sampling;
  |Δ| ≤ 0.5 nats is the tested envelope).
- **Readback** (`--record-readback`) records raw pre/post concept ranks at the write
  port through the band lens. Calibrated verdict setting: rank ≤ 5 at any readback
  layer and at the last (top_m=5, no rank-gain clause). Treat the verdict as a WEAK
  signal, never as an acceptance gate alone: pooled across three corpora (n=120) its
  balanced accuracy is ≈ 0.59 (0.64 on the single best corpus), and it over-promises
  far more often than it under-promises. Behavioral checks on generated text are the
  ground truth; readback is a cheap first filter.
- Lift magnitudes are corpus-dependent, and so is the amplitude you need: a stub style
  that steers weakly at one α often steers reliably at 2α, still within budget. Calibrate
  amplitude to BOTH the model (inverse lens strength) and your corpus (stub difficulty);
  verify on your own stubs before relying on a number.
