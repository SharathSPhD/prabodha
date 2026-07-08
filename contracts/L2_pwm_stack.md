# Contract L2 — E2+E7: lens on the PWM stack + progressive articulation
Status: OPEN · Worktree: loop/l2-pwm-stack · Owner: ralph loop (fresh agent re-entry safe)
Lineage: SPEC §3 L2; HANDOFF "Near (L2)"; L1b closure caveats pre-registered here.

## Objective (domain)
(E2) Fit the J-lens on the HF twin of PWM's cascade fast model and produce its BAND MAP —
including the workspace-onset layer the VimarsaBridge v3 (L3) will write at. (E7) Test the
vāk-hierarchy signature (scoping §2.5): does lens-readout articulation (top-k concentration)
RISE with depth (paśyantī → madhyamā → vaikharī)? GNW predicts no such laminated gradient —
this is the cheapest discriminating observable in the program.

## Model note (disclosed deviation, journaled 2026-07-08)
PWM production serves nemotron-mini:4b via Ollama (quantized, HTTP — no white-box access).
L2 fits on nvidia/Nemotron-Mini-4B-Instruct (HF bf16, 32L, d3072, same lineage). The
bf16-vs-served-quant gap is a standing caveat for transferring L2 findings to production.

## Carried caveats from L1b (all pre-registered in configs/experiments/e2.yaml)
1. H_modulation gains an UNINSTRUCTED-PROMPT CONTROL (stub continuations without the
   instruction sentence); pass requires hit-rate - control >= 0.2 margin, plus the shuffled
   null as before. (Directedness vs incidental concept-capacity.)
2. Modulation band FIXED a priori (depth_middle_third) — same mode as L1b; any cross-size
   comparison uses same-band-mode numbers only.
3. H_report REGISTERED ALTERNATIVE metric: mean model-top-K rho over the LAST 3 layers
   (window justified by both L1 and L1b curve shapes, which consolidate only at the top);
   late-third mean ships as secondary evidence. This is the L2 registration, not a post-hoc
   switch: it is declared here before any nemotron data exists.

## Deliverables
D1 configs/models/nemotron4b.yaml + configs/experiments/e2.yaml (pre-registered).
D2 evaluator: H_articulation (topk_negentropy + depth-gradient rho, permutation-gated) +
   uninstructed control + report-window option — unit-tested CPU-side.
D3 scripts/dispatch/l2/run.sh + compose service l2 (courtesy caps; guard default floor).
D4 gates/gate_L2.json + band map (workspace-onset layer recorded in journal + state.json)
   + slice page on a PWM-flavored prompt.
D5 journal + SPEC/PRD evolution at closure; adversarial review; milestone merge.

## Closure criteria
CODE GATE: CI green; smoke suite green in-container; run completes on GB10 within budget.
DOMAIN GATE (screen tier, from e2.yaml): H_bands three-band structure present (contrast >=
0.15); H_articulation gradient rho >= 0.5 with p <= 0.05; H_modulation >= 0.5 with control
margin >= 0.2; H_report_last3 >= 0.4 with p <= 0.05. Split verdicts are expected and
reportable (calibration lineage); adversarial review attacks the interpretation either way.
GPU budget: 2.0 GPU-h cap (L2 line).

## Iteration record (2026-07-08, GB10, three eval runs on one fit)
- Run 1: H_modulation all-zeros incl. both nulls — BOS pollution (SentencePiece prepends <s>;
  every candidate's "first id" was BOS; 30/30 variants flagged). Fixed (specials=False for
  candidates only), regression-tested. gate_L2_run1.json preserved.
- Run 2: modulation 0.20 = shuffled null 0.196 = uninstructed control 0.20, all "hits" zh
  byte-fallback pieces. Adversarial review (#4) flagged the zh pieces as noise; amendment:
  concept_variant_policy single_token_only (disclosed, eval-only).
- Run 3 (final, gates/gate_L2.json): H_modulation 0.0 = null 0.0 = control 0.0 with clean
  candidates — ZERO directed modulation on the PWM twin (the same English variants fire on
  Qwen3-4B at 0.10 and Qwen3.6-27B at 0.55). H_articulation PASS 0.639 (p≈2e-4).
  H_report(last3) 0.384 (thr 0.4, p≈1e-4) near-miss; last layer 0.614. H_bands 0.137
  (thr 0.15) near-miss with visually clean bands [0,6)/[6,26)/[26,32). ~0.5 GPU-h of 2.0.
- Review #4 verdicts: articulation ARTIFACT-SUSPECT (tautology attack: lens is trained to
  transport toward final logits — does sharpening follow from lens construction? plus the
  non-monotonic start, layer-0 negentropy 0.572) — CARRIED CAVEAT: register a shuffled-
  final-logits null before articulation claims leave screen tier; modulation-null VALID
  (control margin 0; strengthened by run 3); bands near-miss VALID (structure real, contrast
  honestly below the pre-registered threshold — pruned/distilled lineage shows smeared
  banding vs both Qwens, candidate architectural finding); iteration honesty VALID.
- L3 ENTRY GATE adopted from review #4: before any write at the onset layer, measure
  Selectivity@5 — fraction of the model's final top-5 recoverable from layer-6 states via
  the lens. GO >= 0.75; NO-GO < 0.60; 0.60-0.75 requires readback verification per write.
  Record as gates/gate_L3_readiness.json.

## Closure: SPLIT VERDICT AS REGISTERED (calibration lineage)
The PWM twin: has the articulation gradient (E7 signature present), has visually clean but
weak-contrast bands, consolidates report-correspondence only at the final layers (like both
Qwens), and does NOT load instructed concepts into its middle band at all. For H2 steering
(L3): the write path does not depend on instruction-loading (it writes via the lens
directly), but the ZERO instructed-loadability and weak banding mean the readback verifier
is the load-bearing component — hence the Selectivity@5 entry gate.

Operator sign-off: SharathSPhD (in-session)  Date: 2026-07-09
