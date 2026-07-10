# L20 Trained-Bridge Comparator Contract

**Date:** 2026-07-10  
**Loop:** L20  
**Status:** pre-registered (before any dispatch)

## Hypothesis (H_trained_bridge)

**Question:** Does a trained-bridge write path (using PWM's CittaStore Hopfield retrieval) achieve comparable steering lift to prabodha's analytic J^T u write path, when both are entropy-gated and budget-matched?

**Predicted outcome:** The trained bridge will achieve lift ≥ 0.2 (absolute concept surface-rate gain) within the svātantrya budget (entropy cost ∈ [-0.5, +0.5] nats), matching or exceeding the analytic arm's performance on the standard corpus.

**Honest negatives path:** If CittaStore cannot produce write vectors that (a) have numerically stable norm, (b) are compatible with the band's geometric embedding, or (c) produce lift within the budget on even the screen tier, this will be recorded as a BLOCKED-WITH-DIAGNOSIS gate (no further attempts; the item is resolved as "attempted but infeasible under current GB10 configuration").

## Method

### Pre-registration Locks
- **Arm set:** `baseline`, `analytic_gated` (existing entropy-gated arm, reference), `trained_bridge_gated` (new arm, CittaStore-driven)
- **Corpus:** standard (fire/memory/dream prompts, 3 stubs each)
- **Seeds:** 42, 123, 777 (existing clean-stream seeds; no new seeds)
- **Entropy budget:** τ = 60th percentile of baseline entropy (self-calibrated per e4 protocol); both arms use same τ
- **Write layer:** 24 (Qwen3-4B band exit, established in L13; no re-sweeping)
- **Alpha:** 0.2 (fixed; no dose-response sweep; within Qwen3's confirmed active range per L14)
- **Tier:** screen tier first (n=1 seed); if screen passes, advance to confirm tier (n=3 seeds)

### Procedure
1. Initialize PWM's CittaStore on GB10 (pre-trained or warm-started from L19 session if available; if not available, initialize empty and proceed—the arm may fail gracefully)
2. Warm up CittaStore with a few example concept embeddings (e.g., sample 10 past successful firings from L13/L14 gates, if available in the ledger)
3. Run `prabodha steer` with the new `trained_bridge` arm, alongside `analytic_gated` and `baseline`, on one seed (42) with all three arms on identical prompts and seeds (stream_tag matching for reproducible per-generation seeding)
4. Record raw output: surface rate, entropy delta, readback, behavioral hit per (arm, concept, stub)
5. Emit `SteerTrace` JSON for each run (for replay theatre)

### Success Criterion (screen tier, n=1 seed)

**PASS:** trained_bridge lift ≥ 0.15 (absolute), within entropy budget [-0.5, +0.5], and analytic_gated serves as a reference (aim for trained_bridge ≥ analytic_gated - 0.05, i.e., no >5pp gap).

**FAIL-ON-MARGIN:** trained_bridge lift ∈ [0.1, 0.15) or entropy delta outside [-0.5, +0.5].

**BLOCKED-WITH-DIAGNOSIS:** 
- CittaStore.recall() produces zero/NaN direction vectors consistently
- Encoding/decoding mismatch between CittaStore and band layer
- No stubs achieve lift > 0.05 (suggests fundamental incompatibility)

### Confirm Tier (if screen passes)

Run the same experiment on seeds 123 and 777; require trained_bridge lift ≥ 0.15 on ≥2/3 seeds and no seed with entropy delta outside the budget. If both conditions hold, upgrade verdict to `confirm`.

## Ledger Entry Format

```json
{
  "loop": "L20",
  "candidate": "trained_bridge_arm",
  "screen_verdict": "pass|fail-on-margin|blocked",
  "confirm_verdict": "pass|fail|pending",
  "gate_file": "gates/gate_L20_trained_bridge.json"
}
```

## Honest-Negatives & Open Items

- If warm-start CittaStore data is unavailable or stale, cold-start is permitted (expect degraded performance)
- If trained-bridge fails on screen, no retry with different CittaStore initialization is planned (one attempt; carries forward as a resolved blocker)
- Cross-arm offset drift (other arms' entropy levels vs L8 baseline) is NOT in scope for L20; only trained vs analytic is compared
- Seed 777 is historically harder (L8 note); if it fails but others pass, record as a seed-effect note, not a contradiction

## References

- Handoff §3 claim #3 (core gated claim: 0.30–0.35 lift, 6-seed confirm)
- Handoff §4 (trained-bridge blocker carried since menu 3)
- gate_L13_recipe.json, gate_L14_multiseed.json (reference analytic performance)
- PWM/pwm/memory/citta_store.py (CittaStore interface)
