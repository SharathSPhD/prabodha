/**
 * Depth toggle for showing "Explorer" (plain-language, story/example)
 * vs "Researcher" (deep mechanism, real math/method) views.
 * Persisted in localStorage as "prabodha-depth-mode"
 */

export type DepthMode = "explorer" | "researcher";

export const getDepthMode = (): DepthMode => {
  if (typeof window === "undefined") return "explorer";
  const stored = localStorage.getItem("prabodha-depth-mode");
  return (stored as DepthMode) || "explorer";
};

export const setDepthMode = (mode: DepthMode) => {
  if (typeof window !== "undefined") {
    localStorage.setItem("prabodha-depth-mode", mode);
  }
};

/**
 * Inline glossary entries for key terms.
 * Each term maps to both explorer and researcher explanations.
 */
export const glossary: Record<
  string,
  { explorer: string; researcher: string }
> = {
  workspace_band:
    {
      explorer:
        "The part of the model where it 'thinks' — you write ideas here and the model reads them.",
      researcher:
        "The global workspace layer (J-space, ~layer 24-26) where information is globally broadcast; steering operates via concept vectors written into this band.",
    },
  sphuratta:
    {
      explorer: "A 'flash' when the model notices a steering suggestion.",
      researcher:
        "Gating moment: when entropy drops below a threshold, indicating the model's attention has unified around the concept.",
    },
  alpha:
    {
      explorer: "The strength dial — higher = stronger steering influence.",
      researcher:
        "Amplitude coefficient for the direction vector; controls write norm and measured in standardized effect units.",
    },
  arm:
    {
      explorer: "The timing style — when to inject the steering suggestion.",
      researcher:
        "Control arm: 'baseline' (no steer), 'gated' (entropy-gated), 'continuous' (every step), 'logit-bias' (output layer).",
    },
  entropy_budget:
    {
      explorer: "How much you can change the model's output freedom.",
      researcher:
        "Freedom cost constraint; steering must not exceed ±0.5 nats change in output entropy (svātantrya autonomy preservation).",
    },
};

export const getGlossary = (
  term: string,
  mode: DepthMode
): string | undefined => {
  const entry = glossary[term];
  return entry ? entry[mode] : undefined;
};
