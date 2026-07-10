# Quickstart: lens + steer on Nemotron (second lineage)

The Nemotron transfer sequence (gates L12-L15); this model has stronger band-exit
Jacobians than Qwen3, so steering works at lower amplitudes (α ≈ 0.1–0.2).
Expected numbers below are the committed gate results.

## 1. Fit a band-targeted lens

```bash
prabodha lens-fit --model configs/models/nemotron.yaml --lens configs/lens_mid.yaml \
  --out outputs/lens_nemotron_mid30.pt
```

The target layer must be the band-exit layer for Nemotron (verify in your model config).

## 2. Calibrate amplitude and verify dose curve

Nemotron's Jacobians are stronger, so amplitude ∝ 1/lens-strength applies here too,
but the working range is lower. Sweep from α = 0.05 to 0.2:

```bash
for A in 0.05 0.1 0.15 0.2; do
  prabodha steer --model configs/models/nemotron.yaml \
    --mid-lens outputs/lens_nemotron_mid30.pt --exp configs/experiments/e13full.yaml \
    --alpha $A --norm-cap-rel $A --loop demo --out gates/demo_nemotron_a$A.json
done
```

Expected (gates L14-transfer, L15-transfer-joint; three seeds each within ±0.10):
gated lift `0.00 → ~0.15 → 0.32–0.38 → 0.58–0.65`, trajectory-entropy delta
within ±0.5 nats. The rule transfers cleanly: weaker transport = stronger amplitude needed.

## 3. Verify against committed gates

The gate JSON contains the dual-verdict summary. Check:
- `domain_gate.verdict` = "pass" if both code and domain gates pass
- `domain_gate.evidence.summary.H_gated_budget.pass` = true if lift ≥ min_lift threshold

All numbers should match the committed gates; any drift indicates model/corpus variation.
