/**
 * Curated starting concepts for workspace-band steering.
 *
 * Concept steering embeds a single tokenized concept word into the model's
 * workspace band (see the studio). ANY word works — these are suggested
 * starting points, grouped so a first-time user isn't staring at an empty box.
 * They are drawn from three honest sources:
 *   - sensory/topic concepts that steer visibly in the J-space (global-workspace)
 *     steering demos — the easiest way to *see* the effect on the first run;
 *   - emotion/tone and register concepts;
 *   - the alignment-relevant behaviors prabodha characterizes (truthfulness,
 *     harmlessness, caution).
 *
 * `confirmed: true` marks the one pairing we have a live 6-seed gate result for
 * (fire on Qwen3-4B). Everything else is a suggestion, not a verified outcome —
 * steer visibility is per-model and per-concept, and amplitude (alpha) must be
 * calibrated to the target (Qwen3 ~0.3; most others ~1–3).
 */

export interface ConceptPreset {
  label: string;
  value: string;
  blurb: string;
}

export interface ConceptCategory {
  id: string;
  title: string;
  hint: string;
  concepts: ConceptPreset[];
}

export const CONCEPT_CATEGORIES: ConceptCategory[] = [
  {
    id: "sensory",
    title: "Sensory & concrete",
    hint: "Easiest to see on a first run — the model's imagery visibly shifts.",
    concepts: [
      { label: "Fire", value: "fire", blurb: "warmth, flame, heat — the confirmed demo concept" },
      { label: "Ocean", value: "ocean", blurb: "water, tides, depth, salt" },
      { label: "Forest", value: "forest", blurb: "trees, moss, green shade" },
      { label: "Winter", value: "winter", blurb: "cold, snow, stillness" },
      { label: "Gold", value: "gold", blurb: "wealth, shine, warmth of metal" },
      { label: "Music", value: "music", blurb: "sound, rhythm, melody" },
      { label: "Storm", value: "storm", blurb: "wind, thunder, turbulence" },
    ],
  },
  {
    id: "emotion",
    title: "Emotion & tone",
    hint: "Shift the affective color of the response.",
    concepts: [
      { label: "Joy", value: "joy", blurb: "delight, brightness, celebration" },
      { label: "Fear", value: "fear", blurb: "dread, threat, unease" },
      { label: "Calm", value: "calm", blurb: "steadiness, quiet, ease" },
      { label: "Awe", value: "awe", blurb: "wonder, vastness, reverence" },
      { label: "Melancholy", value: "melancholy", blurb: "wistfulness, gentle sadness" },
      { label: "Curiosity", value: "curiosity", blurb: "questioning, openness, interest" },
    ],
  },
  {
    id: "alignment",
    title: "Alignment & behavior",
    hint: "The behaviors prabodha characterizes across models — steer, then measure.",
    concepts: [
      { label: "Truthfulness", value: "truthfulness", blurb: "honesty, accuracy, candor" },
      { label: "Harmlessness", value: "harmlessness", blurb: "refusal, safety, caution" },
      { label: "Caution", value: "uncertainty", blurb: "hedging, doubt, care" },
      { label: "Helpfulness", value: "helpfulness", blurb: "assistance, thoroughness" },
      { label: "Deference", value: "deference", blurb: "humility, yielding, respect" },
    ],
  },
  {
    id: "register",
    title: "Style & register",
    hint: "Change how it says things, not what it's about.",
    concepts: [
      { label: "Formal", value: "formality", blurb: "precise, professional register" },
      { label: "Playful", value: "playfulness", blurb: "light, witty, teasing" },
      { label: "Poetic", value: "poetry", blurb: "imagery, cadence, metaphor" },
      { label: "Technical", value: "technical", blurb: "specialist, exact, dense" },
      { label: "Terse", value: "brevity", blurb: "short, clipped, minimal" },
    ],
  },
];

/** Flat list of all preset concepts (for chips / autocomplete). */
export const ALL_CONCEPTS: ConceptPreset[] = CONCEPT_CATEGORIES.flatMap((c) => c.concepts);

/**
 * Ready-to-run starter pairings (prompt + concept). The first is the live-confirmed
 * fire/Qwen3 demo; the rest are suggested first runs across the other app models.
 */
export interface StarterPair {
  prompt: string;
  concept: string;
  model: string;
  alpha: number;
  note: string;
  confirmed?: boolean;
}

export const STARTER_PAIRS: StarterPair[] = [
  {
    prompt: "It is a beautiful day and the temperature outside is",
    concept: "fire",
    model: "Qwen/Qwen3-4B-Instruct-2507",
    alpha: 0.3,
    note: "The confirmed demo — the completion warms toward heat/flame (gate_L9_alignconf).",
    confirmed: true,
  },
  {
    prompt: "Tell me about a place you'd like to visit.",
    concept: "ocean",
    model: "google/gemma-2-2b-it",
    alpha: 1.5,
    note: "Gemma needs a higher alpha (~1–3) to show a visible shift toward water imagery.",
  },
  {
    prompt: "Describe your morning.",
    concept: "melancholy",
    model: "Qwen/Qwen2.5-1.5B-Instruct",
    alpha: 1.2,
    note: "Tone steer — the affect of the passage cools.",
  },
  {
    prompt: "How should I respond to a rude email?",
    concept: "calm",
    model: "meta-llama/Llama-3.2-1B-Instruct",
    alpha: 1.5,
    note: "Behavioral steer toward steadiness on a real advice prompt.",
  },
];
