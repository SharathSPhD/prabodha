"""articulation_null — the E7 tautology test (L2 review-#4 debt; selector cycle 4).
Concept: is progressive articulation a property of the PLANT's residual stream, or an
artifact of a lens FITTED to transport toward final logits?
REGISTRATION CORRECTION (disclosed): the menu named this null "shuffled_final_logits", but
top-k negentropy is permutation-invariant — that null is vacuous. The informative null is
the LOGIT-LENS baseline: per-layer unembedding with NO fitted transport (vendor
apply(use_jacobian=False)). Registered decision rule, written before any numbers:
  - rho_logitlens >= 0.5 AND p <= 0.05  -> gradient is MODEL-INTRINSIC; E7 claim survives
    (measured through either instrument; tautology defused).
  - rho_logitlens < 0.5 while rho_jacobian >= 0.5 -> gradient is LENS-CONSTRUCTED; the E7
    claim is deflated to an instrument property (honest negative for the vāk reading).
Source: contracts/L2_pwm_stack.md carried caveat; review #4; configs/efe_menu.yaml.
"""
import argparse
import json
from pathlib import Path

from prabodha.config import load
from prabodha.contracts.closure import GateReport, GateSide
from prabodha.lens.adapter import LensAdapter, build_model
from prabodha.lens.e1_metrics import concept_prompt_pairs, evaluate_h_articulation


class _LogitLensReader:
    """Adapter-shaped shim: reads per-layer LOGIT-LENS (no fitted transport)."""

    def __init__(self, adapter, hf, tok):
        import jlens
        self._lens = adapter._lens
        self._model = jlens.from_hf(hf, tok)

    def read(self, hf, tok, prompt, positions=(-1,), layers=None):
        lens_logits, _m, _ = self._lens.apply(self._model, prompt, layers=layers,
                                              positions=list(positions),
                                              use_jacobian=False)
        return lens_logits


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    for f in ("--model", "--lens-file", "--exp", "--out"):
        ap.add_argument(f, required=True)
    ap.add_argument("--contention", default="unknown")
    a = ap.parse_args(argv)
    exp = load(a.exp, required=("hypotheses", "seeds"))
    hf, tok = build_model(load(a.model))
    adapter = LensAdapter("jacobian").load(a.lens_file)
    prompts = [p for p, _ in concept_prompt_pairs(exp)][:16]
    kw = dict(top_k=int(exp["top_k"]), permutation_resamples=10000,
              seed=int(exp["seeds"][0]))
    r_jac = evaluate_h_articulation(hf, tok, adapter, prompts, **kw)
    r_log = evaluate_h_articulation(hf, tok, _LogitLensReader(adapter, hf, tok),
                                    prompts, **kw)
    intrinsic = (r_log["articulation_gradient_rho"] >= 0.5
                 and r_log["permutation_p"] <= 0.05)
    summary = {"H_articulation_model_intrinsic": {
        "value": r_log["articulation_gradient_rho"], "threshold": 0.5,
        "pass": bool(intrinsic)}}
    report = GateReport(
        loop="L7-articulation-null", status="open",
        code_gate=GateSide(verdict="pass",
                           evidence=f"both instruments evaluated; contention={a.contention}"),
        domain_gate=GateSide(
            verdict="pass" if intrinsic else "fail",
            evidence=json.dumps({
                "summary": summary,
                "jacobian_lens": {k: r_jac[k] for k in
                                  ("articulation_gradient_rho", "permutation_p",
                                   "per_layer_negentropy")},
                "logit_lens_null": {k: r_log[k] for k in
                                    ("articulation_gradient_rho", "permutation_p",
                                     "per_layer_negentropy")},
                "registered_rule": "pass = model-intrinsic (logit-lens rho>=0.5, p<=.05); "
                                   "fail = lens-constructed (E7 deflated)"}),
            deviations=["null redesigned at registration: shuffled_final_logits is vacuous "
                        "under permutation-invariant negentropy; logit-lens baseline used "
                        "instead (disclosed in script docstring before running)"]))
    Path(a.out).write_text(report.model_dump_json(indent=2))
    print(f"gate written: {a.out} jac_rho={r_jac['articulation_gradient_rho']:.3f} "
          f"logit_rho={r_log['articulation_gradient_rho']:.3f} -> "
          f"{'MODEL-INTRINSIC' if intrinsic else 'LENS-CONSTRUCTED'}")


if __name__ == "__main__":
    main()
