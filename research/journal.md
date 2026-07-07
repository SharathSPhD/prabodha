# prabodha research journal (append-only)

## 2026-07-07 — L0 foundation
- Scoping doc adopted as conceptual source of truth (copied to docs/).
- Interview decisions: E1 (Qwen replication) is L1; GB10 only (5090 not set up; prabhasa+PSALM
  co-resident, bandwidth-bound); ralph closure = code AND domain; GitHub via connector (tools not
  yet exposed — publish deferred).
- TRIZ C1–C3 resolved (docs/triz_log.md). Sibling harvest (docs/prior_art_internal.md): porting
  prabhasa EFE selector/ledger/autopilot + gpu_guard; ACD metrics patterns; neo-fm five-point gate.
- Infrastructure honest negative: SMB projects mount cannot host live git (unlink/lock semantics) —
  canonical repo lives in dev VM + GitHub; mount gets rsync mirror + git bundle. Sublated the
  "repo lives on the drive" assumption with evidence (failed lock/rm operations logged in session).

## 2026-07-07 — GPU policy sublation + GB10 handoff
- SUBLATION (bādha): v1 guard rule "real runs require idle GPU" (precision: cautious default) is
  sublated by operator instruction "share with prabhasa, don't hesitate" (higher precision: owner's
  explicit policy). v2 = shared mode: proceed under co-residency at nice=10 with contention recorded
  in gate JSON; refuse only on kill-switch or <24GiB free unified memory. Old rule preserved here,
  not deleted.
- GitHub repo SharathSPhD/prabodha exists (public, empty — awaiting first push). Cowork sandbox has
  no push credentials and no network route to the Spark (tailnet unreachable); publish handoff runs
  via the GB10-side session or operator (see docs/gb10_handoff.md).
- Dockerized: Dockerfile (NGC pytorch aarch64) + docker-compose (courtesy caps 48g/10cpu). Docker is
  the preferred GB10 execution route (operator instruction; replaces venv route).

## 2026-07-07 — L1 GB10 session start (Claude Code on the Spark)
- Bundle history published: main @ abf8f5d pushed to github.com/SharathSPhD/prabodha (was empty).
  Session works in a Claude Code worktree; commit identity set to qbz506@york.ac.uk.
- INFRA CORRECTION (bādha, evidence: df -T): /home/sharaths/projects on the Spark is native ext4,
  not SMB — the .smbdelete ghosts are relics of the mirror copy. The parent checkout
  ~/projects/prabodha has an odd all-deleted index state (mirror-copy artifact); left untouched
  (harness denied hard reset — operator may want to re-clone from GitHub instead).
- FIX: gpu_guard v2.1 — GB10 nvidia-smi reports [N/A] for memory.used/total (unified memory);
  fallback to /proc/meminfo MemAvailable as the free-memory floor. v2 semantics preserved.
- BUILT: pretraining_like corpus resolver (deferred at L0 by design). Decision: flat
  one-prompt-per-line file generated once by scripts/tools/make_fit_corpus.py from the LOCAL
  wikitext-2-raw-v1 arrow cache (seed 42, 64 non-overlapping 128-word windows) — keeps dataset
  libs out of the runtime image, fit corpus inspectable. Known deviation from paper protocol
  (model's own pretraining distribution, n≈1000): wikitext-2 proxy at n=64, screen tier;
  Nanda reports n≈1–10 near-parity.
- Shared-mode reality at dispatch: PSALM GPT-BERT run live (train_100m_gb10.py); prabhasa
  train_130m not running. Guard: proceed, nice=10, contention=psalm recorded.

- 2026-07-07 E1 gate written (gates/gate_L1.json): code=pass domain=fail contention=psalm

## 2026-07-07 — L1 first gate: code=pass, domain=fail (1/3 hypotheses) — and what it teaches
- gates/gate_L1.json: H_report -0.32 (thr 0.5) FAIL; H_bands contrast 0.42 (thr 0.15) PASS but
  degenerate partition [0,2)/[2,6)/[6,36); H_modulation 0.0 FAIL — read at band_layers=[2..5]
  inherited from that partition (failure is downstream). contention=psalm throughout.
- DIAGNOSIS (verified on CPU with synthetic logits): the union-top-K Spearman metric has a
  structural null floor of ≈ -0.72 (disjoint top-K sets anti-correlate over the union support);
  zero correspondence reads as -0.7, not 0. Observed curve rises monotonically layer 0 (-0.69,
  ≈ the null floor) -> layer 34 (+0.43): the QUALITATIVE verbal-report signature (rho rising
  with depth) is PRESENT; the 0.5 threshold was mis-calibrated for this metric geometry.
- GPU ledger: L1_spent 1.3h of 2.0h cap (incl. 12min lost to the honest-contention restart and
  the 64->16 prompt sublation at the prompt-16 checkpoint).
- Next per protocol: adversarial domain review (fresh agent, contract+gate only), then iterate
  eval-only (metric recalibration = disclosed pre-registration amendment; no refit needed) or
  prune per e1.yaml prune_rule.
- OBSERVATION (unconverged thread "meta-tokens", HANDOFF §5): slice page for the instructed-fire
  prompt tracks 51 distinct CJK chars incl. 火/焰/炎 (fire/flame/blaze) and weather terms
  (热/冷/晴) — Nanda-style dense Chinese tokens surface as lens verbalizations on Qwen3-4B.
  Consequence for H_modulation: the hit criterion counts only the ENGLISH first-token id;
  cross-lingual verbalization (fire -> 火) is structurally missed. Second candidate explanation
  for the 0.0 hit-rate, alongside the degenerate band inheritance. Artifact: outputs/l1/slice_sample.html.

- 2026-07-07 E1 gate written (gates/gate_L1.json): code=pass domain=fail contention=psalm

## 2026-07-07 — L1 run 2 (eval-only, amendments A1–A3): the picture becomes coherent
- gates/gate_L1.json regenerated (run-1 preserved as gate_L1_run1.json). Still domain=fail
  (1/3), but now INTERPRETABLE:
  - H_report (calibrated support, null~0): 0.180 vs thr 0.4 — FAIL, but permutation p≈1e-4:
    correspondence is REAL and rising (layer 33: 0.39, layer 34: 0.62); it is concentrated in
    the last ~3 layers rather than the whole late third. Per-prompt spread -0.20..0.42.
  - H_bands: PASS 0.306 with SANE bands [0,6)/[6,30)/[30,36) after min_band_size 6 —
    early/middle/late three-band structure present (run-1's degenerate cut eliminated).
  - H_modulation: 0.10 (4/40) vs shuffled-concept null 0.0104 — ~10x chance, far below 0.5.
    Hits: water, music x2, bread (all en_mid variant; zh variants did not fire).
- Screen-tier reading: instrument mechanically sound; all three signatures qualitatively
  present and significant vs null; quantitatively weaker on 4B than thresholds implicitly
  calibrated to Nanda's 27B replication. The prune_rule's size-matched (27B) retry cannot fit
  L1's residual budget (spent 1.45h of 2.0h cap) — escalation is an operator decision.
