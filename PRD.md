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
