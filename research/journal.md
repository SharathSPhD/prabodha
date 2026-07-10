# prabodha research journal (append-only)

## 2026-07-07 — L0 foundation
- Scoping doc adopted as conceptual source of truth (copied to docs/).
- Interview decisions: E1 (Qwen replication) is L1; GB10 only (5090 not set up; prabhasa+PSALM
  co-resident, bandwidth-bound); ralph closure = code AND domain; GitHub via connector (tools not
  yet exposed — publish deferred).
- TRIZ C1–C3 resolved (docs/triz_log.md). Sibling harvest (docs/prior_art_internal.md): porting
  prabhasa EFE selector/ledger/autopilot + gpu_guard; ACD metrics patterns; neo-fm five-point gate.
- Infrastructure honest negative: SMB projects mount cannot host live git (unlink/lock semantics) —
  canonical repo lives in dev VM + GitHub; mount gets rsync mirror + git bundle. Sublated the
  "repo lives on the drive" assumption with evidence (failed lock/rm operations logged in session).

## 2026-07-07 — GPU policy sublation + GB10 handoff
- SUBLATION (bādha): v1 guard rule "real runs require idle GPU" (precision: cautious default) is
  sublated by operator instruction "share with prabhasa, don't hesitate" (higher precision: owner's
  explicit policy). v2 = shared mode: proceed under co-residency at nice=10 with contention recorded
  in gate JSON; refuse only on kill-switch or <24GiB free unified memory. Old rule preserved here,
  not deleted.
- GitHub repo SharathSPhD/prabodha exists (public, empty — awaiting first push). Cowork sandbox has
  no push credentials and no network route to the Spark (tailnet unreachable); publish handoff runs
  via the GB10-side session or operator (see docs/gb10_handoff.md).
- Dockerized: Dockerfile (NGC pytorch aarch64) + docker-compose (courtesy caps 48g/10cpu). Docker is
  the preferred GB10 execution route (operator instruction; replaces venv route).

## 2026-07-07 — L1 GB10 session start (Claude Code on the Spark)
- Bundle history published: main @ abf8f5d pushed to github.com/SharathSPhD/prabodha (was empty).
  Session works in a Claude Code worktree; commit identity set to qbz506@york.ac.uk.
- INFRA CORRECTION (bādha, evidence: df -T): /home/sharaths/projects on the Spark is native ext4,
  not SMB — the .smbdelete ghosts are relics of the mirror copy. The parent checkout
  ~/projects/prabodha has an odd all-deleted index state (mirror-copy artifact); left untouched
  (harness denied hard reset — operator may want to re-clone from GitHub instead).
- FIX: gpu_guard v2.1 — GB10 nvidia-smi reports [N/A] for memory.used/total (unified memory);
  fallback to /proc/meminfo MemAvailable as the free-memory floor. v2 semantics preserved.
- BUILT: pretraining_like corpus resolver (deferred at L0 by design). Decision: flat
  one-prompt-per-line file generated once by scripts/tools/make_fit_corpus.py from the LOCAL
  wikitext-2-raw-v1 arrow cache (seed 42, 64 non-overlapping 128-word windows) — keeps dataset
  libs out of the runtime image, fit corpus inspectable. Known deviation from paper protocol
  (model's own pretraining distribution, n≈1000): wikitext-2 proxy at n=64, screen tier;
  Nanda reports n≈1–10 near-parity.
- Shared-mode reality at dispatch: PSALM GPT-BERT run live (train_100m_gb10.py); prabhasa
  train_130m not running. Guard: proceed, nice=10, contention=psalm recorded.

- 2026-07-07 E1 gate written (gates/gate_L1.json): code=pass domain=fail contention=psalm

## 2026-07-07 — L1 first gate: code=pass, domain=fail (1/3 hypotheses) — and what it teaches
- gates/gate_L1.json: H_report -0.32 (thr 0.5) FAIL; H_bands contrast 0.42 (thr 0.15) PASS but
  degenerate partition [0,2)/[2,6)/[6,36); H_modulation 0.0 FAIL — read at band_layers=[2..5]
  inherited from that partition (failure is downstream). contention=psalm throughout.
- DIAGNOSIS (verified on CPU with synthetic logits): the union-top-K Spearman metric has a
  structural null floor of ≈ -0.72 (disjoint top-K sets anti-correlate over the union support);
  zero correspondence reads as -0.7, not 0. Observed curve rises monotonically layer 0 (-0.69,
  ≈ the null floor) -> layer 34 (+0.43): the QUALITATIVE verbal-report signature (rho rising
  with depth) is PRESENT; the 0.5 threshold was mis-calibrated for this metric geometry.
- GPU ledger: L1_spent 1.3h of 2.0h cap (incl. 12min lost to the honest-contention restart and
  the 64->16 prompt sublation at the prompt-16 checkpoint).
- Next per protocol: adversarial domain review (fresh agent, contract+gate only), then iterate
  eval-only (metric recalibration = disclosed pre-registration amendment; no refit needed) or
  prune per e1.yaml prune_rule.
- OBSERVATION (unconverged thread "meta-tokens", HANDOFF §5): slice page for the instructed-fire
  prompt tracks 51 distinct CJK chars incl. 火/焰/炎 (fire/flame/blaze) and weather terms
  (热/冷/晴) — Nanda-style dense Chinese tokens surface as lens verbalizations on Qwen3-4B.
  Consequence for H_modulation: the hit criterion counts only the ENGLISH first-token id;
  cross-lingual verbalization (fire -> 火) is structurally missed. Second candidate explanation
  for the 0.0 hit-rate, alongside the degenerate band inheritance. Artifact: outputs/l1/slice_sample.html.

- 2026-07-07 E1 gate written (gates/gate_L1.json): code=pass domain=fail contention=psalm

## 2026-07-07 — L1 run 2 (eval-only, amendments A1–A3): the picture becomes coherent
- gates/gate_L1.json regenerated (run-1 preserved as gate_L1_run1.json). Still domain=fail
  (1/3), but now INTERPRETABLE:
  - H_report (calibrated support, null~0): 0.180 vs thr 0.4 — FAIL, but permutation p≈1e-4:
    correspondence is REAL and rising (layer 33: 0.39, layer 34: 0.62); it is concentrated in
    the last ~3 layers rather than the whole late third. Per-prompt spread -0.20..0.42.
  - H_bands: PASS 0.306 with SANE bands [0,6)/[6,30)/[30,36) after min_band_size 6 —
    early/middle/late three-band structure present (run-1's degenerate cut eliminated).
  - H_modulation: 0.10 (4/40) vs shuffled-concept null 0.0104 — ~10x chance, far below 0.5.
    Hits: water, music x2, bread (all en_mid variant; zh variants did not fire).
- Screen-tier reading: instrument mechanically sound; all three signatures qualitatively
  present and significant vs null; quantitatively weaker on 4B than thresholds implicitly
  calibrated to Nanda's 27B replication. The prune_rule's size-matched (27B) retry cannot fit
  L1's residual budget (spent 1.45h of 2.0h cap) — escalation is an operator decision.

## 2026-07-07 — L1 adversarial reviews + disposition handoff
- Review #1 (fresh agent, contract+gate only): converged independently on the support-calibration
  artifact ("polarity"), degenerate bands, and modulation protocol opacity; five evidence demands.
- Review #2 (same reviewer, amended gate): demands 1,2,4,5 met; demand 3 (functional band
  validation) unmet — refitting bands and re-targeting modulation in the same run is circular.
  NEXT-LOOP RULE: pre-register fixed bands before scoring modulation. Composite verdict:
  "UNDERPOWERED, not broken"; recommendation (b) 27B size-matched retry (~6–7 GPU-h shared).
- Disposition (a: proceed to L2 with caveats / b: 27B retry / c: prune-at-4B) is the operator's
  per prune_rule "escalate to 27B decision at gate". Contract card updated; sign-off pending.
- Loop L1 status: review-complete, sign-off pending. All state in repo; fresh-agent re-entry safe.

## 2026-07-07 — L2 scouting (read-only, pre-contract)
- PWM Phase-7 TTFT cascade model identified: fast path C1/C2 = nemotron-mini:4b via OLLAMA
  (quantized blob, OpenAI-compatible HTTP at :11434; engine.py:41,251-269; ADR-001), slow path
  nemotron-3-super:120b (local GGUF symlink, pwm-phase3/models). CONSTRAINT for L2: the J-lens
  needs white-box access (residual streams + backward) — impossible over Ollama HTTP. L2 must
  fit on the HF bf16 checkpoint of the same architecture (nvidia Nemotron-Mini-4B family),
  with the bf16-vs-Ollama-quant mismatch disclosed as a deviation. To be encoded in the L2
  contract card at loop start.

## 2026-07-08 — L1 signed off (disposition b); L1b opened
- Operator sign-off in-session; PR #1 squash-merged to main (aea5c1b). Disposition (b):
  27B size-matched retry, new budget line L1b_cap=6.0 GPU-h.
- L1b pre-registered (configs/experiments/e1b.yaml) INCLUDING the decision rule and the
  review-#2 circularity fix: modulation band FIXED a priori (depth_middle_third).
- Target: Qwen/Qwen3.6-27B (Nanda's exact reference; apache-2.0, safetensors). bf16 ~54GB
  weights -> idle-window job: guard min_free=80GiB (new per-job floor arg); compose service
  l1b without courtesy caps. PSALM at step ~41k/48.3k (~3.3s/step) -> idle window expected
  in ~6-7h; weights downloading meanwhile (network-only, no GPU touch).
- L1b pre-flight (CPU, no GPU touch): qwen3_5 is a HYBRID arch (linear-attention layers; HF
  falls back to slow torch path absent fla/causal-conv1d kernels — fit will run slower than
  a pure-transformer estimate). jlens layout detection + fit + apply verified on a shrunken
  random Qwen3_5ForCausalLM. Checkpoint keys are model.language_model.* with mtp.*/model.visual.*
  in _keys_to_ignore_on_load_unexpected -> AutoModelForCausalLM.from_pretrained loads the text
  backbone cleanly (vision tower + MTP head dropped by design). Weights (54GB) cached locally.
  Idle-window watcher armed (PSALM exit + >=80GiB free).
- L2 target identified (subagent scout): Ollama nemotron-mini:4b == HF nvidia/Nemotron-Mini-4B-Instruct
  (nemotron arch, 32 layers, d3072, ~8GB bf16, NOT gated, plain AutoModelForCausalLM, no
  trust_remote_code; lineage Minitron-4B-Base <- Nemotron-4 15B distillation). Weights being
  cached. L2 deviation to pre-register at loop open: lens on bf16 HF twin vs Ollama-quantized
  production serving.
- L1b dispatched in the idle window (PSALM completed 10:32 BST, ~6h earlier than projected —
  watcher had a pgrep self-match bug, caught by manual check). Guard: contention=none, 115GiB.

## 2026-07-08 — L1b run 2 (fast-path kernels): pace and budget
- Torch-fallback run 1 aborted after prompt 1 measured 52 min (13.8h projected). fla 0.5.1 +
  causal-conv1d 1.6.2 baked into image ("Blackwell detected" — kernels engage on GB10).
- Run 2 prompt 1: 1103s (18.4 min) — 2.8x faster. Projection 0.9h (aborted attempt) + 4.9h fit
  + ~0.5h eval ≈ 6.3h. L1b cap raised 6.0 -> 7.0 GPU-h, inside the operator-cleared "~6-7"
  range (contract sign-off), to preserve the pre-registered 16-prompt fit (n-comparability
  with L1) instead of cutting prompts again. Disclosed here and in e1b.yaml.

- 2026-07-08 E1 gate written (gates/gate_L1b.json): code=pass domain=fail contention=none

## 2026-07-08 — L1b gate: SPLIT verdict, and it is the finding
- gates/gate_L1b.json (27B, idle window, contention=none; NOTE: internal loop field reads "L1"
  — compose_gate hardcoded the label; plumbed --loop for future runs, JSON left untouched as a
  generated artifact). GPU: 6.1h of 7.0h cap (0.9h aborted torch-fallback attempt + 5.2h run).
- H_modulation 0.55 PASS (22/40 vs shuffled null 0.068; FIXED depth-middle-third band, layers
  21..41 of 63 — no CKA circularity). On 4B: 0.10. DIRECTED MODULATION SCALES WITH SIZE and
  passes on Nanda's reference — first full hypothesis pass; validates the workspace-band
  loading concept the steering doctrine (L3+) depends on. All hits en_mid/en_bare; zh variants
  never fired on either size (cross-lingual verbalization NOT confirmed at readout level).
- H_bands 0.269 PASS, bands [0,8)/[8,54)/[54,64) — three-band architecture replicates across
  sizes with similar proportions (4B: [0,6)/[6,30)/[30,36)).
- H_report 0.124 FAIL (p≈1e-4 above null; curve rises only in final ~3 layers to 0.353 at
  L62). Same weak regime as 4B (0.180, last-layer 0.617). The late-third-mean metric fails on
  BOTH sizes while significant-above-null on both: the anomaly is now isolated to the METRIC
  SHAPE (or a genuinely-final-layers-only consolidation), NOT model size.
- Decision-rule readout: none of the three registered branches fired cleanly (rule anticipated
  uniform scaling); the split IS the result. Comparison: research/l1_vs_l1b_comparison.md.

## 2026-07-08 — L1b closed VALID_WITH_CAVEATS (adversarial review #3)
- Review verdicts: modulation-scaling VALID (with null-comparability attack — rebutted: S/N
  ratios comparable 9.6x/8.1x, absolute threshold uniquely crossed at 27B, band confound runs
  AGAINST the claim); bands UNDERDETERMINED; H_report metric-shape UNDERDETERMINED; honesty
  VALID. Full record in contracts/L1b_size_matched_retry.md.
- Caveats carried to L2 pre-registration (also in research/state.json): uninstructed-prompt
  modulation control; same-band-mode comparisons; registered alternative H_report metric.
- Milestone merge to main per operator /goal directive; formal sign-off line remains open in
  the contract card for the operator.

- 2026-07-08 E1 gate written (gates/gate_L2.json): code=pass domain=fail contention=none

- 2026-07-08 E1 gate written (gates/gate_L2.json): code=pass domain=fail contention=none

## 2026-07-08 — L2 gate (runs 1+2): articulation passes; the control does its job
- Run 1: H_modulation 0.0 with shuffled null AND uninstructed control BOTH exactly 0.0 —
  the all-zeros signature diagnosed as BOS pollution (30/30 candidate variants flagged
  multi-token; SentencePiece prepends <s>). Fixed (specials=False for candidate ids only),
  regression-tested, run-1 gate preserved (gates/gate_L2_run1.json), eval-only rerun.
- Run 2 (gates/gate_L2.json, contention=none, ~0.4 GPU-h of 2.0 cap):
  - H_articulation PASS 0.639 (p≈2e-4): top-k negentropy of the lens readout RISES with
    depth on the PWM twin — the vāk-hierarchy (paśyantī→madhyamā→vaikharī) laminated
    articulation gradient E7 predicted and GNW does not. First pass of the program's
    discriminating observable.
  - H_report(last3) 0.384 vs 0.4 — near-miss, p≈1e-4, last layer 0.614: the final-layer
    consolidation shape replicates on a third model/architecture.
  - H_bands 0.137 vs 0.15 — near-miss with visually sane bands [0,6)/[6,26)/[26,32):
    the pruned/distilled Minitron lineage shows WEAKER (smeared) band contrast than either
    Qwen — candidate architectural finding (pruning homogenizes inter-layer structure?).
  - H_modulation 0.20 = shuffled null 0.196 = uninstructed control 0.20 → NO directed
    modulation on the PWM twin (margin 0.0; all 'hits' are two CJK piece-ids appearing
    regardless of instruction). The L1b-caveat control caught exactly what it was built to
    catch: incidental capacity masquerading as loading. Contrast: Qwen3.6-27B 0.55 vs null
    0.068. Directed loadability now looks size- AND lineage-dependent.
- prune_rule check: articulation PASSED, so L3 is NOT blocked; workspace-onset layer for the
  L3 write site = 6 (band map recorded in state.json), with the weak-contrast caveat.

- 2026-07-08 E1 gate written (gates/gate_L2.json): code=pass domain=fail contention=none

## 2026-07-08 — L2 closed (split-as-registered); review #4; L3 entry gate adopted
- Run 3 (single_token_only candidates): modulation 0.0 = null = control — the run-2 0.2 was
  zh byte-fallback noise, as review #4 suspected. Conclusion CLEAN: zero instructed
  loadability on the PWM twin, with candidates that fire on both Qwens.
- Review #4: articulation ARTIFACT-SUSPECT (lens-construction tautology + non-monotonic
  start) -> registered follow-up null (shuffled final logits); bands near-miss VALID;
  honesty VALID. L3 entry gate: Selectivity@5 at layer 6 (details in contract card).
- Milestone merge to main per standing directive. Full record: contracts/L2_pwm_stack.md.

## 2026-07-08 — L3 readiness: NO_GO at layer 6; selectivity sweep reframes the write-site question
- gates/gate_L3_readiness.json: Selectivity@5(layer 6) = 0.013 -> NO_GO (review-#4 gate).
- Full sweep (outputs/l2/selectivity_sweep.json): 0.00 for layers 0-5, rises smoothly through
  the "workspace band" (0.01@6 ... 0.36@25), crosses 0.60/0.75 ONLY at layer 30 (0.7625) —
  the final fitted layer. On the PWM twin, no intermediate layer is inside the report funnel
  as seen by a FINAL-TARGET lens.
- Two live readings (do not force closure — touches the unconverged "where recognition lives"
  thread): (i) the twin's report content genuinely consolidates only at the top (consistent
  with H_report's shape and the smeared bands on the distilled lineage) — then the "write at
  workspace onset" doctrine fails on this plant for the mirror-image reason H5b's v2 failed
  (too far upstream instead of too far downstream); (ii) the final-target lens is simply
  blind to mid-band structure (the articulation ARTIFACT-SUSPECT caveat, and W-space-beyond-
  J-space §10.3) — then the fix is lenses fit with INTERMEDIATE target layers (vendor fit()
  supports target_layer), giving each band its own decoder before any write experiment.
- L3 design fork (operator input wanted): (a) write-site sweep as the experiment itself;
  (b) switch plant to Qwen3-4B (known modulation 0.10 > 0, same consolidation shape though);
  (c) intermediate-target lenses first (reading (ii)) — cheapest, ~1 GPU-h, and it
  discriminates between the two readings before any interventional spend.

## 2026-07-08 — L2b mid-lens probe: the band speaks when asked in its own voice
- gates/gate_L2b.json: mid-target lens (target_layer 26 = band exit) in band [6,26):
  instructed hit rate 0.200 across SEVEN distinct concepts (iron/fire/water/bread/snow/gold/
  moon, both English variants), uninstructed control 0.000, shuffled null 0.023. The SAME
  probe through the FINAL-target lens read 0.000 (gate_L2.json run 3).
- Registered rule files this as outcome (ii) (hit 0.2 < 0.3 threshold) — recorded as such,
  no goalpost moves. But the evidence pattern materially supports weak reading (i): the band
  DOES carry directed, verbalizable loading that a final-target lens is blind to. Vāk
  reading: madhyamā content is audible only to a madhyamā-tuned instrument; the final-target
  lens hears only vaikharī. (Connects W-space-beyond-J-space, scoping §10.3.)
- L3 DESIGN CONSEQUENCE (firm): the readback verifier must read through BAND-TARGETED lenses.
  Write-site choice remains the operator's fork, now better informed: writes at the band with
  band-lens readback are instrumentally possible; final-behavior effect size is the open
  question the L3 experiment itself answers. Cost: 0.35 GPU-h (fit 47s/prompt + probe).

## 2026-07-09 — operator sign-off (L1b, L2, L2b); L3 opened on fork option (c)
- Sign-off recorded in contract cards. Fork decision: option (c) per-band-lens design —
  operator signed off without overriding the builder recommendation; L2b evidence (band
  content real but final-lens-invisible) is the empirical basis. Recorded here per the
  "decide and record" rule.

## 2026-07-09 — L3/E3 gate: band writes WORK; svātantrya is the binding constraint
- gates/gate_L3.json (contention=none, ~0.2 GPU-h): domain FAIL on both registered
  hypotheses — and the malas histogram is the finding:
  - svātantrya 20/40: FULL lens-visible uptake (loaded+amplified+persistent through the
    band lens) but entropy budget blown — mean output-entropy delta -2.081 nats vs the
    ±0.5 cap. The write steers too hard: continuous per-decode-step injection collapses
    freedom. karma 14/40 (loaded, faded by band exit). āṇava only 2/40.
  - Behavior: lift v3 = 0.40 vs v2 = 0.17 (bias 6.0), baseline 0.00 (bare stubs — clean).
    The band write DOMINATES the mouth write behaviorally (8/10 concepts, up to 0.75).
  - Quality: camatk drop v3 0.063 vs v2 0.021 — consistent with the entropy collapse
    (deterministic outputs -> repetition -> diversity/imagery loss).
- READING: the doctrine's per-unit-gentleness prediction is INVERTED at this operating
  point — v3 is stronger AND costlier. The failure mode is not loading (āṇava≈0) but
  temporal dosage. The evidence points at event-gated timing (write at selected moments,
  not every step) — precisely the L4 sphurattā mechanism. Alternative knobs: alpha down;
  prefill-only injection.
- REGISTERED FOLLOW-UP DECLINED WITH REASONS: e3.yaml permitted one alpha-0.2 retry on
  H_uptake failure — but uptake failed on the ENTROPY criterion, not loading; raising alpha
  would worsen exactly the binding constraint. Mechanical compliance against evidence would
  be pariṇāma without pratyabhijñā; recorded here instead of run.

## 2026-07-09 — L3 closed (honest-fail-with-finding); review #5; L4 = event-gated timing
- Registered α=0.2 follow-up RUN per review #5 (decline was selective-stopping-adjacent):
  bit-identical to α=0.1 — the cap binds; follow-up was structurally inert as registered.
  Lesson banked: check follow-up knobs against their own caps at registration time.
- Exploratory α=0.05 (labeled): triple dissociation — amplitude→lens loading; timing→
  behavior+entropy. Sphurattā-gated writes (scoping §3, deferred at L3 by design) are now
  the evidence-selected L4 mechanism, endorsed independently by review #5.
- Claims softened per review: "at ~10x entropy cost vs an untrained comparator, 2.3x surface
  rate; CIs overlap at n=40" — no dominance claim until dose-response + trained bridge.

## 2026-07-09 — L4/E4 gate: honest negative on entropy-gated timing; prefill write does the work
- gates/gate_L4.json (domain FAIL both): gated lift 0.17 (<0.2, one hit short) within budget
  (+0.39 nats); alignment advantage 0.00 (gated == rate-matched every_k == prefill_only).
- THE DOSE-RESPONSE: 1 prefill write -> 0.17 lift (+0.09 nats); ~8 timed decode writes ->
  0.17; 26 continuous -> 0.40 (+0.82). Decode-time writes at alpha=0.1 have near-zero
  marginal value AT ANY TIMING; only saturation writing adds lift, at ~9x entropy exposure.
- Honest negative: the high-entropy ("uncommitted moment") operationalization of sphurattā
  did NOT beat rate-matched or single-write controls on this plant. Candidate re-readings
  for a future registration: (a) sphurattā = commitment FLASH (entropy DROP) — the opposite
  gate; (b) alignment genuinely doesn't matter for band writes; (c) the useful knobs are
  prefill-write strength / multi-layer writes, not decode timing.
- Budget-currency note: continuous shows +0.82 mean-step-entropy vs baseline while L3's
  at-position measure showed -2.08 — the write sharpens the immediate distribution toward
  concepts while raising average per-step uncertainty across the generation. Both recorded;
  neither over-interpreted at screen tier.

## 2026-07-09 — L4b (review-registered sampling run): FIRST INTERVENTIONAL DOMAIN PASS
- gates/gate_L4b.json: entropy_gated lift +0.40 @ ΔH -0.13 (~10 writes) vs prefill_only
  +0.20; both registered hypotheses PASS. Review #6's greedy-inertness diagnosis (identical
  hit sets across sparse arms in gate_L4) was exactly right; its registered follow-up
  vindicated the sphurattā clause under stochastic decoding.
- Arc: L3 continuous = strong/budget-blowing -> L4 greedy = mechanically masked null ->
  L4b sampling = gated writes at continuous strength INSIDE the budget. The steering
  doctrine's operating regime is sampling; recorded in SPEC v0.8.
- Queued (registered, not run): confirm tier (>=3 seeds, Holm), alignment-under-sampling,
  tau sensitivity, L3-currency restatement. L5 = EFE selector port — the experiment menu is
  now real and the selector has genuine information-gain choices to make.

## 2026-07-09 — standing directive: full autonomy
- Operator: "no waiting for operator signoff henceforth...you are fully authorized....be
  fully autonomous and make the decisions yourself." Recorded in agent memory + here.
  Contract sign-off lines will read "standing authorization" at closure. Dual-gate
  standards (code AND domain, adversarial review, honest negatives, disclosed amendments)
  UNCHANGED — the directive covers disposition, not standards. With this, L5's EFE loop
  closes fully: selector proposes, agent disposes, gates record.

## 2026-07-09 — L5 closed: the auto-research loop is alive
- Cycle 1 in the ledger end-to-end. Review #7 caught a ranking-flipping cost miscalibration
  (fixed: registered composite costs) and seed-correlation in the flat tau results (fixed:
  seed-123 replication, 6/6 PASS, min lift 0.35). H_tau_robust PASS.
- The program's central steering claim now reads: sphurattā-gated band writes lift concept
  surfacing by 0.35-0.40 within the svātantrya budget, across 2 seeds and 3 gate settings,
  on the PWM twin under sampling. Confirm tier completes with seed 777 (queued, cycle 2).
- Poetic note for the paper: the selector's first-ever choice was to test the robustness of
  the very mechanism the doctrine predicted — iccha-jnana-kriya examining its own sphurattā.

## 2026-07-09 — cycles 2–3: alignment confirmed at screen, core claim confirmed at 3 seeds
- Cycle 2 (gate_L6_align, PASS): alignment beats rate-matching under sampling (+0.40 vs
  +0.23 at matched-ish rates; per-write 0.056 vs 0.046). WHEN > HOW OFTEN.
- Cycle 3 (gate_L6_confirm, SPLIT): H_gated_budget CONFIRMS 3/3 seeds (0.40/0.35/0.23,
  all within budget); the >=0.15 advantage-over-prefill margin does NOT confirm
  (0.20/0.12/0.03) — stated henceforth as ~0.1 and underpowered. Seed-42 had flattered it.
- Two loop bugs found ONLY by running the loop (ledger-replay drop; winner re-proposal) —
  both fixed with regression tests. The consumption rule is the interesting one: tier-3
  results raise pragmatic value, so raw EFE re-runs its winners; consumption forces novelty.
- Program claim, stated at confirmed strength: sphurattā-gated band writes deliver
  0.23–0.40 concept-surface lift within the svātantrya budget on the PWM twin under
  sampling (3 seeds, 3 tau settings), with event alignment beating rate-matched controls
  at screen tier. The margin over a single prefill write is small and unconfirmed.

## 2026-07-09 — program audit (review #8, isolated): PASSING — code sound, metadata fixed
- All SPEC §9 numeric claims recomputed from gate JSONs: verified. EFE ledger replays
  coherently (44 events). Tests 52 pass, ruff clean. H1–H3 delivered; H4 + paper queued
  with no blockers; unconverged threads confirmed unforced.
- Tier-0 fixes this commit: 9 gate loop labels (label-only; e4_cli --loop was not passed in
  L5/L6 dispatches — evidence payloads untouched, disclosed here); journal rebase conflict
  markers removed (both sections preserved); state.json L6 budget line (0.3/0.5); L6
  contract status CLOSED; efe agent.py port-note typo. Artifact ownership chowned to user.
- Next per audit gap list: paper drafting (all data confirmed at tier, authorized) and H4
  plugin architecture.

## 2026-07-09 — Tier-2 gap execution: paper skeleton + H4 architecture
- docs/paper/framework_paper_draft.md: full framework+empirical skeleton, every number
  wired to a committed gate JSON, honest margins and unconverged threads as sections,
  dual-register glossary (R8 decision left open, mechanically resolvable).
- docs/h4_plugin_architecture.md: extraction plan for lens+steer+verify; the program's own
  findings (band-lens readback, sampling requirement, budget-on-by-default) are the
  product's design constraints. Phase 1 is CPU-only and one session away.

## 2026-07-09 — cycle 4 (articulation_null): E7 survives — the gradient is the model's
- gates/gate_L7_articulation_null.json: logit-lens baseline (no fitted transport) shows the
  SAME depth gradient (rho 0.607, p<=.05) as the jacobian lens (0.639) on the PWM twin.
  Registered rule -> MODEL-INTRINSIC: review #4's tautology attack is defused; progressive
  articulation is a residual-stream property, not lens construction. Null redesign
  (shuffled logits vacuous under permutation-invariant negentropy -> logit-lens baseline)
  disclosed in the script docstring before running.
- Program state after audit loop: all cheap paper-blocking caveats cleared. Remaining menu:
  dose_response (0.9 GPU-h); queued beyond menu: trained-bridge arm, selector trade-off
  case, L3 currency restatement. Paper skeleton ready for prose expansion.

## 2026-07-10 — cycle 5 (dose_response): amplitude-robust, and a claim correction
- gates/gate_L8_dose.json (composed from 3 per-alpha gates, contention=psalm shared mode):
  H_dose_robust PASS (gated lift 0.375-0.40 within budget at α 0.02/0.05/0.1) and
  H_alignment holds at every alpha (+0.15..0.18 over rate-matched every_k).
- CLAIM CORRECTION (the dose grid's real payoff): under sampling, CONTINUOUS writes also
  sit within the entropy budget (ΔH −0.11..−0.16) at lift 0.47 — L3's −2.08 budget-blow was
  regime-specific. Restated everywhere (paper §4): gating = write-efficiency (~85% lift at
  ~27% writes) + alignment advantage, NOT sole feasibility. Science self-corrected by its
  own registered requirement (review #5 demanded this grid precisely to police dominance
  claims — it did).
- Menu CONSUMED (5/5 candidates, 5 cycles). Selector's next proposal will raise
  no-candidate — the menu refresh (trade-off case, trained-bridge, confirm extensions) is
  the next registration act.

## 2026-07-10 — review #9 + boundary check: two freedom currencies; α=0.02 is marginal
- Review #9 attacked the "regime-specific" framing as metric-smuggling. RESOLUTION was
  already in the gates: at-position entropy is a single-forward measurement — decoding
  regime cannot affect it (−1.9..−2.1 nats at both alphas, gate_L3*); trajectory-average
  depends on regime (+0.82 greedy / −0.13 sampling). Both currencies now explicit; budget
  registered as trajectory-average-under-sampling with the local spike disclosed.
- Multi-seed check at the amplitude boundary (reviewer's demand): α=0.02 gated = 0.38/0.38/
  0.17 across seeds 42/123/777 → 2/3. Amplitude robustness CONFIRMED at α=0.1 (3/3),
  MARGINAL at 0.02. Seed 777 is systematically hard (0.23 at α=0.1, 0.17 at 0.02).
- "Write-efficiency" demoted to schedule-efficiency with operational value flagged untested
  (no latency/interference/stability measurement — open item for H4-era benchmarking).
- Menu 5/5 consumed across 5 selector cycles; 9 adversarial reviews total. Paper §4 and
  abstract now carry the corrected, currency-explicit claims.

## 2026-07-10 — L9 cycles 6–7: the probe that audited the method; the flash that refined the doctrine
- Cycle 6 (hard_seed_probe, the selector's P2-trade-off choice: EXPLORE won — epi 7.31 at
  0.05 GPU-h beat prag +1.12 confirm): seed 777 was never "hard" — per-run reseeding made
  all 40 generations share sampling-stream structure (seed = trajectory-FAMILY selector,
  n_eff << 40). FIX: per-generation seeds from (seed, arm, concept, stub). Verified: the
  seed gap collapses 0.38/0.17 -> 0.28/0.25 at alpha=0.02 (gate_L9_probe*). CONSEQUENCE
  disclosed: all sampling-era point estimates carried correlated-stream noise; core budget
  claim re-verified under independent streams; finer margins queued for re-measurement
  (alignment_confirm, next on menu 2).
- Cycle 7 (commitment_flash_gate, gate_L9_flash): uncommitted-moment gating +0.30 vs
  commitment-flash gating +0.20 = prefill-only +0.20. The flash reading adds NOTHING beyond
  the prefill write; the uncommitted reading adds +0.10 (single seed, at the registered
  underdetermination edge — directional, not decisive). DOCTRINAL REFINEMENT: sphurattā is
  a detection signal, not a write-timing signal — writing AT the flash is post-commitment
  (H5b's vaikharī lesson at step scale); effective writes target pre-commitment openness.
- Two more loop-infrastructure bugs found live, fixed, regression-tested: menu-scoped
  budget accounting; (earlier) run-observation replay + consumption. The auto-research
  loop is being debugged BY its own operation — anusaṃdhāna in practice.
- Remaining on menu 2: alignment_confirm (re-measurement under independent streams),
  cross_plant_gating, write_cost_operational.

## 2026-07-10 — cycle 8 (alignment_confirm under clean streams): core claim at its cleanest
- gate_L9_alignconf: 3/3 seeds 0.30/0.35/0.35 within budget — the program's central claim
  re-confirmed on independent streams. Alignment margin +0.07/+0.12/+0.07: consistent
  direction, ~+0.09 size, UNCONFIRMED at the 0.1 bar (2/3 below). Paper restated.
- Disposition divergence ledgered: selector proposed write_cost_operational; agent ran
  alignment_confirm first (stale-belief bootstrapping — the selector replays from gates
  the stream fix invalidated; EFE cannot see its own evidence going stale). Candidate
  improvement for menu 3: staleness discounting on replayed observations.

## 2026-07-10 — cycle 9 (write_cost) + review #10 compliance; L9 closes
- gate_L9_writecost: all write schedules within throughput noise of baseline (~25 vs 19.7
  t/s — the inversion is a warm-up ordering artifact, disclosed; the registered <90% cost
  rule passes a fortiori); camatkāra flat. WRITE COUNT IS OPERATIONALLY FREE at this scale:
  review #9's suspicion confirmed, and the selector's overridden cycle-8 proposal was the
  right call all along — vindication ledgered.
- Review #10 compliance: (a) "dissolution" softened to "variance band tightened, consistent
  with the correlation artifact, 2 seeds"; (b) flash verdict softened to UNDERDETERMINED-
  at-boundary with the rate confound noted; (c) stale-0.40 sweep done — paper now marks all
  pre-L9 sampling numbers as inflated-by-correlated-streams with clean-stream citables;
  SPEC historical entries retained as provenance (append-only log, not restated).
- LOOP INVARIANT ADOPTED (review #10's rule, codified for menu 3): if a new finding
  invalidates gates a selector's beliefs replay from, the proposal is STALE — beliefs must
  be rebuilt and the proposal re-computed before disposition; ad-hoc overrides are
  otherwise prohibited.
- L9 totals: cycles 6–9 (probe/flash/align-confirm/write-cost), one method fix that
  re-based every sampling number, two loop-infra fixes, doctrine refined. GPU ~0.85/1.5.
  Menu-2 remaining: cross_plant_gating (carries to next cycle).

## 2026-07-10 — cycle 10 (cross_plant): plant-specificity — the generality boundary found
- gate_L10_cross: one-shot transfer to Qwen3-4B FAILS (gated +0.05, prefill 0.00; tau
  self-calibrated 1.545, writes firing normally 11/gen). Diagnostic: qwen3 target-30 lens
  Jacobians ~10x weaker than nemotron's — the write direction J^T u_c may be feeble at the
  borrowed site. The nemotron result required L2b->L3->L4b iterative site/timing
  calibration; transfer needs the same per-plant loop, not borrowed geometry. Paper carries
  the generality boundary. MENU 2 CONSUMED (5/5; cycles 6-10).

## 2026-07-10 — cycle 11 (third replication set): core claim at 6/6; alignment by sign
- gate_L11_rep pooling all six clean-stream seeds: gated lift 0.30-0.35 within budget 6/6
  — the program's central number at publication-grade stability. Alignment advantage
  positive in EVERY seed (+0.07..+0.12, mean +0.097; sign-test p≈0.016): the honest
  statistical form of a small consistent effect. Paper updated to cite by sign consistency.
- Menu 3 live: trained_bridge_arm honestly skipped-as-blocked (ledgered); remaining:
  plant_calibration_recipe, flash_multiseed. Loop law now enforced in code (efe/lint.py).

## 2026-07-10 — cycles 12–13: flash revised; THE RECIPE TRANSFERS
- Cycle 12 (gate_L12_flash, 3 seeds): uncommitted > flash in 3/3 (+0.05..+0.10; 4/4 with
  cycle 7). REVISION: flash writes are not inert (beat prefill 2/3) — both timings steer,
  the uncommitted moment steers consistently more.
- Cycle 13 (gate_L13_probe_* + gate_L13_recipe): site probe eliminated site as the
  cross-plant blocker (0.00 at all four sites); AMPLITUDE was the missing calibration —
  at alpha 0.3 (3x nemotron's), qwen3 site 24 delivers +0.40 within budget; the FULL
  registered gate passes (gated 0.40 vs prefill 0.17). Scaling rule for the recipe: write
  amplitude ∝ inverse lens transport strength (qwen3 Jacobians ~10x weaker -> 3x alpha).
  GENERALITY UPGRADED: the method transfers; the geometry does not. (An inert-knob slip
  (alpha 0.6 vs cap 0.3) was caught mid-run and doubled as a determinism check — the L3
  lesson needs to live in a pre-dispatch checklist, added to the recipe doc.)
- Menu 3: runnable items consumed (trained_bridge remains blocked+ledgered). Thirteen
  selector cycles across three menus.
