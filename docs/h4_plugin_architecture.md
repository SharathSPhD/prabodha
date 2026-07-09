# H4 plugin architecture — lens + steer + verify for any HF decoder
*Drafted 2026-07-09 per audit gap list (H4 was correctly gated behind H1/H2; both now
delivered at their tiers, so architecture can start). External API surface is CLEAN
(RULES R8: no Śaiva vocabulary leaks); the doctrine lives in docs, not identifiers.*

## What ships (extraction targets, all existing and tested)
| Plugin capability | Source module (tested) | External name |
|---|---|---|
| Fit a lens (any target layer) | prabodha.lens.adapter (+ vendor jlens) | `lens fit` |
| Read/readout at layers/positions | adapter.read / read_with_model | `lens read` |
| Band map + articulation profile | lens.e1_metrics (CKA bands, negentropy) | `lens map` |
| Slice page (self-contained HTML) | lens.vis_cli | `lens vis` |
| Plan+apply a concept write | steering.writer / injector | `steer write` |
| Timing policies | steering.timing (Strategy registry) | `--timing continuous\|prefill\|every-k\|entropy-gated` |
| Readback verdict + failure taxonomy | steering.verifier | `steer verify` |
| Quality guard | steering.scoring | `steer score` |
| Experiment selection over a menu | prabodha.efe | `research propose` |

## Design constraints (from the program's own findings — these ARE the product insights)
1. Readback must default to a band-targeted lens (final-target lenses are blind to band
   content — gate_L2b). `lens fit --target-layer` is therefore first-class, not exotic.
2. `steer write` defaults: sampling decoding required (greedy masks decode-time writes —
   gate_L4); entropy-gated timing with self-calibrated τ; svātantrya budget cap on by
   default with the entropy delta REPORTED on every call.
3. Every write is a replayable Command (config+seed) and every verify emits the failure
   taxonomy (no-load / no-amplify / no-persist / budget) — silent failure is a bug.
4. Model support: standard HF decoders work out of the box (Qwen3, Nemotron tested);
   hybrid linear-attention archs need optional extras (`pip install prabodha[hybrid]` →
   flash-linear-attention + causal-conv1d --no-build-isolation).

## Packaging plan
- Phase 1 (library): `pip install prabodha` — the existing package IS the library; add a
  `prabodha` console entrypoint wrapping the four CLIs. Cost: CPU-only, ~1 session.
- Phase 2 (Claude Code plugin): skills for `lens map`, `steer write --verify`, and
  `research propose` over a project-local menu; MCP is unnecessary (all local CLI).
- Phase 3 (community): examples on 2 public models, NOTICE/license audit (Apache-2.0 +
  vendored jlens Apache-2.0 — compatible), README with the glossary's engineering column only.

## Open before release
- Readback calibration (uptake thresholds are screen-tier settings, not universals).
- The articulation_null and dose_response menu items (claims that would ship in docs).
- API freeze after the trained-bridge comparison lands (may change steer defaults).
