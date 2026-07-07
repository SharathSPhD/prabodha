# HANDOFF.md — context transfer to the Claude Code agent on the GB10
*Written 2026-07-07 by the Cowork session that birthed this project. Read this BEFORE SPEC/PRD.
This file records what the living documents do NOT: the conversation arc, the user's steering
decisions verbatim, infrastructure truths discovered the hard way, and the project's ethos.*

---

## 0. Ethos — read this twice

**This project is about wide-spectrum exploration converging into innovation — NOT hypothesis
testing.** The operator (Sharath) said it explicitly, twice, in different words:

> "falsification of a hypothesis is not the aim.. it is to innovate just [as] the j-space came about"

> "hypothesis and falsification are not the core...it is creative parallel...utility driven...pwm,
> gnw and j-space can all come together without worrying about the philosophical hypothesis testing
> on consciousness..the claim is not consciousness, but novel understanding and steering of LLM and
> world model creation and its use by leveraging all the concepts"

Statistics exist here as a **pruning shears for the exploration tree**, not as the point:
> "even though hypothesis testing is not the goal, use the statistical rigour of hypothesis testing
> to prune viable directions for research and application"

And the builder's trap is named:
> "focus on the concepts, just don't be lost in building"

Practical meaning for you: when a gate fails, the question is never "reject H?" but "what does this
teach, what gets pruned, what new direction opens?" Honest negatives are shipped results (PWM's H5b
is the founding example — its diagnosis *created* this project's L3). Keep multiple parallels alive
(the scoping doc grades ten of them); convergence happens by evidence-weighted pruning over loops,
not by upfront commitment. The J-space paper itself began as a reframe, not a hypothesis — that is
the model of contribution.

## 1. How this project came to be (conversation arc, compressed)

1. **Brainstorm seed:** operator noticed an "uncanny parallel" between Anthropic's J-space paper
   (*Verbalizable Representations Form a Global Workspace in Language Models*, transformer-circuits
   2026; companion repo anthropics/jacobian-lens, vendored here) and the Pratyabhijñā concepts
   already engineered in his PWM project — and that the parallel was MISSING from PWM (verified:
   PWM's corpus never mentions GNW/workspace/lens methods).
2. **The anchor insight (mine, ratified by operator):** the paper's core finding — the functional
   workspace is *defined by verbalizability* — was anticipated by Utpaladeva, ĪPK 1.5.13: vimarśa
   (reflexive awareness) IS parā vāk (supreme Word). GNW never predicted a linguistic workspace;
   vimarśavāda did. Quantitatively: ~94% non-J-space variance = prakāśa (bare manifestation), ~6%
   verbalizable = vimarśa (all reportable/flexible/causal function).
3. **Debate rounds** (kept deliberately unconverged, per operator): (a) deep parallel vs modality
   artifact — discriminating question: is a non-text model's workspace verbal? (b) "ignition IS
   recognition" — sphurattā as the flash where graded evidence snaps to committed identity ("this
   is that") — operator chose to keep it ONE OF SEVERAL parallels, not the spine; (c) H5b re-read:
   PWM's logit-bias bridge failed because it wrote at vaikharī (the mouth) after the workspace
   closed — the fix is writing at the workspace-onset band. This became VimarsaBridge v3 (L3).
4. **Division-of-labor frame** that organizes everything: **J-space = actuator** (read/write port),
   **GNW = theory of the plant** (where/when/what-counts-as-uptake), **Pratyabhijñā/PWM = the
   missing control theory** (what to write: vimarśa; when: sphurattā events; acceptance test: āgama
   re-cognition via readback; failure taxonomy: three malas; constraint: svātantrya budget;
   continuity: anusaṃdhāna). The interpretability world has an actuator with no doctrine of use —
   that doctrine is prabodha's contribution.
5. **Scoping doc** (docs/jspace_pratyabhijna_scoping.md) captures all of this: ten graded parallels
   (§2), steering doctrine (§3), anusaṃdhāna latent memory (§4), malas/svātantrya metrics (§5),
   bidirectional bridge + meta-tokens + monitoring + plugin (§6), experiment menu E1–E9 (§7). It is
   the conceptual source of truth. SPEC/PRD derive from it; when in doubt, the scoping doc wins.

## 2. Operator decisions verbatim (from interview rounds — recorded nowhere else)

- Anchoring parallels: **"this is exploratory..so consider everything and focus as you progress"**
- Stance toward GNW: **"again brainstorm...no fixed views"**
- Outcomes wanted: **"empirical and paper and tool and claude code plugin and application"** (ALL
  five horizons stay live — PRD §3 encodes this as H1–H4)
- Which gap to attack first: **"brainstorm and fine tune towards that"** (so L5's EFE selector, not
  a human decree, will pick between sphurattā-bimodality E5 and anusaṃdhāna E6)
- Frame: **"Keep both in tension"** — yantra (controller–actuator–plant) AND saṃvāda (two cognizers,
  āgama offered and freely re-cognized). The saṃvāda frame generated the bidirectional bridge
  (scoping §6.1): lens readouts of the LLM's workspace as observations for the WM posterior.
- Doc depth: develop ALL four clusters **"and beyond"**
- Lens targets: **Qwen replication AND PWM's 4B cascade model** ("1 and 2") — hence L1 then L2
- Vocabulary: **"Sanskrit-forward"** internally; but PWM's SSE-whitelist doctrine holds for external
  surfaces (RULES R8) — decide per deliverable for papers (open question §10.6 of scoping doc)
- Loop 1 scope: **E1 Qwen lens replication** (validate the instrument against Nanda's known-good
  Qwen replication BEFORE pointing it at PWM's stack)
- Ralph closure: **"it is both code and domain closures..not just tests passing..it has to meet the
  research/domain objectives"** → RULES R1 dual gates; pydantic-enforced in
  src/prabodha/contracts/closure.py; five-point closure in AGENTS.md
- GPU: **"5090 is not setup yet..so use gb10 only...there should still be room to run"**, later
  strengthened to **"manage the gpu by sharing with the prabhasa work (don't hesitate)"** — this
  SUBLATED guard v1 (idle-only) into v2 (shared mode, nice=10, contention recorded, refuse only on
  kill-switch or <24GiB free). Sublation recorded in research/journal.md — old rule preserved, not
  deleted (pratyaksha discipline: bādha, never silent deletion).
- Docker over venv: **"create dockers and install instead of going the venv route"** → Dockerfile
  (NGC pytorch aarch64) + docker-compose courtesy caps. Prefer `docker compose run l1`.
- Repo identity: public repo **prabodha**, sole contributor **SharathSPhD**, commits authored
  **qbz506@york.ac.uk** (already set in local git config).
- **"interview me to get clarity before assuming"** — carry this forward: when a decision is genuinely
  the operator's, ask; otherwise decide and record.

## 3. Infrastructure truths (discovered empirically; will bite you if forgotten)

- **SMB projects mount cannot host live git** (lock/unlink semantics, .smbdelete ghosts). Canonical
  repo must live on native ext4 + GitHub. The mount carries a file mirror + `prabodha.bundle` only.
  Operator: "don't use smb" for work — agreed and encoded in docs/gb10_handoff.md.
- **The Cowork sandbox** (where this file was written) has NO GPU, NO route to the Spark (tailnet
  100.98.74.5 unreachable, mDNS fails), NO GitHub push credentials. You, on the GB10, have all
  three — which is why this handoff exists.
- **GitHub:** SharathSPhD/prabodha exists, public, EMPTY at handoff time. First action: push the
  bundle history (§5). The Cowork-side GitHub MCP was never authorized; the operator's GitHub setup
  lives in YOUR session.
- **GB10 facts** (harvested from prabhasa/ACD docs): sm_121, CUDA 13, bf16 only (NO FP8; MXFP8/NVFP4
  broken), ~121.7GiB unified memory, ~273GB/s → **bandwidth-bound: co-residency costs tok/s even
  when VRAM fits**. prabhasa trainer detectable via `pgrep -f train_130m`; PSALM also co-resident.
  Report contention ratios (prabhasa convention), don't pretend isolation.
- **Vendored jlens API vs README** (fixes live in src/prabodha/lens/adapter.py comments): tokenizer
  must return BatchEncoding (attribute access); SKIP_FIRST_N_POSITIONS=16 silently discards short
  prompts (pass skip_first for small models); fit checkpoint format ≠ lens save format (adapter
  uses <out>.fit-ckpt); apply() returns lens AND model logits (use read_with_model for H_report).
- **Sandbox pip proxy quirks** (only relevant if resuming Cowork-side): download.pytorch.org 403s;
  aarch64 torch from PyPI latest is a CUDA build that fails import — 2.8.0 CPU wheel works.
- Sibling-project harvest with exact paths: docs/prior_art_internal.md. The EFE auto-research port
  (prabhasa application/efe/*) is the designated L5 engine; ACD's POMDP agent is its upgrade path.
- The pratyaksha context-engineering plugin's MCP tools were unreachable in the Cowork session; its
  discipline (Sākṣī witness invariant, typed context, sublation) is discharged through CLAUDE.md +
  research/journal.md. If your session has the plugin live, mirror CLAUDE.md's Sākṣī via set_sakshi.
  The triz-engine plugin was flaky (server drops) — matrix results already banked in docs/triz_log.md.

## 4. State at handoff

Commits (main): b8bfd57 foundation → 6a617bd smoke closure → 2f6e2a9 shared-mode guard + docker +
handoff doc → f0017b7 E1 evaluators (→ this file's commit). Tests: **19 unit + 2 smoke, all green**;
ruff clean. Worktree `loop/l1-e1-qwen` exists (unused yet — L1 build happened on main pre-publish;
use worktrees properly from L2 on, per CLAUDE.md). L0 gate: closed (gates/gate_L0.json). L1 gate:
open, pre-registered in configs/experiments/e1.yaml. Tiny-model sanity: rho curve rises 0.11→0.65
across layers; random model correctly FAILS domain gate — the mechanics work.

## 5. Your staged plan (carry forward; adjust and record)

**Immediate (first session):**
1. `git clone <mount>/prabodha/prabodha.bundle ~/projects/prabodha && cd ~/projects/prabodha`
   `git remote set-url origin https://github.com/SharathSPhD/prabodha.git && git push -u origin main`
2. `docker compose build` (NGC base pull is large; one-time), then `docker compose run l1` —
   guard-wrapped: fits lens on Qwen3-4B-Instruct-2507 (configs/models/qwen3.yaml; adjust size ONLY
   via config, R4), runs E1 evaluators, emits gates/gate_L1.json with contention recorded.
3. **Adversarial domain review** (AGENTS.md point 5): spawn a FRESH agent briefed ONLY with
   contracts/L1_qwen_replication.md + gate_L1.json — no builder context — to attack the
   interpretation. Then operator sign-off on the contract card. Only then is L1 closed (or iterated:
   thresholds/size-matched retry per the prune_rule in e1.yaml).
4. Close L1: update SPEC/PRD evolution logs + journal; squash-merge; push.

**Near (L2):** lens on PWM's 4B cascade model (the Phase-7 TTFT model — find it in the PWM repo /
neo-fm stack); band map + workspace-onset layer; E7 progressive articulation (vāk-hierarchy gradient
— cheapest observational win, scoping §2.5). Keep a logit-lens baseline arm (PRD risk table).

**Mid (L3–L4):** VimarsaBridge v3 — k-sparse non-negative codes over J-lens vectors injected at
workspace-onset band, sphurattā-event-timed, readback-verified (uptake criteria scoping §3.3), mala
classification on failure, svātantrya budget (R3). The decisive experiment: SAME WM content through
v2 logit-bias arm vs v3 workspace arm, camatkāra scoring per PWM protocol. Clone PWM components as
needed (bridge, event machinery, CittaStore) — operator pre-authorized cloning.

**Later (L5+):** port prabhasa's EFE selector (candidates = experiment menu E5/E6/E8...; observations
= gate outcomes; cost = GPU-hours; ledger-replayed beliefs) — auto-research chooses next experiments
by expected information gain; human disposes at gates. Then: plugin extraction (H4), paper(s) —
framework paper (Sanskrit-forward, "philosophy as engineering specification" lineage) + empirical
paper as gates accumulate.

**Deliberately unconverged threads** (do NOT force closure; revisit as evidence arrives): camatkāra's
J-space counterpart (workspace-turnover surprise?); simulated-vs-real continuity in anusaṃdhāna;
W-space beyond single-token J-space; the modality confound (E9, expensive, deepest); where recognition
lives — WM only (yantra wins) or also in the plant's ignition (saṃvāda becomes literal); Nanda's
interpretative meta-tokens as free sphurattā detectors on the LLM side (cheap to check during L1 —
Qwen's dense Chinese tokens made them findable; look for them).

## 6. Operating style expected of you

Ralph loops, hybrid form: stateless re-entry (ALL state in repo: research/state.json, journal,
contract cards, gates), contract-gated exits, dual closure, `pruned` is a valid closure, exit code
75 = skip-not-fail. Specialist delegation per AGENTS.md table (spawn fresh agents for adversarial
review; use skills for stats validation, code review, documentation). Config over constants; every
module docstring cites Concept/Source/Primitive. Sanskrit-forward inside, clean API surfaces outside.
Update SPEC/PRD evolution logs at EVERY closure — they are living documents, "not cut in stone"
(operator's phrase). Interview the operator when the decision is genuinely his. And the Sākṣī, always:
**concepts lead; building serves concepts.**
