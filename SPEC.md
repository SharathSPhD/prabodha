# SPEC.md — prabodha technical specification
**v0.2 (L0 closure) — LIVING DOCUMENT: revised at every loop closure; see Evolution Log (§9).**

## 1. Object
Build and validate **recognition-gated workspace steering**: a control loop in which a small stateful
world model (controller) writes into, and reads back from, the global workspace of a frozen decoder
LLM (plant) via the Jacobian lens (actuator/port). Conceptual grounding and all parallels:
`docs/jspace_pratyabhijna_scoping.md` (§1–§6). Claim discipline: utility only (RULES R-claims; CLAUDE.md).

## 2. Architecture (pattern-annotated)
```
                 ┌────────────────────────────────────────────────┐
                 │ frozen LLM (plant)                             │
 configs ──►     │   workspace band  ◄── inject (sparse J-code)   │
 (Strategy:      │        │  ▲                                    │
  lens backend)  │        ▼  │ readback (lens readout)            │
 ┌─────────────┐ └────────┼──┼──────────────────────────────────-─┘
 │ LensAdapter │◄─────────┘  │
 │ (Adapter over vendor jlens; Strategy: jacobian|logit)          │
 └──────┬──────┘             │
        ▼                    │
 ┌─────────────────────────────────┐   ┌──────────────────────────┐
 │ steering/ VimarsaBridgeV3       │   │ stats/ tiered pruning    │
 │  writer (Command), readback     │   │ (permutation, g, Holm)   │
 │  verifier (Observer), timing    │   └──────────────────────────┘
 │  policy (Strategy: event-gated) │   ┌──────────────────────────┐
 └─────────────────────────────────┘   │ efe/ auto-research       │
                                        │ selector (prabhasa port) │
                                        └──────────────────────────┘
```
Design patterns in force: **Adapter** (vendor jlens → LensAdapter), **Strategy** (lens backend; timing
policy; injection site), **Command** (each write is a replayable command with config+seed), **Observer**
(readback verifier subscribes to generation steps), **Template Method** (ralph loop runner), **Registry**
(experiment candidates for EFE). Anti-pattern guard: no God-objects; śakti-cascade rule from PWM —
shared state over fragmented agents.

## 3. Loops (roadmap = contract queue; each is a worktree + card in contracts/)
- **L0 foundation** — this repo, dual-closure machinery, TRIZ log, mirrors. *(closed)*
- **L1 E1: Qwen lens replication** — fit vendor lens on Qwen3 (GB10-sized), reproduce verbal-report
  ordering + CKA sensory/workspace/motor banding vs Nanda's known-good Qwen replication. Domain gate:
  qualitative signatures present AND quantitative thresholds in configs/experiments/e1.yaml met.
- **L2 E2+E7: PWM-stack lens + progressive articulation** — fit on PWM 4B cascade model; band map;
  vāk-hierarchy articulation gradient (scoping §2.5).
- **L3 E3: H5b redo** — same WM content, logit-bias (v2) vs J-space injection (v3) arms; camatkāra
  scoring per PWM protocol; malas diagnostics; svātantrya budget (R3).
- **L4 E4: readback/āgama verification** — uptake signatures vs behavioral effect.
- **L5 E5/E6 selection by EFE** — sphurattā bimodality vs anusaṃdhāna reload: the efe/ selector
  proposes based on L1–L4 information gain per GPU-hour; human gates.
- **Lx tool/plugin** — extract lens+steer+verify as a Claude Code plugin once APIs stabilize (PRD §4).

## 4. Statistical pruning protocol (innovation-first, rigor-as-pruner)
Tiered per RULES R6. Screen tier: paired permutation (10k resamples), Hedges' g with BCa CI.
Confirm tier: ≥3 seeds, Holm-Bonferroni across the loop's hypothesis family. Ports: ACD
`src/core/metrics.py` patterns; thresholds live in each experiment config (R4). A direction is
**pruned** when the confirm-tier CI excludes the minimum effect of interest stated in its config —
pruning is a closure, not a failure (R5).

## 5. GPU execution model (GB10 only; prabhasa/PSALM co-resident)
Sandbox (this dev environment) has no GPU: it builds **job packs** — self-contained
`scripts/dispatch/<loop>/run.sh` + configs + pinned deps — executed on the DGX Spark by operator (or
autopilot later). Mandatory `gpu_guard.sh` (adapted from prabhasa): refuses when a trainer is live
(`train_130m`, PSALM patterns), honors `research/KILL_SWITCH`, enforces per-loop GPU-hour budget from
configs/gpu/gb10_guard.yaml. TRIZ C3 resolutions applied: pulsed short jobs w/ checkpoint-resume
(P18), bf16 + small batch (P35), container isolation + idle-window scheduling (P39), contention
ratios reported not suppressed (P22). Lens fitting is cheap (Nanda: n≈1–10 prompts viable) — L1 fits
budget ≤ 2 GPU-hours.

## 6. Steering doctrine spec (L3+; from scoping §3)
Write = k-sparse non-negative code over J-lens vectors (k ≤ workspace capacity budget), at workspace-
onset band, at sphurattā events only. Readback within ≤3 tokens: loading Δcosine, amplification gain,
broadcast-head relay, persistence. Uptake fail → mala classification (āṇava/māyīya/kārma per scoping
§2.8) → retry|recode|defer (bounded). TRIZ C1 resolutions: closed-loop gain (P15 dynamics), local
sparse site-specific writes (P3), legible token-indexed logging of every write (P32).

## 7. Auto-research (efe/)
Port prabhasa `application/efe/{agent,candidates,ledger,runner}` — candidates become experiments
(E-menu), observations become gate outcomes discretised to tiers, cost = GPU-hours; JSONL ledger
replayed to rebuild beliefs; EXPLORE→CONFIRM emerges. Active inference is used HERE as method
(auto-research), independent of PWM's use of it as model substrate.

## 8. Interfaces
- `prabodha.lens`: `fit(model_cfg, lens_cfg) -> LensHandle`, `read(handle, prompt, positions, layers)`,
  `save/load`. Backends: `jacobian` (vendor), `logit` (baseline control).
- `prabodha.steering`: `plan_write(wm_state|content, lens, cfg) -> WriteCommand`,
  `apply(cmd) -> Readback`, `verify(readback, cfg) -> UptakeVerdict(mala|ok)`.
- `prabodha.stats`: `permutation_p`, `hedges_g(+bca_ci)`, `holm`, `screen(...)`, `confirm(...)`.
- `prabodha.contracts`: pydantic `GateReport` (dual verdicts), `ExperimentConfig` loader.
All configs YAML; schema-validated; seeds explicit.

## 9. Evolution Log (append-only)
- v0.1 (L0 start): initial draft from scoping doc + interview decisions (E1 first; GB10 only;
  hybrid ralph with dual closure; GitHub MCP pending auth).
- v0.2 (L0 close): TRIZ resolutions C1–C3 folded into §5/§6; sibling-project ports enumerated
  (prabhasa EFE+guard+autopilot; ACD POMDP+metrics; neo-fm five-point gate; sco2rl RULES pattern);
  SMB mount cannot host live git → canonical repo on GitHub, mount carries mirror + bundle.
