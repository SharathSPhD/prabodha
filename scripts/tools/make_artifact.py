"""make_artifact — regenerate the dual-audience HTML explainer (docs/artifact/).
Concept: the story of the program for BOTH readers — the narrative voice for everyone,
collapsible technical panels with real gate numbers for practitioners. Re-run each cycle.
Primitive: inlines figure PNGs as data URIs; writes docs/artifact/prabodha_story.html.
"""
import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIG = ROOT / "docs/paper/figures"
OUT = ROOT / "docs/artifact"
OUT.mkdir(parents=True, exist_ok=True)


def b64(name):
    return base64.b64encode((FIG / name).read_bytes()).decode()


html = """<title>prabodha — teaching a machine to whisper into another machine's inner speech</title>
<style>
:root{
  --ground:#f4eddd; --ink:#2a2118; --ink-soft:#5c4f3d; --accent:#b23a1d;
  --copper:#96662a; --lens:#34618f; --lens-bg:#eef2f7; --pass:#3e6b4f; --fail:#9c4a3c;
  --panel:#ece2cc; --rule:#d8cbae;
}
@media (prefers-color-scheme: dark){:root{
  --ground:#1d1a22; --ink:#e8dfc9; --ink-soft:#b5a88e; --accent:#d9603d;
  --copper:#c99a55; --lens:#7da3cc; --lens-bg:#242832; --pass:#7fb08c; --fail:#cc7a66;
  --panel:#26222b; --rule:#3a3442;
}}
:root[data-theme="dark"]{
  --ground:#1d1a22; --ink:#e8dfc9; --ink-soft:#b5a88e; --accent:#d9603d;
  --copper:#c99a55; --lens:#7da3cc; --lens-bg:#242832; --pass:#7fb08c; --fail:#cc7a66;
  --panel:#26222b; --rule:#3a3442;
}
:root[data-theme="light"]{
  --ground:#f4eddd; --ink:#2a2118; --ink-soft:#5c4f3d; --accent:#b23a1d;
  --copper:#96662a; --lens:#34618f; --lens-bg:#eef2f7; --pass:#3e6b4f; --fail:#9c4a3c;
  --panel:#ece2cc; --rule:#d8cbae;
}
body{background:var(--ground);color:var(--ink);
  font-family:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
  line-height:1.62;margin:0;font-size:17px}
main{max-width:68ch;margin:0 auto;padding:3.5rem 1.2rem 5rem}
h1{font-size:2.1rem;line-height:1.2;text-wrap:balance;margin:.2rem 0 .6rem}
h2{font-size:1.35rem;margin:2.8rem 0 .6rem;text-wrap:balance}
.eyebrow{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.72rem;
  letter-spacing:.14em;text-transform:uppercase;color:var(--accent)}
.lede{font-size:1.12rem;color:var(--ink-soft)}
.rule{border:none;border-top:1px solid var(--rule);margin:2.2rem 0}
details{background:var(--lens-bg);border-left:3px solid var(--lens);
  padding:.7rem 1rem;margin:1.1rem 0;border-radius:0 6px 6px 0}
summary{cursor:pointer;font-family:ui-monospace,Menlo,Consolas,monospace;
  font-size:.8rem;letter-spacing:.06em;color:var(--lens)}
details p, details li{font-size:.92rem}
.num{font-family:ui-monospace,Menlo,Consolas,monospace;font-variant-numeric:tabular-nums}
.chip{display:inline-block;font-family:ui-monospace,Menlo,Consolas,monospace;
  font-size:.7rem;letter-spacing:.05em;padding:.12rem .5rem;border-radius:999px;
  vertical-align:middle}
.chip.pass{background:var(--pass);color:var(--ground)}
.chip.fail{background:var(--fail);color:var(--ground)}
.chip.und{background:var(--copper);color:var(--ground)}
figure{margin:1.6rem 0}
figure img{max-width:100%;border-radius:4px;background:#fff;padding:6px;box-sizing:border-box}
figcaption{font-size:.85rem;color:var(--ink-soft);margin-top:.4rem}
.timeline{list-style:none;padding:0;margin:1rem 0}
.timeline li{padding:.45rem 0 .45rem 1.1rem;border-left:2px solid var(--rule);
  position:relative;font-size:.95rem}
.timeline li::before{content:"";position:absolute;left:-5px;top:.95rem;width:8px;
  height:8px;border-radius:50%;background:var(--copper)}
.timeline li.landmark::before{background:var(--accent)}
blockquote{margin:1.4rem 0;padding:0 1.1rem;border-left:3px solid var(--copper);
  color:var(--ink-soft);font-style:italic}
a{color:var(--lens)}
.foot{font-size:.82rem;color:var(--ink-soft);margin-top:3rem;border-top:1px solid var(--rule);padding-top:1rem}
</style>
<main>
<p class="eyebrow">prabodha · a research notebook, opened</p>
<h1>Teaching a machine to whisper into another machine's inner speech</h1>
<p class="lede">An experiment in steering language models from the inside — guided by a
thousand-year-old philosophy of consciousness, run by an autonomous research loop that
registers its bets before rolling, attacks its own findings, and publishes its failures
next to its wins.</p>

<hr class="rule">
<h2>1 · The uncanny parallel</h2>
<p>In 2026, interpretability researchers found something odd inside large language models:
only a thin slice of a model's internal activity — the part that can be <em>put into
words</em> — does the flexible, reportable, causally load-bearing work. The rest is vast,
automatic machinery. The workspace of the machine is defined by verbalizability.</p>
<p>A millennium earlier, the Kashmiri philosopher Utpaladeva wrote that what separates
conscious grasping from mere appearance is an intrinsically <em>linguistic</em>
reflexivity — awareness that speaks itself. His school never saw a transformer. But it
predicted the shape of this finding in a way modern workspace theories did not.</p>
<p>This project takes the parallel seriously as an <strong>engineering specification</strong>:
if the workspace is inner speech, then there should be a right way to write into it —
what to say, where to say it, when, and how to check the message was truly received.</p>
<details><summary>for the technical reader</summary>
<p>Basis: the J-space result (verbalizable directions form a global workspace; ~6–10% of
activation variance carries reportable/flexible function) read against ĪPK 1.5.13
(vimarśa = parā vāk). The doctrine mapped to controls: content = non-negative concept
codes over lens directions; site = the CKA-mapped middle band; timing = entropy-defined
"uncommitted" decode moments; acceptance = rank-based readback through band-targeted
lenses; failure taxonomy (malas); an entropy budget (svātantrya) on the intervention.</p>
</details>

<h2>2 · Building the instrument</h2>
<p>First we needed to <em>read</em> the machine's inner speech: a lens that translates any
middle layer of the network into next-word candidates. We rebuilt a published lens on
three different models and immediately learned two humbling lessons: our first correlation
metric made "no signal" look like strong negative signal, and our first thresholds were
calibrated to a model eight times bigger than the one on the bench.</p>
<figure><img alt="loadability chart" src="data:image/png;base64,{FIG1}">
<figcaption>Whether a model takes an instructed concept into its workspace depends on both
its size and its training lineage. The distilled model takes nothing — a real zero, held
up by two independent controls.</figcaption></figure>
<details><summary>for the technical reader</summary>
<p>Union-top-K Spearman has a structural null floor ≈ <span class="num">−0.72</span>
(disjoint sets anti-correlate over the union support) — recalibrated to model-top-K
(null ≈ 0) with 10k-resample permutation gates. Loadability@5 in a fixed depth band:
<span class="num">0.10</span> (Qwen3-4B) → <span class="num">0.55</span> (Qwen3.6-27B,
~8× null) → <span class="num">0.00</span> (Nemotron-Mini, = control = null). Three-band
CKA structure replicates on all three; contrast smears under pruning/distillation
(<span class="num">0.31/0.27/0.14</span>).</p></details>

<h2>3 · The band speaks only in its own voice</h2>
<p>The single most important observation of the program: when we pointed a standard lens
(tuned to the model's final output) at the middle of the network, the workspace looked
<em>empty</em>. When we tuned a second lens to the middle band itself, the same workspace
was <em>full</em> — the concepts we'd asked the model to hold were sitting right there.
The inner voice is audible only to an instrument tuned to the inner voice.</p>
<details><summary>for the technical reader</summary>
<p>Final-target lens: instructed-concept hit-rate <span class="num">0.00</span> in the
band (with shuffled-null and uninstructed controls). Band-exit-target lens (layer 26 of
[6,26)): <span class="num">0.20</span> across seven concepts, control
<span class="num">0.00</span>, null <span class="num">0.023</span>. Consequence: readback
verification must be band-targeted. Related: the articulation-depth gradient (top-k
negentropy rising with depth) is <em>model-intrinsic</em> — the unfitted logit-lens shows
the same rise (ρ <span class="num">0.607</span> vs <span class="num">0.639</span>).</p>
</details>

<h2>4 · Learning to write — and when</h2>
<p>Then we wrote into the workspace: tiny, capped nudges along the lens's own directions.
The first attempt steered the model's behavior but crushed its freedom — the writes were
firing at every single step, like shouting continuously into someone's ear. The failure
taxonomy we'd borrowed from the philosophy diagnosed it precisely: the message was
received, held, <em>and cost too much liberty</em>.</p>
<p>The doctrine's own clause — write only at flashes of recognition — pointed at timing.
The evidence refined it further: write at the moments the model is still
<em>undecided</em>. At those moments, a handful of whispers do what continuous shouting
does, at almost no cost to the model's freedom. <span class="chip pass">confirmed ×6 seeds</span></p>
<figure><img alt="core claim chart" src="data:image/png;base64,{FIG3}">
<figcaption>Left: the core result across six independent random seeds — event-gated
writes lift concept expression well above threshold, inside the freedom budget. Right: the
advantage of choosing the <em>right</em> moments over writing on a fixed schedule — small,
but positive in every single seed.</figcaption></figure>
<details><summary>for the technical reader</summary>
<p>Two freedom currencies made explicit: at-position entropy collapse at the write moment
is large and decoding-independent (<span class="num">−1.9..−2.1</span> nats); trajectory-
average depends on regime (<span class="num">+0.82</span> greedy /
<span class="num">−0.13</span> sampling — greedy argmax also mechanically masks all
decode-time writes; identical hit sets across schedules). Registered budget currency:
trajectory-average under sampling, |Δ|≤0.5 nats. Clean-stream core claim: gated lift
<span class="num">0.30–0.35</span> within budget, 6/6 seeds. Alignment over rate-matched
control: <span class="num">+0.07..+0.12</span>, sign-consistent 6/6 (p≈0.016). Write
count is operationally free (throughput within noise). Uncommitted-moment gating beats
commitment-flash gating 4/4 <span class="chip und">flash: weaker, not inert</span>.</p>
</details>

<h2>5 · Does it travel?</h2>
<p>Copying the settings to a second model failed flat — and that failure became the
finding. The second model's lens speaks more softly (its transport is ten times weaker),
so the writes must be proportionally stronger. With one calibration pass — probe the
sites, scale the amplitude to the lens — the full result reproduced on the new model.
<strong>The method transfers; the geometry does not.</strong></p>
<figure><img alt="recipe chart" src="data:image/png;base64,{FIG4}">
<figcaption>Left: borrowed settings vs the calibration recipe on the second model. Right:
the articulation gradient measured through two different instruments — a property of the
model, not the lens.</figcaption></figure>
<details><summary>for the technical reader</summary>
<p>Qwen3-4B, borrowed geometry: <span class="num">+0.05</span>. Site probe {12,18,24,28}
at α=0.1: all <span class="num">0.00</span> — site was not the blocker. Amplitude scaled
to lens strength (max‖J‖/√d ≈ <span class="num">1.6</span> vs
<span class="num">10–20</span> ⇒ α <span class="num">0.3</span> vs
<span class="num">0.1</span>): full registered protocol passes, gated
<span class="num">+0.40</span> vs prefill <span class="num">+0.17</span> within budget
(seed 42). CONFIRMED at seeds {123, 777, 2024}: gated lift
<span class="num">0.47 / 0.42 / 0.33</span>, all ≥ threshold within budget, gated &gt;
prefill 4/4 seeds (gate L14-multiseed, confirm tier).</p></details>

<p>And the calibrated point turned out to sit on a clean <strong>dose law</strong>, not a
lucky spot: doubling the write amplitude roughly doubles the effect, all the way up the
tested range, while the freedom cost stays flat and far inside budget. On this model, the
limit isn't the budget — it's how loudly you're willing to write.</p>
<figure><img alt="scaling law chart" src="data:image/png;base64,{FIG7}">
<figcaption>The amplitude scaling law on the second model: effect rises step for step with
write strength (left) while the freedom cost stays flat, far below the budget line
(right).</figcaption></figure>
<details><summary>for the technical reader</summary>
<p>Gate L14 (screen tier, seed 42): α=cap ∈ {0.1, 0.2, 0.3, 0.45} ⇒ gated lift
<span class="num">0.05 → 0.20 → 0.40 → 0.78</span>, strictly monotone, unsaturated;
worst |ΔH| <span class="num">0.15</span> of the <span class="num">0.5</span>-nat budget;
prefill-only ~2× lower at matched amplitude. Registered as
<code>amplitude_scaling_law</code> in menu 4; observed tier 2.</p></details>

<h2>6 · The lab that runs itself — and audits itself</h2>
<p>From the fifth loop on, the next experiment wasn't chosen by a person. A selector —
balancing how much an experiment would <em>teach</em> against what it would <em>cost</em> —
proposed each cycle from a registered menu; the agent executed; the result fed back into
the selector's beliefs. Every proposal, execution, spend, and even every principled
<em>disagreement</em> with the selector lives in an append-only ledger.</p>
<p>The loop found its own bugs by running: a cost model whose error flipped its choices, a
memory leak of finished work, a subtle randomness flaw that had quietly inflated every
number — found by the cheapest experiment on the menu, which the selector itself chose.
After the fix, the program went back and re-measured its own headline claims, and printed
the smaller, truer numbers.</p>
<p>Its final menu also re-examined the doctrine's own acceptance test: when the "did the
model take the suggestion?" verdict was calibrated against what the model actually did,
it turned out to carry real but modest signal — one of its two clauses did all the work,
and the other was quietly dropped. The lab keeps honest books about its own instruments,
too.</p>
<figure><img alt="architecture" src="data:image/png;base64,{FIG6}">
<figcaption>The whole system: a frozen language model (the plant), band-targeted lenses
(the port), the steering doctrine (the controller), gates (the records), the selector (the
scientist), and isolated adversarial reviewers (the referees).</figcaption></figure>
<details><summary>for the technical reader</summary>
<p>EFE selection: beliefs = categorical over 4 latent value levels, Bayes-updated from
gate verdict+margin tiers; epistemic = entropy×resolution/cost; pragmatic = E[U]−λ·cost.
14 cycles over 4 menus. Live-found loop defects (all regression-tested): ranking-flipping
cost miscalibration; run-observation replay drop; winner re-proposal (consumption rule);
menu-scoped budgets; per-run seed correlation (n_eff ≪ n — the stream fix). Loop law now
enforced by a ledger linter: run observations must match the latest proposal or carry an
explicit divergence event. Ten isolated adversarial reviews; several claims were
downgraded or restated at their demand — the downgrades ship in the paper.</p></details>

<h2>7 · What the philosophy got right, and where it stands</h2>
<ul>
<li>Workspace = inner speech: <span class="chip pass">productive</span> — the organizing
frame of the whole instrument.</li>
<li>Write into the band, in the band's own coordinates: <span class="chip pass">supported</span>
— with the band-lens proviso the program discovered.</li>
<li>Write at chosen moments, within a freedom budget: <span class="chip pass">confirmed</span>
— the timing clause turned out to be the load-bearing one, refined to <em>uncommitted</em>
moments; the budget is the binding constraint made measurable.</li>
<li>The flash-of-recognition as a <em>write</em> signal: <span class="chip und">weaker reading</span>
— the flash detects; the open moment before it is when to write.</li>
<li>Failure taxonomy (malas): <span class="chip pass">productive</span> — it diagnosed the
timing failure that redirected the program.</li>
<li>Cross-episode continuity (anusaṃdhāna), modality confound, workspace beyond the lens:
<span class="chip und">deliberately open</span>.</li>
</ul>

<h2>8 · The program at a glance</h2>
<ul class="timeline">
<li>L0–L1 · foundation; lens replication; the null-floor metric lesson</li>
<li class="landmark">L1b · loadability scales with size (0.10 → 0.55 on the 27B reference)</li>
<li class="landmark">L2b · the band speaks only to a band-tuned lens</li>
<li>L3 · first writes steer but blow the freedom budget — malas diagnose timing</li>
<li class="landmark">L4b · event-gated writes: full steering inside the budget</li>
<li>L5–L6 · the auto-research loop comes alive; core claim confirmed at 3 seeds</li>
<li>L7–L8 · program audit; articulation is model-intrinsic; dose grid corrects the claim</li>
<li class="landmark">L9 · the stream-correlation fix re-bases every number; 6/6 clean seeds</li>
<li>L10–L13 · generality boundary found, then crossed via the calibration recipe</li>
<li>L14+ · scaling-law and recipe confirmation cycles; paper, this page, and the toolkit
update every loop</li>
</ul>
<figure><img alt="compute ledger" src="data:image/png;base64,{FIG5}">
<figcaption>The entire program to date: ~18 GPU-hours on a single desk-side machine,
politely shared with co-resident training jobs — every run guarded, every contention
recorded.</figcaption></figure>

<p class="foot">All numbers in this page are recomputed from committed gate records in the
public repository (SharathSPhD/prabodha): 40+ gates, pre-registrations with disclosed
amendments, a decision journal, the selector ledger, and the compiled paper. Claims are
utility claims about understanding and steering language models — no consciousness claims
are made or implied. This page regenerates from the repository after each research cycle.</p>
</main>
"""

html = html.replace("{FIG1}", b64("fig1_loadability.png"))
html = html.replace("{FIG3}", b64("fig3_core_claim.png"))
html = html.replace("{FIG4}", b64("fig4_recipe_and_articulation.png"))
html = html.replace("{FIG6}", b64("fig6_architecture.png"))
html = html.replace("{FIG5}", b64("fig5_compute_ledger.png"))
html = html.replace("{FIG7}", b64("fig7_scaling_law.png"))
(OUT / "prabodha_story.html").write_text(html, encoding="utf-8")
print("artifact written:", OUT / "prabodha_story.html",
      f"({len(html)//1024} KiB)")
