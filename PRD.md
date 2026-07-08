# PRD.md — prabodha product requirements
**v0.2 — LIVING DOCUMENT (evolves with SPEC.md at every loop closure).**

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
- v0.1: drafted at L0 with interview decisions (GB10-only; E1 first; dual-closure ralph).
- v0.2: TRIZ log integrated; agent assignment table moved to AGENTS.md; H4 plugin gated behind H1/H2.
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
