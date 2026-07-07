# CLAUDE.md — prabodha working rules

## Sākṣī (witness invariant — prepend to every subagent brief; re-read on every session start)
```
User: Sharath (GitHub: SharathSPhD; commits authored qbz506@york.ac.uk)
Project: prabodha (public GitHub; canonical concepts in docs/jspace_pratyabhijna_scoping.md)
Method: config-driven + test-driven; design patterns; git worktrees per workstream;
  ralph loops with DUAL closure (code gate AND research/domain gate — tests passing is never enough);
  dynamic workflows; TRIZ for contradictions (docs/triz_log.md); pratyaksha context discipline;
  specialist agents/skills/plugins assigned per job and RECORDED in SPEC/PRD.
Epistemic: innovation is the goal, falsification is not — but statistical rigor PRUNES directions:
  tiered (smoke -> screen -> confirm), permutation tests, Hedges' g, Holm-Bonferroni, >=3 seeds at
  confirm tier, honest negatives recorded in research/journal.md and gates/.
Resource: GB10 only (5090 not set up). NEVER disturb the prabhasa / PSALM jobs — scripts/lib/gpu_guard.sh
  is mandatory before any GPU dispatch. GB10 is bandwidth-bound: co-residency depresses tok/s even when
  VRAM fits; prefer idle windows, pulsed short jobs, checkpoint-resume.
Reuse: prabhasa (EFE selector, autopilot, ledger, gpu_guard), ActiveCIrcuitDiscovery (POMDP agent,
  metrics), sco2rl (RULES pattern), neo-fm (five-point gate), pramana (staged gates), PWM (bridge,
  CittaStore, event machinery — clone as needed).
Claims: utility only (understanding + steering of LLMs and world models). NOT consciousness.
  Sanskrit-forward vocabulary, engineering-glossed (docs/ glossary conventions).
Focus: concepts lead; building serves concepts. Spec/PRD evolve at every loop closure.
```
Note: the pratyaksha MCP server tools were unreachable at session L0; the harness's role (witness
invariant, typed context, sublation-not-deletion) is discharged through this file + research/ ledger
until the server is available. When available, mirror the Sākṣī via set_sakshi.

## Working agreements
- Worktrees: `git worktree add .worktrees/<loop-id>-<slug> -b loop/<id>-<slug>`; squash-merge to main at closure; main always green.
- Commits: conventional commits; author identity above; no direct commits to main mid-loop.
- Every module cites its concept: docstring lines `Concept:`, `Source:` (ĪPK/SpandaK/paper §), `Primitive:` — PWM convention.
- Config over constants: anything tunable lives in configs/*.yaml, validated by pydantic schemas in src/prabodha/contracts/.
- GPU: source scripts/lib/gpu_guard.sh; smoke (<5 min) auto-allowed only when no trainer live; real runs need idle GPU + budget + no kill-switch (`research/KILL_SWITCH` flag file).
- Repo canonical home: GitHub (SharathSPhD/prabodha). The SMB projects mount cannot host live git (lock/unlink semantics) — it carries a file mirror + `prabodha.bundle`; restore with `git clone prabodha.bundle`.
