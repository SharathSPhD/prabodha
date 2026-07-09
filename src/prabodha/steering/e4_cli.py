"""e4 CLI — E4: sphurattā-gated write timing vs rate-matched and fixed-timing controls.
Concept: L3 showed timing (not amplitude) carries both steering and freedom cost; E4 asks
whether writing at UNCOMMITTED moments (entropy-gated; sphurattā as commitment-flash's
complement) preserves behavioral lift within the svātantrya budget — and whether event
ALIGNMENT matters beyond mere write sparsity (every-k rate-matched control).
Source: contracts/L4_sphuratta_timing.md; configs/experiments/e4.yaml; L3 review #5
requirements (per-prompt scatter, dose accounting).
Primitive: arms {baseline, continuous, prefill_only, entropy_gated, every_k(matched)} over
(concept, stub); tau self-calibrated from the baseline arm's own step entropies; k matched
to the gated arm's realized write rate -> gates/gate_L4.json.
"""
import argparse
import json
import logging
from pathlib import Path

import numpy as np

from prabodha.config import load
from prabodha.contracts.closure import GateReport, GateSide
from prabodha.lens.adapter import LensAdapter, build_model
from prabodha.lens.e1_metrics import _concept_candidate_ids
from prabodha.steering.injector import ResidualInjector, entropy_observer
from prabodha.steering.scoring import concept_surface_rate, score_camatk_text
from prabodha.steering.timing import make_policy
from prabodha.steering.writer import plan_write


class EntropyTrace:
    """Records every decode step's next-token entropy; optionally forwards to a policy."""

    def __init__(self, policy=None):
        self.entropies: list[float] = []
        self._policy = policy

    def processor(self):
        inner = entropy_observer(self._policy) if self._policy is not None else None

        def _proc(input_ids, scores):
            import torch
            p = torch.softmax(scores[0].float(), dim=-1)
            self.entropies.append(float(-(p * torch.log(p.clamp_min(1e-30))).sum().item()))
            if inner is not None:
                inner(input_ids, scores)
            return scores
        return _proc


def _generate(hf, tok, prompt: str, max_new: int, processors: list,
              decoding: dict | None = None, seed: int = 42) -> str:
    import torch
    from transformers import LogitsProcessorList
    ids = tok(prompt, return_tensors="pt")["input_ids"].to(hf.device)
    kw = dict(max_new_tokens=max_new, do_sample=False, pad_token_id=tok.eos_token_id,
              logits_processor=LogitsProcessorList(processors))
    if decoding and decoding.get("do_sample"):
        kw.update(do_sample=True, temperature=float(decoding["temperature"]))
        torch.manual_seed(seed)  # registered seed; sampling arms reproducible
    with torch.no_grad():
        out = hf.generate(ids, **kw)
    return tok.decode(out[0, ids.shape[1]:], skip_special_tokens=True)


def main(argv=None) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    ap = argparse.ArgumentParser()
    for f in ("--model", "--mid-lens", "--exp", "--out"):
        ap.add_argument(f, required=True)
    ap.add_argument("--contention", default="unknown")
    ap.add_argument("--tau-percentile", type=float, default=None,
                    help="override exp tau_percentile (L5 tau-sensitivity sweep)")
    a = ap.parse_args(argv)
    import jlens
    exp = load(a.exp, required=("concepts", "stubs", "write_layer", "hypotheses"))
    hf, tok = build_model(load(a.model))
    adapter = LensAdapter("jacobian").load(a.mid_lens)
    lm = jlens.from_hf(hf, tok)
    wl = int(exp["write_layer"])
    J = adapter._lens.jacobians[wl].float().cpu().numpy()
    U = hf.get_output_embeddings().weight.detach().float().cpu().numpy()
    alpha, cap = float(exp["alpha"]), float(exp["norm_cap_rel"])
    max_new = int(exp["max_new_tokens"])
    min_gap = int(exp["min_gap"])
    devs: list[str] = []

    # concept plans (single-token candidates, as L3)
    plans = {}
    for concept in exp["concepts"]:
        cids = _concept_candidate_ids(tok, concept, exp.get("concepts_zh"), devs,
                                      policy="single_token_only")
        if not cids:
            devs.append(f"E4: concept '{concept}' skipped (no single-token variant)")
            continue
        ids = sorted(set(cids.values()))
        plans[concept] = (ids, plan_write(J, U[ids], wl, ids, alpha=alpha,
                                          norm_cap_rel=cap, positions="last"))
    layer_module = lm.layers[wl]
    stubs = list(exp["stubs"])

    def run_arm(arm: str, policy_factory) -> dict:
        texts_by_concept, step_ents, n_writes, records = {}, [], [], []
        for concept, (ids, cmd) in plans.items():
            texts = []
            for stub in stubs:
                trace_policy = policy_factory() if policy_factory else None
                trace = EntropyTrace(trace_policy)
                procs = [trace.processor()]
                if trace_policy is None and arm != "baseline":
                    raise AssertionError("non-baseline arm needs a policy")
                if arm == "baseline":
                    text = _generate(hf, tok, stub, max_new, procs,
                                     decoding=exp.get("decoding"), seed=int(exp["seeds"][0]))
                else:
                    with ResidualInjector(layer_module, cmd, policy=trace_policy) as inj:
                        text = _generate(hf, tok, stub, max_new, procs,
                                         decoding=exp.get("decoding"),
                                         seed=int(exp["seeds"][0]))
                    n_writes.append(inj.n_applications)
                texts.append(text)
                step_ents.extend(trace.entropies)
                records.append({"concept": concept, "stub": stub[:24],
                                "mean_step_entropy": round(float(np.mean(trace.entropies)), 4)
                                if trace.entropies else None,
                                "n_writes": n_writes[-1] if arm != "baseline" else 0,
                                "hit": concept_surface_rate([text], concept) > 0,
                                "events": getattr(trace_policy, "write_events", None)})
            texts_by_concept[concept] = texts
        surface = float(np.mean([concept_surface_rate(t, c)
                                 for c, t in texts_by_concept.items()]))
        camatk = float(np.mean([score_camatk_text(x)
                                for t in texts_by_concept.values() for x in t]))
        return {"arm": arm, "surface": round(surface, 4), "camatk": round(camatk, 4),
                "mean_step_entropy": round(float(np.mean(step_ents)), 4),
                "mean_writes_per_gen": round(float(np.mean(n_writes)), 2) if n_writes else 0.0,
                "records": records}

    results = {}
    results["baseline"] = run_arm("baseline", None)
    base_records = results["baseline"]["records"]
    base_ents = [r["mean_step_entropy"] for r in base_records if r["mean_step_entropy"]]
    # tau: registered percentile of the baseline arm's OWN per-generation mean step
    # entropies (self-calibrated; registered as tau_percentile in e4.yaml). Deterministic
    # from recorded evidence — every value in base_ents ships in the gate records.
    tau_pct = (float(a.tau_percentile) if a.tau_percentile is not None
               else exp.get("tau_percentile"))
    tau = (float(np.percentile(base_ents, float(tau_pct)))
           if a.tau_percentile is not None or "tau_fixed" not in exp
           else float(exp["tau_fixed"]))
    arms_wanted = list(exp.get("arms",
                       ["continuous", "prefill_only", "entropy_gated", "every_k"]))
    if "continuous" in arms_wanted:
        results["continuous"] = run_arm("continuous", lambda: make_policy("continuous"))
    if "prefill_only" in arms_wanted:
        results["prefill_only"] = run_arm("prefill_only",
                                          lambda: make_policy("prefill_only"))
    if "entropy_gated" in arms_wanted:
        results["entropy_gated"] = run_arm(
            "entropy_gated", lambda: make_policy("entropy_gated", tau=tau, min_gap=min_gap))
    k = 0
    if "every_k" in arms_wanted:
        gated_rate = results["entropy_gated"]["mean_writes_per_gen"]
        k = max(1, round(max_new / max(gated_rate, 1.0)))
        results["every_k"] = run_arm("every_k", lambda: make_policy("every_k", k=k))

    base_s, base_c = results["baseline"]["surface"], results["baseline"]["camatk"]
    base_e = results["baseline"]["mean_step_entropy"]
    agg = {"tau": round(tau, 4), "every_k_k": k}
    for arm in [x for x in ("continuous", "prefill_only", "entropy_gated", "every_k")
                if x in results]:
        r = results[arm]
        agg[arm] = {"lift": round(r["surface"] - base_s, 4),
                    "camatk_drop": round(base_c - r["camatk"], 4),
                    "step_entropy_delta": round(r["mean_step_entropy"] - base_e, 4),
                    "writes_per_gen": r["mean_writes_per_gen"]}
    hyp = exp["hypotheses"]
    hg = hyp["H_gated_budget"]
    g = agg["entropy_gated"]
    h_gated = (g["lift"] >= float(hg["min_lift"])
               and abs(g["step_entropy_delta"]) <= float(hg["entropy_epsilon"]))
    summary = {"H_gated_budget": {"value": g["lift"],
                                  "threshold": hg["min_lift"], "pass": bool(h_gated)}}
    if "H_alignment" in hyp and "every_k" in agg:
        ha = hyp["H_alignment"]
        adv = g["lift"] - agg["every_k"]["lift"]
        summary["H_alignment"] = {"value": round(adv, 4),
                                  "threshold": ha["min_lift_advantage"],
                                  "pass": bool(adv >= float(ha["min_lift_advantage"]))}
    if "H_gated_vs_prefill" in hyp and "prefill_only" in agg:
        hp = hyp["H_gated_vs_prefill"]
        adv = g["lift"] - agg["prefill_only"]["lift"]
        summary["H_gated_vs_prefill"] = {"value": round(adv, 4),
                                         "threshold": hp["min_lift_advantage"],
                                         "pass": bool(adv >= float(hp["min_lift_advantage"]))}
    report = GateReport(
        loop="L4", status="open",
        code_gate=GateSide(verdict="pass",
                           evidence=f"E4 ran to completion; contention={a.contention}"),
        domain_gate=GateSide(
            verdict="pass" if all(v["pass"] for v in summary.values()) else "fail",
            evidence=json.dumps({"summary": summary, "aggregates": agg,
                                 "arms": {k2: {x: v[x] for x in
                                               ("surface", "camatk", "mean_step_entropy",
                                                "mean_writes_per_gen")}
                                          for k2, v in results.items()},
                                 "records": {k2: v["records"] for k2, v in results.items()},
                                 "contention": a.contention}),
            deviations=list(exp.get("deviations", [])) + devs))
    Path(a.out).write_text(report.model_dump_json(indent=2))
    print(f"gate written: {a.out} (domain={report.domain_gate.verdict}) tau={tau:.3f} k={k} "
          + " ".join(f"{arm}: lift={agg[arm]['lift']:+.2f} dH={agg[arm]['step_entropy_delta']:+.2f} "
                     f"w={agg[arm]['writes_per_gen']}"
                     for arm in ("continuous", "prefill_only", "entropy_gated", "every_k")
                     if arm in agg))


if __name__ == "__main__":
    main()
