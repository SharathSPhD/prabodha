# Review #18 — Program-Wide Claims Audit (v1.0.0 pre-release)

**Auditor:** isolated adversarial agent (review #18), briefed only with the repo's main
state + the gate files, not prior conversation.
**Date:** 2026-07-10
**Scope:** all six public deliverables — README, paper, GitHub Pages (`web/`), app
(`apps/web`), Claude Code plugin, MCP server — plus cross-surface consistency and the
claims-discipline (utility-only, never consciousness; Sanskrit terms glossed).
**Ground truth:** `gates/*.json`, `docs/HANDOFF_L19_TO_NEXT.md` §3, extended by L20
(`gates/gate_L20_confirm.json`, `gates/gate_L20_s{42,123,777}.json`).

## Verdict: RELEASE-WITH-CORRECTIONS → corrections applied

The program is approved for v1.0.0 after two documentation fixes, both now applied.

### Required fixes (applied this loop)
1. **`docs/paper/sections/discussion.tex`** — the trained-bridge comparator was still
   described as awaiting the PWM stack / "future work," but L20 executed it. Reframed to:
   L20 integrated the PWM CittaStore path and ran it; a *cold/untrained* store steers
   within budget on all 3 seeds and is comparable (not strictly equivalent) to analytic;
   training the store remains the open follow-up.
2. **`docs/paper/sections/conclusion.tex`** — "trained-bridge integration" listed as
   future work; reframed to "training the CittaStore against steering-success targets
   (integration now operational per L20, cold-recall verified)."

### Surfaces that passed clean (no changes)
- **README.md** — every number in the claims table matches its gate; honest negatives
  present (readback BA≈0.59 at n=120; L19 corpus-amplitude fail-on-margin); no
  consciousness language.
- **Paper Finding 7 (`results.tex`)** — all L20 numbers verified exactly against the gate
  (lifts 0.4445/0.5556/0.4445; gaps 0.0000/0.0000/0.1111; 2.2× threshold; 1/9; analytic
  0.3334). Correctly framed as cold/untrained, comparable-not-equivalent, with the
  determinism probe (all 9 seed-123 generations differ between arms) credited.
- **`web/index.html`** (Pages) — Act VI L20 scene numbers consistent with the paper; "not
  a 'trained bridge' but a cold-store proof-of-concept"; open questions explicit.
- **`apps/web`** — no hand-entered numbers (all from exporter-generated `public/data`);
  glossary Sanskrit terms carry engineering glosses; no consciousness language.
- **Plugin + MCP** — gate citations resolve to real files with matching numbers; the
  readback weak-signal caveat is present on the readback surface.

### Consciousness-claims audit: PASS
No unqualified consciousness claims on any surface. The Pratyabhijñā doctrine is used
throughout strictly as an *engineering specification*; every external Sanskrit term
carries an engineering gloss.

### Cross-surface consistency: PASS (after the two paper fixes)
Core steering (L9/L11), readback weakness, corpus-amplitude fail-on-margin, and the L20
result now read consistently across README, paper, pages, app, and plugin.

## L20 ground-truth derivation (spot-checked by the auditor)
Surface metric = concept-hits / 9 corpus cells. Trained: 42→4/9, 123→5/9, 777→4/9.
Analytic: 42→4/9, 123→5/9, 777→3/9. Gaps: 0, 0, 1/9=0.1111. All match the gate. No
data-entry errors.
