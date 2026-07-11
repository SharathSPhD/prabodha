# prabodha Pages — Astro Site

A visually rich, story-driven explainer for prabodha: recognition-gated workspace steering. Serves both advanced researchers (deep technical, full math) and curious lay readers (jargon opened, examples/stories).

## Build & Deploy

### Local Development

```bash
npm install
npm run dev
```

Visit http://localhost:3000/prabodha in your browser.

### Production Build

```bash
npm run build
```

Produces `dist/` (static HTML + assets, ready for GitHub Pages).

The build process:
1. Runs `scripts/build-data.mjs` to extract numbers from `../../gates/*.json`
2. Emits `src/data/scenes.json`, `src/data/replays.json`, `src/data/gates.json`
3. Runs Astro build (Tailwind + static output)

**No hardcoded numbers.** Every figure in every scene traces to a gate file.

## Architecture

```
site/
  src/
    layouts/
      Base.astro         ← HTML skeleton, fonts, dark mode
    styles/
      global.css         ← Type scale, components (cards, buttons, depth toggle)
    components/
      Hero.astro         ← Animated J-space band visualization
      GetStarted.astro   ← pip install, commands, resource links
      DepthToggle.astro  ← Explorer vs Researcher mode (localStorage)
      scenes/
        Parallel.astro   ← Uncanny parallel (J-space ↔ Pratyabhijñā)
        Instrument.astro ← Band-targeted lenses vs final-target lenses
        Action.astro     ← Real steering trace player + live app CTA
        Transfer.astro   ← Recipe calibration (amplitude ∝ 1/lens-strength)
        Comparison.astro ← L21 baseline placeholder (logit-bias, prompt, LoRA)
        HonestLimits.astro ← Readback weak, corpus-amplitude fails margin
    pages/
      index.astro        ← Main page orchestrator
    data/
      scenes.json        ← Generated from gates (build step)
      replays.json       ← Replay trace metadata
      gates.json         ← Gate index (loop→verdict→gate_file)
  scripts/
    build-data.mjs       ← Extract scenes, gate metadata, replay index from repo
  dist/                  ← Output (created by `npm run build`)
  package.json
  astro.config.mjs
  tailwind.config.mjs
```

## Data Flow: Gates → Site

`scripts/build-data.mjs` reads the ground truth:

| Gate(s) | Scene | What it shows |
|---------|-------|---------------|
| gate_L9_alignconf, L11_rep | core-claim | 0.30–0.35 lift within ±0.5 nat budget, 6 seeds |
| gate_L11_rep | alignment | Gated > rate-matched (p≈0.016, 6/6 sign-consistent) |
| gate_L13_recipe, L14_multiseed | transfer | Calibration rule, Qwen3-4B replication (0.40 lift, 4 seeds) |
| gate_L20_confirm | trained-store | Cold-store steering functional (3 seeds), equivalence fails on margin |
| gate_L14–L16, L19 | honest-limits | Readback BA 0.59, corpus-amplitude d≈0.3 |

**Pending L21 gates** (placeholders in site):
- `gate_L21_logitbias`, `gate_L21_prompt`, `gate_L21_lora` → Comparison.astro

Each scene is self-contained and can be read independently. The Depth Toggle (Explorer/Researcher) controls which sub-paragraphs/details render.

## Color System

Defined in `tailwind.config.mjs`, grounded in the research:

```
primary:     #1a1a2e  (deep indigo, workspace band)
accent:      #e94b3c  (rust/terracotta, activation/write events)
bright:      #ffd166  (gold, sphuraṭṭā gating moments)
success:     #6ecb63  (transfer/calibration success)
warning:     #f7b32b  (honest negatives, margin failures)
neutral:     #d4d4d4  (recessive text)
```

## Deployment

### GitHub Actions

`.github/workflows/pages-astro.yml` automates build + deploy to GitHub Pages:

1. Trigger: Manual `workflow_dispatch` (or can auto-trigger on push to main)
2. Build: npm ci + npm run build
3. Upload: `site/dist/` to GitHub Pages artifact
4. Deploy: `actions/deploy-pages@v2`

**Do NOT enable/trigger the workflow yet.** The operator will do so after verifying the branch.

### Manual Testing

Build locally, inspect `dist/index.html`, and preview with:

```bash
npm run preview
```

## Future Enhancements

- [ ] Embed real D3 heatmaps (gate_L2b readback_profile, artifact load heatmap)
- [ ] Animate trace player (trained_bridge_qwen3 per-token flow)
- [ ] Slider for corpus-amplitude dose response (gate_L19 data)
- [ ] Interactive baseline comparison table (L21 gates)
- [ ] Syntax highlighting for code blocks (prabodha CLI examples)
- [ ] Responsive SVG re-rendering (band visualization on mobile)

## Notes

- **Reduced-motion:** All animations respect `prefers-reduced-motion: reduce`.
- **Dark mode:** Automatic via `prefers-color-scheme`; explicit toggle available in CSS.
- **Type:** Serif (Crimson Text), sans (Inter), mono (IBM Plex Mono). Loaded from Google Fonts.
- **Build time:** ~1 second (Astro + Tailwind are fast; no heavy JS).
- **Static output:** No server needed; deploy to any CDN/Pages hosting.

---

**Author:** Claude Fable 5 (working from Sharath S's research)  
**License:** Apache-2.0 (mirrors prabodha package)  
**Version:** v1.0.0  
**Generated:** 2026-07-11
