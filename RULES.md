# RULES.md — hard invariants (sco2rl pattern: rule → rationale → enforcement)

R1. **Dual closure.** No loop closes on green tests alone; the domain gate (research objective met,
    or direction honestly pruned with statistics) must also pass. → Enforced by
    `src/prabodha/contracts/closure.py` (gate JSON invalid without both verdicts) + human sign-off
    line in the contract card. Test: tests/test_closure.py.
R2. **GPU guard mandatory.** No script may invoke CUDA without sourcing scripts/lib/gpu_guard.sh and
    passing its check. Detects prabhasa (`train_130m`), PSALM, and any python holding >10% GPU mem.
    → Enforced by dispatch scripts; violation = loop failure. Test: tests/test_gpu_guard.py (dry-run).
R3. **Svātantrya budget.** Any steering experiment must report output entropy + distinct-n vs
    unsteered baseline; steering that collapses diversity beyond epsilon in configs/experiments/*.yaml
    is a māyīya/kārma failure, not a success. → Enforced in steering evaluators (loop L3+).
R4. **Pre-registration-lite.** Every experiment's hypotheses, metrics, thresholds and seeds are in its
    config BEFORE the run; post-hoc metric changes must be disclosed in the gate JSON (`deviations`).
    → Enforced by runner refusing unconfigured metrics.
R5. **Honest negatives are closures.** A pruned direction closes its loop with status `pruned`, a
    journal entry, and gate JSON — never silent deletion. (Sublation, not deletion.)
R6. **Tiered rigor.** smoke (n=1, no stats) → screen (1 seed, permutation p, g) → confirm (>=3 seeds,
    Holm-Bonferroni across the family). Claims may only be stated at the tier they passed.
R7. **Vendored code is read-only.** vendor/jacobian-lens is never edited; adaptations live in
    src/prabodha/lens/ (Adapter pattern). Upstream sync is a documented ADR.
R8. **No Śaiva vocabulary in external API surfaces** (PWM SSE-whitelist doctrine); internal code and
    docs are Sanskrit-forward.
R9. **Author identity.** All commits: Sharath S <qbz506@york.ac.uk>. Sole contributor: SharathSPhD.
