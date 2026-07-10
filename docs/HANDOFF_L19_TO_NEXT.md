# HANDOFF — prabodha program state at L19 closure (2026-07-10)

**Purpose of this document.** This is a from-scratch briefing for an agent picking up
this program in a *new session with no memory of this conversation*. It is deliberately
long and explicit: it recapitulates the founding intent, the method, everything that has
been found, everything that is open, and exactly which files to read to verify any of
it. Treat it as the single entry point — read this first, then follow its pointers into
the repo rather than re-deriving context from scratch.

Repo: `github.com/SharathSPhD/prabodha` (canonical home). Local clone:
`/home/sharaths/projects/prabodha` (main, currently at commit `6031f85`, PR #22 merged).
This document was authored from a worktree at
`.claude/worktrees/heuristic-golick-c4f418` on branch `loop/l19-menu9` (already merged
to main; the worktree can be removed once you've confirmed main has everything —
`git worktree list` / `git worktree remove` from the main checkout, not from inside the
worktree itself).

---

## 1. What this program IS (read this before anything else)

**One-sentence description:** prabodha operationalizes a philosophical parallel — between
the J-space paper's finding that a language model's functional "global workspace" is
defined by *verbalizability*, and the 10th-century Kashmir Śaiva Pratyabhijñā
("recognition") philosophy's identification of reflexive self-awareness (**vimarśa**)
with the supreme creative Word (**parā vāk**) — as an *engineering specification* for
steering frozen LLMs, then tests every clause of that specification empirically on real
models, with a self-driving research loop and full statistical rigor as the pruning
mechanism, not a genericity filter.

**Why this matters / what's being tested:** Global Workspace Theory (Baars, Dehaene)
never predicted that the workspace would be specifically *linguistic*. Pratyabhijñā
philosophy did (vimarśa = parā vāk, Utpaladeva's Īśvarapratyabhijñākārikā 1.5.13). The
interpretability community has a working *actuator* (Anthropic's Jacobian-lens, from
"Verbalizable Representations Form a Global Workspace in Language Models",
transformer-circuits.pub/2026) but no *doctrine of use* — no answer to what to write,
where, when, how to verify it worked, how it can fail, or what the safe operating budget
is. Pratyabhijñā supplies exactly that doctrine (content codes, site = the workspace
band, timing = sphuraṭṭā/uncommitted-moment events, verification = āgama re-cognition/
readback, failure taxonomy = the three malas, budget = svātantrya/autonomy-preservation).
This program implements each clause on real frozen decoder LLMs and reports, honestly,
which clauses survived contact with the machines and which didn't.

**Claims discipline (non-negotiable, checked by every review):** utility only —
understanding and steering of LLMs and world models. **NOT** a consciousness claim, ever.
Internal vocabulary is Sanskrit-forward (the concepts are precise and the tradition's
terms are the correct handles for them); every external-facing surface (README, plugin,
paper glossary) carries a clean engineering gloss column. See `RULES.md` R8 and the
glossary appendix in `docs/paper/paper.tex`.

**The four founding deliverables** (the operator was explicit about this — it is NOT
merely a research paper): **(1) empirical research** (the gates/ledger/journal
machinery), **(2) a paper** (`docs/paper/paper.pdf`, LaTeX source `paper.tex`), **(3) a
tool** (the `prabodha` Python package + CLI), and **(4) a Claude Code plugin**
(`integrations/claude-code-plugin/`) plus a dual-audience HTML explainer artifact. All
four exist today and are described in detail below (§6).

**Founding method (the operator's explicit standing instructions — do not relax these):**
- **Ralph loops with DUAL closure**: every loop needs BOTH a code gate (tests pass, lint
  clean) AND a domain/research gate (a pre-registered hypothesis is tested against real
  data with an explicit pass/fail criterion). Tests passing is never sufficient by
  itself.
- **Pre-registration**: every experiment's success criterion is written into a config
  file (`configs/experiments/*.yaml` or a menu's candidate description in
  `configs/efe_menu*.yaml`) BEFORE the run, not after.
- **Tiered statistics as pruning shears**: screen tier (single/few seeds, permutation
  tests, Hedges' g) narrows the space cheaply; confirm tier (≥3 independent seeds,
  Holm-Bonferroni-corrected) is required before a claim is treated as load-bearing.
  Statistical rigor prunes DIRECTIONS — it is not there to bless the program's
  ambitions, and honest negatives are shipped results, not failures to hide.
- **Adversarial review at every loop closure**: a FRESH subagent, briefed with ONLY the
  relevant gate JSONs + the registering config (deliberately NOT the journal, NOT the
  paper, NOT prior conversation) attacks each closing claim and returns a verdict
  (MERGE-CLEAN / MERGE-WITH-CORRECTIONS / BLOCK). This has caught real errors — see §5
  below, "Reviews that caught real mistakes" is the single most important part of this
  document to internalize before trusting any claim in the paper.
- **Config over constants**: anything tunable lives in `configs/*.yaml`, not hardcoded.
- **Worktrees per loop**, squash-merge to main at closure, PR per loop, then
  `git -C /home/sharaths/projects/prabodha pull --ff-only` (the operator explicitly
  wants the LOCAL clone kept in sync too, not just GitHub).
- **GPU discipline**: GB10 (DGX Spark) only; the 5090 is not set up. NEVER disturb
  co-resident jobs (prabhasa, PSALM) — `scripts/lib/gpu_guard.sh` is mandatory before
  every GPU dispatch; it checks free memory (via `/proc/meminfo` MemAvailable, since
  `nvidia-smi` reports `[N/A]` on this unified-memory box) and records contention in
  every gate. GB10 is bandwidth-bound — co-residency depresses tok/s even when VRAM
  technically fits; prefer idle windows, short pulsed jobs, checkpoint-resume.
- **Standing operator authorization (2026-07-09, still in force)**: "no waiting for
  operator signoff henceforth... you are fully authorized... be fully autonomous."
  This covers DISPOSITION (when to merge, when to move to the next loop) — it does
  **NOT** relax the dual-gate standard, the adversarial-review requirement, or the
  pre-registration discipline. Autonomy is about not waiting for a human to say "go";
  it is not permission to skip the rigor.

---

## 2. Program trajectory L0 → L19 (what has actually been done, in order)

Every one of these closed with its own PR (all merged to main; see §7 for the full list
with commit-level detail). Full blow-by-blow narrative for each loop is in
`research/journal.md` — it is 757 lines, append-only, and is the single most detailed
record of *why* things happened, in far more depth than this summary can carry. If a
number or decision below seems surprising, `grep` the journal for the loop tag (e.g.
`grep -A20 "## .* L14" research/journal.md`).

- **L0** — foundation: repo, dual-closure machinery (`src/prabodha/contracts/closure.py`
  — the `GateReport`/`GateSide` pydantic schema every gate JSON conforms to), TRIZ log,
  mirrors to the SMB drive + `prabodha.bundle` (the SMB mount cannot host live git —
  lock/unlink semantics — so it carries a file mirror + a restorable bundle).
- **L1/L1b** — E1: fit the vendored Jacobian lens (`vendor/jacobian-lens`, Anthropic's
  reference implementation, Apache-2.0, unmodified per RULES R7) on Qwen3-4B and, in
  L1b, on Qwen3.6-27B (matching Anthropic's model class for a size-matched replication).
  Found: instructed concept "loadability" (does a fitted lens let you read out a
  concept you told the model to think about, at a fixed depth band) scales with model
  size — 0.10 hit-rate@5 on the 4B, 0.55 on the 27B — and depends on lineage (the
  distilled PWM twin, Nemotron-Mini-4B, shows genuine ZERO, not an artifact — confirmed
  via uninstructed-control and shuffled-concept-null arms). Also found and fixed: the
  union-top-K rank-correlation metric has a structural null floor around −0.72 (any two
  unrelated rankings will show *negative* correlation under that metric by construction)
  — recalibrated to model-top-K support, which has a null near 0, with permutation
  gates. Engineering lesson: `qwen3_5`'s hybrid linear-attention architecture needed
  `flash-linear-attention` + `causal-conv1d --no-build-isolation` to run in reasonable
  time (52 min/prompt on plain torch fallback → 17 min/prompt with the kernels).
- **L2/L2b** — E2 (fit on the PWM/Nemotron twin) + E7 (articulation-depth gradient: does
  report-correspondence with a lens rise monotonically with depth, and does it
  consolidate only near the final layers — a signature of the "still integrating" vs
  "output-ready" distinction Pratyabhijñā predicts as madhyamā vs vaikharī). **The single
  most important structural finding of the instrument phase**: a lens targeted at the
  model's FINAL layer reads the workspace band as completely empty (0.00, with controls
  ruling out artifact) — but a lens targeted AT THE BAND'S OWN EXIT LAYER reads directed
  concept-loading clearly in that same band (0.20 hit rate over 7 concepts, vs 0.00
  control, vs 0.023 null). **Engineering consequence used everywhere downstream**:
  readback verification MUST use a band-targeted lens, never a final-target one — a
  final-target lens is structurally blind to intermediate workspace content. Band map on
  the PWM twin: three CKA-clustered bands at layer boundaries roughly [0,6), [6,26),
  [26,32) (24-layer-ish model), band onset at layer 6.
- **L3** — E3 (the first STEERING attempt, not just reading). Registered a
  pre-specified hypothesis (H5b, ported from the sibling PWM project): does writing a
  concept code directly into the workspace band (v3, via the lens's Jacobian transpose
  as a write direction) beat writing via a cruder logit-bias hack (v2)? Result: band
  writes at layer 20 DO load and DO steer downstream behavior (0.40 lift vs 0.175 for
  the v2 arm, vs a genuine 0.00 baseline design) — but under CONTINUOUS per-step
  injection they blow the "svātantrya budget" (the entropy-based autonomy-preservation
  constraint) by a wide margin (−2.08 nats vs a ±0.5 nat target). Triple dissociation
  established: amplitude of the write governs LOADING; TIMING (not amplitude) governs
  the behavioral/entropy tradeoff. This is the finding that made timing (not just "how
  hard do you write") the central lever for the rest of the program. Lesson recorded
  twice (once here, once again in L14): a registered follow-up experiment that changes
  one knob (α) while a hard cap on another knob (norm_cap_rel) silently binds is INERT —
  check registered follow-ups against active caps before dispatching.
- **L4/L4b** — E4: does writing only at "uncommitted moments" (entropy-gated timing,
  the operational reading of **sphuraṭṭā** — the "flash" of pre-linguistic recognition —
  as an event detector, with its threshold τ SELF-CALIBRATED as the 60th percentile of
  the model's own baseline per-token entropies, never a hand-picked constant) let you
  steer within budget where continuous writing couldn't? **FIRST INTERVENTIONAL DOMAIN
  PASS**: under SAMPLING decoding (temperature 0.8, not greedy), entropy-gated writes
  deliver 0.40 lift at only −0.13 nats entropy cost (well within the ±0.5 budget), vs
  0.20 lift for prefill-only writing. Also found (an adversarial review, #6, caught this
  live): GREEDY/argmax decoding MECHANICALLY MASKS all decode-time writes — every
  timing-schedule arm produces literally identical output token sequences under greedy
  decoding, because argmax ignores the entropy landscape a write perturbs. This forced
  the entire program's OPERATING REGIME to be stochastic/sampling decoding from L4
  onward — it's not a preference, it's a mechanical requirement for the phenomenon under
  study to be visible at all.
- **L5/L6** — the AUTO-RESEARCH LOOP goes live: an Expected-Free-Energy (EFE) selector
  (`src/prabodha/efe/`, ported architecturally from a sibling project `prabhasa`) starts
  proposing which experiment to run next from a REGISTERED MENU
  (`configs/efe_menu.yaml`, later menu2..menu9), balancing epistemic value (how much
  would this teach the selector) against pragmatic/registered cost (GPU-hours), with
  every proposal/observation/spend/skip/divergence event appended to
  `research/efe_ledger.jsonl` (stateless-re-entrant — the whole belief state replays
  from this file plus the gates it cites, nothing is held in memory between sessions).
  Cycles 2-3: τ-robustness confirmed across percentiles/seeds; alignment (does the
  EVENT-GATED schedule beat a merely RATE-MATCHED random-sparsity control, i.e. does
  *timing precision* matter beyond *sparsity*) beats rate-matching (+0.40 vs +0.23).
  Core claim (H_gated_budget: gated lift ≥0.2 within ±0.5 nat budget) reaches CONFIRM
  tier at 3/3 seeds. The advantage-over-prefill number is honestly DOWNGRADED from an
  early optimistic reading to "~0.1, unconfirmed at the originally-hoped 0.15 margin."
- **L7** — an isolated PROGRAM AUDIT (review #8: a full adversarial pass over the entire
  claim set, not just one loop) returns PASSING but finds and fixes several Tier-0
  metadata defects (gate loop labels hardcoded "L4" on gates from later loops — this
  exact bug recurs twice more later, see below; conflict markers accidentally committed
  in the journal from a bad rebase). Cycle 4 resolves a standing tautology worry: is the
  articulation-depth gradient (E7) just an artifact of HOW the lens was fitted, or a
  real property of the model? Tested with a completely different, UNFITTED instrument
  (the plain logit-lens) — it shows the same rise (ρ=0.607 vs the fitted lens's
  ρ=0.639). **Model-intrinsic, not lens-construction-intrinsic.** Paper skeleton and H4
  (plugin architecture) planning doc both first drafted here.
- **L8** — the dose-response grid + review #9 corrections. Makes explicit the single
  most subtle methodological finding of the whole program: there are **TWO DIFFERENT
  "FREEDOM COST" CURRENCIES** and they disagree in sign under some regimes. The
  AT-POSITION cost (entropy delta measured exactly at the write moment) is large and
  NEGATIVE regardless of decoding regime (−1.9 to −2.1 nats). The TRAJECTORY-AVERAGE
  cost (mean entropy delta over the whole generation) is POSITIVE under greedy (+0.82)
  but NEGATIVE under sampling (−0.13). The program REGISTERS trajectory-average-under-
  sampling as the official budget currency going forward (documented explicitly so a
  reader doesn't get confused by seeing both numbers in different places). Also: write
  *count* turns out to be operationally free at this scale (throughput within noise of
  baseline) — so the choice between gating schedules is about BEHAVIORAL margins, not
  cost. Amplitude boundary mapped: robust at α=0.1 (3/3 seeds), marginal at α=0.02
  (2/3 seeds, one seed — 777 — systematically hard; 777 recurs as a hard seed
  repeatedly through the whole program, see the seed-audit note in §5).
- **L9/L10** — **THE BIGGEST METHODOLOGICAL FIX IN THE PROGRAM'S HISTORY**: a bug where
  `torch.manual_seed(seed)` was reset identically before EVERY generation in a run
  meant that all "independent" trajectories within one seeded run actually shared
  correlated sampling structure — the effective sample size was far smaller than the
  nominal count (n_eff ≪ 40). Fixed by deriving a PER-GENERATION seed from
  `sha256(f"{seed}|{arm}|{concept}|{stub}")` (see `src/prabodha/steering/e4_cli.py`,
  the `_generate()` function, lines ~49-68 — this hashing scheme becomes load-bearing
  again in L19, see below). Fixing this required RE-BASING every sampling-derived number
  computed before this point. The re-based, "clean-stream canon" numbers are: core
  claim 0.30/0.35/0.35 lift within budget at 3 clean seeds (`gate_L9_alignconf.json`);
  schedule-margin advantage small-but-consistent, ~+0.09, UNCONFIRMED at its original
  0.15 hoped-for margin; flash-timing (commitment-flash gating vs uncommitted-moment
  gating) reported as underdetermined-at-the-boundary rather than a clean win; write
  count reconfirmed operationally free. L10: the FIRST cross-plant transfer attempt (try
  the exact Nemotron-tuned recipe on Qwen3-4B, unmodified) FAILS FLAT (+0.05, nowhere
  near the 0.2 threshold) — an honest negative that becomes the seed of the "calibration
  recipe" story (L13). Diagnosis: Qwen3's band-exit Jacobians are roughly 10× WEAKER in
  transport strength (max‖J‖/√d) than Nemotron's — the geometry doesn't transfer even
  though the method might. Staleness invariant adopted for the ledger (a replay gate
  that gets invalidated must trigger a belief rebuild before any further disposition —
  implemented as `src/prabodha/efe/lint.py`).
- **L11-L13** — **CORE CLAIM REACHES CONFIRM TIER AT 6/6 CLEAN-STREAM SEEDS** (lift
  0.30–0.35 within budget, `gate_L11_rep.json`); alignment advantage (gated > rate-
  matched) is SIGN-CONSISTENT 6/6 (one-sided sign test p≈0.016) — small in magnitude
  (+0.07 to +0.12) but the PAPER CITES IT BY SIGN CONSISTENCY, not by claiming a
  confirmed margin, which is the honest way to report a small-but-real effect. Flash
  (commitment-flash) timing reconfirmed weaker-than-uncommitted-moment, 4/4
  sign-consistent, not refuted just downgraded. **THE RECIPE TRANSFERS**: with a
  CALIBRATED protocol (probe candidate write sites; scale amplitude to the target
  plant's OWN lens transport strength rather than borrowing the source plant's number —
  the rule discovered: amplitude ∝ 1/lens-transport-strength) Qwen3-4B at site 24,
  α=cap=0.3 (3× the Nemotron value, matching its ~10× weaker transport) delivers gated
  0.40 vs prefill 0.17, within budget (`gate_L13_recipe.json`). **"The method
  transfers; the geometry does not"** is the paper's one-line summary of this finding
  and is quoted almost verbatim in the paper (§5, "Generality via recipe").
  The EFE loop debugged ITSELF live across these cycles: a run-observation replay bug
  where rebuilding the belief state silently dropped prior observations; a "consumption
  rule" fix (a candidate that PASSES raises its own pragmatic value under naive EFE
  scoring, so a naive selector will re-propose already-won experiments forever — fixed
  by marking consumed candidates); a cost-model fix (assumed 0.1 GPU-h per candidate
  when actual costs varied 0.15–1.0, which was FLIPPING WHICH CANDIDATE THE SELECTOR
  PICKED — moved to per-candidate registered costs in each menu).
- **L14** — menu 4. Three cycles. (1) amplitude scaling on Qwen3: strictly monotone dose
  response 0.05→0.20→0.40→0.78 at α=0.1/0.2/0.3/0.45, all within budget — but flagged
  as SCREEN-TIER, SINGLE-SEED "trend," not "law," by the closing adversarial review
  (#11) — a distinction that mattered a lot in later loops. (2) recipe transfer
  CONFIRMED at 4 seeds (3 new independent-stream seeds + the original, 0.33–0.48 lift,
  all above threshold, all gated>prefill — `gate_L14_multiseed.json`). (3) readback
  recalibration: the āgama-recognition acceptance test's thresholds (how close must a
  concept's rank get to top-M, how much must it improve, to count as "the model took
  the suggestion") were screen-tier defaults inherited from L3; swept 36 (top_m, gain)
  settings against actual behavioral hits, best setting (top_m=5, gain=0) reaches
  balanced accuracy 0.68 vs a 0.6 bar — flagged by the closing review as an
  UNCORRECTED-multiple-comparisons search (36 settings, report the max) and downgraded
  to "screen-exploratory." **H4 phase 1 SHIPPED here**: the unified `prabodha` console
  entrypoint (`src/prabodha/cli.py`, wired via `pyproject.toml`'s
  `[project.scripts]`). Paper (`docs/paper/paper.tex` → `paper.pdf`) and the dual-
  audience HTML explainer (`docs/artifact/prabodha_story.html`, generated by
  `scripts/tools/make_artifact.py`) BOTH FIRST SHIPPED here and updated every loop
  since.
- **L15** — menu 5, resolving L14's two downgrades. (1) readback recalibration
  HELD-OUT test: the chosen (top_m=5, gain=0) setting, FIXED (no re-sweep), on a
  corpus of stubs disjoint from the calibration set, with the 0.6 threshold
  PRE-REGISTERED before the run (this is the correct way to close a multiple-
  comparisons objection — fix the winner, test it fresh): balanced accuracy 0.637,
  passes 0.6 — but the review (#12) noted the margin (0.037) sits INSIDE the metric's
  own binomial confidence interval at n=40, so it stayed at screen tier rather than
  being promoted to confirm. (2) amplitude "law" upgrade attempt: 2 NEW qwen3 seeds
  (123, 777) reproduce the L14 dose curve almost exactly, monotone per-seed, within
  budget — genuinely earns "confirm" on Qwen3. But the review (#12) caught that the
  SECOND plant's contribution (Nemotron's replayed L8 grid) was FLAT
  (0.375→0.375→0.40, saturated, at an α-boundary L8's own summary had already flagged
  as marginal) — so "law" was narrowed to "confirmed on the weak-transport plant
  (Qwen3) at 3 seeds; the strong-transport plant contributes ordering-only, not
  replication; two-plant dose-response replication stays open." **H4 phase 2 SHIPPED
  here**: the Claude Code plugin, `integrations/claude-code-plugin/`, three skills
  (`lens-map`, `steer-verify`, `research-propose`), every default in the skill docs
  citing a specific gate.
- **L16** — menu 6, from L15's two open scopes. (1) corpus robustness: does the
  core-claim's lift generalize across STUB STYLES, not just the one hand-picked corpus
  used everywhere? Two NEW pre-registered stub styles (narrative-past, descriptive-
  scene) both pass (+0.25, +0.30) alongside the already-known-hard L15 held-out corpus
  (+0.15, known fail) → 2/3, criterion met. Piggybacked `--record-readback` on these
  same runs (triples the readback-calibration sample size at zero extra GPU cost) —
  pooled n=120 balanced accuracy REGRESSES to 0.590, BELOW the 0.6 bar — an honest
  DOWNGRADE of the acceptance test, carried explicitly into the plugin's steer-verify
  skill ("weak signal, never an acceptance gate alone; behavioral checks are ground
  truth"). (2) nemotron fine-grid BELOW its L8 saturation point (α 0.002–0.02): real
  dose response found (0.03→0.15→0.28→0.28, 2/3 pairs rising >0.05), config-scoped to
  this experiment file rather than declared a universal replication.
- **L17** — menu 7, the "self-audit loop": both cycles were pure resolution of prior
  open items, and BOTH surfaced genuine self-corrections. (1) cross-config dose test:
  turns out the two configs (e8dose, e5align) share stubs/concepts/decoding and differ
  ONLY in arm set — so this became "arm-set robustness," narrower than the registered
  name implied (candidate names can overreach their actual test — a lesson worth
  remembering). Because content was matched, this ALSO exposed that `gate_L8_dose.json`
  predates the L9 stream-correlation fix and its gated-arm levels run ~0.1 HIGHER than
  clean-stream re-measurement at the one matched α point — flagged PROVISIONAL (not yet
  proven across the whole grid) pending a dedicated re-run. (2) corpus seed variance:
  the FIRST GENUINE HONEST NEGATIVE OF THE PROGRAM at the pre-registered "stays screen"
  branch: re-running L16's two new corpora at seeds {123, 777}, corpus B
  (descriptive-scene) held (3/3), but corpus A (narrative-past) was SEED-FRAGILE (1/3:
  0.25/0.075/0.10) — its L16 single-seed pass was a favorable draw. This retroactively
  QUALIFIES the L16 claim. **Prompted a full single-seed audit of every confirm-tier
  claim in the program** — reassuringly, ALL of them (core claim 6 seeds, alignment 3,
  recipe transfer 4, amplitude-Qwen3 3) were already multi-seed; the fragility was
  entirely confined to the screen-tier corpus work, and was caught right there. H4
  phase 3 (README results table, `examples/quickstart_qwen3.md`, NOTICE/license audit)
  shipped here.
- **L18** — menu 8, resolving L17's two provisional/open items — **the loop where the
  program caught ITS OWN adversarial-review-prompted error**. (1) canonical L8
  re-measurement: full grid on current code, ONE seed (42) — gated-arm level exactly
  −0.10 at ALL THREE α points, a suspiciously clean uniform number. I initially inferred
  this meant a "global additive stream-bias." **The closing review (#15) demanded I
  check the offset across ALL arms, not just the gated one — and it turned out to be
  ARM-SPECIFIC** (gated −0.10 uniformly, but the continuous arm actually rose +0.10 at
  low α, others varied). The "additive bias" inference was formally WITHDRAWN; only the
  gated-arm's specific levels are superseded (fig2 now sources the corrected numbers);
  L8's headline ORDERING conclusion (gated beats prefill; gating = schedule-efficiency)
  stands untouched. This is documented as a general lesson: a clean uniform number,
  checked on only ONE dimension, can hide dimension-specific structure — check across
  every dimension before inferring a mechanism. (2) narrative-past seed-fragility
  diagnosed as UNDER-AMPLITUDE, not corpus-intrinsic: at α=0.2 (double the original)
  the corpus passes 3/3 seeds (0.43/0.28/0.23, one — seed 777 — barely). This SUGGESTED
  (not yet established — flagged explicitly as a hypothesis) that the calibration
  recipe might have a per-CORPUS amplitude axis (stub difficulty) in addition to its
  per-MODEL axis (lens transport strength).
- **L19** — menu 9, confirming L18's two flagged debts — **the loop where the program
  caught an EVEN MORE SUBTLE version of the same error class**. (1) L8 gated-arm offset
  re-run at 2 MORE seeds (123, 777) at both α: mean offset −0.108/−0.067, all 6
  per-seed offsets negative, both means inside the registered [−0.15,−0.05] band → the
  gated-arm supersession from L18 is now CONFIRMED at n=3 seeds, not n=1
  (`gate_L19_l8ms.json`, tier=confirm). Variance (2.5× spread across seeds) is
  disclosed rather than smoothed over. (2) corpus-amplitude axis, run as a fresh
  SAME-SESSION 2×2×2 grid (2 corpora × α{0.1,0.2} × seeds{42,777}) to remove the
  cross-session confound the L18 result carried: BOTH corpora's mean lift roughly
  DOUBLES with amplitude (a strong directional confirmation), but the STRICT registered
  margin criterion on the single hardest cell (narrative-past, seed 777, needing ≥0.05
  margin over the 0.2 threshold) fails — it reads 0.225, a 0.025 margin. **I initially
  wrote that this cell's EXACT match to its earlier L18 cross-session reading "rules out
  noise, points to a stable harder floor."** The closing review (#16) caught something
  the L9 stream-fix should have made me suspicious of immediately: checking
  `e4_cli.py`'s per-generation seeding scheme
  (`hash(seed | arm | concept | stub)` — see §1's L9 note) shows it does **NOT**
  depend on α or the `--loop` tag. Re-dispatching the IDENTICAL (seed=777, corpus=A,
  α=0.2) cell across two different loop labels was THEREFORE MECHANICALLY GUARANTEED
  to reproduce bit-for-bit — it is one deterministic computation observed twice, NOT
  two independent draws, and building a scientific inference ("stable floor," "rules
  out noise") on it was wrong in a much deeper way than "it's just one data point."
  The inference was fully withdrawn; the gate relabeled from "PARTIAL" (which risks
  reading as a qualified pass) to "FAIL-ON-MARGIN"; only genuinely n=1 independent
  observation stands at that cell.

**The throughline across L17→L18→L19** (this is the single most important
methodological pattern to carry forward): **every one of the last three loops involved
the adversarial review catching a real reasoning error the closing agent had made**, not
just tightening prose. Read that as: the review step is not decorative, and the same
family of trap — "a number looks clean/reproduces exactly, therefore it must mean
something" — recurred THREE TIMES (L9's stream-correlation bug, L18's arm-specific
offset misread as global, L19's determinism-guaranteed reproduction misread as
independent replication). **Any future agent should treat "this reproduced exactly" or
"this offset is suspiciously uniform" as a prompt to check the code path that produced
it BEFORE writing an inference about the underlying phenomenon**, not after.

---

## 3. Current confirmed claim set (as of PR #22 / commit 6031f85)

This is the load-bearing summary — cross-check every number against its cited gate file
in `gates/` before repeating it anywhere new. Do not trust this table blindly; it is a
snapshot, and the whole point of this program is that gates are the ground truth, not
prose.

| # | Claim | Tier | Evidence |
|---|---|---|---|
| 1 | Workspace-band structure + verbalizable content replicate across 3 model families, 2 sizes; loadability scales with size, collapses on distilled lineage | screen, multi-model | `gate_L1*.json`, `gate_L2*.json` |
| 2 | A workspace band is legible ONLY to a lens targeted at that band's own exit; final-target lenses are structurally blind to it | screen | `gate_L2b.json` |
| 3 | Event-gated (sphuraṭṭā/uncommitted-moment) writes steer behavior within the entropy budget — the CORE CLAIM | **confirm, 6 seeds** | `gate_L9_alignconf.json`, `gate_L11_rep.json` |
| 4 | Gated schedule beats rate-matched control (alignment matters beyond mere sparsity) | sign-consistent 6/6, p≈0.016 | `gate_L11_rep.json` |
| 5 | Greedy/argmax decoding mechanically masks all decode-time writes; sampling regime required | mechanism, established | `gate_L4b.json` |
| 6 | Method transfers to a second plant (Qwen3-4B) via a calibration recipe (amplitude ∝ 1/lens-transport-strength) | **confirm, 4 seeds** | `gate_L13_recipe.json`, `gate_L14_multiseed.json` |
| 7 | Amplitude dose-response is monotone on the weak-transport plant (Qwen3) across seeds; the strong-transport plant (Nemotron) confirms an active range one order of magnitude lower, saturating | **confirm (Qwen3, 3 seeds)** / screen (Nemotron active range) | `gate_L15_amp_joint.json`, `gate_L16_fine.json` |
| 8 | Steering lift generalizes across two of two new pre-registered stub styles at a fixed amplitude; the recipe likely has a per-corpus amplitude axis (raising amplitude fixed the one seed-fragile style) — **the corpus-amplitude axis DIRECTION is confirmed; the strict margin criterion on the hardest cell is NOT met (fail-on-margin)** | screen / fail-on-margin | `gate_L16_corpus.json`, `gate_L17_cvar.json`, `gate_L18_npretry.json`, `gate_L19_cax.json` |
| 9 | āgama-readback verdict (the "did the model take the suggestion" acceptance test) is a WEAK, non-oracle predictor of behavioral hits (balanced accuracy 0.59–0.64 depending on corpus, over-promises far more than it under-promises) — never use it as a sole acceptance gate | screen, honest negative | `gate_L14_readback.json`, `gate_L15_readback.json`, `gate_L16_corpus.json` |
| 10 | `gate_L8_dose.json`'s gated-arm LEVELS were pre-stream-fix inflated by ~0.10 (confirmed at 3 seeds, arm-specific — other arms not similarly affected); L8's ORDERING conclusion (gated>prefill; gating=schedule-efficiency) is UNAFFECTED and stands | confirm (offset), n/a (ordering was never in question) | `gate_L18_l8redo.json`, `gate_L19_l8ms.json` |
| 11 | The research program itself ran as a 26-cycle expected-free-energy selection loop over 9 registered menus, with 16 isolated adversarial reviews, at least 3 of which caught genuine reasoning errors before merge | meta-level, self-evidencing | `research/efe_ledger.jsonl`, `research/journal.md` |

**Honest negatives / open items currently on record** (do not silently resolve these
without a registered experiment — see §4 for what's already pre-registered):
- The ≥0.15 schedule-margin advantage over prefill never confirmed at that magnitude
  (reported by sign-consistency instead, see claim #4).
- Commitment-flash timing is directionally weaker than uncommitted-moment gating,
  4/4 sign-consistent, but not formally refuted as a mechanism — just downgraded.
- The trained-bridge comparator (PWM's CittaStore-based write path vs the current
  analytic `J^T u` write) is BLOCKED — the PWM world-model stack is not yet integrated
  on GB10. This has been carried, unaddressed, since menu 3. It is the single largest
  standing scope gap in the program.
- Cross-episode continuity (**anusaṃdhāna** in the Pratyabhijñā vocabulary) is
  deliberately unconverged/untested.
- The modality confound (does any of this depend on the model being purely text, vs
  multimodal) and "W-space beyond J-space" (is there a workspace structure the current
  Jacobian-lens instrument literally cannot see) are deliberately unconverged.
- Whether OTHER arms (continuous, prefill, every_k — not just entropy_gated) have their
  OWN seed-dependent offsets vs `gate_L8_dose.json` is UNEXAMINED — only the gated
  arm's offset was in scope for the L18/L19 work.
- The corpus-amplitude axis's hardest cell (narrative-past, seed 777) needs a
  GENUINELY NEW independent seed to move past fail-on-margin — re-dispatching the same
  (seed, α, corpus) triple will NOT produce new information (see the L19 determinism
  lesson above; the seeding is deterministic on this triple regardless of loop label).

---

## 4. Already-registered next steps (menu 9's carry-forward + explicit TODOs)

Configs already exist for these — an agent should USE them rather than re-registering:
- `configs/efe_menu9.yaml` was fully consumed by L19 (both its non-blocked candidates
  ran; `trained_bridge_arm` remains blocked). **No menu 10 exists yet** — the next
  session should either (a) register a fresh menu (menu 10) from the debts in §3's
  "Open items" list above, using `configs/efe_menu9.yaml` as a structural template
  (each candidate needs `id`, `cost_gpu_hours`, `resolution`, a `description` with an
  EXPLICIT, falsifiable success criterion stated in prose, and a `replay:` list of
  gates it should rebuild belief from), or (b) treat the program as substantively
  complete for now and move to a pure consolidation/closure pass (see §8).
- The trained-bridge blocker (`trained_bridge_arm` in every menu since menu 3) needs a
  SEPARATE, non-EFE-loop piece of work: integrating the PWM (Pratyabhijñā World Model)
  project's CittaStore-based write path onto this GB10. That is a substantial
  integration task, not a single experiment — it would likely deserve its own
  contract/loop rather than living inside a menu candidate. Check the sibling project
  (referenced in `NOTICE` and `docs/prior_art_internal.md`) for what's needed.
- H4 phase 3 is PARTIALLY done (README table, one quickstart example, license audit) —
  phase 3's remaining item per `docs/h4_plugin_architecture.md` is a SECOND public-model
  example (the existing one only covers Qwen3; a Nemotron or other-lineage example would
  round it out) plus a formal ADR-style decision record if the API needs any changes
  after the trained-bridge integration lands.

---

## 5. Reviews that caught real mistakes (read this before trusting any single-session claim)

There have been 16 isolated adversarial reviews. Most tightened wording or caught minor
scope issues. These three are qualitatively different — each one changed a CONCLUSION,
not just its phrasing, and each is illustrative of a recurring trap:

- **Review #9 (~L9)**: found that `torch.manual_seed(seed)` reset identically before
  every generation within a run correlated all "independent" trajectories — the fix
  (per-generation hashing) re-based every single sampling-derived number in the
  program up to that point. **Trap: shared randomness silently creates dependence
  between samples that look independent.**
- **Review #15 (L18)**: caught that a uniform-looking −0.10 offset across three
  amplitude points, taken as evidence of a "global additive stream-bias," was actually
  ARM-SPECIFIC once checked across all four arms (not just the one arm under test).
  **Trap: a clean number checked along only ONE dimension can hide structure visible
  along another dimension — always check the dimension you didn't originally look at.**
- **Review #16 (L19)**: caught that an "exact reproduction across two dispatch
  sessions" of one experimental cell, initially read as "rules out noise, this is a
  stable phenomenon," was in fact a MECHANICAL GUARANTEE of the pipeline's own
  deterministic per-generation seeding scheme (which does not vary with amplitude or
  loop label) — meaning the two readings were never independent observations at all.
  **Trap: "this reproduced exactly" is not automatically evidence about the
  phenomenon — it might be evidence about the measurement pipeline's own determinism.
  Always check whether the code path that produced a value could produce that SAME
  value again mechanically, independent of what's being tested, before treating
  reproduction as corroboration.**

**Practical instruction for the next agent**: before writing an inference of the form
"X reproduced, therefore Y is a real/stable phenomenon" or "this number is suspiciously
clean, that must mean Z", stop and grep the relevant CLI/composer code for where the
value came from, and ask specifically whether identical inputs (seed, config, dispatch
label) could produce that identical value BY CONSTRUCTION. This has now happened three
times and each time cost a review round to catch after the fact — catching it before
writing the finding down would be strictly better.

---

## 6. The four founding deliverables — current state and where to find them

1. **Empirical research** — `research/journal.md` (append-only decision log, 757
   lines, the deepest narrative record), `research/efe_ledger.jsonl` (machine-readable
   propose/observe/spend/skip/divergence event log, stateless-replayable),
   `research/state.json` (loop statuses + GPU-hour budget ledger per loop),
   `gates/*.json` (118 files; every one is a `GateReport` — see
   `src/prabodha/contracts/closure.py` for the pydantic schema — with a `code_gate`
   and a `domain_gate`, each with a `verdict` and `evidence`; composed/derived gates
   like `gate_L19_cax.json` typically have a `scripts/tools/compose_L*.py` script that
   built them from raw per-run gates).
2. **Paper** — `docs/paper/paper.tex` (LaTeX source, sections: parallel-as-spec,
   instrument, band-voice, steering clause-by-clause, generality-via-recipe,
   active-inference method, honest negatives, reproducibility, dual-register glossary
   appendix), compiled to `docs/paper/paper.pdf` via `latexmk -pdf`
   (`~/.local/bin/latexmk` on this box). Figures are ALL derived, never hand-edited:
   `scripts/tools/make_figures.py` regenerates all 7 figures
   (`docs/paper/figures/fig1..fig7_*.{pdf,png}`) from the gate JSONs directly — RE-RUN
   THIS ANY TIME A CITED GATE CHANGES, then recompile the PDF. Do not edit figures by
   hand; edit the composer script that reads the gate and regenerate.
3. **Tool** — the `prabodha` Python package (`src/prabodha/`), installable via
   `pip install -e .` (or `.[hybrid]` for linear-attention model support), exposing a
   console entrypoint `prabodha` (wired in `pyproject.toml`'s `[project.scripts]`,
   implemented in `src/prabodha/cli.py`) with subcommands `lens-fit`, `lens-eval`,
   `lens-vis`, `steer`, `research`, `figures` — each dispatches to the corresponding
   tested module CLI. `examples/quickstart_qwen3.md` is a gate-backed walkthrough
   (expected numbers are the actual committed gate results, so a reader can tell
   instrument drift from user error).
4. **Claude Code plugin** — `integrations/claude-code-plugin/` (`.claude-plugin/
   plugin.json` + three skills under `skills/`: `lens-map`, `steer-verify`,
   `research-propose`). Every default documented in these skills cites the specific
   gate that measured it — e.g. the steer-verify skill's guidance on amplitude
   calibration cites the recipe-transfer gates, its readback-verdict caveat cites the
   L14/L15/L16 readback gates. **Plus** the dual-audience HTML explainer artifact,
   `docs/artifact/prabodha_story.html` (generated by `scripts/tools/make_artifact.py`,
   same "regenerate from gates, never hand-edit" discipline as the paper figures),
   published as a Claude Artifact — the URL is stable across republishes as long as
   you pass the SAME file path to the Artifact tool from within a Claude Code session:
   `https://claude.ai/code/artifact/79a57137-58bf-4ca3-b464-5211adb81970` (favicon 🪔;
   republishing the same file path updates this URL in place — do not create a new one
   unless deliberately starting a new artifact).

**Update discipline for all of the above**: the operator was explicit — "keep updating
paper & html in each loop... paper and html are side consolidations only [to the
research], keep your focus on your objectives and run." In practice this has meant:
after every cycle that produces a new gate worth citing, (a) update
`scripts/tools/make_figures.py` if a figure needs a new data source, (b) regenerate
figures, (c) add/edit the relevant paragraph in `paper.tex`, recompile, (d) mirror the
same content change into `scripts/tools/make_artifact.py`'s HTML generation and
regenerate, (e) republish via the Artifact tool. Do this EVERY loop, not just at
milestones — it has never once been skipped across 19 loops and should not start being
skipped now.

---

## 7. Full PR history (all merged, chronological; use `gh pr view <n>` for full bodies)

```
#1  L1: E1 Qwen lens replication — review-complete, sign-off pending
#2  L1b: 27B size-matched retry — modulation scales and passes; closed VALID_WITH_CAVEATS
#3  L2: PWM-stack lens + E7 articulation — split-as-registered; L3 entry gate defined
#4  L3-prep: Selectivity@5 readiness gate — NO_GO at layer 6; sweep isolates write-site fork
#5  L2b: mid-target-lens discriminator — the band speaks when asked in its own voice
#6  L3: E3 H5b redo — band writes steer, svātantrya binds; timing (not amplitude) is the lever
#7  L4: sphurattā-gated timing — first interventional domain PASS (under sampling)
#8  L5: auto-research cycle closed — EFE selector proposes, agent disposes, gates feed back
#9  L6: selector cycles 2-3 — alignment beats rate-matching; core claim confirmed 3 seeds
#10 L7: isolated program audit (review #8) — PASSING; Tier-0 metadata fixed; paper skeleton
#11 L7b: articulation null — E7 survives (model-intrinsic gradient); selector cycle 4
#12 L8: dose grid — two freedom currencies, amplitude boundary mapped
#13 L9: menu-2 cycles 6-9 — stream-correlation fix re-bases all sampling numbers
#14 L10: cross-plant honest negative — generality boundary; menu 2 consumed
#15 L11: menu 3 + cycle 11 — core claim 6/6 seeds; alignment sign-consistent; loop law in code
#16 L12-13: flash revised; the per-plant recipe TRANSFERS — gated 0.40 on Qwen3-4B
#17 L14: menu-4 cycles 14-16 — recipe CONFIRMED 4/4 seeds; paper/HTML/CLI consolidations
#18 L15: menu-5 confirms (dose law qwen3 3/3 seeds; readback held-out) + Claude Code plugin
#19 L16: menu-6 — corpus robustness 2/2; nemotron active-range dose; readback honest negative
#20 L17: menu-7 consolidation — self-audits (L8 levels, single-seed claims) + H4 phase 3
#21 L18: resolution loop — L8 levels superseded (arm-specific), narrative-past under-amplitude
#22 L19: menu-9 confirms — L8 offset confirmed 3 seeds; corpus-amplitude fail-on-margin
```

---

## 8. How to continue — concrete next actions, in priority order

1. **Verify you're starting from a clean, merged state.** `git -C
   /home/sharaths/projects/prabodha log --oneline -1` should show `6031f85` (or later
   if this document is stale — check `research/state.json`'s `current_loop` field and
   the PR list via `gh pr list --state merged --limit 5` to see if anything has landed
   since this document was written). If a worktree from L19 still exists
   (`.claude/worktrees/heuristic-golick-c4f418`, branch `loop/l19-menu9`, already merged)
   it is safe to `git worktree remove` it from the MAIN checkout, not from inside it.
2. **Decide: another EFE cycle, or a closure/consolidation pass?** The program has run
   26 cycles across 9 menus; the core claims (§3, rows 3, 4, 6) are solid confirm-tier
   results, unlikely to move. The remaining open items (§3's honest-negatives list,
   §4's registered-but-unresolved items) are each individually small. A reasonable
   judgment call: either (a) run ONE more focused menu (menu 10) targeting the single
   highest-value remaining open item — likely the corpus-amplitude axis's fail-on-margin
   cell, since it needs only a genuinely new seed, not new infrastructure — then move
   to closure, or (b) treat the program as at a natural stopping point for empirical
   work and shift fully to consolidation (finish H4 phase 3, do a final full-program
   adversarial audit analogous to the L7 program audit, write a "final state" summary
   into SPEC.md/PRD.md's evolution logs). Either is defensible; this document does not
   mandate one over the other — that judgment belongs to whoever picks this up, informed
   by whatever the operator says next.
3. **If registering menu 10**: open a new worktree (`git worktree add
   .claude/worktrees/<slug> -b loop/l20-menu10`), write `configs/efe_menu10.yaml`
   following the exact structure of `configs/efe_menu9.yaml` (id/cost/resolution/
   description-with-explicit-criterion/replay), add a budget line to
   `research/state.json` (`L20_spent: 0`, `L20_cap: <hours>`) BEFORE the first dispatch
   (the guard will correctly refuse otherwise — see the L14 opening of this session's
   history for exactly this mistake and its fix), propose the first cycle via
   `src/prabodha/efe/runner.py`'s `propose_next()`, and follow the dual-gate,
   pre-registration, adversarial-review discipline exactly as every prior loop did.
4. **If closing the program (or this phase of it)**: run one final program-wide
   adversarial audit (isolated agent, briefed with the gates directory + this handoff
   document, explicitly tasked to attack the CURRENT claim table in §3 the way review
   #8 attacked the whole program at L7), fold any corrections into the paper/HTML one
   last time, update `SPEC.md` and `PRD.md`'s evolution logs to reflect final status,
   and consider whether the operator wants a final consolidated release tag.
5. **Either way**: keep updating `research/journal.md`, `research/efe_ledger.jsonl`,
   `research/state.json`, the paper, and the HTML artifact at every step — this has
   never been skipped in 19 loops and is core to the program's own claim of being
   self-auditing. Do not let this handoff document itself go stale without a note —
   if you make significant progress, either update this document in place or write a
   new dated one and link it from here.

---

## 9. Key files index (for quick navigation)

- `CLAUDE.md` — the project's working-agreement contract; READ THIS, it takes
  precedence over everything in this handoff if they ever conflict.
- `HANDOFF.md` — the ORIGINAL handoff from the operator at project start (historical;
  this document supersedes it for current state but not for founding intent — both are
  worth reading).
- `docs/jspace_pratyabhijna_scoping.md` — the conceptual source of truth for the
  parallel this whole program operationalizes.
- `SPEC.md`, `PRD.md` — living technical spec / product doc, evolved at every loop
  closure (see each file's own "Evolution Log" section).
- `RULES.md` — hard invariants (R1–R8ish; R7 = vendor code unmodified, R8 = clean
  external API surfaces, claims discipline).
- `AGENTS.md` — which specialist agents/skills are assigned to which kind of work.
- `docs/triz_log.md` — TRIZ contradiction-resolution log for engineering tradeoffs
  (e.g. GB10 bandwidth-bound contention).
- `research/journal.md` — the deepest narrative record, append-only, chronological.
- `research/efe_ledger.jsonl` — machine-readable, replayable EFE selector event log.
- `research/state.json` — loop statuses + GPU-hour budgets.
- `gates/*.json` — 118 gate records, the ground truth for every number in this doc.
- `configs/efe_menu*.yaml` — registered experiment menus, one per "menu era."
- `configs/experiments/*.yaml` — individual experiment pre-registrations.
- `configs/models/*.yaml` — model configs (qwen3, qwen27b, nemotron4b, tiny_smoke).
- `src/prabodha/` — the library: `lens/` (instrument), `steering/` (writer/timing/
  verifier/injector/scoring — the doctrine implementation), `efe/` (auto-research
  selector/ledger/runner/lint), `contracts/` (the gate schema), `cli.py` (H4 entrypoint).
- `vendor/jacobian-lens/` — Anthropic's reference lens implementation, vendored
  unmodified.
- `scripts/lib/gpu_guard.sh` — mandatory pre-dispatch GPU safety check.
- `scripts/tools/make_figures.py`, `make_artifact.py` — regenerate paper figures / HTML
  from gates; NEVER hand-edit the outputs.
- `scripts/tools/compose_L*.py` — one script per composed/derived gate; read these to
  understand exactly how any headline number was computed from raw per-run gates.
- `docs/paper/paper.tex` / `paper.pdf` — the paper.
- `docs/artifact/prabodha_story.html` — the dual-audience HTML explainer (published as
  a Claude Artifact).
- `docs/h4_plugin_architecture.md` — the H4 (tool + plugin) packaging plan and status.
- `integrations/claude-code-plugin/` — the Claude Code plugin (H4 phase 2).
- `examples/quickstart_qwen3.md` — gate-backed public-model walkthrough (H4 phase 3).
- `docker-compose.yml`, `Dockerfile` — the GB10/aarch64 dispatch environment (image
  `prabodha/gb10:0.1`; services `l1`/`l1b`/`l2`/`l3`/`l4` all `pid: host` so
  `gpu_guard.sh` can see co-resident processes outside the container's own namespace;
  **note: application source is BAKED INTO the image at build time — only
  `outputs/`, `gates/`, and the HF cache are volume-mounted — so `docker compose build
  l4` is required after ANY change to `src/prabodha/` before the next dispatch, or the
  container will run stale code**, a mistake made once in L15/L16 and worth avoiding.
- `/home/sharaths/.claude/projects/-home-sharaths-projects-prabodha/memory/
  prabodha-l1-state.md` — the CROSS-SESSION memory file (outside this repo, in Claude
  Code's own memory store) that a fresh Claude Code session will load automatically;
  it carries a compressed version of everything in this document and should be kept in
  sync with it, but this document is the authoritative long-form version.

---

## 10. A note on tone and scope discipline for whoever reads this next

This program's defining discipline is not "find impressive results" — it is "find out
what's true, report the honest size of every finding, and let three independent
adversarial checks catch what one pass misses." The paper and HTML artifact are
deliberately conservative relative to what a less careful pass might have written: "law"
was downgraded to "trend" until multi-seed evidence justified restoring it; a
"reproduces exactly" observation that felt like strong corroboration turned out to be a
mechanical artifact and was fully withdrawn rather than softened; an honest negative
(narrative-past's seed fragility) was allowed to stand and retroactively qualify an
earlier confirmed-sounding claim rather than being quietly patched over. Whoever
continues this work should preserve that discipline exactly — the program's actual
scientific product, at this point, is as much the METHOD (dual-gate ralph loops +
adversarial review catching real errors, on the record, three separate times) as it is
any single steering result. Do not let a desire to "finish" or "make more progress"
erode the standard that got the program this far.
