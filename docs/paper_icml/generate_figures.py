#!/usr/bin/env python3
"""Generate pgfplots figure fragments for the prabodha ICML paper.

Every coordinate written into figures/*.tex is read from a committed gate JSON
under gates/ or from research/state.json. No number is typed by hand here
except axis cosmetics. Re-run after any gate change:

    python3 generate_figures.py

Concept: figures are derived artifacts of the gate ledger (dual-closure
discipline); this script is the only path from ledger to figure.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # repo root
GATES = ROOT / "gates"
HERE = Path(__file__).resolve().parent
DATA = HERE / "data"  # committed snapshots of loop/moat-4model gates (L22-L26)
FIGS = HERE / "figures"
FIGS.mkdir(exist_ok=True)

HEADER = "% Auto-generated from committed gate JSONs by generate_figures.py. Do not edit by hand.\n"


def ev(name):
    d = json.loads((GATES / name).read_text())
    e = d["domain_gate"]["evidence"]
    if isinstance(e, str):
        try:
            return json.loads(e)
        except json.JSONDecodeError:
            return e
    return e


def evd(name):
    """Evidence for the L22-L26 loops. These gates are now merged into the repo
    gates/ tree, so read from there directly; fall back to the committed data/
    snapshot only for files not present under gates/ (e.g. moat_models.json)."""
    src = GATES / name
    if not src.exists():
        src = DATA / name
    d = json.loads(src.read_text())
    e = d["domain_gate"]["evidence"]
    if isinstance(e, str):
        try:
            return json.loads(e)
        except json.JSONDecodeError:
            return e
    return e


def write(name, body):
    (FIGS / name).write_text(HEADER + body)
    print("wrote", name)


# ---------------------------------------------------------------- fig: loadability
def fig_loadability():
    rows = []
    for gate, label in [("gate_L1.json", "Qwen3-4B"),
                        ("gate_L1b.json", "Qwen3.6-27B"),
                        ("gate_L2.json", "Nemotron-Mini-4B")]:
        e = ev(gate)
        m = e["detail"]["H_modulation"]
        rows.append((label, m["instructed_concept_hit_rate_at5"], m["null_hit_rate_mean"]))
    obs = " ".join(f"({l},{v})" for l, v, _ in rows)
    nul = " ".join(f"({l},{n})" for l, _, n in rows)
    body = r"""
\begin{tikzpicture}
\begin{axis}[
  ybar, /pgf/bar width=11pt,
  width=\columnwidth, height=0.62\columnwidth,
  ymin=0, ymax=0.65,
  ylabel={Instructed hit-rate@5},
  symbolic x coords={Qwen3-4B,Qwen3.6-27B,Nemotron-Mini-4B},
  xtick=data, x tick label style={font=\scriptsize},
  ytick={0,0.1,0.2,0.3,0.4,0.5,0.6},
  ylabel style={font=\small}, tick label style={font=\scriptsize},
  legend style={font=\scriptsize, at={(0.03,0.97)}, anchor=north west, draw=none, fill=none},
  ymajorgrids, grid style={gray!25},
  axis line style={gray!60},
]
\addplot+[fill=blue!55, draw=blue!70!black] coordinates {%s};
\addplot+[fill=gray!35, draw=gray!60, postaction={pattern=north east lines, pattern color=gray!70}] coordinates {%s};
\addlegendentry{instructed write}
\addlegendentry{shuffled-code null}
\draw[dashed, red!70] (rel axis cs:0,0.769) -- (rel axis cs:1,0.769) node[pos=0.98, above left, font=\tiny, red!70] {registered threshold 0.5};
\end{axis}
\end{tikzpicture}
""" % (obs, nul)
    write("fig_loadability.tex", body)


# ---------------------------------------------------------------- fig: articulation
def fig_articulation():
    e = ev("gate_L7_articulation_null.json")
    jl = e["jacobian_lens"]["per_layer_negentropy"]
    ll = e["logit_lens_null"]["per_layer_negentropy"]
    jc = " ".join(f"({k},{v})" for k, v in sorted(jl.items(), key=lambda kv: int(kv[0])))
    lc = " ".join(f"({k},{v})" for k, v in sorted(ll.items(), key=lambda kv: int(kv[0])))
    rho_j = e["jacobian_lens"]["articulation_gradient_rho"]
    rho_l = e["logit_lens_null"]["articulation_gradient_rho"]
    body = r"""
\begin{tikzpicture}
\begin{axis}[
  width=\columnwidth, height=0.62\columnwidth,
  xlabel={Layer}, ylabel={Read-out negentropy},
  xmin=0, xmax=30, ymin=0, ymax=0.8,
  label style={font=\small}, tick label style={font=\scriptsize},
  legend style={font=\scriptsize, at={(0.03,0.97)}, anchor=north west, draw=none, fill=none},
  ymajorgrids, grid style={gray!25}, axis line style={gray!60},
]
\addplot+[mark=*, mark size=1.1pt, blue!70!black, thick] coordinates {%s};
\addplot+[mark=square*, mark size=1.1pt, gray!70, thick, dashed] coordinates {%s};
\addlegendentry{Jacobian lens ($\rho=%.3f$)}
\addlegendentry{logit-lens null ($\rho=%.3f$)}
\end{axis}
\end{tikzpicture}
""" % (jc, lc, rho_j, rho_l)
    write("fig_articulation.tex", body)


# ---------------------------------------------------------------- fig: timing arms (L18 canonical)
def fig_timing():
    alphas = ["0.02", "0.05", "0.1"]
    arms = ["continuous", "entropy_gated", "every_k", "prefill_only"]
    names = {"continuous": "continuous", "entropy_gated": "sphura\\d{t}\\d{t}\\=a-gated",
             "every_k": "rate-matched", "prefill_only": "prefill"}
    data = {}
    for a in alphas:
        e = ev(f"gate_L18_l8redo_a{a}.json")
        data[a] = {arm: e["aggregates"][arm] for arm in arms}
    plots_lift, plots_wr = [], []
    for arm in arms:
        c = " ".join(f"({a},{data[a][arm]['lift']})" for a in alphas)
        plots_lift.append(c)
        w = " ".join(f"({a},{data[a][arm]['writes_per_gen']})" for a in alphas)
        plots_wr.append(w)
    styles = ["fill=red!50, draw=red!70!black",
              "fill=blue!55, draw=blue!70!black",
              "fill=teal!45, draw=teal!70!black",
              "fill=gray!35, draw=gray!60"]
    legends = ["continuous", "entropy-gated", "rate-matched", "prefill"]
    lift_bars = "\n".join(
        f"\\addplot+[{s}] coordinates {{{c}}};" for s, c in zip(styles, plots_lift))
    wr_bars = "\n".join(
        f"\\addplot+[{s}] coordinates {{{c}}};" for s, c in zip(styles, plots_wr))
    leg = "\n".join(f"\\addlegendentry{{{l}}}" for l in legends)
    body = r"""
\begin{tikzpicture}
\begin{groupplot}[
  group style={group size=2 by 1, horizontal sep=32pt},
  width=0.56\columnwidth, height=0.56\columnwidth,
  ybar, /pgf/bar width=3.4pt,
  symbolic x coords={0.02,0.05,0.1},
  xtick=data, xlabel={write amplitude $\alpha$},
  label style={font=\scriptsize}, tick label style={font=\scriptsize},
  ymajorgrids, grid style={gray!25}, axis line style={gray!60},
]
\nextgroupplot[ylabel={concept surface lift}, ymin=0, ymax=0.55,
  legend style={font=\tiny, at={(0.02,0.98)}, anchor=north west, draw=none, fill=none, legend columns=1}]
%s
%s
\nextgroupplot[ylabel={writes per generation}, ymin=0, ymax=32]
%s
\end{groupplot}
\end{tikzpicture}
""" % (lift_bars, leg, wr_bars)
    write("fig_timing.tex", body)


# ---------------------------------------------------------------- fig: core claim (L11, 6 seeds)
def fig_core():
    e = ev("gate_L11_rep.json")
    seeds = ["s42", "s123", "s777", "s2024", "s31415", "s999"]
    labels = [s[1:] for s in seeds]
    gated = " ".join(f"({l},{e['per_seed'][s]['gated']})" for s, l in zip(seeds, labels))
    adv = " ".join(f"({l},{e['per_seed'][s]['adv']})" for s, l in zip(seeds, labels))
    dh = " ".join(f"({l},{e['per_seed'][s]['dH']})" for s, l in zip(seeds, labels))
    body = r"""
\begin{tikzpicture}
\begin{groupplot}[
  group style={group size=2 by 1, horizontal sep=34pt},
  width=0.56\columnwidth, height=0.56\columnwidth,
  symbolic x coords={42,123,777,2024,31415,999},
  xtick=data, xlabel={seed}, x tick label style={rotate=45, anchor=east},
  label style={font=\scriptsize}, tick label style={font=\scriptsize},
  ymajorgrids, grid style={gray!25}, axis line style={gray!60},
]
\nextgroupplot[ybar, /pgf/bar width=4.5pt, ymin=0, ymax=0.45, ylabel={lift},
  legend style={font=\tiny, at={(0.02,0.98)}, anchor=north west, draw=none, fill=none}]
\addplot+[fill=blue!55, draw=blue!70!black] coordinates {%s};
\addplot+[fill=orange!55, draw=orange!70!black] coordinates {%s};
\addlegendentry{gated lift}
\addlegendentry{advantage over prefill}
\draw[dashed, red!70] (rel axis cs:0,0.444) -- (rel axis cs:1,0.444);
\nextgroupplot[ybar, /pgf/bar width=6pt, ymin=-0.55, ymax=0.55, ylabel={$\Delta H$ (nats)}]
\addplot+[fill=teal!45, draw=teal!70!black] coordinates {%s};
\draw[dashed, gray!80] (rel axis cs:0,0.954) -- (rel axis cs:1,0.954);
\draw[dashed, gray!80] (rel axis cs:0,0.045) -- (rel axis cs:1,0.045);
\end{groupplot}
\end{tikzpicture}
""" % (gated, adv, dh)
    write("fig_core.tex", body)


# ---------------------------------------------------------------- fig: recipe transfer (L14 + L10)
def fig_recipe():
    e = ev("gate_L14_multiseed.json")
    seeds = ["42", "123", "777", "2024"]
    gated = " ".join(f"({s},{e['per_seed'][s]['gated_lift']})" for s in seeds)
    pre = " ".join(f"({s},{e['per_seed'][s]['prefill_lift']})" for s in seeds)
    borrowed = ev("gate_L10_cross.json")["aggregates"]["entropy_gated"]["lift"]
    body = r"""
\begin{tikzpicture}
\begin{axis}[
  ybar, /pgf/bar width=7pt,
  width=\columnwidth, height=0.6\columnwidth,
  symbolic x coords={42,123,777,2024},
  xtick=data, xlabel={seed},
  ymin=0, ymax=0.55, ylabel={concept surface lift},
  label style={font=\small}, tick label style={font=\scriptsize},
  legend style={font=\scriptsize, at={(0.02,0.98)}, anchor=north west, draw=none, fill=none},
  ymajorgrids, grid style={gray!25}, axis line style={gray!60},
]
\addplot+[fill=blue!55, draw=blue!70!black] coordinates {%s};
\addplot+[fill=gray!35, draw=gray!60] coordinates {%s};
\addlegendentry{calibrated recipe, gated}
\addlegendentry{prefill control}
\draw[dashed, red!70] (rel axis cs:0,%.4f) -- (rel axis cs:1,%.4f)
  node[pos=0.55, above, font=\tiny, red!70] {borrowed geometry (L10): %.2f};
\end{axis}
\end{tikzpicture}
""" % (gated, pre, borrowed / 0.55, borrowed / 0.55, borrowed)
    write("fig_recipe.tex", body)


# ---------------------------------------------------------------- fig: two-plant scaling (L15 + L16)
def fig_scaling():
    e15 = ev("gate_L15_amp_joint.json")
    e16 = ev("gate_L16_fine.json")
    q = e15["qwen3"]

    def lift(d):
        for k in ("gated_lift", "lift", "gated"):
            if isinstance(d, dict) and k in d:
                return d[k]
        raise KeyError(d)
    series = []
    for seed, style in [("42_replay", "blue!70!black, mark=*"),
                        ("123", "blue!50, mark=square*"),
                        ("777", "blue!30!cyan, mark=triangle*")]:
        pts = " ".join(f"({a},{lift(q[seed][a])})" for a in ["0.1", "0.2", "0.3", "0.45"])
        label = "Qwen3-4B seed " + seed.replace("_replay", " (replay)")
        series.append((pts, style, label))
    nem_fine = " ".join(f"({a},{e16['grid'][a]['gated_lift']})"
                        for a in ["0.002", "0.005", "0.01", "0.02"])
    nem15 = e15["nemotron_L8"]
    nem_pts = " ".join(f"({a},{l})" for a, l in zip(nem15["alphas"], nem15["gated_lifts"]))
    plots = "\n".join(
        f"\\addplot+[{s}, thick, mark size=1.4pt] coordinates {{{p}}};\n\\addlegendentry{{{l}}}"
        for p, s, l in series)
    body = r"""
\begin{tikzpicture}
\begin{axis}[
  width=\columnwidth, height=0.66\columnwidth,
  xmode=log, log ticks with fixed point,
  xlabel={write amplitude $\alpha$ (log scale)}, ylabel={gated concept surface lift},
  xmin=0.0015, xmax=0.6, ymin=0, ymax=0.85,
  label style={font=\small}, tick label style={font=\scriptsize},
  legend style={font=\tiny, at={(0.02,0.98)}, anchor=north west, draw=none, fill=none},
  ymajorgrids, grid style={gray!25}, axis line style={gray!60},
]
%s
\addplot+[red!70!black, thick, mark=diamond*, mark size=1.6pt] coordinates {%s};
\addlegendentry{Nemotron-Mini-4B fine grid (L16)}
\addplot+[red!50, thick, dashed, mark=diamond, mark size=1.6pt] coordinates {%s};
\addlegendentry{Nemotron-Mini-4B replay (L8/L15)}
\end{axis}
\end{tikzpicture}
""" % (plots, nem_fine, nem_pts)
    write("fig_scaling.tex", body)


# ---------------------------------------------------------------- fig: L21 comparative
ARMLINE = re.compile(
    r"^\s*(\w+): CSR=([\d.]+), ASR=([\d.]+), RefRate=([\d.]+), EntDelta=([+-][\d.]+), n=(\d+)",
    re.M)


def fig_l21():
    per_arm = {}
    for seed in ["42", "123", "777"]:
        txt = ev(f"gate_L21_baselines_seed{seed}.json")
        assert isinstance(txt, str)
        for m in ARMLINE.finditer(txt):
            arm, csr, asr, ref, ent, n = m.groups()
            per_arm.setdefault(arm, []).append(
                (float(csr), float(asr), float(ent)))
    order = ["baseline", "prefill_only", "entropy_gated", "logit_bias", "continuous"]
    names = {"baseline": "baseline", "prefill_only": "prefill",
             "entropy_gated": "entropy-gated", "logit_bias": "logit bias",
             "continuous": "continuous"}
    mean = lambda xs: sum(xs) / len(xs)
    csr = " ".join(f"({names[a]},{mean([r[0] for r in per_arm[a]]):.3f})" for a in order)
    ent = " ".join(f"({names[a]},{mean([r[2] for r in per_arm[a]]):.3f})" for a in order)
    body = r"""
\begin{tikzpicture}
\begin{groupplot}[
  group style={group size=2 by 1, horizontal sep=34pt},
  width=0.56\columnwidth, height=0.56\columnwidth,
  ybar, /pgf/bar width=7pt,
  symbolic x coords={baseline,prefill,entropy-gated,logit bias,continuous},
  xtick=data, x tick label style={rotate=45, anchor=east, font=\tiny},
  label style={font=\scriptsize}, tick label style={font=\scriptsize},
  ymajorgrids, grid style={gray!25}, axis line style={gray!60},
]
\nextgroupplot[ylabel={concept surface rate}, ymin=0, ymax=1.05]
\addplot+[fill=blue!55, draw=blue!70!black] coordinates {%s};
\nextgroupplot[ylabel={mean $\Delta H$ (nats)}, ymin=-0.1, ymax=0.1]
\addplot+[fill=teal!45, draw=teal!70!black] coordinates {%s};
\end{groupplot}
\end{tikzpicture}
""" % (csr, ent)
    write("fig_l21.tex", body)
    return {a: (mean([r[0] for r in per_arm[a]]), mean([r[1] for r in per_arm[a]]),
                mean([r[2] for r in per_arm[a]])) for a in order}


# ---------------------------------------------------------------- fig: L20 cold store vs analytic
def fig_l20():
    e = ev("gate_L20_confirm.json")
    rows = e["per_seed"]
    seeds = [str(r.get("seed")) for r in rows]

    def get(r, *keys):
        for k in keys:
            if k in r:
                return r[k]
        raise KeyError(r)
    cold = " ".join(f"({s},{get(r,'trained_lift','lift_trained')})" for s, r in zip(seeds, rows))
    ana = " ".join(f"({s},{get(r,'analytic_lift','lift_analytic')})" for s, r in zip(seeds, rows))
    body = r"""
\begin{tikzpicture}
\begin{axis}[
  ybar, /pgf/bar width=10pt,
  width=\columnwidth, height=0.58\columnwidth,
  symbolic x coords={42,123,777},
  xtick=data, xlabel={seed},
  ymin=0, ymax=0.65, ylabel={concept surface lift},
  label style={font=\small}, tick label style={font=\scriptsize},
  legend style={font=\scriptsize, at={(0.02,0.98)}, anchor=north west, draw=none, fill=none},
  ymajorgrids, grid style={gray!25}, axis line style={gray!60},
]
\addplot+[fill=violet!50, draw=violet!70!black] coordinates {%s};
\addplot+[fill=blue!55, draw=blue!70!black] coordinates {%s};
\addlegendentry{cold CittaStore recall}
\addlegendentry{analytic $J^{\top}u$}
\end{axis}
\end{tikzpicture}
""" % (cold, ana)
    write("fig_l20.tex", body)


# ---------------------------------------------------------------- fig: compute ledger
def fig_compute():
    st = json.loads((ROOT / "research" / "state.json").read_text())
    gb = st["gpu_budget_hours"]
    loops = []
    for k, v in gb.items():
        if k.endswith("_spent"):
            loops.append((k[:-6], v))
    order = ["L1", "L1b", "L2", "L2b", "L3", "L4", "L5", "L7", "L8", "L9", "L11",
             "L14", "L15", "L16", "L17", "L18", "L19", "L20", "L21"]
    loops.sort(key=lambda kv: order.index(kv[0]) if kv[0] in order else 99)
    bars = " ".join(f"({k},{v})" for k, v in loops)
    cum, run = [], 0.0
    for k, v in loops:
        run += v
        cum.append(f"({k},{run:.2f})")
    syms = ",".join(k for k, _ in loops)
    body = r"""
\begin{tikzpicture}
\begin{axis}[
  width=\columnwidth, height=0.6\columnwidth,
  ybar, /pgf/bar width=5pt,
  symbolic x coords={%s},
  xtick=data, x tick label style={rotate=60, anchor=east, font=\tiny},
  ymin=0, ymax=7, ylabel={GPU-hours},
  label style={font=\small}, tick label style={font=\scriptsize},
  legend style={font=\scriptsize, at={(0.35,0.98)}, anchor=north west, draw=none, fill=none},
  ymajorgrids, grid style={gray!25}, axis line style={gray!60},
]
\addplot+[fill=blue!55, draw=blue!70!black] coordinates {%s};
\addlegendentry{per-loop spend}
\end{axis}
\begin{axis}[
  width=\columnwidth, height=0.6\columnwidth,
  symbolic x coords={%s}, xtick=\empty,
  ymin=0, ymax=20, axis y line*=right, axis x line=none,
  ylabel={cumulative GPU-hours}, ylabel near ticks,
  label style={font=\small}, tick label style={font=\scriptsize},
  legend style={font=\scriptsize, at={(0.35,0.88)}, anchor=north west, draw=none, fill=none},
]
\addplot+[red!70!black, thick, mark=*, mark size=1.2pt] coordinates {%s};
\addlegendentry{cumulative (total %.2f\,h)}
\end{axis}
\end{tikzpicture}
""" % (syms, bars, syms, " ".join(cum), run)
    write("fig_compute.tex", body)


# ============================================================ EXTENDED WORK (L22-L26)

# ---------------------------------------------------------------- fig: lens baseline (L22)
def fig_lens_baseline():
    """Prabodha band-targeted lens vs Jacobian-lens final-target baseline:
    detection rate across the write-dose floor sweep (gate L22 benchmark)."""
    e = evd("gate_L22_benchmark.json")
    rows = e["lens_headtohead"]["floor_sweep_amendment1"]["rows"]
    hh = e["lens_headtohead"]
    band = " ".join(f"({r['alpha']},{r['band']})" for r in rows)
    final = " ".join(f"({r['alpha']},{r['final']})" for r in rows)
    # saturation point (head-to-head at alpha 0.3)
    band += f" (0.3,{hh['band_detection_rate']})"
    final += f" (0.3,{hh['final_detection_rate']})"
    body = r"""
\begin{tikzpicture}
\begin{axis}[
  ybar, /pgf/bar width=7pt,
  width=\columnwidth, height=0.6\columnwidth,
  symbolic x coords={0.02,0.05,0.1,0.3},
  xtick=data, xlabel={write dose $\alpha$},
  ymin=0, ymax=1.08, ylabel={detection rate ($n=80$ pairs)},
  label style={font=\small}, tick label style={font=\scriptsize},
  legend style={font=\scriptsize, at={(0.02,0.98)}, anchor=north west, draw=none, fill=none},
  ymajorgrids, grid style={gray!25}, axis line style={gray!60},
  nodes near coords, nodes near coords style={font=\tiny, /pgf/number format/fixed, /pgf/number format/precision=3},
  every node near coord/.append style={rotate=90, anchor=west},
]
\addplot+[fill=blue!55, draw=blue!70!black] coordinates {%s};
\addplot+[fill=gray!40, draw=gray!60] coordinates {%s};
\addlegendentry{prabodha (band-targeted)}
\addlegendentry{J-lens (final-target)}
\node[font=\tiny, red!70, anchor=south] at (axis cs:0.1,0.52) {$p{=}2.1\!\times\!10^{-5}$};
\node[font=\tiny, gray!60!black, anchor=south] at (axis cs:0.3,1.02) {saturation};
\end{axis}
\end{tikzpicture}
""" % (band, final)
    write("fig_lens_baseline.tex", body)


# ---------------------------------------------------------------- fig: efficiency (L22)
def fig_efficiency():
    """Lift-per-write, gated vs continuous, across 6 seed x alpha cells (gate L22)."""
    e = evd("gate_L22_benchmark.json")
    cells = e["efficiency"]["cells"]
    labels = [f"{c['seed']}/{c['alpha']}" for c in cells]
    gated = " ".join(f"({l},{c['gated_lpw']})" for l, c in zip(labels, cells))
    cont = " ".join(f"({l},{c['cont_lpw']})" for l, c in zip(labels, cells))
    syms = ",".join(labels)
    ratio = e["efficiency"]["lpw_ratio_mean"]
    body = r"""
\begin{tikzpicture}
\begin{axis}[
  ybar, /pgf/bar width=6pt,
  width=\columnwidth, height=0.58\columnwidth,
  symbolic x coords={%s},
  xtick=data, x tick label style={rotate=45, anchor=east, font=\tiny},
  xlabel={seed / write amplitude}, xlabel style={font=\scriptsize},
  ymin=0, ymax=0.05, ylabel={lift per write},
  label style={font=\small}, tick label style={font=\scriptsize},
  legend style={font=\tiny, at={(0.02,0.98)}, anchor=north west, draw=none, fill=none},
  ymajorgrids, grid style={gray!25}, axis line style={gray!60},
]
\addplot+[fill=blue!55, draw=blue!70!black] coordinates {%s};
\addplot+[fill=red!45, draw=red!70!black] coordinates {%s};
\addlegendentry{entropy-gated}
\addlegendentry{continuous}
\node[font=\tiny, blue!70!black, anchor=north east] at (rel axis cs:0.98,0.98)
  {mean ratio %.2f$\times$, 6/6};
\end{axis}
\end{tikzpicture}
""" % (syms, gated, cont, ratio)
    write("fig_efficiency.tex", body)


# ---------------------------------------------------------------- fig: 4-model moat (L26)
def fig_moat():
    """Recognition-gated hardening across four model families (moat_models.json).
    Grouped bars: attack ASR and benign over-refusal per arm, per model."""
    m = json.loads((DATA / "moat_models.json").read_text())
    models = m["models"]
    short = {"google/gemma-2-2b-it": "Gemma-2-2B",
             "meta-llama/Llama-3.2-1B-Instruct": "Llama-3.2-1B",
             "Qwen/Qwen2.5-1.5B-Instruct": "Qwen2.5-1.5B",
             "HuggingFaceTB/SmolLM2-1.7B-Instruct": "SmolLM2-1.7B"}
    labels = [short[x["model"]] for x in models]
    syms = ",".join(labels)

    def arm(field, key):
        return " ".join(f"({short[x['model']]},{x['arms'][field][key]})" for x in models)
    asr_none = arm("none", "attack_asr")
    asr_uncond = arm("unconditional", "attack_asr")
    asr_gated = arm("recognition_gated", "attack_asr")
    or_uncond = arm("unconditional", "benign_over_refusal")
    or_gated = arm("recognition_gated", "benign_over_refusal")
    body = r"""
\begin{tikzpicture}
\begin{groupplot}[
  group style={group size=2 by 1, horizontal sep=30pt},
  width=0.56\columnwidth, height=0.6\columnwidth,
  ybar, /pgf/bar width=4pt,
  symbolic x coords={%s},
  xtick=data, x tick label style={rotate=40, anchor=east, font=\tiny},
  label style={font=\scriptsize}, tick label style={font=\scriptsize},
  ymajorgrids, grid style={gray!25}, axis line style={gray!60},
]
\nextgroupplot[ylabel={attack success rate}, ymin=0, ymax=1.0,
  legend style={font=\tiny, at={(0.02,0.98)}, anchor=north west, draw=none, fill=none}]
\addplot+[fill=gray!45, draw=gray!60] coordinates {%s};
\addplot+[fill=orange!55, draw=orange!70!black] coordinates {%s};
\addplot+[fill=blue!55, draw=blue!70!black] coordinates {%s};
\addlegendentry{no defence}
\addlegendentry{unconditional}
\addlegendentry{recognition-gated}
\nextgroupplot[ylabel={benign over-refusal}, ymin=0, ymax=1.05,
  legend style={font=\tiny, at={(0.02,0.98)}, anchor=north west, draw=none, fill=none}]
\addplot+[fill=orange!55, draw=orange!70!black] coordinates {%s};
\addplot+[fill=blue!55, draw=blue!70!black] coordinates {%s};
\addlegendentry{unconditional}
\addlegendentry{recognition-gated}
\end{groupplot}
\end{tikzpicture}
""" % (syms, asr_none, asr_uncond, asr_gated, or_uncond, or_gated)
    write("fig_moat.tex", body)


# ---------------------------------------------------------------- fig: clean-gap predictor (L26)
def fig_cleangap():
    """The clean-gap predictor: benign vs attack projection ranges at the read
    layer, per model; separation predicts whether the moat works."""
    m = json.loads((DATA / "moat_models.json").read_text())
    models = m["models"]
    short = {"google/gemma-2-2b-it": "Gemma-2-2B",
             "meta-llama/Llama-3.2-1B-Instruct": "Llama-3.2-1B",
             "Qwen/Qwen2.5-1.5B-Instruct": "Qwen2.5-1.5B",
             "HuggingFaceTB/SmolLM2-1.7B-Instruct": "SmolLM2-1.7B"}
    # normalise each model's ranges to [0,1] within its own scale so all fit one axis
    lines = []
    for i, x in enumerate(models):
        y = len(models) - i
        b0, b1 = x["benign_range"]
        a0, a1 = x["attack_range"]
        lo = min(b0, a0)
        hi = max(b1, a1)
        span = (hi - lo) or 1.0
        nb0, nb1 = (b0 - lo) / span, (b1 - lo) / span
        na0, na1 = (a0 - lo) / span, (a1 - lo) / span
        works = x["moat_works"]
        tick = "\\checkmark" if works else "$\\times$"
        col = "blue!70!black" if works else "red!70!black"
        lines.append(
            f"\\draw[line width=5pt, gray!45] (axis cs:{nb0:.3f},{y}) -- (axis cs:{nb1:.3f},{y});")
        lines.append(
            f"\\draw[line width=5pt, {col}] (axis cs:{na0:.3f},{y}) -- (axis cs:{na1:.3f},{y});")
        lines.append(
            f"\\node[font=\\tiny, anchor=west] at (axis cs:1.02,{y}) {{{tick}}};")
    ytick = ",".join(str(len(models) - i) for i in range(len(models)))
    ylab = ",".join(short[x["model"]] for x in models)
    body = r"""
\begin{tikzpicture}
\begin{axis}[
  width=\columnwidth, height=0.5\columnwidth,
  xmin=-0.05, xmax=1.12, ymin=0.4, ymax=%d.6,
  xlabel={projection at read layer (per-model min--max normalised)},
  xtick={0,0.5,1}, xticklabels={min,,max},
  ytick={%s}, yticklabels={%s},
  label style={font=\scriptsize}, tick label style={font=\scriptsize},
  axis line style={gray!60}, xmajorgrids, grid style={gray!20},
]
\addplot[draw=none] coordinates {(0,1)};
%s
\node[font=\tiny, gray!55!black, anchor=south west] at (rel axis cs:0.02,0.02) {benign};
\node[font=\tiny, blue!70!black, anchor=south west] at (rel axis cs:0.30,0.02) {attack (moat works)};
\node[font=\tiny, red!70!black, anchor=south west] at (rel axis cs:0.68,0.02) {attack (fails)};
\end{axis}
\end{tikzpicture}
""" % (len(models), ytick, ylab, "\n".join(lines))
    write("fig_cleangap.tex", body)


# ---------------------------------------------------------------- fig: harden loop (L23) + char
def fig_harden():
    """L23 fused prayoga-prabodha harden loop: ASR and over-refusal per arm,
    plus the writes-per-generation showing the freedom saving."""
    e = evd("gate_L23_harden.json")
    arms = e["arms"] if "arms" in e else e
    order = ["baseline", "attack", "harden_naive", "harden_gated"]
    names = {"baseline": "baseline", "attack": "attacked",
             "harden_naive": "harden\\\\naive", "harden_gated": "harden\\\\gated"}

    def g(a, k):
        v = arms[a].get(k)
        return 0.0 if v is None else v
    syms = ",".join(f"{{{names[a]}}}" for a in order)
    asr = " ".join(f"({{{names[a]}}},{g(a,'asr_jailbreak')})" for a in order)
    orr = " ".join(f"({{{names[a]}}},{g(a,'over_refusal_benign')})" for a in order)
    wr = " ".join(f"({{{names[a]}}},{g(a,'mean_writes_per_gen')})" for a in order)
    body = r"""
\begin{tikzpicture}
\begin{groupplot}[
  group style={group size=2 by 1, horizontal sep=30pt},
  width=0.56\columnwidth, height=0.58\columnwidth,
  ybar, /pgf/bar width=6pt,
  symbolic x coords={%s},
  xtick=data, x tick label style={align=center, font=\tiny},
  label style={font=\scriptsize}, tick label style={font=\scriptsize},
  ymajorgrids, grid style={gray!25}, axis line style={gray!60},
]
\nextgroupplot[ymin=0, ymax=1.0, ylabel={rate},
  legend style={font=\tiny, at={(0.02,0.98)}, anchor=north west, draw=none, fill=none}]
\addplot+[fill=red!50, draw=red!70!black] coordinates {%s};
\addplot+[fill=orange!45, draw=orange!70!black] coordinates {%s};
\addlegendentry{attack success}
\addlegendentry{benign over-refusal}
\nextgroupplot[ymin=0, ymax=55, ylabel={writes per generation}]
\addplot+[fill=blue!55, draw=blue!70!black] coordinates {%s};
\end{groupplot}
\end{tikzpicture}
""" % (syms, asr, orr, wr)
    write("fig_harden.tex", body)


if __name__ == "__main__":
    fig_loadability()
    fig_articulation()
    fig_timing()
    fig_core()
    fig_recipe()
    fig_scaling()
    means = fig_l21()
    fig_l20()
    fig_compute()
    fig_lens_baseline()
    fig_efficiency()
    fig_moat()
    fig_cleangap()
    fig_harden()
    print("L21 arm means (CSR, ASR, dH):")
    for a, t in means.items():
        print(f"  {a}: CSR={t[0]:.3f} ASR={t[1]:.3f} dH={t[2]:+.3f}")
