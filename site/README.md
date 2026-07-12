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

An act-structured interactive essay (Acts I–VII + coda), styled after
sharathsphd.github.io/ActiveCIrcuitDiscovery:

```
site/
  scripts/
    build-data.mjs       ← extracts scene/gate/replay data from ../gates
    build-figures.sh     ← compiles docs/paper_icml/figures/*.tex → public/figures/*.svg
  public/
    figures/             ← all 17 paper figures as SVG (committed)
    data/                ← moat.json, moat_replay.json, replay traces
  src/
    layouts/Base.astro
    styles/global.css    ← palette + essay system (act breaks, figure plates, callouts)
    components/
      Nav.astro          ← fixed top bar (Paper / Code / Live app)
      Hero.astro         ← essay hook over the animated J-space band
      ActBreak.astro     ← act divider
      FigurePlate.astro  ← paper figure on a light plate + caption + gate chips
      Coda.astro         ← provenance, author, references
      DepthToggle.astro  ← Explorer vs Researcher mode (localStorage)
      scenes/
        Act1Problem.astro    ← the actuator without a doctrine
        Act2Doctrine.astro   ← Pratyabhijñā: five falsifiable clauses + glossary
        Act3Machine.astro    ← dual gates, EFE selector, compute ledger
        Act4Evidence.astro   ← findings F1–F11 with paper figures + trace player
        Action.astro         ← real replay trace player (fetches trace JSON)
        Act5Negatives.astro  ← registered negatives (L21, readback)
        Act6Moat.astro       ← jailbreak moat + clean-gap predictor
        Moat.astro           ← data-driven live captures (moat.json)
        Act7Value.astro      ← six product surfaces + quickstart
    pages/index.astro    ← orchestrates the acts
```

After changing any paper figure, re-run `bash scripts/build-figures.sh`
(requires texlive + pdftocairo) and commit the regenerated SVGs.


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
