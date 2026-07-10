# PRD.md — prabodha product requirements
**v0.21 (v1.0.0 release) — LIVING DOCUMENT (evolves with SPEC.md at every loop closure).**

## 1. Users & jobs-to-be-done
- **Sharath (researcher-operator):** advance the PWM×J-space research program; publish; reuse in neo-fm.
- **PWM/neo-fm (downstream system):** a working VimarsaBridge v3 that beats v2 (resolve H5b) without
  hurting fluency; production monitoring of workspace content (scoping §6.3).
- **Interpretability community (later):** maintained lens+steer+verify toolkit / Claude Code plugin.

## 2. Product principles
Concepts lead, artifacts serve (Sākṣī). Utility claims only. Sanskrit-forward internally, clean
external API surfaces (RULES R8). Everything reproducible from configs+seeds. Honest negatives are
shipped results.

## 3. Requirements by horizon
**H1 Instrument (L1–L2):** P0 fit/apply lens on Qwen3 + PWM 4B on GB10 within guard budgets; P0
replication gate vs known-good; P1 slice-vis pages for qualitative reading; P1 band map for PWM stack.
**H2 Steering (L3–L4):** P0 v3 injection beating v2 arm OR honest prune with diagnosis (malas);
P0 svātantrya budget reporting; P1 readback verifier with ≤3-token latency; P2 event-gated timing
from PWM sphurattā machinery.
**H3 Auto-research (L5+):** P1 EFE selector proposing next experiment from gate ledger; human-gated.
**H4 Tool (Lx):** P2 plugin packaging (fit/read/write/verify/visualize) for any HF decoder; P2
docs + examples; P3 community release checklist (license/NOTICE, no Śaiva leak in API).

## 4. Non-goals (now)
No consciousness claims; no 5090 dispatch (not set up); no training of the frozen LLMs; no
production deployment into neo-fm before H2 closes; no multi-token lens research before H1 closes
(tracked as open question, scoping §10.3).

## 5. Success metrics (per-loop gates; details in contracts/)
L1: replication signature score ≥ threshold in e1.yaml; fit cost ≤ 2 GPU-h; zero guard violations.
L3: v3 vs v2 camatkāra Δ with screen-tier g>0 and confirm-tier family-corrected significance, at
svātantrya budget ≤ ε entropy loss — or a pruned closure with mala diagnosis.
Program: every closed loop updates SPEC/PRD (this file's version bump is itself gated).

## 6. Risks & mitigations
GitHub connector unauthorized (publish blocked) → mirror+bundle fallback, manual push path documented.
GB10 contention (bandwidth-bound, PSALM co-resident) → guard + pulsed jobs + idle windows (TRIZ C3).
Lens quality on non-Qwen models unknown → L2 keeps logit-lens baseline arm for comparison.
Sanskrit-forward alienates reviewers → dual-register glossary; external surfaces clean (R8).
Sandbox↔SMB git incompatibility → canonical on GitHub; bundle in mirror (documented in CLAUDE.md).

## 7. Evolution Log
- v0.21 (WS7 closure, v1.0.0 release, 2026-07-10): L20 integrated PWM CittaStore (trained-
  bridge scope gap from menu-3 onwards: RESOLVED at the implementation level; honest scope:
  cold store, 3/3 seeds steering within budget, functional confirm; trained-store training
  remains OPEN). Six deliverables SHIPPED: (1) PyPI library `prabodha` (pip-installable,
  RELEASED on PyPI); (2) HF lens fittings `qbz506/prabodha-lenses` (huggingface.co);
  (3) Claude Code plugin + MCP steering server (`integrations/claude-code-plugin/` +
  `integrations/mcp-server/`); (4) Next.js/Supabase/Vercel web app "J-space theatre"
  (live GB10 trace replay); (5) research paper (MDPI template, sole author Sharath Sathish,
  Independent Researcher, `docs/paper/paper.tex/.pdf`); (6) GitHub Pages site
  (`sharathsphd.github.io/prabodha`, ACD-caliber technical exposition). Reviews #17 (L20
  adversarial) and #18 (program audit) PASS; #17 flagged an overclaim in framing (fixed).
  Determinism check rerun: 9/9 seed-123 generations differ between arms (refutes the "bug"
  hypothesis from loop L16 #16). HONEST OPEN ITEMS CARRIED INTO v1.0.0: trained-store
  training, cross-episode continuity, live GB10 auto-deployment, W-space/modality
  convergence. All documented in docs/RELEASE_NOTES_v1.0.0.md and this file's §6 risk
  table. H1-H4 requirements met at ship quality; §2 principle "honest negatives are shipped
  results" stands validated by three adversarial-caught self-corrections (stream-correlation,
  arm-specific offset misread, determinism-guaranteed-reproduction misread).
- v0.20 (L7-L19 catch-up, PR #10-#22, 2026-07-10): closes a 13-loop gap (v0.8 was L5;
  paper/HTML carried the living-document role through L7-L19 while this file lagged —
  corrected here). H1 (instrument) DELIVERED: 3 model families, 2 sizes; band content
  legible only via band-targeted lens (gate_L2b) — this is now a hard design constraint
  in H2/H4, not just a finding. H2 (steering) DELIVERED past P0: core claim confirm-tier
  6 seeds; v3 beats v2/prefill; svātantrya budget reported every run; event-gated timing
  from sphurattā beats commitment-flash 4/4 sign-consistent. H3 (auto-research) DELIVERED
  well past first-cycle scope: 26 cycles, 9 menus, self-found+self-fixed 3 loop bugs
  (replay-drop, consumption-rule, cost-model) plus a staleness invariant now enforced by
  src/prabodha/efe/lint.py. H4 (tool) DELIVERED: P2 plugin packaging done
  (integrations/claude-code-plugin/, 3 skills) + P2 docs/examples
  (examples/quickstart_qwen3.md, README results table) — P3 community checklist PARTIAL
  (license/NOTICE audit clean; only 1 of a planned 2 public-model examples shipped).
  NEW risk (add to §6): trained_bridge_arm has been BLOCKED since menu 3 on PWM WM stack
  integration — this is now the single largest standing scope gap in the program and
  deserves its own contract/loop rather than continuing to live as an EFE menu line-item
  that never runs. NEW finding for §2 (product principles): "honest negatives are shipped
  results" has been tested three times by adversarial review catching the CLOSING AGENT's
  own overclaims (not just experimental noise) — see docs/HANDOFF_L19_TO_NEXT.md §5 for
  the three specific catches (stream-correlation, arm-specific offset, determinism-
  guaranteed reproduction) — this is now documented as a recurring trap-shape to watch
  for, not a one-off. Full state: docs/HANDOFF_L19_TO_NEXT.md.
- v0.1: drafted at L0 with interview decisions (GB10-only; E1 first; dual-closure ralph).
- v0.2: TRIZ log integrated; agent assignment table moved to AGENTS.md; H4 plugin gated behind H1/H2.
- v0.8 (L5 close): H3 auto-research DELIVERED at first-cycle scope — selector proposes,
  agent disposes (standing authorization), gates feed back; cost model registered per
  candidate after review #7 caught a ranking-flipping miscalibration. The steering claim
  (event-gated writes within budget) now holds across 2 seeds x 3 tau settings.
- v0.7 (L4/L4b close): H2's core mechanism DEMONSTRATED at screen tier — event-gated
  workspace writes steer at continuous strength within the freedom budget (single seed,
  sampling regime, untrained-v2 caveat outstanding). Path to H2 closure: confirm tier
  (3 seeds), alignment control under sampling, then the v2-trained-bridge comparison.
- v0.6 (L3 close): H2 partially advanced — v3 machinery works and steers, but not yet
  "beats v2 without hurting fluency": at current operating point v3 trades MORE fluency
  (camatkāra 0.063 vs 0.021 drop) for MORE content. NEW REQUIREMENT (review #5): any
  dominance claim needs dose-response at matched entropy + a trained-bridge comparator.
  L4 = event-gated timing (sphurattā port from PWM, standalone per scout). Risk: untrained
  v2 comparator inflates v3 advantage — trained bridge requires full WM stack (H2-late).
- v0.5 (L2 close): H1 instrument delivered for the PWM stack (band map + onset layer +
  articulation profile + slice page). CRITICAL H2 INPUT: the production-twin model does NOT
  load instructed concepts into its workspace band (0.0 with controls) — VimarsaBridge v3
  cannot assume instruction-priming; direct lens-writes + readback verification carry the
  design (Selectivity@5 entry gate before L3 writes). NEW RISK: distilled/pruned models may
  have degraded workspace structure — if Selectivity@5 fails, consider PWM's larger cascade
  model as the L3 plant instead.
- v0.4 (L1b close): H1 replication gate resolved as calibration — instrument validated on
  Nanda's reference size (modulation PASS 0.55, bands replicate); thresholds now known to be
  size-sensitive for modulation and metric-shape-sensitive for report-ordering. Risk table
  update: "lens quality on non-Qwen models unknown" now carries the L1b protocol (fixed bands,
  null baselines, kernel requirements for hybrid archs) as mitigation; NEW risk: hybrid-arch
  models need arch-specific kernels or budgets explode (52 vs 17 min/prompt). L2 (PWM stack:
  nvidia/Nemotron-Mini-4B-Instruct, cached) proceeds with disclosed caveats.
- v0.3 (L1 review-complete): H1 partially met — lens fits+reads Qwen3-4B on GB10 inside guard
  budget (1.45/2.0 GPU-h, contention=psalm disclosed); replication gate FAIL at pre-registered
  thresholds with all signatures present and significant vs null ("underpowered, not broken" —
  adversarial review). NEW RISK: thresholds implicitly calibrated to Nanda's 27B; 4B effect
  sizes ~40–80% weaker → mitigation: null-calibrated metrics + permutation gates (done), size
  question escalated to operator (27B retry vs proceed vs prune). Slice-vis page shipped;
  CJK meta-token observation (fire→火/焰) recorded as free sphurattā-detector lead for L2+.
