# Internal prior art — sibling-project harvest (paths on DGX: /home/sharaths/projects/...)
Ranked ports into prabodha:
1. **prabhasa-samskrutam** — EFE auto-research selector/ledger/runner (`src/prabhasa/application/efe/`),
   autopilot durable loop (`scripts/orchestrate/autopilot.py`), six-layer closure contract
   (`src/prabhasa/domain/contracts/closure.py`), **gpu_guard.sh** (`scripts/lib/`) — adopted, extended.
   GPU facts: GB10 sm_121, bf16 only (no FP8), ~121.7GiB unified, ~273GB/s bandwidth-bound; PSALM
   co-resident; prabhasa trainer detected via `pgrep -f train_130m`; VRAM 15/26/50GiB @ mbs 8/16/32.
2. **ActiveCIrcuitDiscovery** — POMDP/EFE intervention-selection over interpretability actions
   (`src/active_inference/pomdp_agent.py`), stats toolkit (`src/core/metrics.py`), matched-baseline
   ladder (`src/experiments/run_real_experiments.py`), DGX aarch64 Dockerfiles. Closest domain sibling:
   EFE choosing ablate/patch/steer actions by expected info gain — prabodha L5 selector may upgrade
   from prabhasa's analytic selector to this learned-A POMDP.
3. **sco2rl** — RULES.md rule→rationale→enforcement pattern (adopted); config partition scheme;
   worktree-per-stage.
4. **oak/ACORN** — worktree-per-concern, role-scoped agents, kernel/skill compounding (candidate for
   plugin phase).
5. **pramana** — staged gates w/ GPU-hour+cost budgets per stage; Z3 verification as domain-closure
   analogue (our stats gates play that role).
6. **neo-fm** — five-point phase gate (adopted in AGENTS.md), squash-merge always-green-main,
   conventional commits, pinned aarch64 images; also prabodha's H2 customer (VimarsaBridge v3).
