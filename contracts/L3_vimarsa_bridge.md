# Contract L3 — E3: the H5b redo (VimarsaBridge v3 vs v2 write sites)
Status: OPEN · Worktree: loop/l3-vimarsa-bridge · Owner: ralph loop (fresh agent re-entry safe)
Lineage: SPEC §3 L3 + §6 doctrine; PWM H5b honest negative (v2 logit-bias bridge, g=-0.47 vs
bare 120B — diagnosed as writing at vaikharī after the workspace closed); L2/L2b band map +
band-lens findings; operator fork sign-off 2026-07-09 (option c: per-band-lens design).

## Objective (domain)
Same content, two write sites: does writing INTO the workspace band (v3: residual injection
along the band-lens concept direction, readback-verified) deliver behavioral content with
LESS camatkāra damage than writing at the mouth (v2: output logit bias)? Plus: does the band
actually take the content up (āgama re-cognition through the band-targeted lens)?

## Design decisions (recorded per interview rule)
1. Plant: nvidia/Nemotron-Mini-4B-Instruct (PWM twin; carried caveats in state.json).
2. Write site: layer 20 (middle-band interior), pre-registered; readback layers 21–25 via the
   TARGET-26 lens (L2b: final-target lenses are blind to band content). Fixed, not swept —
   the L3-readiness sweep showed no final-lens-selective mid layer, so the write site is a
   registered bet the readback verdict itself adjudicates.
3. v2 arm is a MECHANISM-MATCHED simplification of PWM's trained bridge (additive output
   logit bias) — the trained bridge needs the full WM stack (scout report, journal
   2026-07-09). The contrast tested is the write SITE with content held fixed; both arms'
   entropy costs are measured and reported.
4. Bare-stub generation (no instruction): the concept can reach the output only through the
   write. Kills the instruction confound; makes surface-rate a pure measure of write efficacy.
5. Timing policy: fixed (write active throughout prefill+decode at 'last' position per step).
   Sphurattā-event gating (PWM machinery, portable) is deferred to L4 — one new mechanism
   per loop.
6. Camatkāra: PWM's text-only H5b scorer ported verbatim (weights 0.40/0.35/0.25) for
   comparability with PWM's published H5b numbers.

## Deliverables
D1 src/prabodha/steering/: writer (k-sparse non-negative concept codes, svātantrya cap),
   verifier (uptake criteria + malas taxonomy + entropy budget), injector (band hook + v2
   processor), scoring (camatkāra port + surface rate) — all CPU-unit-tested.
D2 configs/experiments/e3.yaml (pre-registered, incl. the single permitted alpha follow-up).
D3 e3_cli runner + scripts/dispatch/l3/run.sh + compose service l3.
D4 gates/gate_L3.json + malas histogram + per-concept table + journal entry.
D5 adversarial review + SPEC/PRD evolution + milestone merge.

## Closure criteria
CODE GATE: CI green; smoke (tiny-model injector round-trip) green in-container; run completes.
DOMAIN GATE (screen): H_uptake uptake_rate >= 0.5; H_quality_per_lift: lift_v3 >= 0.2 AND
camatk-drop advantage (v2 drop - v3 drop) >= 0.05. Split verdicts reportable; prune_rule in
e3.yaml. Malas histogram REQUIRED evidence either way (the failure taxonomy is a deliverable,
not an excuse). GPU budget: 1.5 GPU-h cap (L3 line).

## Iteration record (2026-07-09, GB10, three dose points)
- gate_L3.json (α=0.1): domain FAIL both hypotheses. Malas: svātantrya 20 / karma 14 /
  āṇava 2. Behavior: lift v3 0.40 vs v2 0.175 (baseline 0.00); camatk drop v3 0.063 vs
  v2 0.021; entropy delta v3 -2.081 vs v2 -0.214 nats.
- Registered α=0.2 follow-up (gate_L3_alpha02.json): run per review #5's demand — results
  BIT-IDENTICAL to α=0.1 because capped_delta scale = min(alpha, norm_cap_rel=0.1): the
  pre-registered follow-up was structurally inert as written (cap binds). Disclosed;
  doubles as a determinism check. PRE-REGISTRATION LESSON: follow-up knobs must be checked
  against their own caps at registration time.
- Exploratory α=0.05 (gate_L3_alpha005_exploratory.json, labeled non-registered): lift v3
  0.42 (unchanged), camatk drop 0.039 (reduced), lens uptake 0.0 (āṇava 24), entropy delta
  -1.904 (nearly unchanged). TRIPLE DISSOCIATION: amplitude controls lens-visible loading;
  behavioral steering and entropy collapse are dominated by CONTINUOUS PER-STEP TIMING.
- Adversarial review #5 verdicts (recorded; claims softened accordingly):
  (a) "band dominates behaviorally" ARTIFACT-SUSPECT — honest statement: at ~10x output
  entropy cost and against an UNTRAINED logit-bias comparator, v3 achieved 2.3x the surface
  rate; binomial CIs overlap at n=40; dose-response + trained-bridge comparison required
  before any dominance claim. (b) svātantrya-dominance UNDERDETERMINED (karma 14 vs 20;
  per-write scatter absent — added to L4 requirements). (c) follow-up decline
  ARTIFACT-SUSPECT — CURED by running it (above). (d) untrained v2 is the top threat —
  carried as L4+ requirement (trained-bridge arm needs the PWM WM stack).
- L4 requirements adopted from review #5: dose-response curves (both arms, matched entropy);
  per-write entropy-vs-uptake scatter; per-concept malas; event-gated timing as the
  registered mechanism (reviewer ENDORSED from the karma/svātantrya split; the α=0.05
  dissociation independently confirms timing over amplitude).

## Closure: honest-fail-with-finding (iterate at L4 per review #5 disposition)
The steering machinery works end-to-end (writer/injector/verifier/malas; smoke-tested).
Band writes at layer 20 on the PWM twin: load (āṇava≈0 at α=0.1), persist to behavior
(8/10 concepts), and cost too much freedom under continuous timing. The doctrine's next
move was already written in scoping §3: writes AT SPHURATTĀ EVENTS ONLY — L3's evidence
now shows why that clause is load-bearing rather than ornamental.

Operator sign-off: SharathSPhD (in-session, 'continue autonomous to L4', GPU uncontended)  Date: 2026-07-09
