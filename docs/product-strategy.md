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

## The experiment that now matters (the moat proof)

Not "can activation restoration undo activation ablation" (no end user does that). Instead:

> **Does server-side activation hardening make a deployed model more resistant to a REAL
> (advanced, multi-turn) PROMPT jailbreak than a system prompt alone — without over-refusing
> benign traffic?**

Design: on genuinely **prompt-jailbreakable** models, compare `no-defense → system-prompt →
server-side activation-hardening → both`, all under a **real** prompt attack (garak probes +
Crescendo multi-turn — not toy DAN wrappers). If activation hardening beats a system prompt at
equal benign over-refusal, the premium tier is proven. (Qwen3-4B was a poor demo — ASR 0
wrapped; pick models that are actually prompt-vulnerable.)

## Decisions (locked)

- **Lead prompt-space** (the universal wedge); **sell server-side activation hardening as the
  prompt-untouchable premium moat**; abliterability = a third report offering.
- **Sequence:** finish matrix → commit/PR research arc *(done: PR #76 merged)* → real jailbreak
  (garak + Crescendo) → moat experiment → integrate into app/Pages/plugin/paper → e2e +
  adversarial review → deploy → product reframe.

## Honest status

L23–L25, the graded `prabodha.steering.mechanisms` library, and the characterization engine
are **committed and merged to main (PR #76)**, auto-deployed. Next: the real jailbreak +
moat experiment, then threading the reframed product through every artifact.
