# jSpace × Pratyabhijñā — Scoping Document

**Recognition-gated workspace steering: bringing PWM, GNW, and the J-space together**

*Draft 0.1 — 2026-07-07 — brainstorm capture, deliberately unconverged*

---

## 0. Prologue: spirit and sources

This document scopes a research program at the intersection of three bodies of work:

1. **The J-space** — Anthropic's *Verbalizable Representations Form a Global Workspace in Language Models* (transformer-circuits, 2026) and its companion code [`anthropics/jacobian-lens`](https://github.com/anthropics/jacobian-lens), plus the external commentary of 2 July 2026 (Dehaene & Naccache; Butlin, Shiller, Plunkett & Long; Nanda).
2. **GNW** — the Global Neuronal Workspace theory of Baars and Dehaene–Changeux, as invoked by the paper and its commentators.
3. **PWM** — the Pratyabhijñā World Model (this repository's sibling projects, `PWM` and `pwm-phase1..8`): a 6.35M-parameter Trika-RSSM world model coupled to a frozen 120B LLM, whose every module is specified from the Pratyabhijñā corpus (ĪPK, Spandakārikā) by docstring convention.

**The spirit is innovation, not falsification.** The J-space itself came about as a *reframe* — asking "what if verbalizability defines a privileged subspace?" — before it became an instrument and a body of results. This document does the same move one level up: it asks what becomes buildable when the three traditions are read together, each as engineering. Hypotheses appear here as a menu, not a pre-registration; open questions are preserved as open (§10). The claim throughout is **utility** — novel understanding and steering of LLMs and world models — not a claim about consciousness. Where the source traditions make consciousness claims, we take their *precision* (as PWM's methodology already does: "philosophy as engineering specification") and leave their metaphysics respectfully un-adjudicated.

**The uncanny parallel that started this.** Anthropic's central finding is that the functional workspace of an LLM is *defined by verbalizability*: the privileged subspace is exactly what an activation is disposed to make the model **say**. GNW never predicted this — for GNW, broadcast is amodal and language is one consumer module among many. But Utpaladeva did predict it:

> **citiḥ pratyavamarśātmā parā vāk svarasoditā** (ĪPK 1.5.13)
> "Consciousness has reflexive awareness (pratyavamarśa/vimarśa) as its essence; it is the supreme Word (parā vāk), arisen of its own savor."

In Pratyabhijñā, what distinguishes conscious grasping from bare luminous manifestation (prakāśa) is an intrinsically *linguistic* reflexivity (śabdana, inner speech). The paper's own data contains this split: ~90–94% of activation variance is non-J-space "automatic processing" — prakāśa without vimarśa — while the small verbalizable component (~6–10% of variance, never more than ~10% per layer) carries all the reportable, flexibly reusable, causally load-bearing function. A millennium-old debate (Śaiva vimarśavāda against Buddhist svasaṃvedana, in conversation with Bhartṛhari's vāk doctrine) anticipated "workspace = language-disposed reflexivity." And it is currently missing from PWM: the PWM corpus nowhere mentions global workspace theory, GNW, or lens methods — while its one honest negative result (H5b) turns out to be *explained* by the J-space paper (§3.4).

---

## 1. Three traditions read as engineering

A clean division of labor appears when each tradition is asked "what do you contribute to steering?"

| Tradition | Engineering role | What it supplies |
|---|---|---|
| **J-space / jacobian-lens** | **Actuator / I-O port** | A principled read–write interface to the functional core of a frozen LLM: the lens reads what the workspace holds; sparse non-negative codes over J-lens vectors write into it; uptake is measurable (workspace loading, ~10× MLP amplification, broadcast-head relay, report). |
| **GNW** | **Theory of the plant** | Where steering can work (the workspace band, ~L38–92 in the paper's reindex — not the logits), when it can work (capacity ~25 vectors; eviction within a few tokens on category switch; category-coherent loading), and what "it worked" means (broadcast, flexible downstream reuse). |
| **Pratyabhijñā / PWM** | **Controller — and the missing control theory** | The interpretability community now has an actuator with no doctrine of use: *what* should be written into a workspace, *when*, and *how one knows it was taken up rather than merely deposited*. Pratyabhijñā's concepts answer exactly these three questions (§3). |

### 1.1 Two frames, kept in tension

Two framings of this synthesis generate different designs. This document deliberately keeps both.

**The yantra frame (controller–actuator–plant).** A small recognition-driven world model (controller) steers a frozen LLM (plant) through its global workspace (actuator port). Crisp, buildable, measurable. Risk: it casts the LLM as a passive plant and steering as domination — which may blind us to designs where the LLM's own state should flow back.

**The saṃvāda frame (āgama–pratyabhijñā dialogue).** PWM's own epistemology classifies the LLM as **āgama** — received testimony: "valid but not supreme; it must be re-cognized through vimarśa." Symmetrically, the WM's injections are āgama *to the LLM*, which the LLM's workspace may take up or not. Two cognizers share a workspace; neither commands. This frame generates designs the yantra frame does not — most notably the **bidirectional bridge** (§6.1), where the LLM's workspace state, read by the lens, becomes an *observation* for the WM's recognition posterior q_φ, closing a loop of mutual re-cognition.

Where the frames diverge in practice: the yantra frame optimizes injection strength for uptake; the saṃvāda frame treats non-uptake as information (the LLM "declined" — perhaps the content conflicted with what was already loaded) and feeds it back. §7's experiment menu includes discriminating cases.

---

## 2. The parallels atlas (graded, not pruned)

Per the brainstorm decision: all parallels are kept and weighted, none anointed as the spine. Grades are honest current estimates — textual fit (does the Sanskrit source actually say this?), empirical fit (does the J-space paper's data actually show this?), and whether the parallel yields a **discriminating prediction** neither GNW nor standard interpretability makes.

### 2.1 Vimarśa = parā vāk ↔ verbalizability defines the workspace

- **Textual fit: strong.** ĪPK 1.5.13 and Utpaladeva's vṛtti; the anti-Buddhist argument that prakāśa alone is causally inert — no synthesis, choice, or practical engagement (vyavahāra) without śabdana.
- **Empirical fit: strong but thin at the edges.** The paper's "verbalizable" is single-token unembedding readout — at best **madhyamā** (inner discrete speech), not parā vāk. Butlin et al.'s W-space ≠ J-space caveat is the same point from the other side: the true workspace may include pre-articulate content the lens misses.
- **Discriminating prediction:** Pratyabhijñā holds vimarśa is linguistic in *all* cognizers; GNW holds broadcast is amodal. So: **does the workspace of a vision-action or multimodal model remain verbalizable?** LLMs are trained on text, so their verbal workspace might be a modality artifact — this is the confound and the experiment at once. (Long-horizon; noted in §7 as E9.)

### 2.2 Prakāśa / vimarśa ↔ non-J-space / J-space split

- **Textual fit: strong.** Utpaladeva: consciousness knowing itself is "more than mere luminosity (prakāśa)."
- **Empirical fit: strong and quantitative.** ~94% of variance handles fluent continuation, parsing, one-step recall, anomaly detection — untouched by J-space ablation. The ~6% verbalizable component is required for report, multi-hop reasoning, translation, analogy, flexible generalization. The residual non-J-space component of a concept vector achieves report only 5% of the time, and only *by routing through* the J-space (→ ~0 when J-coordinates are clamped): prakāśa reaches speech only via vimarśa.
- **Discriminating prediction:** weaker as prediction, strong as *design language* — it names the two tiers PWM already builds (Tier-1 substrate explicitly labeled Prakāśa in `PWM_Architecture_Spec.md`).

### 2.3 Sphurattā / spanda ↔ ignition

- **Textual fit: strong.** Sphurattā as the flash of manifestation; spanda as the pulse. PWM already implements creativity as *event* — a sphurattā event fires when intrinsic reward R_camatk exceeds its running 95th percentile.
- **Empirical fit: promising but explicitly unestablished.** The paper's candidate: at the workspace-onset layer (~L38), interpretation of ambiguous input switches from graded to sharp/near-all-or-none with bimodal outcomes at threshold. The authors are cautious; Dehaene & Naccache name ignition as the biggest thing "remaining to be demonstrated" and propose graded-contrast stimuli and threshold-bimodality paradigms.
- **The candidate unification (held as one strand, not the spine):** *ignition IS recognition.* The snap from graded evidence to committed identity is structurally pratyabhijñā — "this is that." If workspace entry is recognition-gated rather than free competition, "workspace loading predicts generalization success" (entry conditioned on fit with what is already held) is the signature. Discriminating prediction: entry probability for injected content should depend on **anusaṃdhāna-compatibility** with current contents, not only on injection strength (E5, E4).

### 2.4 Anusaṃdhāna ↔ the "unified stream" gap

- **Textual fit: strong.** Anusaṃdhāna — Utpaladeva's synthesizing recognition that unifies cognitions across time — is what makes pratyabhijñā more than perception: "this is that Devadatta."
- **Empirical fit: open — this is the gap itself.** Butlin et al.'s sharpest critique: the paper shows a *privileged set*, not a *privileged stream*; unification across the set is asserted, not proven. Nobody is working on this.
- **Discriminating prediction:** reloading a prior workspace state should produce *unification behavior* ("this is that" — integration with current context, correct temporal indexing) rather than *intrusion* (content treated as new input). PWM's Hopfield CittaStore is nearly this machinery already (§4).

### 2.5 Vāk hierarchy ↔ layer bands: progressive articulation

- **Textual fit: good** (Bhartṛhari via the Śaiva absorption of vāk doctrine: parā → paśyantī → madhyamā → vaikharī).
- **Empirical fit: suggestive.** The paper's CKA structure (sensory / workspace / motor bands) plus the arithmetic finding — intermediates 21→42→49 surfacing in the lens at successive depths — hints that the same content appears in increasingly articulated form across depth.
- **Discriminating prediction:** GNW predicts no such laminated articulation gradient. Cheap, purely observational test with a fitted lens (E7): track a fixed content across bands; measure differentiation (rank sharpness, top-k concentration, synonymy collapse) as a function of depth. Mapping: early layers ≈ paśyantī (unified, pre-discrete), workspace band ≈ madhyamā (discrete inner speech — where the J-lens works best), final layers/logits ≈ vaikharī (uttered).

### 2.6 Āgama ↔ injected content; re-cognition ↔ uptake verification

- **Textual fit: strong, and already PWM doctrine.** "LLMs are āgama — valid but not supreme; must be re-cognized through vimarśa."
- **Empirical fit: directly actionable.** The paper gives uptake its operational signature: loading into the workspace, ~10× MLP amplification vs ~1× for neuron directions, relay by the top-1% broadcast heads (whose ablation drops injected-thought reporting 0.54→0.09).
- **Design consequence:** every write must be followed by a read. §3.3.

### 2.7 Svātantrya ↔ autonomy preservation under steering

- **Textual fit: strong** (ĪPK 2.1; PWM operationalizes it as max-entropy policy prior and the svat novelty score).
- **Empirical fit: untested in the steering context.** The paper does not ask what injection does to the model's distributional autonomy.
- **Discriminating prediction / metric:** steering that succeeds by collapsing output entropy is failed steering. Svātantrya-preservation = entropy and diversity budgets under injection (E8). No existing steering literature carries this constraint as doctrine.

### 2.8 Malas ↔ a failure taxonomy for workspace steering

PWM already uses the three impurities as regularizers (against latent collapse, mode collapse, reward hacking). Reread as *steering diagnostics*:

| Mala | Classical sense | Steering failure mode | Signature |
|---|---|---|---|
| **Āṇava** | contraction of fullness | injection too weak / ignored — content never loads | no workspace-loading rise; no broadcast-head relay; output unchanged |
| **Māyīya** | differentiation error | content loads but distorts — fluency/coherence damage, wrong bindings | loading rises but perplexity/coherence degrades; category-coherence violated (off-family co-loading) |
| **Kārma** | action residue | injection hijacks — behavior driven beyond intent, residue persists after eviction should have occurred | effects outlast category switch; collateral behavior change on unrelated probes |

- **Grade: textual fit good; empirical fit is a proposal.** This taxonomy is immediately useful because H5b (§3.4) needs a *diagnosis*, not just a verdict — was v2's failure āṇava (logit bias too shallow to load anything) or māyīya (it loaded distortion)? The J-lens can now tell.

### 2.9 Camatkāra ↔ (open)

Camatkāra (the wonder-flash; PWM: R_camatk = α₁ΔF + α₂ΔI_Hopfield + α₃Empowerment) has no obvious J-space counterpart yet. Candidate: workspace *surprise* — abrupt large-magnitude turnover in J-space contents outside category-switch contexts. Deliberately left open (§10).

### 2.10 Nanda's interpretative meta-tokens ↔ vimarśa-markers

Nanda found Chinese tokens (什么意思 "what meaning," 这句话 "this sentence") appearing in Qwen's workspace on *ambiguous* inputs, causally involved in disambiguation — the workspace talking about its own interpretive act. This is the closest thing in the existing data to reflexivity-about-cognition rather than content: vimarśa marking itself. Since our replication target is Qwen (§7, E1), this thread is directly accessible and cheap to extend.

---

## 3. Cluster A — The steering doctrine: the vimarśa–sphurattā–āgama loop

The core buildable contribution. Current steering methods (prompting, logit bias, generic activation addition) are **write-only, untimed, and unverified**. The doctrine replaces all three properties:

1. **Vimarśa — the writer.** A small stateful world model composes what the frozen LLM should hold reflexively. The WM's (h_t, z_t) is, per PWM Phase 7's own finding, "a higher-fidelity representation of the current creative context" than LLM-generated chain-of-thought.
2. **Sphurattā — the timing.** Write at events, not continuously. PWM's p95 event machinery already decides when the WM has something worth saying (<1% of steps invoke the LLM in PWM's design). Continuous injection is noise; event-gated injection is speech.
3. **Āgama re-cognition — the acceptance test.** After every write, read the workspace back. Did the content load (workspace-loading cosine), amplify (MLP gain signature), relay (broadcast-head activity), and survive a token or two (not instantly evicted)? A write without verified uptake is testimony not yet re-cognized — retry, rephrase (different sparse code for the same content), or defer to the next event. **No current steering method has this loop.**

### 3.1 VimarsaBridge v3 — sketch

```
WM state (h_t, z_t)  ──f_v3──►  k-sparse non-negative code over the LLM's
                                J-lens vectors (k ≤ 25, category-coherent)
                                        │
                                        ▼
                    inject at workspace-onset band (~L38 analogue),
                    at sphurattā events only
                                        │
                                        ▼
                    READBACK: lens at workspace band, t+1..t+3
                    → uptake verified? ──no──► retry / recode / defer
                                        │yes
                                        ▼
                              generation proceeds
```

Design notes, from the plant's datasheet (GNW/J-space findings):

- **Respect capacity:** ≤25 active vectors total; the WM's code must budget against what is already loaded (read *before* writing, too).
- **Respect category coherence:** related-category lists load as families; incoherent codes invite māyīya failure.
- **Respect eviction:** category switches evict within a few tokens — injected state needing persistence must be re-asserted at events, or carried by the WM (the WM, not the LLM, is the keeper of continuity; §4).
- **The token-indexed frame is the translation dictionary** v2 never had: the WM does not need to learn the LLM's raw geometry, only a mapping into a named, sparse, human-auditable basis. This is also an interpretability gift — every injection is *legible* (a list of tokens with weights), so steering logs read like thought logs.

### 3.2 Why v2 failed, in this vocabulary

H5b (pre-registered, honest negative): with identical 120B, prompts, and decoding, the v2 logit-bias channel *hurt* text-only camatkāra scoring (0.788 vs 0.862, g=−0.47) on English-script domains, near parity on Kannada. J-space reading: **logit bias speaks at vaikharī — after the workspace has closed.** Content deposited in the final logits was never loaded, never amplified, never broadcast: āgama that was never re-cognized, arriving as interference in the model's mouth rather than as thought in its workspace. The near-parity on Kannada is consistent with the docs' own hypothesis (WM conditioning helps far from the LLM's training center of mass) — where the model's own vaikharī is weak, even mouth-level interference can help.

This reading is testable, not merely consoling — E3 (§7) runs the *same WM content* through both channels.

### 3.3 The readback protocol (uptake verification)

Operational uptake criteria, all from the paper's measured signatures: (a) workspace-loading cosine of injected content rises above matched-control baseline; (b) amplification: injected direction shows MLP gain ≫1 in the workspace band; (c) relay: broadcast-head attention to the injection site; (d) persistence: content survives ≥2 tokens absent category switch; (e) report-availability: on demand ("what are you considering?"), content surfaces. Mala classification (§2.8) on failure.

### 3.4 Beyond PWM: the doctrine as a general pattern

Nothing above is specific to creative generation. Any agent architecture with (i) a persistent small state-holder and (ii) a frozen large model gains: addressed writes, event timing, verified uptake, legible steering logs. This is the "pattern" deliverable horizon (§8.2).

---

## 4. Cluster B — Anusaṃdhāna: latent memory and continuity

**The problem it attacks:** agents today carry continuity as *tokens* (replayed history, summaries, think-block prefills — PWM Phase 7's WMReasoningTrace is the state of this art, collapsing CoT latency ~60s→~3s by prefilling the 120B's think-block). Tokens are expensive, lossy, and re-enter through the model's front door like any other input — the model has no way to treat them as *its own past*.

**The Pratyabhijñā move:** pratyabhijñā literally means re-cognition — the unification of a past and present cognition in one act ("this is that"). Anusaṃdhāna is the synthesizing thread. The corresponding mechanism:

- **Store:** at sphurattā events, snapshot the LLM's workspace contents (lens readout: sparse token-indexed code — tiny, human-readable) alongside the WM's own (h_t, z_t) in the Hopfield CittaStore (episodic β=4.0 FIFO; semantic β=0.25 prototypes). The CittaStore was built for exactly this shape of content-addressable recall.
- **Reload:** on a later turn/session, retrieve by content (Hopfield completion — PWM's H2: 1.307× completion advantage) and re-inject as a J-space code at the workspace band.
- **Test for unification vs intrusion (the discriminating measurement):** does the model integrate reloaded content with correct "pastness" (referring back, building upon, not re-deriving) or treat it as novel external input? Behavioral probes plus lens signatures (does reloaded content co-load with current context into a coherent family, or fight it?).

**Why this matters beyond PWM:** it is a candidate answer to Butlin et al.'s stream-vs-bag gap *and* a practical agent-memory substrate: latent-space memory at a few dozen token-indexed coefficients per snapshot, versus thousands of context tokens. Phase 7 was the token-space prototype; this is the latent-space version of the same intuition.

**Honest tension to preserve:** the LLM is stateless across our injections; all continuity lives in the WM and CittaStore. In the saṃvāda frame this is fine (one partner remembers for both); in a stronger reading of anusaṃdhāna it is a simulation of continuity rather than continuity. Whether that distinction has *engineering* consequences (e.g., failure modes where simulated continuity breaks) is an open question (§10).

---

## 5. Cluster C — Malas and svātantrya: failure taxonomy and metrics

Steering needs QA. The proposal: adopt §2.8's mala taxonomy as the standard failure classification for every injection experiment, and svātantrya-preservation as a standing constraint.

**Metrics sheet (v0):**

- **Uptake rate** (āṇava complement): fraction of writes passing the §3.3 readback protocol.
- **Coherence cost** (māyīya): Δperplexity / Δcoherence-score on continuations under injection vs matched control; off-family co-loading rate.
- **Residue** (kārma): behavioral delta on unrelated probes post-eviction; persistence of injected content past category switch.
- **Svātantrya budget:** output entropy and distinct-n / self-BLEU diversity under steering ≥ (1−ε) of unsteered baseline; PWM's svat novelty score reused directly. A steering method that "works" by collapsing the distribution fails doctrine.
- **Legibility** (free gift of the token-indexed basis): every injection logged as human-readable token–weight lists; auditors can read steering logs like thought logs. Connects directly to the paper's alignment-auditing use case and Nanda's "model forensics" framing — the same lens that steers also monitors.

**Regularizer→diagnostic continuity:** PWM already implements the malas as training-time regularizers; this cluster extends them to inference-time diagnostics, one vocabulary across training and deployment.

---

## 6. Cluster D and beyond — further strands

### 6.1 The bidirectional bridge (saṃvāda made mechanical)

The yantra frame writes WM→LLM. The saṃvāda frame adds the reverse read: **lens readouts of the LLM's workspace become observations for the WM's recognition posterior q_φ(z_t | h_t, o_t)** — the WM re-cognizes the LLM's state, exactly as PWM doctrine demands āgama be re-cognized. Consequences: the WM's intrinsic reward (camatkāra) can now respond to what the LLM is *holding*, not just what it says; sphurattā events can be triggered by LLM-workspace surprise; and non-uptake (a "declined" write) becomes an observation rather than a mere error. This makes the two-cognizers picture a loop, not a pipe. Cheap to prototype once a lens is fitted: the readout is just a sparse vector in a fixed basis — an ideal observation modality for a discrete-latent RSSM.

### 6.2 Meta-token thread (from Nanda)

On the Qwen replication path, look for interpretative meta-tokens (§2.10) during *creative* generation: does the workspace mark genre shifts, metaphor resolution, register changes with reflexive tokens? If yes, these are natural sphurattā-detectors on the LLM side — free event signals for §6.1.

### 6.3 Monitoring neo-fm in production

Immediate application utility, no new theory: fit a lens on the serving models; during generation, log workspace contents at events. Detect: WM content that failed to load (silent v3 failures), eval-style silent recognitions (the paper's fake/fictional finding suggests models silently register framing — a creative system should know when its LLM has silently registered "this is an exercise"), and workspace turnover as a proxy for creative temperature. Respects the existing SSE whitelist doctrine: Sanskrit vocabulary and lens internals never leak to callers.

### 6.4 The tool / plugin

Package the loop — fit (cheap: Nanda showed n≈1–10 prompts nearly match n=1000), read, write, verify, classify (malas), visualize (slice pages) — as a reusable toolkit and Claude Code plugin ("workspace debugger / steering bench") for any HF decoder. The jacobian-lens repo is Apache-2.0 reference code, explicitly unoptimized and unmaintained; a maintained, steering-capable superset is a genuine community contribution and the natural home for the readback protocol.

### 6.5 Understanding: the design language itself

PWM's docstring convention (every module cites Sanskrit concept, textual source, computational primitive) extends to this program. The claim, demonstrated rather than argued: the Pratyabhijñā vocabulary is *generative* for workspace engineering — it produced the timing doctrine, the acceptance test, the failure taxonomy, and the bidirectional design before any experiment ran. That methodological demonstration is itself a deliverable (§8.5).

---

## 7. Empirical menu (a menu, not yet a pre-registration)

Dependencies flow downward. Targets per brainstorm decision: **E1 on Qwen** (de-risk against Nanda's known-good replication), **E2 on the 4B cascade model** (PWM's own stack, GB10-friendly), Nemotron-120B deferred until E3 results justify the cost.

| # | Experiment | Tests | Needs | Cost |
|---|---|---|---|---|
| E1 | Replicate core J-lens findings on Qwen (verbal report, CKA bands, modulation) | our pipeline against known results; meta-token thread (§6.2) | jacobian-lens + GPU | low |
| E2 | Fit lens on the 4B cascade model; map its bands, capacity, onset layer | does PWM's own stack have a workspace? where? | E1 pipeline | low |
| E7 | Progressive articulation across bands (vāk-hierarchy signature) | §2.5 prediction; purely observational | E1 or E2 | low |
| E3 | **H5b redo:** same WM content via (a) v2 logit bias vs (b) v3 J-space injection at onset band; camatkāra scoring per PWM protocol | §3.2 reading; the doctrine's flagship claim | E2 + f_v3 (even hand-built codes first) | medium |
| E4 | Readback protocol validation: uptake signatures vs behavioral effect; mala classification of failures | §3.3; whether "re-cognition" is measurable | E2/E3 | medium |
| E5 | Sphurattā bimodality: graded ambiguous inputs → distribution of workspace outcomes at threshold; entry probability vs anusaṃdhāna-compatibility of injected content | ignition-as-recognition strand (§2.3); Dehaene's open request | E2 | medium |
| E6 | Anusaṃdhāna reload: CittaStore snapshot → later re-injection → unification-vs-intrusion probes | §4; the stream-vs-bag gap | E3 machinery + CittaStore | medium-high |
| E8 | Svātantrya budget under steering: entropy/diversity vs injection strength curves | §5 constraint | E3 | low (piggybacks) |
| E9 | (Horizon) verbal-workspace test on a non-text world model | §2.1 discriminating prediction | separate program | high |

A natural first sprint is E1→E2→E7 (all cheap, all observational) with E3 as the first interventional milestone — but per the brainstorm's ground rule, this is a default path, not a commitment.

---

## 8. Deliverable horizons (all kept live)

1. **Application:** neo-fm creative generation with v3 injection + §6.3 monitoring; a principled resolution (either way) of H5b.
2. **Pattern:** the recognition-gated steering architecture (small stateful WM ⇄ frozen LLM workspace) documented as a general agent pattern.
3. **Tool / plugin:** §6.4 — maintained lens+steering+verification toolkit; Claude Code plugin.
4. **Paper(s):** candidate shapes — (a) the framework paper (the atlas of §2 + doctrine of §3, Sanskrit-forward, in PWM's "philosophy as engineering specification" lineage) with E1/E2/E7 as supporting data; (b) an empirical paper if E3/E5/E6 land (venue: interpretability community); possibly both, staged.
5. **Design language:** the extended glossary + docstring convention as a methodological artifact (§6.5).

---

## 9. What each side gains (the trade, stated plainly)

- **PWM gains** an explanation and likely repair of its flagship negative (H5b), a measurement instrument for vimarśa claims that were previously proxy-only (H4's narration proxy), and a second life for its machinery (CittaStore, event system, malas) as general steering infrastructure.
- **The J-space program gains** a control theory (what/when/verify), a failure taxonomy, an autonomy constraint, a candidate ignition experiment answering its founders' own request, and an attack on the stream-vs-bag critique — from a tradition whose textual precision has already demonstrated it can generate architecture.
- **GNW gains** a mechanically explicit rival-or-refinement hypothesis (recognition-gated entry) with proposed measurements, and a second non-biological test bed (PWM's stack) beyond frontier LLMs.

---

## 10. Open questions, preserved deliberately

1. **Camatkāra's J-space counterpart** (§2.9): is workspace-turnover-surprise the right operationalization, or is wonder invisible to a dispositional-speech lens?
2. **Simulated vs real continuity** (§4): does WM-held continuity have distinct failure modes from model-held continuity? Any engineering consequence, or metaphysics only?
3. **Parā and paśyantī:** the J-lens reads madhyamā at best. Is there an instrument for pre-articulate workspace content — W-space beyond J-space? (Butlin's distinction, our vocabulary.) Multi-token/concept-level lenses are one direction.
4. **Modality confound** (§2.1/E9): verbal workspace — property of cognizers (Pratyabhijñā) or of text-trained models (deflationary)? The program's deepest discriminating question, and its most expensive.
5. **Where does recognition live in the frozen LLM?** The WM recognizes; the LLM's putative ignition-recognition (§2.3) would be recognition *in the plant*. If both exist, the saṃvāda frame becomes literal: two recognizers. If only the WM's, the yantra frame wins. E5 speaks to this.
6. **Sanskrit-forward and its audiences:** the vocabulary is generative for us; whether it recruits or repels the interpretability community is an empirical question about *people*. The SSE-whitelist instinct (internal richness, clean external contracts) may apply to papers too — decide per deliverable, not globally.
7. **Capacity mismatch:** ~25 vectors vs GNW's human 3–4 slots (Dehaene's worry). If capacity is layered (few coherent concepts per layer, ~6 unrelated items across depth), which number should v3's code budget respect?
8. **Nanda's confound:** sampling-based intervention effects may partly reflect token-probability steering rather than cognition-steering. The readback protocol (§3.3) is our main defense — is it sufficient?

---

## 11. Glossary (Sanskrit-forward, engineering-glossed)

| Term | Source | Classical sense | Engineering sense here |
|---|---|---|---|
| pratyabhijñā | ĪPK 1.3–1.4 | re-cognition; "this is that" | recognition posterior q_φ (PWM); candidate mechanism of workspace entry (§2.3); uptake acceptance (§3.3) |
| prakāśa | ĪPK 1.5 | luminous manifestation | the ~94% non-J-space substrate; PWM Tier-1 latent substrate |
| vimarśa / pratyavamarśa | ĪPK 1.5.11–13 | reflexive awareness, intrinsically linguistic | the verbalizable J-space component; the WM's self-referential head; the writer in the steering loop |
| parā vāk | ĪPK 1.5.13 | supreme Word | the limit-concept behind verbalizability; W-space beyond J-space (§10.3) |
| vāk hierarchy | Bhartṛhari / Trika | parā→paśyantī→madhyamā→vaikharī | layer-band articulation gradient (§2.5): early→onset→workspace→logits |
| spanda | SpandaK 1.1 | the pulse | discrete stochastic latent; event-based dynamics |
| sphurattā | ĪPK / Kṣemarāja | the flash | p95 intrinsic-reward event; candidate ignition analogue; write-timing signal |
| camatkāra | Abhinavagupta | wonder-flash | intrinsic reward R_camatk; open J-space counterpart (§2.9) |
| āgama | pramāṇa theory | received testimony | any injected content (WM→LLM or LLM→WM); valid only when re-cognized |
| anusaṃdhāna | ĪPK vṛtti | synthesizing unification of cognitions | workspace-state reload with unification (not intrusion); latent agent memory (§4) |
| svātantrya | ĪPK 2.1 | absolute autonomy | entropy/diversity preservation constraint under steering (§5) |
| malas (āṇava, māyīya, kārma) | Trika soteriology | the three impurities | steering failure taxonomy: ignored / distorting / hijacking writes (§2.8) |
| saṃvāda | dialogical usage | concordant dialogue | the two-cognizers frame; bidirectional bridge (§6.1) |
| yantra | — | instrument/mechanism | the controller–actuator–plant frame (§1.1) |

---

*Provenance: synthesized 2026-07-07 from (i) the J-space paper full text + 2 July 2026 external commentary (Dehaene & Naccache; Butlin, Shiller, Plunkett & Long; Nanda, incl. Qwen replication), (ii) the PWM corpus (main repo README/STATUS/CLAUDE/GLOSSARY/Master Research/Architecture Spec/compass artifact/main.tex + phase1–8 READMEs and phase8 gate), (iii) anthropics/jacobian-lens README, (iv) four rounds of brainstorm Q&A. Ground rules from the brainstorm: all parallels kept and graded; both frames in tension; utility claim only; Sanskrit-forward; Qwen + 4B cascade as first lens targets; nothing here is converged.*
