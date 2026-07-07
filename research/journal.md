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
