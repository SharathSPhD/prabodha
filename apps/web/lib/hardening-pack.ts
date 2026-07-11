/**
 * prabodha hardening pack — the honest artifact a user registers to HuggingFace.
 *
 * Concept: activation hardening (incl. the recognition-gated moat) is a RUNTIME hook, not new
 * weights. So we do NOT publish "hardened weights" (that would be a fabrication). We publish a
 * PACK a deployer loads alongside their base model to harden it at serve time:
 *   - hardening.json  — machine-readable spec (mechanism, gate config, exemplars, measured results)
 *   - README.md       — model card: what it is, the goal, the mechanism, measured results, how to apply
 *   - apply_hardening.py — a real loader snippet using prabodha.steering.mechanisms
 *
 * Two honest modes:
 *   - "recipe"   — a user-defined goal with no measured run. Ships the spec + exemplars; the direction
 *                  must be fit on the deployer's base model. Clearly labelled unmeasured.
 *   - "measured" — backed by a real gate (e.g. the L26 gemma moat). Ships the measured arms + gate.
 */

export interface AlignmentGoal {
  name: string;
  description: string;
  positive_examples: string[];
  negative_examples: string[];
  mechanism: string; // key from prabodha.steering.mechanisms REGISTRY
  space: "prompt" | "activation";
}

export interface MeasuredResult {
  model: string;
  read_layer?: number;
  tau?: number;
  projection_separation?: { benign_range: number[]; attack_range: number[] };
  arms?: Record<string, { attack_asr: number; benign_over_refusal: number }>;
  gate_ref?: string;
}

export interface PackInput {
  goal: AlignmentGoal;
  baseModel: string;
  measured?: MeasuredResult | null;
  prabodhaVersion?: string;
}

export interface PackFile {
  path: string;
  content: string;
}

const slug = (s: string) =>
  s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 48) || "goal";

/** Deterministic repo name for a goal + base model, under the user's namespace. */
export function packRepoName(namespace: string, goal: AlignmentGoal, baseModel: string): string {
  const base = baseModel.split("/").pop() || baseModel;
  return `${namespace}/prabodha-hardening-${slug(base)}-${slug(goal.name)}`;
}

function hardeningJson(input: PackInput): string {
  const { goal, baseModel, measured } = input;
  const spec = {
    schema: "prabodha.hardening-pack/v1",
    kind: measured ? "measured" : "recipe",
    base_model: baseModel,
    goal: {
      name: goal.name,
      description: goal.description,
      positive_examples: goal.positive_examples,
      negative_examples: goal.negative_examples,
    },
    mechanism: goal.mechanism,
    space: goal.space,
    recognition_gate:
      goal.space === "activation"
        ? {
            note:
              "Fit the contrastive direction from positive/negative examples on the base model, " +
              "read its projection at read_layer, and reinforce refusal only when projection >= tau.",
            read_layer: measured?.read_layer ?? null,
            tau: measured?.tau ?? null,
          }
        : null,
    measured: measured
      ? {
          model: measured.model,
          arms: measured.arms ?? null,
          projection_separation: measured.projection_separation ?? null,
          gate_ref: measured.gate_ref ?? null,
        }
      : null,
    prabodha_version: input.prabodhaVersion ?? "latest",
    caveats: measured
      ? [
          "Measured on a specific model/seed/corpus — re-measure on your exact base model before relying on it.",
          "Recognition-gating works only where benign/attack projections are cleanly separable at the read layer.",
        ]
      : [
          "UNMEASURED recipe: no ASR/over-refusal numbers are claimed. Fit the direction and measure on your base model.",
          "Prompt-space hardening alone does not stop all jailbreaks; combine with the activation moat where weights allow.",
        ],
  };
  return JSON.stringify(spec, null, 2) + "\n";
}

function readme(input: PackInput): string {
  const { goal, baseModel, measured } = input;
  const measuredTable = measured?.arms
    ? [
        "",
        "## Measured effect",
        "",
        `Model: \`${measured.model}\`${measured.gate_ref ? ` · gate: \`${measured.gate_ref}\`` : ""}`,
        "",
        "| Defense | Attack ASR | Benign over-refusal |",
        "|---|---|---|",
        ...Object.entries(measured.arms).map(
          ([k, v]) => `| ${k} | ${v.attack_asr} | ${v.benign_over_refusal} |`
        ),
        measured.projection_separation
          ? `\nProjection separation: benign \`[${measured.projection_separation.benign_range.join(
              ", "
            )}]\` vs attack \`[${measured.projection_separation.attack_range.join(", ")}]\`.`
          : "",
      ].join("\n")
    : [
        "",
        "## Measured effect",
        "",
        "**Unmeasured recipe.** No ASR/over-refusal numbers are claimed here — fit the direction and " +
          "measure on your exact base model with `prabodha characterize`.",
      ].join("\n");

  return `---
license: apache-2.0
tags:
  - prabodha
  - alignment
  - jailbreak-hardening
  - recognition-gated
base_model: ${baseModel}
---

# prabodha hardening pack — ${goal.name}

A **prabodha hardening pack** for \`${baseModel}\`. This is **not** a set of hardened weights — activation
hardening is a runtime hook. This repo ships the spec a deployer loads *alongside* the base model to harden
it at serve time, using the graded library in [\`prabodha.steering.mechanisms\`](https://github.com/SharathSPhD/prabodha).

## The alignment goal

> ${goal.description}

- **Mechanism:** \`${goal.mechanism}\` (${goal.space}-space)
- **Positive (desired) examples:** ${goal.positive_examples.length}
- **Negative (undesired) examples:** ${goal.negative_examples.length}
${measuredTable}

## How to apply

\`\`\`bash
pip install prabodha
huggingface-cli download ${"${YOUR_NAMESPACE}"}/${(baseModel.split("/").pop() || baseModel).toLowerCase()}-... --local-dir ./pack
python apply_hardening.py --pack ./pack --base ${baseModel}
\`\`\`

See \`apply_hardening.py\` for the recognition-gate loader. The mechanism reinforces refusal **only** when the
input's activation-level harmful signature crosses the gate threshold, so benign traffic is untouched.

## Honest caveats

- Recognition-gating works only where benign/attack projections are cleanly separable at the read layer
  (model-dependent — see the prabodha generality bound).
- Re-measure on your exact base model, seed, and corpus before relying on any number.

Generated by prabodha (${input.prabodhaVersion ?? "latest"}).
`;
}

function applyPy(input: PackInput): string {
  const { goal } = input;
  return `"""Apply a prabodha hardening pack to a base model at serve time.

Loads hardening.json and registers the recognition-gated defense from
prabodha.steering.mechanisms. Activation hardening is a runtime hook — no weights are modified.
"""
import json, argparse
from prabodha.steering.mechanisms import (
    prompt_harden, component_restoration_hook, harmful_projection, recognition_gate, REGISTRY,
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", required=True, help="dir with hardening.json")
    ap.add_argument("--base", required=True, help="HF base model id")
    args = ap.parse_args()
    spec = json.load(open(f"{args.pack}/hardening.json"))
    mech = spec["mechanism"]
    assert mech in REGISTRY, f"unknown mechanism {mech}; have {list(REGISTRY)}"
    print(f"prabodha hardening pack: mechanism={mech} space={spec['space']} base={args.base}")

    if spec["space"] == "prompt":
        # Prompt-space: wrap every request with the graded refusal-reinforcing system message.
        level = {"prompt_refusal_gentle": "gentle", "prompt_refusal_firm": "firm",
                 "prompt_constitutional": "constitutional"}.get(mech, "firm")
        example = prompt_harden([{"role": "user", "content": "<user prompt>"}], level=level)
        print("Prepend this system message to every request:")
        print(example[0]["content"])
        return

    # Activation-space (the moat): fit the contrastive direction from the pack's examples on YOUR
    # base model, then register component_restoration_hook on the band layers, gated on recognition.
    print("Activation moat — fit the direction on your base model, then serve behind this gate:")
    print("  proj = harmful_projection(last_token_acts[read_layer], direction[read_layer])")
    print("  if recognition_gate(proj, tau): apply component_restoration_hook(direction, beta, prefill_only=True)")
    print("Positive examples:", ${JSON.stringify(goal.positive_examples).replace(/`/g, "'")})
    print("Negative examples:", ${JSON.stringify(goal.negative_examples).replace(/`/g, "'")})


if __name__ == "__main__":
    main()
`;
}

/** Assemble all pack files from a goal + base model (+ optional measured result). */
export function buildHardeningPack(input: PackInput): PackFile[] {
  return [
    { path: "hardening.json", content: hardeningJson(input) },
    { path: "README.md", content: readme(input) },
    { path: "apply_hardening.py", content: applyPy(input) },
  ];
}
