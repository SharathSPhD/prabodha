---
name: research-propose
description: Run the expected-free-energy experiment selector over a project-local registered menu — propose the next experiment, replay beliefs from gate records, and keep an auditable propose/observe/spend ledger. Use when the user wants principled experiment selection or an auditable research loop.
---

# EFE research loop

Selection discipline: candidates are REGISTERED in a menu YAML before any run; gates
(dual-verdict JSON records) are the selector's observations; every proposal,
disposition, spend, and divergence is appended to a JSONL ledger.

## Workflow

1. Register a menu (`configs/efe_menu.yaml`): candidates with `id`, `cost_gpu_hours`,
   `resolution`, `description`, optional `replay:` gates and `blocked:` flags, plus a
   `budget_gpu_hours` for the menu.
2. Propose the next cycle:
   ```bash
   prabodha research --menu configs/efe_menu.yaml --propose
   ```
   Beliefs replay from the ledger and the named gates; the ranked proposal balances
   epistemic value against registered cost.
3. Run the proposed experiment; convert its gate to an observation and log
   observe+spend via `prabodha.efe` (see `runner.py` for the 6-line pattern).
4. Lint the ledger (cycle-integrity and staleness invariants):
   ```bash
   python -m prabodha.efe.lint
   ```

## Rules the loop learned by breaking
- One budget line per menu, opened BEFORE the first dispatch.
- Winners get consumed: a passed candidate is not re-proposed (success raises
  pragmatic value; the consumption rule prevents loops).
- Costs are per-candidate and registered; a shared cost assumption flipped rankings
  once.
- If replay gates are later invalidated, rebuild beliefs before any disposition
  (staleness invariant — enforced by the linter).
