export default function GlossaryPage() {
  const glossary = [
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
      sanskrit: "sphuraṭṭā",
      english: "the flash / emergence",
      context: "A moment of pre-linguistic recognition; operationalized as entropy-gated write timing—detect moments when the model is least confident (highest entropy).",
    },
    {
      sanskrit: "āgama",
      english: "recognition / re-cognition",
      context: "Accepting the validity of something known; in prabodha, readback verification—did the model's workspace band actually take the steering cue?",
    },
    {
      sanskrit: "svātantrya",
      english: "autonomy / freedom / spontaneity",
      context: "The model's own degree of freedom; constrained in prabodha to ±0.5 nats of entropy cost—don't over-steer.",
    },
    {
      sanskrit: "māla",
      english: "limitation / impurity",
      context: "Three malas (ānava-, māyīya-, karma-māla) define failure modes in steering: does the write overreach, does the readback misfire, does timing go wrong?",
    },
  ];

  return (
    <main className="min-h-screen bg-gradient-to-b from-night-950 to-night-900 py-12 px-6">
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
            <a href="/docs/paper.pdf" className="text-indigo-400 hover:text-indigo-300">
              docs/paper/paper.pdf
            </a>
          </p>
        </div>
      </div>
    </main>
  );
}
