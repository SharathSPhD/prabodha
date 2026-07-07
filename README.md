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

## Status
Loop **L0 (foundation)** closed by this commit. Loop **L1 (E1: Qwen lens replication)** in progress — see `contracts/L1_qwen_replication.md`.

## Provenance & credit
`vendor/jacobian-lens` is [anthropics/jacobian-lens](https://github.com/anthropics/jacobian-lens) (Apache-2.0), companion code for *Verbalizable Representations Form a Global Workspace in Language Models* (transformer-circuits, 2026). PWM concepts and machinery: Sharath S, *Pratyabhijñā World Model* (arXiv, 2026). See `NOTICE`.

Author: Sharath S <qbz506@york.ac.uk> · GitHub: SharathSPhD · License: Apache-2.0
