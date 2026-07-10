"""write_cost — operational cost of write schedules (menu-2 item; review #9/#10 demand).
Concept: the missing denominator — does write COUNT cost anything the user feels?
Source: configs/efe_menu2.yaml write_cost_operational; reviews #9 (efficiency currency)
and #10 (rate confound in the flash comparison).
Primitive: wall-clock tokens/sec + camatkāra per arm {baseline, prefill_only,
entropy_gated, continuous} over the standard stubs, independent streams, one seed.
Registered rule (before running): a schedule has REAL operational cost iff its throughput
is > 10% below baseline. Otherwise write-count is operationally free at this scale and
per-write "efficiency" arguments carry no product weight (report says so).
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np

from prabodha.config import load
from prabodha.contracts.closure import GateReport, GateSide
from prabodha.lens.adapter import LensAdapter, build_model
from prabodha.lens.e1_metrics import _concept_candidate_ids
from prabodha.steering.e4_cli import EntropyTrace, _generate
from prabodha.steering.injector import ResidualInjector
from prabodha.steering.scoring import score_camatk_text
from prabodha.steering.timing import make_policy
from prabodha.steering.writer import plan_write


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    for f in ("--model", "--mid-lens", "--exp", "--out"):
        ap.add_argument(f, required=True)
    ap.add_argument("--contention", default="unknown")
    a = ap.parse_args(argv)
    import jlens
    exp = load(a.exp, required=("concepts", "stubs", "write_layer"))
    hf, tok = build_model(load(a.model))
    adapter = LensAdapter("jacobian").load(a.mid_lens)
    lm = jlens.from_hf(hf, tok)
    wl = int(exp["write_layer"])
    J = adapter._lens.jacobians[wl].float().cpu().numpy()
    U = hf.get_output_embeddings().weight.detach().float().cpu().numpy()
    devs: list[str] = []
    concepts = exp["concepts"][:5]
    stubs = exp["stubs"][:2]
    max_new = int(exp["max_new_tokens"])
    seed = int(exp["seeds"][0])
    arms = {"baseline": None, "prefill_only": "prefill_only",
            "entropy_gated": "entropy_gated", "continuous": "continuous"}
    results = {}
    for arm, pol in arms.items():
        toks, secs, cams = 0, 0.0, []
        for concept in concepts:
            cids = _concept_candidate_ids(tok, concept, exp.get("concepts_zh"), devs,
                                          policy="single_token_only")
            ids = sorted(set(cids.values()))
            cmd = plan_write(J, U[ids], wl, ids, alpha=float(exp["alpha"]),
                             norm_cap_rel=float(exp["norm_cap_rel"]))
            for stub in stubs:
                policy = make_policy(pol, tau=2.7, min_gap=2) if pol == "entropy_gated" \
                    else (make_policy(pol) if pol else None)
                trace = EntropyTrace(policy)
                t0 = time.perf_counter()
                if arm == "baseline":
                    text = _generate(hf, tok, stub, max_new, [trace.processor()],
                                     decoding=exp.get("decoding"), seed=seed,
                                     stream_tag=f"{arm}|{concept}|{stub}")
                else:
                    with ResidualInjector(lm.layers[wl], cmd, policy=policy):
                        text = _generate(hf, tok, stub, max_new, [trace.processor()],
                                         decoding=exp.get("decoding"), seed=seed,
                                         stream_tag=f"{arm}|{concept}|{stub}")
                secs += time.perf_counter() - t0
                toks += len(trace.entropies)
                cams.append(score_camatk_text(text))
        results[arm] = {"tok_per_sec": round(toks / secs, 2),
                        "camatk": round(float(np.mean(cams)), 4)}
    base_tps = results["baseline"]["tok_per_sec"]
    costly = {arm: r["tok_per_sec"] < 0.9 * base_tps for arm, r in results.items()
              if arm != "baseline"}
    any_cost = any(costly.values())
    report = GateReport(loop="L9-writecost", status="open",
        code_gate=GateSide(verdict="pass",
                           evidence=f"throughput instrumented; contention={a.contention}"),
        domain_gate=GateSide(
            verdict="fail" if any_cost else "pass",
            evidence=json.dumps({"summary": {"H_write_count_operationally_free": {
                "value": min(r["tok_per_sec"] / base_tps for arm, r in results.items()
                             if arm != "baseline"),
                "threshold": 0.9, "pass": not any_cost}},
                "per_arm": results, "baseline_tps": base_tps,
                "rule": "cost is REAL iff throughput <90% of baseline; else write-count "
                        "is operationally free at this scale"}),
            deviations=devs))
    Path(a.out).write_text(report.model_dump_json(indent=2))
    print(f"gate written: {a.out} " + " ".join(
        f"{arm}:{r['tok_per_sec']}t/s(cam {r['camatk']})" for arm, r in results.items()))


if __name__ == "__main__":
    main()
