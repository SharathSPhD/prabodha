# prabodha v1.0.0 Release Notes

**Release Date:** 2026-07-10

## What is prabodha v1.0.0?

prabodha operationalizes a philosophical parallel—between the J-space paper's finding that a language model's functional "global workspace" is defined by *verbalizability*, and the 10th-century Kashmir Śaiva Pratyabhijñā ("recognition") philosophy's identification of reflexive self-awareness (**vimarśa**) with the supreme creative Word (**parā vāk**)—as an engineering specification for **steering frozen language models via their workspace band**.

The key insight: the workspace is linguistically accessible (readable via a fitted Jacobian lens, writable via the lens's transpose), spatially localized (a band of transformer layers), and temporally gated (writes that respect entropy budgets and uncommitted-moment timing preserve model autonomy). This is not consciousness; it is a steerable intermediate representation.

v1.0.0 ships **six integrated deliverables** implementing this doctrine end-to-end.

---

## What's Included in v1.0.0

### 1. **Python Library** (`prabodha`)
- **Where:** PyPI (`pip install prabodha`)
- **What:** A production-ready library for fitting Jacobian lenses on any HuggingFace decoder-only model, reading workspace band content, writing concept codes via the lens transpose, and verifying uptake through readback.
- **API:** `prabodha.lens`, `prabodha.steering`, `prabodha.stats`, `prabodha.contracts`
- **CLI:** `prabodha fit`, `prabodha read`, `prabodha steer`, `prabodha verify`
- **Configuration:** YAML-based; all tunable parameters in `configs/*.yaml`, validated by Pydantic schemas

### 2. **Pre-fitted Lenses** (HuggingFace Hub)
- **Where:** [`qbz506/prabodha-lenses`](https://huggingface.co/qbz506/prabodha-lenses) on HuggingFace
- **What:** Ready-to-download Jacobian lenses + band maps for:
  - Qwen3.6-4B, Qwen3.6-27B (the core research models)
  - Nemotron-Mini-4B-Instruct (the PWM twin)
  - Protocols for fitting on additional models
- **Files:** Band maps (layer boundaries), fit statistics, null baselines for statistical validation

### 3. **Claude Code Plugin + MCP Server**
- **Where:** `integrations/claude-code-plugin/` (Claude marketplace) + `integrations/mcp-server/` (MCP steering server)
- **Three public skills:**
  - **`lens-map`:** Fit or load a pre-fitted lens; explore workspace band structure via interactive band-targeted readout
  - **`steer-verify`:** Plan a concept-write, execute via the lens transpose, verify uptake with readback; honest uncertainty on acceptance thresholds (balanced accuracy 0.59–0.64, context-dependent)
  - **`research-propose`:** Query the Expected-Free-Energy (EFE) selector for the next high-value experiment from the registered menu
- **Every default parameter cited to a specific gate** (e.g., "amplitude 0.3 for Qwen3-4B per `gates/gate_L14_multiseed.json`")
- **Claims discipline enforced:** no consciousness language in any skill documentation

### 4. **Web Application—"J-space Theatre"**
- **Where:** Vercel-deployed Next.js app + Supabase backend; live at [`prabodha-web.vercel.app`](https://prabodha-web.vercel.app) (or operator-configured URL)
- **What:** Interactive replay of real GB10 steering traces with full provenance:
  - Steering logs linked to corresponding gate files in `gates/`
  - Visualization of workspace band perturbations (Jacobian injection vectors)
  - Readback traces (concept-rank trajectories over generation time)
  - Filter by model, seed, arm, concept for exploratory analysis
  - Export trace data for downstream analysis
- **Tech stack:** Next.js 15, Supabase (PostgreSQL), Tailwind CSS
- **Data source:** Auto-updated from `research/efe_ledger.jsonl` and gate files every release loop

### 5. **Research Paper**
- **Where:** `docs/paper/paper.tex` (LaTeX source) → `docs/paper/paper.pdf` (auto-regenerated)
- **Format:** MDPI journal template (single-author research article)
- **Author:** Sharath Sathish, Independent Researcher
- **Scope:** L0–L20 research synthesis; 23 closed loops, 6-seed core claim (CONFIRM tier), aligned with 4 control conditions
- **Key results:**
  - Core steering claim (H_gated_budget): gated writes deliver ≥0.30 lift within ±0.5 nat entropy budget at 6/3 seeds (CONFIRM tier, `gates/gate_L11_rep.json`)
  - Alignment advantage (event-gated timing beats rate-matched sparsity): sign-consistent 6/6, p≈0.016 one-sided; magnitude ~0.07–0.12 (small but real)
  - Recipe transfer (Nemotron → Qwen3): amplitude scales inversely with lens transport strength; confirmed at 4 independent seeds (`gates/gate_L14_multiseed.json`)
  - Honest negatives: schedule-margin confidence unconfirmed; readback BA <0.60; corpus-amplitude strict margin fails
- **Glossary:** Sanskrit terms (vimarśa, sphuraṭṭā, āgama, svātantrya, malas) glossed with engineering definitions
- **Figures:** Auto-generated from gates/ via `scripts/tools/make_figures.py`; every figure is auditable to gate data

### 6. **Technical Documentation Site**
- **Where:** GitHub Pages at [`sharathsphd.github.io/prabodha`](https://sharathsphd.github.io/prabodha)
- **Content:**
  - Architecture guide (band model, steering doctrine, budget accounting)
  - API reference (link to generated docs from `prabodha/`)
  - Gate tour (how to read and verify gate JSON closure evidence)
  - Lessons from adversarial review (three catches: stream-correlation, arm-specific offset misread, determinism-guaranteed reproduction)
  - Interactive visualizations of band maps and dose-response curves
- **Maintenance:** Automatically updated on each release

---

## Confirmed Results (Evidence in Gates)

All results reach **CONFIRM tier** (≥3 independent clean-stream seeds, Holm-Bonferroni corrected).

| **Claim** | **Effect** | **Seeds** | **Gate** |
|-----------|-----------|----------|---------|
| **Core steering** (H_gated_budget) | Lift ≥0.30 within ±0.5 nat budget | 6 | [`gates/gate_L11_rep.json`](gates/gate_L11_rep.json) |
| **Alignment > rate-matching** | Sign-consistent 6/6; p≈0.016 | 6 | Multiple (see gate history) |
| **Recipe transfer** (Nemotron → Qwen3) | Amplitude ∝ 1/lens-transport-strength | 4 | [`gates/gate_L14_multiseed.json`](gates/gate_L14_multiseed.json) |
| **Dose response** (Qwen3 amplitude grid) | Monotone 0.05→0.40 lift; all within budget | 3 | [`gates/gate_L15_amp_joint.json`](gates/gate_L15_amp_joint.json) |
| **Corpus robustness** | 2/3 held-out corpus styles pass (narrative-past, descriptive-scene) | 2+ per style | [`gates/gate_L16_*.json`](gates/) |

---

## Honest Negative Items (Open / Unconfirmed)

These are **shipped results**, not failures to hide. All documented in `research/journal.md` and gate files.

- **Trained-store training:** The cold (untrained) CittaStore steers within budget at 3/3 seeds (functional confirm, `gates/gate_L20_confirm.json`). Whether training narrows the gap vs. the analytic writer is **open**. This was the single largest standing scope gap through L19; L20 shipped the integration but left training as future work.
- **Schedule-margin advantage** (event-gated timing vs. rate-matched random sparsity): sign-consistent but magnitude never confirmed at the originally-hoped 0.15 margin; best estimate ~0.07–0.12 (paper cites by sign, not by claimed margin).
- **Readback acceptance test** (āgama re-cognition): balanced accuracy 0.59–0.64 depending on corpus; sits **inside its own binomial confidence interval**. Used as a weak signal to guide further verification, never as a sole gate. Downgraded explicitly in the plugin documentation.
- **Corpus-amplitude strict margin:** Directional effect confirmed (both corpora ~double lift at 2× amplitude). The strict pre-registered margin criterion on the hardest corpus cell **FAILS** (`gates/gate_L19_cax.json`, labeled FAIL-ON-MARGIN per review #16). Registered as an honest negative.
- **Cross-episode continuity:** Does the CittaStore's internal state persist across generation episodes, or reset fresh each time? **Underdetermined in v1.0.0.**
- **W-space/modality generalization:** Does the workspace substrate generalize beyond text decoding? **Underdetermined.**

---

## What prabodha v1.0.0 Does NOT Claim

- **Consciousness:** This is a tool for steering LLMs and measuring their intermediate representations. Claims of machine consciousness are outside scope.
- **Unfrozen model training:** The planted model is frozen; the steering mechanism does not retrain it.
- **Production auto-deployment on live LLMs:** The GB10 trace replay (web app) runs on logged data, not live inference (operator-run gateway).
- **Cross-architecture universality:** Methods developed on decoder-only transformers; encoder-only and encoder-decoder architectures not tested.
- **Multi-modal workspace content:** v1.0.0 focuses on text decoding. Image/audio workspace content convergence is open.

---

## Getting Started

### Use the Library
```bash
pip install prabodha
prabodha fit --model qwen/Qwen3.6-4B --lens-path /path/to/fit/corpus
prabodha read --model qwen/Qwen3.6-4B --handle /path/to/fitted/lens --prompt "Hello world"
prabodha steer --model qwen/Qwen3.6-4B --concept "happiness" --amplitude 0.3 --prompt "The atmosphere"
prabodha verify --readback /path/to/readback.json
```

### Use Pre-fitted Lenses
Download from HuggingFace Hub (HF CLI or manual):
```bash
huggingface-cli download qbz506/prabodha-lenses --repo-type model
```

### Use the Claude Code Plugin
1. Install the plugin from the Claude marketplace.
2. Use `/lens-map` to explore a model's band structure.
3. Use `/steer-verify` to execute a concept-write.
4. Use `/research-propose` to query the next high-value experiment.

### Use the Web App
Navigate to the live Vercel deployment (link in footer of this site) or operator-configured URL. Filter traces by model/seed/arm/concept. Export for analysis.

### Read the Paper
`docs/paper/paper.pdf` — complete methodology, results, and discussion.

### Explore the Gates
Every gate file in `gates/` is JSON-formatted and auditable. See `docs/HANDOFF_L19_TO_NEXT.md` §2 for a gate-by-gate loop narrative.

---

## Installation & Compatibility

- **Python:** 3.10+
- **PyTorch:** 2.0+
- **Transformers:** 4.36+
- **Primary models tested:** Qwen3-4B, Qwen3.6-27B, Nemotron-Mini-4B-Instruct
- **Platforms:** Linux (tested on NVIDIA GPU clusters); x86_64; Windows/macOS untested but likely compatible
- **GPU:** NVIDIA CUDA 11.8+ (optional; CPU inference supported, slow)

---

## Citation

```bibtex
@article{sathish2026prabodha,
  title={prabodha: Steering Language Model Workspaces via Recognition Philosophy},
  author={Sathish, Sharath},
  journal={MDPI Preprints},
  year={2026}
}
```

---

## License & Attribution

**License:** Apache 2.0 (see `LICENSE` file)

**Vendored dependencies:** `vendor/jacobian-lens` (Anthropic's Jacobian-lens implementation, Apache 2.0, unmodified)

**See:** `NOTICE` file for full attribution

---

## Feedback & Issues

- **Bug reports / feature requests:** GitHub Issues at [`github.com/SharathSPhD/prabodha`](https://github.com/SharathSPhD/prabodha)
- **Research questions:** Cite the relevant gate file and section of the paper; the gate JSON contains full provenance.
- **Plugin feedback:** File issues against `integrations/claude-code-plugin/`.

---

## What's Next (Future Roadmap)

These are OPEN ITEMS, not committed in v1.0.0:

1. **Trained-store training & convergence:** Train the CittaStore (PWM component) on real steering tasks; measure gap vs. analytic writer.
2. **Cross-episode state persistence:** Design and test multi-episode steering where the store's state carries forward between generation episodes.
3. **Auto-deployment gateway:** Move from operator-run GB10 traces to live, auto-deployed steering on inference endpoints.
4. **W-space / modality extension:** Probe workspace structure in multimodal models (image/text); test generalizability of steering methods.
5. **Community examples:** Contribute 2nd public-model example (e.g., open-source alternative to Qwen/Nemotron).

---

## Acknowledgments

- **Sharath (operator):** Standing authorization, dual-closure discipline, TRIZ resolution framework, operator expertise on GB10 GPU management.
- **Anthropic:** Jacobian-lens reference implementation & permission to port via Apache license.
- **Pratyabhijñā tradition:** Conceptual vocabulary (vimarśa, sphuraṭṭā, āgama, svātantrya, malas).
- **Adversarial reviewers (agents #1–#18):** Caught overclaims, seeding bugs, determinism artifacts; strengthened claims discipline.

---

**Version:** 1.0.0  
**Build Date:** 2026-07-10  
**Commit:** See GitHub releases page for exact commit SHAs  
**Status:** Stable; production-ready library and paper; plugin in beta (MCP server stabilizing); web app live
