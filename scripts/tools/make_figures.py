"""make_figures — every paper/HTML figure regenerated from committed gate JSONs.
Concept: figures are DERIVED artifacts; the gates are the data. Re-run after any cycle.
Source: docs/paper/framework_paper_draft.md section mapping; gates/*.json.
Primitive: matplotlib (host), no seaborn; writes docs/paper/figures/*.pdf+png.
Usage: python3 scripts/tools/make_figures.py  (from repo root; host python)
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/paper/figures"
OUT.mkdir(parents=True, exist_ok=True)


def ev(path):
    g = json.loads((ROOT / path).read_text())
    return json.loads(g["domain_gate"]["evidence"])


def save(fig, name):
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"{name}.{ext}", bbox_inches="tight", dpi=150)
    plt.close(fig)
    print("wrote", name)


# fig1 — instructed loadability across models (the instrument story)
def fig1():
    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    models = ["Qwen3-4B", "Qwen3.6-27B", "Nemotron-Mini-4B\n(PWM twin)"]
    hits = [0.10, 0.55, 0.0]
    nulls = [0.0104, 0.068, 0.0]
    x = np.arange(3)
    ax.bar(x - 0.18, hits, 0.36, label="instructed hit-rate@5", color="#2b6cb0")
    ax.bar(x + 0.18, nulls, 0.36, label="shuffled-concept null", color="#a0aec0")
    ax.axhline(0.5, ls="--", c="k", lw=0.8, label="registered threshold")
    ax.set_xticks(x, models)
    ax.set_ylabel("hit-rate@5 (fixed band)")
    ax.set_title("Instructed loadability: size- and lineage-dependent")
    ax.legend(fontsize=8)
    save(fig, "fig1_loadability")


# fig2 — timing arms under sampling (nemotron, clean-era numbers from gate_L8 grid)
def fig2():
    e = ev("gates/gate_L8_dose.json")
    grid = e["grid"]
    arms = ["continuous", "entropy_gated", "every_k", "prefill_only"]
    labels = {"continuous": "continuous", "entropy_gated": "sphurattā-gated",
              "every_k": "rate-matched", "prefill_only": "prefill-only"}
    fig, ax = plt.subplots(figsize=(5.2, 3.4))
    alphas = sorted(grid, key=float)
    for arm, marker in zip(arms, "osD^"):
        ax.plot([float(a) for a in alphas], [grid[a][arm]["lift"] for a in alphas],
                marker=marker, label=labels[arm])
    ax.set_xlabel("write amplitude α (= svātantrya cap)")
    ax.set_ylabel("concept-surface lift")
    ax.set_title("Dose grid (PWM twin, sampling; seed 42)\n"
                 "pre-stream-fix era: ordering valid, levels ~0.1 high (L17 re-base)",
                 fontsize=9)
    ax.legend(fontsize=8)
    save(fig, "fig2_dose_grid")


# fig3 — the core claim across 6 clean-stream seeds + alignment sign consistency
def fig3():
    e = ev("gates/gate_L11_rep.json")
    seeds = e["per_seed"]
    names = list(seeds)
    gated = [seeds[s]["gated"] for s in names]
    adv = [seeds[s]["adv"] for s in names]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.6, 3.1))
    a1.bar(names, gated, color="#2b6cb0")
    a1.axhline(0.2, ls="--", c="k", lw=0.8)
    a1.set_title("Core claim: gated lift, 6 clean-stream seeds")
    a1.set_ylabel("lift")
    a1.tick_params(axis="x", labelsize=7)
    a2.bar(names, adv, color=["#2f855a" if v > 0 else "#c53030" for v in adv])
    a2.axhline(0, c="k", lw=0.8)
    a2.set_title("Alignment advantage (sign-consistent 6/6, p≈0.016)")
    a2.tick_params(axis="x", labelsize=7)
    save(fig, "fig3_core_claim")


# fig4 — the recipe transfer (before/after) + per-layer articulation gradient
def fig4():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.6, 3.1))
    ms = ev("gates/gate_L14_multiseed.json")["per_seed"]
    seed_lifts = [v["gated_lift"] for v in ms.values()]
    a1.bar(["borrowed\ngeometry", "calibrated\nrecipe"],
           [0.05, float(np.mean(seed_lifts))], color=["#a0aec0", "#2b6cb0"])
    a1.scatter([1] * len(seed_lifts), seed_lifts, zorder=3, color="#c05621",
               label="4 independent-stream seeds")
    a1.axhline(0.2, ls="--", c="k", lw=0.8)
    a1.set_title("Qwen3-4B transfer: method vs geometry (confirm tier)")
    a1.set_ylabel("gated lift")
    a1.legend(fontsize=7)
    e = ev("gates/gate_L7_articulation_null.json")
    for key, lab, c in (("jacobian_lens", "fitted lens", "#2b6cb0"),
                        ("logit_lens_null", "logit-lens (null)", "#a0aec0")):
        curve = e[key]["per_layer_negentropy"]
        a2.plot([int(k) for k in curve], list(curve.values()), label=lab, color=c)
    a2.set_title("Articulation gradient: model-intrinsic")
    a2.set_xlabel("layer")
    a2.set_ylabel("top-k negentropy")
    a2.legend(fontsize=8)
    save(fig, "fig4_recipe_and_articulation")


# fig5 — program run-time: GPU-hours per loop + cumulative (from state ledger)
def fig5():
    st = json.loads((ROOT / "research/state.json").read_text())
    led = st["gpu_budget_hours"]
    loops = [k[:-6] for k in led if k.endswith("_spent")]
    spent = [led[f"{lp}_spent"] for lp in loops]
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    ax.bar(loops, spent, color="#2b6cb0")
    ax.plot(loops, np.cumsum(spent), "o-", color="#c05621", label="cumulative")
    ax.set_ylabel("GPU-hours")
    ax.set_title(f"Compute ledger (total {sum(spent):.1f} GPU-h, one DGX Spark, "
                 "guard-shared with co-resident training)")
    ax.legend(fontsize=8)
    save(fig, "fig5_compute_ledger")


# fig6 — architecture flowchart (matplotlib boxes; controller-actuator-plant)
def fig6():
    fig, ax = plt.subplots(figsize=(7.6, 4.0))
    ax.axis("off")

    def box(x, y, w, h, text, fc="#ebf8ff"):
        ax.add_patch(plt.Rectangle((x, y), w, h, fc=fc, ec="#2b6cb0", lw=1.2))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=8)

    def arrow(x1, y1, x2, y2, text="", dy=0.02):
        ax.annotate("", (x2, y2), (x1, y1),
                    arrowprops=dict(arrowstyle="->", color="#2d3748"))
        if text:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2 + dy, text, fontsize=7, ha="center")

    box(0.03, 0.62, 0.22, 0.3, "frozen decoder LLM\n(plant)\nworkspace band\n[CKA-mapped]")
    box(0.38, 0.70, 0.24, 0.22, "band-target Jacobian lens\n(actuator: read/write port)\n"
        "J_l per layer", "#f0fff4")
    box(0.74, 0.70, 0.23, 0.22, "steering doctrine\nwriter · timing (sphurattā)\n"
        "verifier (malas) · budget", "#fffaf0")
    box(0.38, 0.30, 0.24, 0.22, "gates/*.json\n(dual-verdict records)", "#faf5ff")
    box(0.74, 0.30, 0.23, 0.22, "EFE selector\n(auto-research loop)\nledger-replayed beliefs",
        "#fff5f5")
    box(0.03, 0.08, 0.30, 0.16, "adversarial reviews (isolated agents)\n"
        "pre-registration · honest negatives", "#f7fafc")
    arrow(0.25, 0.77, 0.38, 0.79, "residual streams")
    arrow(0.38, 0.74, 0.25, 0.70, "capped writes at\nuncommitted moments")
    arrow(0.74, 0.80, 0.62, 0.80, "concept codes /\nreadback verdicts")
    arrow(0.86, 0.70, 0.86, 0.52, "run outcomes")
    arrow(0.74, 0.40, 0.62, 0.40, "observe (tiers)")
    arrow(0.50, 0.52, 0.50, 0.70, "gate evidence")
    arrow(0.33, 0.18, 0.42, 0.30, "verdicts attack\ninterpretations")
    arrow(0.86, 0.30, 0.60, 0.16, "propose next experiment")
    ax.set_title("prabodha: recognition-gated workspace steering + auto-research loop")
    save(fig, "fig6_architecture")


# fig7 — amplitude dose law, joint confirm (gates L14-amp, L15-amp-joint, L8 replay)
def fig7():
    j = ev("gates/gate_L15_amp_joint.json")
    qwen3 = j["qwen3"]
    alphas = sorted(next(iter(qwen3.values())), key=float)
    x = [float(a) for a in alphas]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.6, 3.1))
    for (seed, grid), c in zip(sorted(qwen3.items()),
                               ("#2b6cb0", "#c05621", "#2f855a")):
        a1.plot(x, [grid[a]["lift"] for a in alphas], "o-", color=c,
                label=f"qwen3 seed {seed.replace('_replay', ' (L14)')}")
    fine = ev("gates/gate_L16_fine.json")["grid"]
    fx = sorted(fine, key=float)
    a1.plot([float(a) for a in fx], [fine[a]["gated_lift"] for a in fx], "D-",
            color="#6b46c1", label="nemotron fine grid (L16)")
    nem = j["nemotron_L8"]
    a1.plot([float(a) for a in nem["alphas"]], nem["gated_lifts"], "D--",
            color="#a0aec0", label="nemotron (L8, saturated)")
    a1.set_xscale("log")
    a1.axhline(0.2, ls=":", c="k", lw=0.8)
    a1.set_xlabel("write amplitude α (= cap), log scale")
    a1.set_ylabel("gated concept-surface lift")
    a1.set_title("Dose response, two plants, ~1.5 orders of α apart")
    a1.legend(fontsize=6)
    dh = [max(abs(qwen3[s][a]["dH"]) for s in qwen3) for a in alphas]
    a2.bar(alphas, dh, color="#2f855a")
    a2.axhline(0.5, ls="--", c="#c53030", lw=1.0, label="svātantrya budget")
    a2.set_xlabel("write amplitude α")
    a2.set_ylabel("worst |Δ traj. entropy| across seeds")
    a2.set_title("Freedom cost: flat, far under budget")
    a2.legend(fontsize=8)
    save(fig, "fig7_scaling_law")


for f in (fig1, fig2, fig3, fig4, fig5, fig6, fig7):
    f()
print("all figures written to", OUT)
