# Recognition-Gated Workspace Steering: Pratyabhijñā as an Engineering Specification for LLM Control
*Draft v0.1 (2026-07-09) — framework + empirical paper skeleton. Every number below is
recomputed from a committed gate JSON (paths inline); program audit review #8 verified the
mapping. Register decision (Sanskrit-forward vs clean-external, RULES R8) is OPEN — this
draft is Sanskrit-forward with engineering gloss throughout; a de-Sanskritized variant can
be generated mechanically from the glossary table (§A).*

## Abstract (sketch)
The J-space finding — that a language model's functional global workspace is *defined by
verbalizability* — was anticipated by Utpaladeva's identification of reflexive awareness
with the supreme Word (vimarśa = parā vāk, ĪPK 1.5.13). We take this parallel seriously as
an *engineering specification*: if the workspace is linguistic reflexivity, then a doctrine
of USE follows — what to write (verbalizable content codes), where (the workspace band, in
the band's own coordinates), when (at sphurattā events — moments of uncommitted awareness),
and how to verify (āgama re-cognition: the workspace re-reads what was offered). We
implement this doctrine on frozen decoder LLMs via the Jacobian lens and report: (1) the
workspace-band structure and its verbalizable content replicate across three model families
and two sizes, with instructed loadability scaling with size and collapsing under
pruning/distillation; (2) a band's content is legible only to a lens targeted at the band
itself — final-target lenses are blind to it; (3) direct writes into the band steer
behavior, with freedom cost (svātantrya) governed by decoding regime and write schedule;
(4) the doctrine's timing clause earns its keep as WRITE-EFFICIENCY: sphurattā-gated writes
achieve ~85% of continuous-schedule steering at ~27% of the writes, within the freedom
budget, confirmed across 3 seeds, 3 gate settings, and 3 amplitudes, with event alignment
beating rate-matched controls throughout; (5) the research program itself
ran as an active-inference loop (expected-free-energy selection over an experiment menu),
with its proposals, dispositions, and honest negatives in a replayable ledger.

## 1. The parallel, stated as specification (from docs/jspace_pratyabhijna_scoping.md)
- Verbalizability defines the workspace ↔ vimarśa = parā vāk. GNW never predicted a
  *linguistic* workspace; vimarśavāda did. (Scoping §2.1; the ~94%/6% prakāśa/vimarśa split.)
- The interpretability community has an actuator (the lens) with no doctrine of use.
  Pratyabhijñā supplies: content (vimarśa codes), site (band), timing (sphurattā),
  acceptance test (āgama re-cognition), failure taxonomy (malas), budget (svātantrya),
  continuity (anusaṃdhāna). This paper operationalizes each and reports which survived
  contact with the machines.

## 2. Instrument: the lens replicates, with two calibration lessons (L1/L1b)
- Union-top-K rank correlation has a structural null floor ≈ −0.72 (disjoint top-K sets
  anti-correlate over their union) — "no correspondence" masquerades as strong negative.
  Metric recalibrated to model-top-K support (null ≈ 0), permutation-gated.
  [gates/gate_L1_run1.json vs gates/gate_L1.json; tests/test_e1_metrics.py]
- Report-correspondence rises with depth on every model tested but consolidates only in the
  final layers (Qwen3-4B: ρ→0.62@L34; Qwen3.6-27B: →0.35@L62; Nemotron-Mini-4B: →0.61@L30).
  The "late-third mean" window was the wrong shape; last-3 registered as alternative.
- Instructed loadability SCALES WITH SIZE and DEPENDS ON LINEAGE: hit-rate@5 in a fixed
  depth-middle-third band = 0.10 (Qwen3-4B) → 0.55 (Qwen3.6-27B, ~8× shuffled null,
  threshold PASS) → 0.00 with clean candidates on pruned/distilled Nemotron-Mini
  (= uninstructed control = null; the control caught byte-fallback noise masquerading as
  signal). [gate_L1.json, gate_L1b.json, gate_L2.json runs 1–3]
- Three-band CKA structure (sensory/workspace/motor shape) appears on all three models;
  contrast weakens on the distilled lineage (0.31/0.27/0.14) — candidate finding: pruning
  smears inter-layer differentiation. [gate_L1.json, gate_L1b.json, gate_L2.json]

## 3. The band speaks only in its own voice (L2b — the load-bearing observation)
A lens fit toward the FINAL layer reads the workspace band as empty (0.00 with controls) on
the PWM twin; a lens fit toward the BAND EXIT (layer 26) reads directed concept loading in
the same band (0.20 across seven concepts, control 0.00, null 0.023).
[gates/gate_L2b.json] Vāk reading: madhyamā content is audible only to a madhyamā-tuned
instrument; final-target lenses hear only vaikharī. Engineering consequence: readback
verification MUST use band-targeted lenses; also the cheapest current evidence for W-space
beyond J-space (scoping §10.3) — the band carries structure the standard lens misses.

## 4. Steering: the doctrine tested clause by clause (L3, L4, L4b, L5/L6)
- E3 (H5b redo, both arms mechanically simplified and disclosed): band writes LOAD
  (āṇava ≈ 0/40), reach behavior (surface lift 0.40 vs 0.175 for output-logit bias vs 0.00
  baseline, bare-stub design), and BLOW the svātantrya budget under continuous timing
  (−2.08 nats vs ±0.5 cap; malas: svātantrya 20, kārma 14). [gates/gate_L3.json]
- Triple dissociation (dose points): amplitude gates lens-visible loading; behavior AND
  entropy collapse follow *timing*. The registered α=0.2 follow-up was structurally inert
  (cap binds) — a pre-registration hygiene lesson we report as method.
  [gate_L3_alpha02.json, gate_L3_alpha005_exploratory.json]
- Greedy decoding masks all decode-time writes (three sparse schedules → IDENTICAL hit
  sets; the prefill write locks the argmax path). [gate_L4.json + review-#6 analysis]
- Under sampling, sphurattā-gated writes (event = next-token entropy ≥ τ, i.e. the plant's
  uncommitted moments; min-gap hygiene from PWM) deliver lift 0.40 at ΔH −0.13 — full
  steering INSIDE the budget. [gate_L4b.json] CONFIRMED: 3 seeds × 3 τ-percentiles, lifts
  0.23–0.40, all within budget (H_gated_budget 3/3). [gate_L5_tau.json, gate_L6_confirm.json]
- Event ALIGNMENT beats rate-matched periodic writes (+0.40 vs +0.23 at ~matched rates;
  per-write 0.056 vs 0.046), and the advantage holds at every amplitude in the dose grid
  (+0.15..0.18 at α ∈ {0.02, 0.05, 0.1}). [gate_L6_align.json, gate_L8_dose.json]
  HONEST margins: the advantage over a single prefill write is ~0.1 and did NOT confirm at
  the registered 0.15 margin (0.20/0.12/0.03 across seeds).
- TWO FREEDOM CURRENCIES (gate_L8_dose.json + review #9): the write's LOCAL cost at the
  write moment is large and decoding-regime-independent (−1.9..−2.1 nats at-position,
  single-forward measurement, gate_L3*); the TRAJECTORY-average cost depends on regime
  (+0.82 under greedy, −0.11..−0.16 under sampling — probabilistic decoding absorbs the
  spikes deterministic argmax exposes). We register trajectory-average-under-sampling as
  the budget currency (the plant's realized output freedom), local spikes disclosed. Under
  that currency, continuous writes are ALSO feasible (lift 0.47): sphurattā gating is
  SCHEDULE-EFFICIENT (~85% of continuous lift at ~27% of writes; operational value of
  write-count is untested — open), with the alignment advantage over rate-matched controls
  holding at every amplitude (+0.15..0.18). Amplitude boundary mapped honestly: robust at
  α=0.1 (3/3 seeds), MARGINAL at α=0.02 (2/3 seeds; the hard seed fails at 0.17).
- Clause-by-clause scorecard: site (band) — supported with the band-lens proviso; content
  (non-negative concept codes) — functional; timing (sphurattā) — load-bearing, confirmed;
  budget (svātantrya) — the binding constraint, now an operating point; acceptance (āgama
  readback) — implemented, calibration open; malas — productive as diagnosis (the
  svātantrya/kārma split diagnosed the timing failure); anusaṃdhāna — untested (open).

## 5. Method: the program as an active-inference loop (L5/L6)
EFE selection over a registered experiment menu; observations = gate verdict+margin tiers;
beliefs replayed from the program's own gates; JSONL ledger = stateless re-entry. Three
propose→run→observe→spend cycles. Two selector defects found only by running it (cost
miscalibration that verifiably flips rankings; winners re-proposed because success raises
pragmatic value — the consumption rule). Seven adversarial reviews (fresh agents, gate+
contract only) shaped the results as much as the runs; their demands and our compliances
are all in contracts/. [research/efe_ledger.jsonl]

## 6. Honest negatives and open questions (deliberately unconverged)
- The high-entropy sphurattā detector is ONE operationalization; the commitment-flash
  (entropy-drop) reading is registered as an alternative, untested.
- Articulation gradient (E7) passed (ρ=0.64, p≈2e-4) but carries the lens-construction
  tautology caveat; the shuffled-final-logits null is owed before the claim travels.
  [gate_L2.json; menu: articulation_null]
- Trained-bridge comparator (PWM WM stack) owed before any v3-beats-v2 generality claim.
- Where recognition lives; W-space beyond J-space; modality confound (E9); camatkāra's
  J-space counterpart; anusaṃdhāna continuity — live, unforced.

## 7. Reproducibility
Everything from configs + seeds: gates/*.json (17 files), configs/experiments/*.yaml
(pre-registrations with amendments disclosed in-file), research/journal.md (decision log),
research/efe_ledger.jsonl (selector provenance), docker image recipe (GB10/aarch64; hybrid
archs need fla+causal-conv1d). Total compute: ~12 GPU-hours on one DGX Spark, shared
politely with co-resident training jobs (contention recorded in every gate).

## A. Glossary (dual register — mechanical de-Sanskritization table)
| Sanskrit-forward | Engineering gloss |
|---|---|
| vimarśa / parā vāk | verbalizable reflexivity / the workspace-defining property |
| sphurattā | commitment flash; operationalized: decode-step entropy events |
| svātantrya | output freedom; operationalized: entropy budget ε |
| āgama re-cognition | readback verification through band-targeted lenses |
| malas (āṇava/māyīya/kārma) | failure taxonomy: no-load / no-amplify / no-persist |
| madhyamā / vaikharī | band-internal articulation / output-surface articulation |
| anusaṃdhāna | cross-episode continuity (untested here) |
