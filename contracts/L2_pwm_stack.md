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

Operator sign-off: ______  Date: ______
