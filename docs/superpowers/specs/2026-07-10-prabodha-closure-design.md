# prabodha closure & productization — design spec

**Date:** 2026-07-10
**Status:** approved by operator (design round, this session)
**Supersedes:** nothing — extends `docs/HANDOFF_L19_TO_NEXT.md` §8 option (b)+(a) hybrid
**Operator decisions (recorded verbatim intent):**
- GB10 finalizing runs = trained-bridge integration + comparator. **No new-seed re-validation
  of already-confirmed claims** — the L0–L19 empirical record stands as-is.
- App admin (DGX passthrough) account: `sharath.sathish@outlook.com`.
- Distribution: **PyPI release** (`prabodha` v1.0.0) + **HuggingFace artifacts** (fitted lenses
  + configs, under the authenticated `qbz506` account). GitHub tag/release included trivially.
- Paper: sole author **Sharath Sathish**, affiliation **Independent Researcher**, contact
  **sharath.sathish@gmail.com**, ACD's MDPI Symmetry template.
- Monorepo (Approach A) approved; full autonomy granted; no further human gates except
  genuine operator-position questions.

---

## 1. Goal

Close the prabodha program as a breakthrough contribution that advances J-space + GNW via
Pratyabhijñā, delivered as six public artifacts that exceed a "GitHub project": a usable
library, a sealed plant–controller research claim, an operational steering plugin, a
visually rich web app, a journal-template paper, and a rich GitHub Pages site. Claims
discipline unchanged: utility only (understanding + steering), never consciousness.

## 2. Non-goals

- No re-running or extending seeds on settled claims (core claim stays 6-seed confirm tier
  as recorded; corpus-amplitude stays honestly fail-on-margin; cross-arm offsets stay
  honestly unexamined — all documented as open items, not silently resolved).
- No anusaṃdhāna / multimodal / W-space experiments (deliberately unconverged, stays so).
- No consciousness claims anywhere, in any register.
- No disturbance of co-resident GB10 jobs; `gpu_guard.sh` before every dispatch.

## 3. Workstreams

### WS1 — L20: trained-bridge loop (research, GB10, starts first)

The single largest standing scope gap (blocked since menu 3): compare PWM's **trained**
CittaStore-based write path against prabodha's **analytic** `J^T u` write path.

- Integrate: editable-install the `pwm` package (local at `/home/sharaths/projects/PWM`,
  CittaStore at `pwm/memory/citta_store.py`) into the `prabodha/gb10:0.1` image lineage
  (new image tag; source is baked in, so image rebuild required — known L15/L16 lesson).
- Implement `src/prabodha/steering/bridge_trained.py`: a writer conforming to the existing
  writer interface that derives its write vector from CittaStore retrieval instead of the
  lens transpose. Concept/Source/Primitive docstring per PWM convention.
- Pre-register `contracts/L20_trained_bridge.md` + `configs/experiments/e_l20_bridge.yaml`
  BEFORE dispatch, with an explicit falsifiable criterion of the form: *on the standard
  corpus, at the existing clean-stream seeds (42/123/777), entropy-gated writes using the
  trained bridge achieve lift within Δ of the analytic writer at matched entropy budget —
  report the comparator honestly whichever way it lands* (exact Δ and arms fixed in the
  contract before any run; screen tier first, confirm only if screen passes).
- Budget line `L20_spent/L20_cap` in `research/state.json` before first dispatch.
- Dual gate + isolated adversarial review (review #17), journal + ledger + state updates,
  worktree `loop/l20-bridge`, squash-merge PR.
- Determinism discipline: before writing ANY "reproduced/clean number" inference, check the
  seeding code path (three prior reviews caught exactly this class of error).

**Success:** comparator result at screen tier (either direction) with review verdict
MERGE-CLEAN or MERGE-WITH-CORRECTIONS; the "blocked since menu 3" item resolved on the
record.

### WS2 — library v1.0 (PyPI + HuggingFace)

- Public API surface: `prabodha.lens` (fit/eval/vis) and `prabodha.steer` (write/gate/
  verify) importable as functions, not CLI-only; typed, docstringed, concept-cited.
- README rewritten to Anthropic-library standard (jacobian-lens README as the register):
  what it is, 60-second quickstart, results table (kept honest, gate-cited), provenance.
- Second-lineage quickstart `examples/quickstart_nemotron.md` (H4 phase 3 remainder).
- Version 1.0.0; build sdist+wheel; publish to PyPI (`prabodha`). If no PyPI token is
  configured on this box, everything is prepared and the publish step pauses for the
  operator — that is the only acceptable block.
- HuggingFace: create `qbz506/prabodha-lenses` (or similar) with fitted lens checkpoints
  (Qwen3-4B band lens, Nemotron band lens), model configs, and a model card citing gates
  and licenses (Apache-2.0 vendored lens acknowledged).
- Code gate: tests + ruff green, `pip install prabodha` from a clean venv works (TestPyPI
  or local wheel first). Domain gate: quickstarts' expected numbers match committed gates.

### WS3 — plugin → operational steering tool

- Upgrade `integrations/claude-code-plugin/` from three doc-skills to a tool that actually
  drives steering: skills invoke the installed `prabodha` CLI end-to-end (fit → steer →
  verify) on any HF-hosted open model the user names.
- Add an MCP server (`integrations/mcp-server/`, Python, stdio) exposing tools:
  `lens_map`, `steer_generate`, `readback_verify`, `list_gates` — so ANY MCP client (not
  just Claude Code) can steer open models. Register it in the plugin's `.claude-plugin`.
- Every tool/skill default cites its gate (existing convention, preserved).
- Code gate: plugin validates (plugin-validator agent), MCP server smoke-tested against a
  tiny model config. Domain gate: a scripted end-to-end steer on Qwen3-4B reproduces a
  gate-cited lift direction (smoke scale, not a new claim).

### WS4 — app: `prabodha` on Vercel + Supabase (kundali pattern)

**Stack:** Next.js 14 App Router + Tailwind (custom tokens, kundali's night/gold system
re-themed to prabodha's own palette — deep indigo/teal/saffron, borrowing ACD's tri-accent
discipline), Supabase (auth, RLS, tiers, BYOK), Vercel deploy from monorepo subdir
`apps/web`. New Supabase project + new Vercel project (MCP-connected; cost confirmations
via the Supabase MCP flow).

**Auth/tiers (kundali schema, adapted):** `user_tiers` (basic|paid|guest|admin) with
bootstrap migration granting admin to `sharath.sathish@outlook.com`;
`user_llm_credentials` BYOK rows per (user, provider) with providers
`openrouter|anthropic|openai|llamacpp` (llamacpp = user-supplied base_url);
`runtime_config` (admin-writable RPC) holding `llamacpp_gateway_url` (the GB10 llama.cpp
server behind a Tailscale funnel) + default model; RLS owner-only everywhere,
security-definer admin RPCs.

**Provider routing:** admin/guest → GB10 llama.cpp gateway (no key needed); any tier with
BYOK → their provider (OpenRouter first-class); basic without BYOK → replay-only with an
upgrade/BYOK hint. llama.cpp chosen over Ollama per operator (OpenAI-compatible
`/v1/chat/completions` server mode).

**The J-space theatre (centerpiece):** an animated, stage-like visualization of a steering
episode with three honestly-labeled modes:
1. **Replay** (everyone, no auth): recorded REAL traces from GB10 runs (a new
   `prabodha steer --emit-trace` JSON format: per-token entropy, gate events, write
   amplitudes, band readout top-k, readback verdict), animated as a real-time sequence —
   band heatmap (D3, from slice data), entropy trace with sphuraṭṭā event markers firing,
   dose dial, the band's "voice" (readout tokens surfacing), readback verdict reveal. The
   fire case (`"the fire remembers rivers"`) is the flagship replay.
2. **Live steer** (admin tier): the same theatre driven live by a small FastAPI service on
   the GB10 (`services/steer-gateway/`, wraps the prabodha runtime, streams trace events
   over SSE, exposed via the same Tailscale funnel, secret-protected) — full lens
   read/write, real internals.
3. **BYOK chat** (OpenRouter/keys): steered-concept conversation with the steering recipe
   explained alongside; NO fake internals — the UI states plainly that hosted APIs do not
   expose hidden states, and links to the library for running the real thing.

**Pages:** landing (hero with animated J-space canvas), theatre, glossary (dual-register
Sanskrit/engineering), results (gate-driven charts), settings (BYOK), admin (tier +
gateway config). PWA-light, dark theme, `prefers-reduced-motion` respected.

**Code gate:** typecheck/lint/build green, e2e smoke (playwright) on auth + replay
theatre. Domain gate: every number shown traces to a committed gate JSON (a
`scripts/tools/export_app_data.py` generates the app's data from gates/ — never
hand-entered); replay traces are genuine run outputs.

### WS5 — paper (MDPI template, sole author)

- Migrate `docs/paper/paper.tex` to ACD's structure: copy `Definitions/mdpi.cls` + `mdpi.bst`
  toolchain, split into `sections/*.tex`, Makefile three-pass build.
- Author block: Sharath Sathish, Independent Researcher, sharath.sathish@gmail.com (ORCID
  if provided later; placeholder omitted, not faked).
- Content: current paper's sections mapped into the template + NEW: (a) fire-case slice
  visualization figures (from `lens-vis`, the asset never yet surfaced), (b) the L20
  trained-bridge comparator section (whatever it honestly shows), (c) MDPI mandatory
  metadata (CRediT solo, data availability → GitHub+PyPI+HF, conflicts none).
- Figures stay derived-only: `make_figures.py` extended, never hand-edited.
- Domain gate: every number cites a gate; honest-negatives section intact; review pass by
  a fresh agent against the claim table before final compile.

### WS6 — GitHub Pages (ACD-caliber)

- `web/` folder in prabodha repo, deployed verbatim by `.github/workflows/pages.yml`
  (upload-pages-artifact → deploy-pages, `.nojekyll`) to
  `https://sharathsphd.github.io/prabodha/`.
- ACD's design system as the baseline, prabodha's own palette/typography identity:
  acts/scenes narrative (the uncanny parallel → the instrument → the band's voice →
  timing → the recipe → the trained bridge → honest limits → run it yourself), scroll-spy
  dots, progress bar, animated hero canvas of the J-space band, reduced-motion support.
- Embedded interactive fire-case slice heatmap (adapt `vendor/jacobian-lens`'s
  `slice_vis.html` D3 pattern with REAL exported slice data), gate-driven result charts
  (`web/prabodha-data.js` generated by the same `export_app_data.py`), links to app,
  paper PDF, PyPI, HF, plugin.
- Domain gate: same data-fidelity rule as WS4; content adapted from (not divergent from)
  the paper and `prabodha_story.html`.

### WS7 — closure

- Final program-wide adversarial audit (review #18): isolated agent, briefed only with
  gates/ + the claim table + this spec, attacks every public claim across README, paper,
  app, Pages, plugin. Corrections folded in everywhere at once.
- SPEC.md / PRD.md evolution logs, `research/journal.md`, ledger, `research/state.json`,
  HANDOFF updated; cross-session memory file updated; `prabodha_story.html` regenerated
  and Artifact republished (same file path → same URL).
- `v1.0.0` tag + GitHub release with notes; SMB mirror + bundle refreshed.

## 4. Ordering & parallelism

```
WS1 (L20)  ──────────────┐
WS2 (library) ─┐          ├─→ final numbers flow into WS4/WS5/WS6 content
WS3 (plugin) ──┤ parallel │
WS4 (app scaffold→build) ─┤
WS6 (pages scaffold→build)┘
WS5 (paper) — continuous; finalizes after WS1
WS7 (closure) — strictly last
```

Worktrees per workstream (`loop/l20-bridge`, `feat/library-v1`, `feat/plugin-mcp`,
`feat/app`, `feat/pages`, `feat/paper-mdpi`), PR + squash-merge each, main always green.
Specialist agent teams per workstream; adversarial/code review before each merge.
GPU: only WS1 and trace-recording for WS4 replay touch the GB10; guard mandatory.

## 5. Error handling & risks

- **PyPI/HF/Vercel/Supabase credentials missing** → prepare everything, pause ONLY that
  publish step, surface one operator question; never block sibling workstreams.
- **PWM integration friction** (dependency clashes on aarch64) → isolate in the docker
  image; if CittaStore cannot produce a write vector compatible with the band interface
  within the loop budget, record an honest BLOCKED-WITH-DIAGNOSIS gate rather than forcing
  a degraded comparator (that outcome still resolves the "carried silently" status).
- **Tailscale funnel not configured for llama.cpp** → app ships with replay mode fully
  functional regardless; gateway URL is runtime_config, set post-deploy from admin page.
- **Trace format drift** between library and app → one pydantic schema
  (`contracts/trace.py`) shared by emitter and exporter; app consumes exported JSON only.
- **Claim drift across six surfaces** → WS7's audit is the single sweep; no surface ships
  a number without a gate path next to it in source.

## 6. Testing

- Library/plugin: existing pytest suite + new unit tests for public API + smoke marker
  runs; ruff.
- App: typecheck, lint, build, playwright smoke (login, replay theatre renders, admin
  gate blocks non-admin).
- Pages: HTML validity, link check, data file generated-not-hand-written check.
- Paper: three-pass build clean, no undefined refs/citations.
- Research (WS1): the gate schema itself + adversarial review, as always.

## 7. Success criteria (program-level)

1. `pip install prabodha` + quickstart works for an outsider (both lineages).
2. L20 comparator on the record with review verdict; trained-bridge no longer "blocked".
3. Plugin/MCP server steers a real open model end-to-end from a fresh client.
4. App live on Vercel: replay theatre public, admin live-steer path wired, BYOK works.
5. Paper PDF builds on the MDPI template, sole-author, fire-case figures in, every number
   gate-cited.
6. Pages live at sharathsphd.github.io/prabodha meeting-or-exceeding ACD's bar.
7. Review #18 verdict recorded; v1.0.0 tagged; all ledgers/memories current.
