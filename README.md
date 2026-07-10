# prabodha — प्रबोध

**Recognition-gated workspace steering for language models.**

Prabodha ("awakening") implements the missing control theory for the Jacobian-lens
actuator: steer a frozen LLM through its global workspace using a small recognition-driven
world model. Writes are timed by sphurattā events (uncommitted moments), verified by
āgama re-cognition, bounded by svātantrya (autonomy), and diagnosed by the three malas.

Built as a bridge between PWM (Pratyabhijñā World Model, Sharath S), the J-space
(Anthropic's verbalizable global workspace), and GNW (Global Neuronal Workspace),
read as engineering.

## What it does

| Claim | Evidence | Strength |
|---|---|---|
| Workspace band + verbalizable content replicate across 3 model families, 2 sizes | gates L1, L1b, L2 | screen, multi-model |
| Event-gated writes steer within entropy budget (core claim) | gates L9, L11 | confirm, 6 seeds |
| Alignment beats rate-matched control | gates L11 | p≈0.016, 6/6 sign-consistent |
| Transfers to a 2nd model via calibration | gates L13, L14-ms | confirm, 4 seeds |
| Amplitude ∝ 1/lens-strength; monotone dose in active range | gates L14-amp, L15-amp, L16 | confirm (Qwen3) / screen (Nemotron) |

The readback verdict is weak (BA ≈ 0.59 at n=120 — honest negative, gates L14–L16);
corpus-amplitude coupling is confirmed directionally but fails the strict margin criterion
(gate L19 fail-on-margin). No new claims are made; all numbers are committed to gates.

## 60-second quickstart

```bash
pip install prabodha
```

Fit a lens and steer on a public model (Qwen3-4B, ~6 GB):

```python
from prabodha.lens import fit, vis
from prabodha.steer import write

# 1. Fit a band-targeted lens (one-time; resumable)
fit(
    model_config_path="configs/models/qwen3.yaml",
    lens_config_path="configs/lens_mid.yaml",
    out_path="outputs/lens_qwen3_mid30.pt"
)

# 2. Steer with recognition-gated writes
write(
    model_config_path="configs/models/qwen3.yaml",
    lens_file_path="outputs/lens_qwen3_mid30.pt",
    exp_config_path="configs/experiments/e13full.yaml",
    out_path="gates/my_run.json",
    alpha=0.3,
    seed=42,
    emit_trace="outputs/traces/my_trace.json"  # optional: emit per-token trace
)

# 3. Visualize lens readout (interactive HTML)
vis(
    model_config_path="configs/models/qwen3.yaml",
    lens_file_path="outputs/lens_qwen3_mid30.pt",
    prompt="the fire remembers rivers",
    out_path="outputs/fire_vis.html"
)
```

See `examples/quickstart_qwen3.md` and `examples/quickstart_nemotron.md` for full
command-line workflows with expected numbers (gate-cited).

## Install & use

### Library

```bash
pip install prabodha            # core library + CLI
pip install prabodha[hybrid]    # + flash-linear-attention support
```

### Public API

```python
# Lens operations
from prabodha.lens import fit, eval, vis

# Steering operations
from prabodha.steer import write, gate, verify
```

### CLI

```bash
prabodha --help                           # all subcommands
prabodha lens-fit --model M.yaml --lens L.yaml --out lens.pt
prabodha lens-eval --model M.yaml --lens-file lens.pt --exp E.yaml --out gate.json
prabodha lens-vis --model M.yaml --lens-file lens.pt --prompt "..." --out page.html
prabodha steer --model M.yaml --mid-lens lens.pt --exp E.yaml --out gate.json [--emit-trace trace.json]
prabodha figures                          # regenerate paper figures from gates/
```

## Plugin & MCP integration

Claude Code users: the plugin at `integrations/claude-code-plugin/` ships skills
(`lens-map`, `steer-verify`) with defaults from the measured findings.

MCP server at `integrations/mcp-server/` exposes `lens_map`, `steer_generate`,
`readback_verify`, `list_gates` for any MCP client.

## Provenance & license

Vendored: [anthropics/jacobian-lens](https://github.com/anthropics/jacobian-lens)
(Apache-2.0) — companion code for *Verbalizable Representations Form a Global Workspace*
(Anthropic, 2026).

Prabodha: Sharath S, *Pratyabhijñā World Model* (arXiv, 2026).

License: Apache-2.0.

---

Author: Sharath S <qbz506@york.ac.uk> · GitHub: SharathSPhD · Release: v1.0.0

**Docs:** [jspace_pratyabhijna_scoping.md](docs/jspace_pratyabhijna_scoping.md) ·
**Paper:** [docs/paper/paper.pdf](docs/paper/paper.pdf) ·
**Live app:** [prabodha.vercel.app](https://prabodha.vercel.app) ·
**Pages:** [sharathsphd.github.io/prabodha](https://sharathsphd.github.io/prabodha) ·
**HuggingFace:** [qbz506/prabodha-lenses](https://huggingface.co/qbz506/prabodha-lenses)
