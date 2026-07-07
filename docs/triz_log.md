# TRIZ contradiction log (triz-engine plugin; matrix lookups recorded verbatim)

## C1 — Steering strength vs svātantrya (Strength #14 ↑ / Adaptability #35 ↓) → principles 15, 3, 32
- P15 Dynamics → closed-loop injection gain: readback (āgama verification) modulates strength each
  event; never fixed-gain steering. [SPEC §6]
- P3 Local quality → write sparsely, site-specifically (workspace-onset band, selected positions,
  k-sparse code) instead of global bias — the v2 logit-bias failure was a global-uniform write. [SPEC §6]
- P32 Colour changes → make every write visible: token-indexed weights logged; steering logs read as
  thought logs; doubles as audit surface. [SPEC §6, RULES R3]

## C2 — Rigor vs velocity (Measurement accuracy #28 ↑ / Productivity #39 ↓) → principles 10, 34, 28, 32
- P10 Preliminary action → pre-register thresholds in configs; pre-compute null distributions and
  cache baselines once per loop. [RULES R4]
- P34 Discard & recover → tiered rigor: cheap smoke/screen arms are discarded after pruning; only
  survivors pay confirm-tier cost. [RULES R6]
- P28 Mechanics substitution → automated statistical gates replace ad-hoc human judgment; human
  attention reserved for interpretation sign-off. [contracts/*]
- P32 → rigor made visible: gate JSON is the artifact, not buried notebooks. [gates/]

## C3 — GPU productivity vs harm to prabhasa/PSALM (#39 ↑ / Object-generated harm #31 ↓) → 35, 22, 18, 39
- P35 Parameter changes → bf16, small micro-batch, low priority; lens fitting is inherently light
  (n≈1–10 prompts near-saturates quality — Nanda). [configs/gpu]
- P22 Blessing in disguise → contention itself measured and reported (tok/s ratio arms, prabhasa
  convention) rather than pretended away. [scripts/dispatch]
- P18 Mechanical vibration → pulsed scheduling: short guard-checked bursts with checkpoint-resume,
  yielding between bursts. [scripts/dispatch]
- P39 Inert atmosphere → isolation: containerized jobs, memory caps, run in idle windows; guard
  refuses when any trainer is live. [scripts/lib/gpu_guard.sh]

Open contradiction (parked for L3): injection legibility (P32) vs steering capacity — token-indexed
codes are legible but single-token-limited (scoping §10.3). Revisit with separation-in-space
(internal rich code, legible projection for logs).
