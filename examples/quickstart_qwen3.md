# Quickstart: lens + steer on Qwen3-4B (public model)

The exact sequence the program itself ran (gates L10–L15); expected numbers below are
the committed gate results, so you can tell instrument drift from user error. One CUDA
device, ~6 GB weights + lens fitting headroom; every step is resumable.

## 1. Fit a band-targeted lens
```bash
prabodha lens-fit --model configs/models/qwen3.yaml --lens configs/lens_mid.yaml \
  --out outputs/lens_qwen3_mid30.pt
```
`target_layer` in the lens config must be the band-exit layer (30 for this model), not
the final layer — final-target lenses cannot see band content (gate L2b).

## 2. Probe the write site and calibrate amplitude
Qwen3's band-exit Jacobians are weak (max‖J‖/√d ≈ 1.6 vs 10–20 on stronger-transport
models), so writes need α ≈ 0.3, not the 0.05–0.1 that works elsewhere. The rule that
transfers: **amplitude ∝ 1/lens-transport-strength**, then sweep to confirm you're on
the monotone part of the dose curve:
```bash
for A in 0.1 0.2 0.3 0.45; do
  prabodha steer --model configs/models/qwen3.yaml \
    --mid-lens outputs/lens_qwen3_mid30.pt --exp configs/experiments/e13full.yaml \
    --alpha $A --norm-cap-rel $A --loop demo --out gates/demo_a$A.json
done
```
Expected (gates L14-amp, L15-amp-joint; three seeds each within ±0.05): gated lift
`0.00–0.05 → ~0.18 → 0.40–0.48 → 0.72–0.78`, trajectory-entropy delta within ±0.5 nats
at every point. Pass BOTH `--alpha` and `--norm-cap-rel` — the cap silently binds
otherwise.

## 3. Read the gate
Each run writes a dual-verdict gate JSON. The numbers that matter:
- `aggregates.entropy_gated.lift` — concept surfacing over baseline
- `aggregates.entropy_gated.step_entropy_delta` — the freedom-budget spend
- `aggregates.entropy_gated.writes_per_gen` — ~11 of 40 decode steps at τ=P60

Sanity rules learned the hard way: sampling decoding is required (greedy masks all
decode-time writes — gate L4); lift magnitudes are corpus-dependent, so verify on your
own stubs (gate L16-corpus); treat `--record-readback` verdicts as a weak first filter,
not an acceptance test (BA ≈ 0.59 pooled — gate L16-corpus).
