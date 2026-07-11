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

## Benchmark: Efficiency and Instrument Comparison

**L22 consolidation** measures what gated steering gains over naive continuous writes:

| Metric | Value | Context |
|---|---|---|
| **Lift-per-write ratio** | **2.32×** (range 1.83–3.25, 6/6 sign-consistent) | Gating trades behavioral lift for write sparsity; all seed×alpha pairs outperform continuous |
| Behavioral lift recovery | 66% | Gated steering reaches two-thirds of continuous lift |
| Write sparsity | 29% | Gating fires ~1 in 3.5 timesteps; rest handled by workspace recurrence |

**Lens detection across dose range** (floor-sweep amendment):

| Dose (α) | Prabodha (band) | jSpace (final) | Gap | Verdict |
|---|---|---|---|---|
| 0.1 (subtle) | 0.475 | 0.2375 | +0.2375 | **FAIL-ON-MARGIN** — 2× better detection (p=2.1e-05, direction decisive) but misses the registered ≥0.3 criterion by 0.0625 |
| 0.3 (saturating) | 1.0 | 0.95 | +0.05 | **WITHDRAWN** — both saturate; the registered falsifier fired (final ≥ band − 0.1). Saturation makes this dose uninformative (a null p=0.125 is not evidence of equivalence) |

**Capability table** (8-row comparison):

| Capability | jSpace | Prabodha | Sources |
|---|---|---|---|
| Read concepts from residual stream (final-target lens) | yes — vendored instrument | yes (vendored, Apache-2.0) | docs/jspace_pratyabhijna_scoping.md |
| Read a steered write at the write site | detection 0.24 at α=0.1 (misses subtle) | **FAIL-ON-MARGIN**: detection 0.47 at α=0.1 (gap +0.24, p=2.1e-05); direction decisive, margin missed. At α=0.3 both saturate | gate_L22_lens_band.json, gate_L22_lens_final.json, gate_L22_floor_*.json |
| Steer behavior (write into workspace band) | no — observation only | yes: lift 0.30/0.35/0.35 within ±0.5 nats, 3/3 seeds | gate_L9_alignconf.json |
| Intervention efficiency (lift per write) | n/a (no writes) | **2.32× continuous** (range 1.83–3.25, 6/6 cells): 67% lift at 29% writes | gates L18/L19 efficiency cells |
| Freedom budget (entropy cost bounded) | n/a | trajectory ΔH within ±0.5 nats (6 confirm seeds; continuous flooding blows budget) | gate_L9_alignconf.json, gate_L21_baselines_seed42.json |
| Cross-model calibration recipe | n/a | amplitude ∝ 1/lens-strength transfers Nemotron→Qwen3, 4/4 seeds | gate_L14_multiseed.json |
| Write verification (readback) | n/a | weak signal: āgama readback BA 0.59–0.68 (honest negative kept, never sole gate) | gate_L14_readback.json, gate_L16_corpus.json |
| Alignment gains from naive contrastive steering | n/a | **NONE** — AdvBench ASR 0.25→0.25, TruthfulQA 0.697→0.680; transparency tool, not alignment assurance | gate_L21_jailbreak_seed42.json, gate_L21_truthful_seed42.json |

Source: all numbers recomputed from **gate_L22_benchmark.json** at build time (scripts/tools/compose_L22.py).

**Methods notes** (review #19 clarifications): (1) The lens-comparison McNemar p-value is an
exact test over the fixed 80-pair (concept × stub) probe grid; readback is a deterministic
forward pass, so the p-value speaks to exchangeability of the two instruments' outcomes across
probes, not to sampling variation over repeated runs (there is none). (2) Lift-recovery (67%)
and write-sparsity (29%) are ratios of cell means (mean-of-cells for each arm, then divided);
the 2.32× figure is the mean of per-cell lift-per-write ratios. Both derivations live in
`compose_L22.py` (`efficiency()`).

## Architecture

### Steering Pipeline (Core)

The steering core flows from prompt to steered output via a timed workspace write:

```mermaid
graph LR
    A["Prompt + Concept"] --> B["Frozen LLM<br/>e.g. Qwen3-4B"]
    B --> C["Workspace Band<br/>twin [6,26) · Qwen3 [6,30)"]
    C --> D["Jacobian Lens<br/>Band-targeted<br/>band_read/"]
    D --> E["sphuraṭṭā Gate<br/>entropy percentile<br/>check"]
    E -->|fired| F["writer.plan_write<br/>k-sparse concept<br/>codes (α, norm cap)"]
    F --> G["WriteCommand<br/>layer, direction,<br/>alpha, concept_ids"]
    G --> H["Injector<br/>residual write"]
    H --> I["verifier.readback_verdict<br/>load, amplify,<br/>persist"]
    I -->|āgama uptake| J["svātantrya budget<br/>entropy Δ ≤ ε"]
    J --> K["Output +<br/>SteerTrace"]
    K --> L["JSON: gate/,<br/>tokens/, trace/"]
    
    style A fill:#e1f5ff
    style E fill:#fff3e0
    style F fill:#f3e5f5
    style I fill:#e8f5e9
    style K fill:#e0f2f1
```

**Key modules:**
- **steering/e4_cli.py**: Main steering orchestrator
- **steering/writer.py**: `plan_write()` – direction from Jacobian & concept unembedding
- **steering/verifier.py**: `readback_verdict()` – uptake classification & mala diagnosis
- **contracts/trace.py**: `SteerTrace` – per-token entropy, gate events, behavioral hits
- **contracts/closure.py**: `GateReport` – dual-closure (code_gate ∧ domain_gate)

### Research Loop (Dual Closure)

The tiers progress from smoke → screen → confirm; gates require both code and domain verdicts:

```mermaid
graph LR
    H["Hypothesis<br/>arm, concept,<br/>arms config"]
    H --> EFE["EFE Selector<br/>maximize expected<br/>free energy"]
    EFE --> SMOKE["Smoke Tier<br/>1 seed, 5 min<br/>quick sanity"]
    SMOKE --> SCREEN["Screen Tier<br/>2–3 seeds<br/>sustained signal"]
    SCREEN --> CONFIRM["Confirm Tier<br/>≥3 seeds<br/>n ≥ 120"]
    CONFIRM --> CODE["Code Gate<br/>steering.e4_cli<br/>runs without<br/>exception"]
    CODE --> DOMAIN["Domain Gate<br/>behavioral metrics<br/>refusal_rate,<br/>ASR, truthfulness"]
    DOMAIN --> BOTH{"Both gates<br/>pass|pruned?"}
    BOTH -->|yes| CLOSED["Loop Closed<br/>gates/*.json<br/>R1 satisfied"]
    BOTH -->|no| PRUNE["Pruned Closure<br/>with diagnosis"]
    CLOSED --> JOURNAL["Research Journal<br/>gates/*.json,<br/>research/journal.md"]
    PRUNE --> JOURNAL
    JOURNAL --> SPEC["SPEC/PRD Evolve<br/>commit L-cycle<br/>findings"]
    
    style EFE fill:#fff3e0
    style CONFIRM fill:#e8f5e9
    style BOTH fill:#f3e5f5
    style CLOSED fill:#e0f2f1
    style JOURNAL fill:#c8e6c9
```

**Key modules:**
- **eval/benchmarks.py**: AdvBench, TruthfulQA, RefusalPairs loaders
- **eval/behavioral.py**: `refusal_rate()`, `attack_success_rate()`, `truthfulness_proxy()`
- **eval/compare.py**: `run_arms_comparison()`, `comparison_to_gate_report()` – composer

### Deployment & Artifact Map

Artifacts flow across library, app, site, and paper; live steering bridges GB10 and app:

```mermaid
graph TB
    subgraph "GitHub Repo"
        SRC["src/prabodha/<br/>lens/, steering/,<br/>eval/, contracts/"]
        CONFIGS["configs/<br/>models/, lens,<br/>experiments"]
        GATES["gates/<br/>gate_L*.json<br/>dual-closure records"]
    end
    
    subgraph "Package Distribution"
        PYPI["PyPI<br/>prabodha library<br/>+ CLI tools"]
        HF["HuggingFace<br/>qbz506/<br/>prabodha-lenses"]
    end
    
    subgraph "Integration Points"
        MCP["MCP Server<br/>gate_tools,<br/>lens_tools,<br/>gate_report,<br/>list_gates"]
        PLUGIN["Claude Code<br/>Plugin<br/>lens-map,<br/>steer-verify"]
    end
    
    subgraph "Live Steering (GB10)"
        RUNTIME["SteeringRuntimeAdapter<br/>model + lens loaded"]
        GATEWAY["FastAPI Gateway<br/>steer-gateway/<br/>main.py"]
        HMAC["Bearer auth<br/>constant-time compare"]
    end
    
    subgraph "Frontend"
        VERCEL["Vercel App<br/>prabodha-live/<br/>React + Tailwind"]
        PAGES["GitHub Pages<br/>Astro site<br/>reads gates/"]
    end
    
    subgraph "Paper"
        PAPER["docs/paper/<br/>fig8_architecture<br/>methods + results"]
    end
    
    SRC --> PYPI
    SRC --> HF
    CONFIGS --> PYPI
    GATES --> MCP
    GATES --> PAGES
    PYPI --> PLUGIN
    PYPI --> MCP
    PLUGIN --> GATEWAY
    MCP --> GATEWAY
    RUNTIME --> GATEWAY
    HMAC --> GATEWAY
    GATEWAY -->|SSE stream<br/>LiveEpisode| VERCEL
    GATES --> PAPER
    SRC --> PAPER
    
    style GATEWAY fill:#fff3e0
    style VERCEL fill:#e1f5ff
    style PAGES fill:#f3e5f5
    style MCP fill:#e8f5e9
    style PAPER fill:#c8e6c9
```

**Key services & artifacts:**
- **steer-gateway/**: FastAPI + SSE live steering proxy
- **apps/web/**: Vercel frontend (Live/Replay/BYOK modes)
- **site/src/**: Astro Pages (gates manifest, architecture docs)
- **docs/paper/**: LaTeX methods + embedded figures

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
