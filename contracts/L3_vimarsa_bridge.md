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

Operator sign-off: ______  Date: ______
