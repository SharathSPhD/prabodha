# prabodha — प्रबोध

**Recognition-gated workspace steering for language models.**
PWM (Pratyabhijñā World Model) × the J-space (Anthropic's verbalizable global workspace) × GNW, read as engineering.

Prabodha ("awakening / coming-to-recognition") builds the missing *control theory* for the
Jacobian-lens actuator: a small recognition-driven world model steers a frozen LLM through its
global workspace — writes timed by sphurattā events, verified by āgama re-cognition (readback),
bounded by svātantrya (autonomy preservation), diagnosed by the three malas.

- Conceptual source of truth: [`docs/jspace_pratyabhijna_scoping.md`](docs/jspace_pratyabhijna_scoping.md)
- Living spec: [`SPEC.md`](SPEC.md) · product doc: [`PRD.md`](PRD.md) — both **evolve at every loop closure; nothing is cut in stone**
- Ralph-loop contracts with dual (code + domain) closures: [`contracts/`](contracts/)
- Hard invariants: [`RULES.md`](RULES.md) · agent assignments: [`AGENTS.md`](AGENTS.md)

## Layout
```
src/prabodha/     lens/ (instrument) steering/ (v3 bridge) stats/ (pruning rigor) efe/ (auto-research) contracts/ (closure schema)
vendor/jacobian-lens/   Anthropic reference implementation (Apache-2.0, vendored)
configs/          models · lens · experiments · gpu   (config-driven: no constants in code)
contracts/        one markdown card per ralph loop, with machine-readable gate criteria
gates/            gate_<loop>.json emitted at closure (code + domain verdicts)
scripts/          lib/gpu_guard.sh · dispatch/ (GB10 job packs) · ralph/ (loop runner)
research/         state.json + journal.md — durable loop memory (ralph state lives in the repo)
docs/             scoping doc · triz_log · prior_art_internal · decisions/ (ADRs)
```

## Status (2026-07-10)
Loops **L0–L16 closed** (19 PRs, 20 selector cycles over 6 registered menus, 13 isolated
adversarial reviews, ~21 GPU-hours on one DGX Spark). Full narrative: `docs/paper/paper.pdf`
(technical) and `docs/artifact/prabodha_story.html` (dual-audience).

### Results at a glance (every number cites a gate JSON in `gates/`)
| Claim | Strength | Gate |
|---|---|---|
| Workspace band + verbalizable content replicate across 3 model families, 2 sizes | screen, multi-model | L1, L1b, L2 |
| Band content is legible ONLY to a band-targeted lens | screen | L2b |
| Event-gated writes steer within the entropy budget (core claim) | **confirm, 6 seeds** | L9, L11 |
| Alignment beats rate-matched control | sign-consistent 6/6, p≈0.016 | L11 |
| Method transfers to a 2nd model via calibration recipe | **confirm, 4 seeds** | L13, L14-ms |
| Amplitude ∝ 1/lens-strength; monotone dose in each plant's active range | confirm (qwen3, 3 seeds) / screen (nemotron) | L14-amp, L15-amp, L16-fine |
| Lift generalizes across stub styles at a fixed amplitude for 1 of 2 new styles; the fragile style becomes seed-robust at 2× amplitude (suggests a per-corpus amplitude axis, not yet established) | screen | L16-corpus, L17-cvar, L18-npretry |
| Readback verdict is a weak signal (BA ≈ 0.59 at n=120) — never an acceptance gate alone | honest negative | L14/L15-readback, L16-corpus |
| Greedy decoding masks decode-time writes; sampling regime required | mechanism | L4 |

## Install & use
```bash
pip install -e .            # library + `prabodha` CLI
pip install -e .[hybrid]    # + linear-attention model support
prabodha --help             # lens-fit · lens-eval · lens-vis · steer · research · figures
```
Claude Code users: the plugin in `integrations/claude-code-plugin/` ships skills
(`lens-map`, `steer-verify`, `research-propose`) whose defaults are the measured findings.

## Provenance & credit
`vendor/jacobian-lens` is [anthropics/jacobian-lens](https://github.com/anthropics/jacobian-lens) (Apache-2.0), companion code for *Verbalizable Representations Form a Global Workspace in Language Models* (transformer-circuits, 2026). PWM concepts and machinery: Sharath S, *Pratyabhijñā World Model* (arXiv, 2026). See `NOTICE`.

Author: Sharath S <qbz506@york.ac.uk> · GitHub: SharathSPhD · License: Apache-2.0
