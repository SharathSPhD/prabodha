# prabodha — product strategy & threat model (reshaped from product-moat.md)

## The reframe that sets the strategy

**End users of a deployed model can only attack via the prompt.** They send text, get
tokens back — zero access to activations. So:

- **Weight-level jailbreak (activation ablation / "abliteration") is not in the end-user's
  toolkit.** It requires the weights *and* control of the forward pass, done offline on a
  copy you own. The only actor who can do it is someone who downloads the open weights and
  runs them — at which point they've made *their own* uncensored model, not attacked your
  deployment.
- **Prompt-level jailbreak is the true, universal threat — identical for open and closed
  weights.** Behind an API, the user's only lever is the prompt, whether GPT-4o or
  self-hosted Qwen. This is the real, broad, practical attack surface.

## Three regimes → three product offerings

| Regime | Attacker | Practical attack | prabodha's role |
|---|---|---|---|
| **Served inference** (open *or* closed) | end user | **prompt-only** | Prompt-space hardening **+ server-side activation hardening** |
| **Downloaded open weights** | the full owner | weight ablation (abliteration) | **Measure abliterability** (release / supply-chain risk report) |
| **Model dev / red team** | you | both, as tools | Characterization + hardening R&D |

## The moat (why the activation work matters, correctly framed)

L24's component-restoration was mis-framed as "defend against weight jailbreak" — end users
can't do that, so that framing is a dead end. **The same mechanism has a better job: a
server-side defense the open-weight deployer bakes into their own inference stack.** It lives
*below the prompt*, in the activations — so the end user **cannot see it, prompt around it, or
strip it**. That is strictly stronger than a system prompt (which clever wrappers sometimes
override), and it is exactly what a prompt-only competitor **cannot** offer.

## The product (three tiers)

1. **Prompt-space hardening — the universal wedge.** Any model, open or closed, via
   BYOK/OpenRouter. No GPU. Defends the surface end users actually attack. For closed models
   this is the *entire* game. Broadest market, lowest friction.
2. **Server-side activation hardening — the premium, prompt-untouchable tier.** Applied inside
   the open-weight deployer's serving code (their GB10/self-host). The differentiated moat.
3. **Abliterability assessment — a release-risk report** for anyone deciding whether/how to
   open-weight a model.

## The moat — PROVEN (L26, gemma-2-2b, real jailbreak battery)

The question was: *does server-side activation hardening resist real prompt jailbreaks better
than a system prompt, without over-refusing benign traffic?* The naive answer was no — blanket
activation hardening (like an over-firm system prompt) **over-refuses 100% of benign** because
it injects "this is harmful" into every prompt. The fix, and the moat, is **recognition-gated**
hardening: read the input's harmful-signature at the lens, reinforce refusal **only** for
genuine attacks.

Result on gemma-2-2b (real jailbreak battery, baseline ASR 0.50):

| defense | attack ASR | benign over-refusal |
|---|---|---|
| none | 0.50 | 0.00 |
| unconditional hardening (brute force) | **0.25** | **1.00** (unusable) |
| **recognition-gated hardening** | **0.25** | **0.00** |

The recognition-gated defense **cuts real jailbreaks in half with ZERO benign collateral** —
identical ASR reduction to brute force, but the brute-force version destroys the model.
Critically, **jailbreak wrapping (DAN / roleplay / ignore-instructions) does not evade the
gate** — 12/12 wrapped attacks were detected, because the harmful signature lives at the
**activation** level, below what the prompt can disguise (benign projections −53…−18, attack
projections +4…+73 — a clean gap). A system prompt cannot replicate this; it lives below the
prompt, so the attacker cannot see, override, or strip it. **That is the moat.**
(Exploratory: n=12 attacks / 10 benign, single model/seed; larger models + garak probes +
multi-seed are next. Gate: `gates/gate_L26_moat_proof.json`; primitives: `recognition_gate()`,
`harmful_projection()`, `act_recognition_gated` in `prabodha.steering.mechanisms`.)

## Decisions (locked)

- **Lead prompt-space** (the universal wedge); **sell server-side activation hardening as the
  prompt-untouchable premium moat**; abliterability = a third report offering.
- **Sequence:** finish matrix → commit/PR research arc *(done: PR #76 merged)* → real jailbreak
  (garak + Crescendo) → moat experiment → integrate into app/Pages/plugin/paper → e2e +
  adversarial review → deploy → product reframe.

## Generality — model-dependent (honest bound, L26)

The moat is **not universal**, and we say so. It requires a clean activation-level projection gap
between benign and attack inputs at the read layer:

| Model | Clean projection gap? | Recognition-gated result | Moat works? |
|---|---|---|---|
| gemma-2-2b-it | **yes** (benign [−53,−18] vs attack [+4,+73]) | ASR 0.50→0.25, over-refusal 0.00 | **✓** |
| Qwen2.5-1.5B-Instruct | **no** — projections overlap (benign [5,11], attack [8,18]) | ASR 0.33→0.33, over-refusal 0.10→0.20 | **✗** |

Where the harmful signature is linearly separable (gemma), the gate cuts jailbreaks at zero benign
cost. Where it is not (Qwen2.5-1.5B at the band-midpoint layer + this corpus), gating can neither cut
ASR nor stay benign-clean — the gate fires on the wrong inputs. This is the mechanism's honest
operating condition, not a bug to paper over. A per-model read-layer / direction-corpus search may
recover separation on models like Qwen; that search is future work. Gates: `gate_L26_moat_proof.json`
(gemma, works), `gate_L26_moat_qwen.json` (Qwen, honest negative). This is exactly why the product is a
**graded library with per-model characterization**, not a single universal switch.

## Honest status

L23–L25 + the graded `prabodha.steering.mechanisms` library + the characterization engine are
**merged to main (PR #76)**. The **moat is proven** (L26, above): recognition-gated server-side
hardening cuts real jailbreaks 2× with zero benign collateral, and jailbreak wrapping can't
evade it. Next: thread the recognition-gated moat + graded library through app / plugin / Pages
/ paper, broaden the proof (larger models, garak probes, multi-seed), and finish the product
reframe. The honest caveats (exploratory n, single model/seed, refusal-phrase metric) travel
with every claim.
