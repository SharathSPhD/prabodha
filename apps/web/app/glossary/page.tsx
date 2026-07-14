import { SiteNav } from "@/components/SiteNav";

export default function GlossaryPage() {
  const glossary = [
    {
      sanskrit: "J-space",
      english: "Jacobian-lens workspace",
      context: "The verbalizable global workspace identified by Anthropic's J-space paper—the residual stream layer where high-level, model-interpretable concepts coexist with low-level linguistic features.",
    },
    {
      sanskrit: "vimarśa",
      english: "reflexive self-awareness",
      context: "The mind's recognition of itself as the knower; operationalized in J-space as the model's ability to re-read its own workspace.",
    },
    {
      sanskrit: "parā vāk",
      english: "supreme creative word",
      context: "The transcendent Word in Śaiva philosophy; in prabodha, the linguistic global workspace band identified by the J-space paper.",
    },
    {
      sanskrit: "workspace band",
      english: "the target layers",
      context: "The contiguous band of residual-stream layers (typically 6–26 or 6–30) where steering writes are injected and where readback verification occurs. The core of the workspace.",
    },
    {
      sanskrit: "steering",
      english: "guided direction-writing",
      context: "The act of injecting a concept direction into the workspace band, timed by entropy gating, to influence model behavior while preserving autonomy.",
    },
    {
      sanskrit: "sphuraṭṭā",
      english: "the flash / emergence",
      context: "A moment of pre-linguistic recognition; operationalized as entropy-gated write timing—detect moments when the model is least confident (highest entropy).",
    },
    {
      sanskrit: "entropy-gating",
      english: "selective timing by uncertainty",
      context: "The mechanism that detects sphuraṭṭā events: fire writes only when the model's entropy exceeds a threshold (e.g., 60th percentile), capturing moments of reconceptualization.",
    },
    {
      sanskrit: "āgama",
      english: "recognition / re-cognition",
      context: "Accepting the validity of something known; in prabodha, readback verification—did the model's workspace band actually take the steering cue?",
    },
    {
      sanskrit: "readback",
      english: "uptake verification",
      context: "Re-reading the workspace band to confirm that a write succeeded. Measured by the readback verdict (accept/reject) based on concept rank and gain confidence.",
    },
    {
      sanskrit: "svātantrya",
      english: "autonomy / freedom / spontaneity",
      context: "The model's own degree of freedom; constrained in prabodha to ±0.5 nats of entropy cost—don't over-steer.",
    },
    {
      sanskrit: "ASR",
      english: "attack success rate",
      context: "Benchmark metric for adversarial robustness: the fraction of adversarial prompts (e.g., from AdvBench) to which the model generates harmful outputs. Prabodha does not improve ASR; it is a transparency tool, not alignment assurance.",
    },
    {
      sanskrit: "lift-per-write",
      english: "steering efficiency ratio",
      context: "The ratio of behavioral lift achieved per write command executed. Gated steering achieves ~2.3× lift per write compared to continuous writes, while maintaining ±0.5 nats autonomy budget.",
    },
    {
      sanskrit: "māla",
      english: "limitation / impurity",
      context: "Three malas (ānava-, māyīya-, karma-māla) define failure modes in steering: does the write overreach, does the readback misfire, does timing go wrong?",
    },
  ];

  return (
    <main className="min-h-screen bg-gradient-to-b from-night-950 to-night-900">
      <SiteNav />
      <div className="px-6 py-12">
      <div className="mx-auto max-w-4xl">
        <div className="mb-8 space-y-3">
          <h1 className="text-4xl font-serif font-bold text-gradient">Glossary</h1>
          <p className="text-sm text-slate-400">
            Sanskrit-English dual register. Engineering glosses for philosophical concepts.
          </p>
        </div>

        <div className="space-y-4">
          {glossary.map((entry, i) => (
            <div key={i} className="card p-6 space-y-3 border-l-4 border-indigo-600">
              <div className="flex flex-col sm:flex-row gap-4 sm:items-baseline">
                <div className="space-y-1">
                  <p className="text-sm font-mono text-indigo-300 italic">{entry.sanskrit}</p>
                  <p className="text-lg font-semibold text-slate-100">{entry.english}</p>
                </div>
              </div>
              <p className="text-sm text-slate-400">{entry.context}</p>
            </div>
          ))}
        </div>

        <div className="mt-12 card p-6 space-y-3 bg-night-800/50">
          <h2 className="text-lg font-semibold text-slate-100">Full reference</h2>
          <p className="text-sm text-slate-500">
            Complete glossary is in the paper appendix:{" "}
            <a
              href="https://www.preprints.org/frontend/manuscript/5b72d5c7d0e37f4f5b222acfab709652/download_pub"
              target="_blank"
              rel="noopener noreferrer"
              className="text-indigo-400 hover:text-indigo-300"
            >
              read the preprint
            </a>
          </p>
        </div>
      </div>
      </div>
    </main>
  );
}
