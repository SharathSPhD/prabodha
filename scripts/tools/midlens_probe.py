"""midlens_probe.py — L2b registered discriminator: is the workspace band's content invisible
to a FINAL-target lens (lens-blindness) or genuinely absent (top-consolidation)?
Concept: madhyamā-parīkṣā — asking the middle voice with an instrument tuned TO the middle
(a lens whose target is the band exit), not one tuned to the mouth.
Source: research/journal.md 2026-07-08 L3-readiness fork, option (c); contracts/L2_pwm_stack.md.
Primitive: mid-target lens (configs/lens/fit_mid26.yaml) -> evaluate_h_modulation in the
band [6,26) with uninstructed control + shuffled null + single_token_only candidates ->
gates/gate_L2b.json. REGISTERED OUTCOMES (declared before the run):
  (i) hit_rate >= 0.3 AND hit_rate - control >= 0.2  -> band content EXISTS, final-target
      lens was blind -> L3 design: per-band lenses (option c wins);
  (ii) margin ~ 0 (whatever the absolute rate)       -> top-consolidation reading
      strengthened -> L3: write-site sweep or plant switch (operator's fork).
"""
import argparse
import datetime
import json
from pathlib import Path

from prabodha.config import load
from prabodha.contracts.closure import GateReport, GateSide
from prabodha.lens.adapter import LensAdapter, build_model
from prabodha.lens.e1_metrics import concept_prompt_pairs, evaluate_h_modulation


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--lens-file", required=True)
    ap.add_argument("--exp", required=True, help="experiment yaml (concepts/templates/knobs)")
    ap.add_argument("--band", nargs=2, type=int, default=[6, 26])
    ap.add_argument("--out", required=True)
    ap.add_argument("--contention", default="unknown")
    a = ap.parse_args(argv)
    exp = load(a.exp, required=("concepts", "templates", "seeds"))
    hf, tok = build_model(load(a.model))
    adapter = LensAdapter("jacobian").load(a.lens_file)
    band = [layer for layer in adapter.source_layers if a.band[0] <= layer < a.band[1]]
    pairs = concept_prompt_pairs(exp)[:40]
    stubs = [p.split(". ", 1)[1] if ". " in p else p for p, _ in pairs]
    r = evaluate_h_modulation(
        hf, tok, adapter, pairs, band,
        translations=exp.get("concepts_zh"),
        null_shuffles=int(exp.get("modulation_null_shuffles", 200)),
        seed=int(exp["seeds"][0]), control_stubs=stubs,
        variant_policy=exp.get("concept_variant_policy", "single_token_only"))
    value = r["instructed_concept_hit_rate_at5"]
    control = r["uninstructed_control_hit_rate"]
    margin = value - control
    outcome = "band_content_exists_final_lens_blind" if (value >= 0.3 and margin >= 0.2) \
        else "top_consolidation_supported"
    devs = r.pop("deviations", [])
    report = GateReport(
        loop="L2b", status="open",
        code_gate=GateSide(verdict="pass",
                           evidence=f"mid-lens probe completed; contention={a.contention}"),
        domain_gate=GateSide(
            verdict="pass" if outcome == "band_content_exists_final_lens_blind" else "fail",
            evidence=json.dumps({"registered_outcome": outcome, "hit_rate": value,
                                 "control": control, "margin": margin,
                                 "band": band, "date": str(datetime.date.today()),
                                 "detail": r}),
            deviations=devs))
    Path(a.out).write_text(report.model_dump_json(indent=2))
    print(f"L2b probe: hit={value:.3f} control={control:.3f} margin={margin:+.3f} "
          f"-> {outcome} ({a.out})")


if __name__ == "__main__":
    main()
