# WS3 Domain-Gate Validation — Deferred for GPU

**Status:** PREPARED (not executed in this session)  
**Target:** GB10 orchestrator  
**Date:** 2026-07-10

## Summary

Task 8 (domain-gate validation: end-to-end steer on Qwen3-4B, reproduce gate-cited lift direction) is deferred to the GPU orchestrator because it requires:
- Isolated GPU (GB10)
- Minimal co-residency (PSALM/prabhasa isolation check)
- cpu_guard.sh dispatch

The validation script and exact command are prepared below for the orchestrator to execute.

## Prepared Validation Script

**Location:** `scripts/mcp-domain-gate-validation.sh`

The script:
1. Verifies prabodha CLI is available
2. Checks for tiny_smoke config (optional CPU smoke test)
3. Confirms GPU status via gpu_guard
4. Runs steering episode: fire concept on Qwen3-4B (entropy_gated arm, seed 42, alpha 0.3)
5. Inspects the trace JSON (per-token entropy, gating, band readout)
6. Verifies gate-cited lift direction (consults gates/gate_L9_alignconf.json)

## Exact Command for Orchestrator

```bash
cd /home/sharaths/projects/prabodha/.claude/worktrees/plugin-mcp
bash scripts/mcp-domain-gate-validation.sh
```

## Expected Output

- **Trace file:** `outputs/traces/steer_fire_42.json` (SteerTrace JSON with per-token entropy, gating decisions, write norms, band readout, readback verdict)
- **Gate reference:** `gates/gate_L9_alignconf.json` (arm/seed/alpha semantics from L9)
- **Console output:** Token sequence, gated token count, readback verdict (if available)

## Success Criteria

1. Steering episode runs without errors (no CUDA/OOM/timeout)
2. Trace JSON created with valid schema (per-token entropy, gating, band readout)
3. Gate-cited lift direction verified (gate JSON readable and cites arm/seed/alpha)
4. Readback verdict (if available) logged for interpretation

## Honest Negatives

- Readback is a **weak signal**; single runs are not confirmatory. Multi-seed readback at confirm tier (gates/) is required for claims.
- Lift magnitudes are corpus-dependent; single seeds do not establish reproducibility.
- CPU smoke test (tiny_smoke.yaml) is optional and may not be representative of full model behavior.

## Notes

- GPU isolation is mandatory (see `scripts/lib/gpu_guard.sh` and CLAUDE.md resource discipline)
- No changes to PSALM or prabhasa jobs during execution
- Do NOT commit GPU-only artifacts to feat/plugin-mcp (use outputs/ which is .gitignored)
