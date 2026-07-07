# AGENTS.md — specialist assignment table + ralph protocol

## Ralph loop protocol (hybrid: stateless re-entry, contract-gated exits)
State lives in the repo (research/state.json, journal, contract cards) — any fresh agent can resume.
Loop = read contract card → plan → build in worktree → test → validate (stats tier per R6) →
emit gates/gate_<loop>.json (dual verdict) → update SPEC.md + PRD.md "evolution log" → squash-merge.
Closure requires the FIVE POINTS (adapted from neo-fm AGENTS.md):
 1. CI green (code gate)  2. runs on real target (GB10 job proof, not mocks)
 3. real verifiable research output (numbers/plots in gates/ + research/journal.md)
 4. regenerable artifact committed (configs + seeds reproduce it)
 5. adversarial domain review (a *different* agent/skill attacks the interpretation) + human sign-off.
`pruned` is a valid closure (R5). Exit code 75 convention (prabhasa): unsupported → skip, not fail.

## Assignment table (job → agent/skill/plugin) — living table, update per loop
| Job | Assignee |
|---|---|
| Contradiction discovery/resolution | triz-engine plugin (matrix + principles agents); log to docs/triz_log.md |
| Context discipline, witness invariant | pratyaksha-context-eng-harness (sakshi-keeper at session start; buddhi before side-effecting merges; manas for cheap drafts) |
| Codebase exploration / prior art | Explore agent (read-only, breadth per need) |
| Implementation planning | Plan agent per loop before build |
| Build/refactor | general-purpose agents in worktrees; engineering:code-review skill before merge |
| Statistical validation | data:statistical-analysis + data:validate-data skills; src/prabodha/stats (ported ACD metrics patterns) |
| Experiment selection (auto-research) | src/prabodha/efe selector (ported from prabhasa EFE agent) — proposes; human disposes at gates |
| Adversarial domain review (point 5) | fresh general-purpose agent briefed ONLY with contract + gate JSON (no builder context) |
| Docs/spec evolution | engineering:documentation skill at each closure |
| Debugging | engineering:debug skill |
| GitHub publish/merge | GitHub MCP connector (pending auth) or manual push fallback |
| Web verification of claims | WebSearch/web_fetch; deep-research skill for surveys |
| Visualization | data:create-viz for gate plots; vendor slice-vis for lens pages |
