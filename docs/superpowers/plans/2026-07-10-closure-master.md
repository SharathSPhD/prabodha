# prabodha Closure & Productization — Master Orchestration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Orchestrate seven workstreams that close the prabodha program as six public artifacts (library, sealed research claim, plugin/MCP tool, app, paper, Pages site) plus a final audit and v1.0.0 release.

**Architecture:** One monorepo (`SharathSPhD/prabodha`). Shared interface contracts (this plan, §Interfaces) land on `main` FIRST via Task 0; each workstream then runs in its own worktree from that base, with its own detailed plan (`docs/superpowers/plans/2026-07-10-ws*.md`), its own agent team, and its own PR. WS7 runs strictly last.

**Tech Stack:** Python 3.10+ (pydantic v2, torch, FastAPI), Next.js 14 + Tailwind + Supabase, LaTeX (MDPI class), static HTML/JS (D3, React-from-CDN), GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-07-10-prabodha-closure-design.md` (operator-approved). Every workstream plan inherits that spec's Non-goals (§2) and risks (§5) verbatim.

## Global Constraints

- Claims discipline: utility only, never consciousness; Sanskrit-forward with engineering gloss on every external surface.
- Every displayed/printed number traces to a committed `gates/*.json`; generated data files are never hand-edited.
- GPU work: GB10 only; `source scripts/lib/gpu_guard.sh` before every dispatch; never disturb co-resident jobs; image rebuild (`docker compose build`) required after any `src/prabodha/` change before dispatch.
- No new-seed re-validation of settled claims (operator decision 2026-07-10). Existing clean-stream seeds: 42, 123, 777.
- Commits: conventional, author qbz506@york.ac.uk, `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`; worktree per workstream; squash-merge PRs; main always green.
- Admin account (app): `sharath.sathish@outlook.com`. Paper author: Sharath Sathish, Independent Researcher, sharath.sathish@gmail.com. HF namespace: `qbz506`. PyPI package: `prabodha` v1.0.0.
- Vendored `vendor/jacobian-lens` stays unmodified (RULES R7).

---

## Interfaces (cross-workstream contracts — exact, locked here)

### I1 — `SteerTrace` schema: `src/prabodha/contracts/trace.py` (Task 0)

```python
"""Steering episode trace — the shared record consumed by app replay, Pages, and gateway.

Concept: sākṣāt-darśana (direct seeing) extended to the steering episode as a whole.
Source: paper §steering; gate_L9_alignconf.json (arm/seed semantics).
Primitive: trace emission (pure record; no behavior).
"""
from __future__ import annotations
from pydantic import BaseModel, Field

SCHEMA_VERSION = 1

class TraceToken(BaseModel):
    t: int                              # decode step index (0-based)
    token: str                          # decoded token text
    entropy: float                      # per-token predictive entropy in nats, measured pre-write
    gated: bool                         # True iff a sphuraṭṭā-gated write was applied at this step
    write_norm: float | None = None     # L2 norm of the applied write (None when not gated)
    band_topk: list[str] | None = None  # band-lens readout top-k tokens (None if not sampled at this step)

class ReadbackResult(BaseModel):
    verdict: str                        # "accepted" | "rejected"
    top_m: int
    gain: float
    concept_rank: int | None = None

class SteerTrace(BaseModel):
    schema_version: int = SCHEMA_VERSION
    model_id: str                       # e.g. "Qwen/Qwen3-4B"
    prompt: str
    concept: str                        # e.g. "fire"
    arm: str                            # baseline|prefill|entropy_gated|rate_matched|continuous|trained_bridge
    seed: int
    alpha: float
    tau_percentile: int
    site_layer: int
    tokens: list[TraceToken] = Field(default_factory=list)
    readback: ReadbackResult | None = None
    behavioral_hit: bool | None = None
    gate_ref: str | None = None         # repo-relative path of the gate JSON this run fed, if any
    created_at: str                     # ISO-8601 UTC
```

Emitters: `prabodha steer --emit-trace <out.json>` (WS2 wires the flag through `steering/e4_cli.py`); the WS4 gateway emits the same objects live. Consumers: `export_app_data.py`, app theatre, Pages.

### I2 — Data exporter: `scripts/tools/export_app_data.py` (WS2)

CLI: `python scripts/tools/export_app_data.py --repo-root . --out-app apps/web/public/data --out-web web/prabodha-data.js`
- Reads `gates/*.json` (claim-table sources exactly as `make_figures.py` does) and `outputs/traces/*.json` (SteerTrace files).
- Writes `apps/web/public/data/results.json` (`{"claims": [{"id", "text", "tier", "gates": [paths], "numbers": {...}}]}`), `apps/web/public/data/replays/<slug>.json` (verbatim SteerTrace), and `web/prabodha-data.js` (`window.PRABODHA = {results: ..., replays: {...}};`).
- Refuses to run if any output would contain a number with no `gates/` provenance (domain-gate enforcement in code).

### I3 — Steer gateway: `services/steer-gateway/` (WS4)

FastAPI on the GB10, behind Tailscale funnel. `POST /steer` body `{"prompt": str, "concept": str, "alpha": float|null, "arm": "entropy_gated"}`, header `Authorization: Bearer <STEER_GATEWAY_SECRET>`. Response: SSE stream — events `token` (one `TraceToken` JSON each) then `done` (full `SteerTrace` JSON). `GET /health` unauthenticated `{"ok": true, "model_id": str}`.

### I4 — Repo layout additions

```
apps/web/                  # Next.js app (Vercel root directory = apps/web)
web/                       # GitHub Pages static site (deployed verbatim)
services/steer-gateway/    # FastAPI GB10 service
integrations/mcp-server/   # MCP stdio server
outputs/traces/            # emitted SteerTrace JSONs (replay sources; committed selectively)
docs/paper/                # migrated in place to MDPI layout (Definitions/, sections/, Makefile)
```

### I5 — Worktrees & branches

| WS | worktree slug | branch |
|---|---|---|
| WS1 | l20-bridge | loop/l20-bridge |
| WS2 | library-v1 | feat/library-v1 |
| WS3 | plugin-mcp | feat/plugin-mcp |
| WS4 | app | feat/app |
| WS5 | paper-mdpi | feat/paper-mdpi |
| WS6 | pages | feat/pages |

Created as `git worktree add .claude/worktrees/<slug> -b <branch>` from post-Task-0 main.

---

## Dependency graph

```
Task 0 (trace contract, on main) ─→ ALL workstreams branch after it
WS1 (L20)            — GPU; produces gate_L20*, trained-bridge trace, journal/ledger
WS2 (library)        — produces --emit-trace, exporter, PyPI/HF; fire-case traces for replay
WS3 (plugin/MCP)     — depends on WS2's public API names only (locked in WS2 plan)
WS4 (app)            — scaffold immediately; replay data from WS2 exporter; L20 numbers late-bound
WS5 (paper)          — template migration immediately; L20 section after WS1 merges
WS6 (pages)          — scaffold immediately; data via exporter; final content after WS1/WS5
WS7 (closure)        — strictly after all merges
```

GPU serialization: WS1 owns the GB10 until its runs complete; WS2's fire-case trace-recording runs (short, pulsed) slot into idle windows with gpu_guard; WS4's gateway deploys after WS1's runs finish.

---

### Task 0: Shared trace contract (this session, straight to main via PR)

**Files:**
- Create: `src/prabodha/contracts/trace.py` (content = Interface I1 verbatim)
- Test: `tests/test_trace_contract.py`

**Interfaces:** Produces I1 for every workstream.

- [ ] **Step 1: Write the failing test**

```python
"""Trace contract round-trip and validation tests."""
import json
import pytest
from pydantic import ValidationError


def test_steer_trace_round_trip():
    from prabodha.contracts.trace import SteerTrace, TraceToken, ReadbackResult, SCHEMA_VERSION
    tr = SteerTrace(
        model_id="Qwen/Qwen3-4B", prompt="the fire remembers rivers", concept="fire",
        arm="entropy_gated", seed=42, alpha=0.3, tau_percentile=60, site_layer=24,
        tokens=[TraceToken(t=0, token=" The", entropy=2.31, gated=False),
                TraceToken(t=1, token=" fire", entropy=1.02, gated=True,
                           write_norm=0.30, band_topk=["fire", "flame", "ember"])],
        readback=ReadbackResult(verdict="accepted", top_m=5, gain=0.0, concept_rank=2),
        behavioral_hit=True, gate_ref="gates/gate_L13_recipe.json",
        created_at="2026-07-10T00:00:00Z",
    )
    blob = json.loads(tr.model_dump_json())
    assert blob["schema_version"] == SCHEMA_VERSION
    assert SteerTrace.model_validate(blob) == tr


def test_steer_trace_rejects_missing_required():
    from prabodha.contracts.trace import SteerTrace
    with pytest.raises(ValidationError):
        SteerTrace(model_id="x", prompt="p", concept="c")  # missing arm/seed/alpha/... fields
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_trace_contract.py -v`
Expected: FAIL — `ModuleNotFoundError`/`ImportError: cannot import name 'SteerTrace'`

- [ ] **Step 3: Write the implementation** — create `src/prabodha/contracts/trace.py` with the I1 code block verbatim.

- [ ] **Step 4: Run tests to verify pass**

Run: `python -m pytest tests/test_trace_contract.py -v && python -m pytest tests -x -q -m "not smoke"`
Expected: new tests PASS; existing suite stays green.

- [ ] **Step 5: Commit and PR to main**

```bash
git add src/prabodha/contracts/trace.py tests/test_trace_contract.py
git commit -m "feat(contracts): SteerTrace shared trace schema (I1) for app/pages/gateway consumers"
```
PR from this worktree branch (includes the spec + plans), squash-merge, `git -C /home/sharaths/projects/prabodha pull --ff-only`.

### Task 1: Generate the six workstream plans (parallel planning agents)

- [ ] Dispatch six planning agents (briefs reference the spec + this master plan's Interfaces), each writing `docs/superpowers/plans/2026-07-10-ws<N>-<slug>.md` in this worktree.
- [ ] Review each plan against the spec (coverage, no placeholders, interface-name consistency with I1–I5), fix inline.
- [ ] Commit plans; include in the Task 0 PR.

### Task 2: Launch workstream execution

- [ ] After Task 0 merges: create the six worktrees per I5.
- [ ] WS1 team starts immediately (GPU idle window confirmed); WS2/WS3/WS5 teams start in parallel; WS4/WS6 scaffold in parallel, content-bind after WS1/WS2 outputs exist.
- [ ] Each team executes its plan via superpowers:subagent-driven-development; adversarial/code review before each merge; squash-merge PRs in dependency order (WS2 before WS3 final; WS1 before WS5 final).

### Task 3: WS7 — closure (this plan owns it; runs strictly last)

**Files:**
- Modify: `SPEC.md`, `PRD.md` (evolution logs), `research/journal.md`, `research/state.json`, `docs/HANDOFF_L19_TO_NEXT.md` (closure note + successor pointer), `~/.claude/.../memory/prabodha-l1-state.md`
- Create: `docs/reviews/review18_program_audit.md`, git tag `v1.0.0`, GitHub release

- [ ] **Step 1: Final program-wide adversarial audit (review #18).** Isolated agent briefed ONLY with: `gates/` directory, the claim table (handoff §3), the closure spec, and the six merged PR diffs' public-facing surfaces (README, paper.pdf text, app copy export, web/ copy, plugin skill docs). Task: attack every public claim; verdict per surface (MERGE-CLEAN / CORRECTIONS / BLOCK). Write `docs/reviews/review18_program_audit.md`.
- [ ] **Step 2: Fold corrections into every affected surface at once** (one PR: paper + README + app copy + web/ + plugin docs + `make_artifact.py`), regenerate figures/HTML, republish the Claude Artifact (same file path `docs/artifact/prabodha_story.html` → same URL).
- [ ] **Step 3: Update ledgers and memory.** journal entry (L20 + closure), `state.json` (`current_loop: "closed-v1.0.0"`), SPEC/PRD evolution logs, handoff doc closure note, cross-session memory file.
- [ ] **Step 4: Verify program-level success criteria** (spec §7, all seven) — record evidence per criterion in the journal entry.
- [ ] **Step 5: Tag and release.**

```bash
git -C /home/sharaths/projects/prabodha tag -a v1.0.0 -m "prabodha v1.0.0 — recognition-gated workspace steering: library, plugin, app, paper, pages"
git -C /home/sharaths/projects/prabodha push origin v1.0.0
gh release create v1.0.0 --title "prabodha v1.0.0" --notes-file docs/reviews/release_notes_v1.md
```
- [ ] **Step 6: Refresh SMB mirror + `prabodha.bundle`** per CLAUDE.md working agreements.
