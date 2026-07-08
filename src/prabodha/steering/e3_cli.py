"""e3 CLI — the H5b redo: same content, mouth-write (v2) vs workspace-write (v3).
Concept: E3 (scoping §7) — v2 failed by writing at vaikharī after the workspace closed;
v3 writes into the band and verifies uptake by āgama re-cognition (band-lens readback).
Generation prompts are BARE stubs (no instruction): the concept reaches the output only if
the WRITE carries it — no instruction confound.
Source: contracts/L3_vimarsa_bridge.md; configs/experiments/e3.yaml (pre-registered);
PWM h5_ablation protocol (camatk_text scorer, ported).
Primitive: per (concept, stub): baseline gen / v2 gen (logit bias) / v3 gen (band injection
+ readback verdict) -> surface rates, camatkāra, entropy deltas, malas -> gates/gate_L3.json.
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
from prabodha.steering.injector import ResidualInjector, logit_bias_processor
from prabodha.steering.scoring import concept_surface_rate, score_camatk_text
from prabodha.steering.verifier import entropy, readback_verdict
from prabodha.steering.writer import plan_write


def _rank_of(logits_row, token_id: int) -> int:
    return int((logits_row > logits_row[token_id]).sum().item())


def _generate(hf, tok, prompt: str, max_new: int, processor=None) -> str:
    import torch
    from transformers import LogitsProcessorList
    enc = tok(prompt, return_tensors="pt")
    ids = enc["input_ids"].to(hf.device)
    kwargs = dict(max_new_tokens=max_new, do_sample=False,
                  pad_token_id=tok.eos_token_id)
    if processor is not None:
        kwargs["logits_processor"] = LogitsProcessorList([processor])
    with torch.no_grad():
        out = hf.generate(ids, **kwargs)
    return tok.decode(out[0, ids.shape[1]:], skip_special_tokens=True)


def main(argv=None) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    ap = argparse.ArgumentParser()
    for f in ("--model", "--mid-lens", "--exp", "--out"):
        ap.add_argument(f, required=True)
    ap.add_argument("--journal", required=False)
    ap.add_argument("--contention", default="unknown")
    a = ap.parse_args(argv)
    import jlens
    import torch
    exp = load(a.exp, required=("concepts", "stubs", "write_layer", "hypotheses"))
    hf, tok = build_model(load(a.model))
    adapter = LensAdapter("jacobian").load(a.mid_lens)
    lm = jlens.from_hf(hf, tok)
    wl = int(exp["write_layer"])
    rb_layers = [layer for layer in adapter.source_layers
                 if wl < layer <= wl + int(exp["readback_span"])]
    J = adapter._lens.jacobians[wl].float().cpu().numpy()
    U = hf.get_output_embeddings().weight.detach().float().cpu().numpy()
    alpha = float(exp["alpha"])
    cap = float(exp["norm_cap_rel"])
    eps = float(exp["entropy_epsilon"])
    max_new = int(exp["max_new_tokens"])
    devs: list[str] = []

    results = {"per_concept": [], "deviations": devs}
    arms: dict[str, dict[str, list]] = {arm: {"texts_by_concept": []} for arm in
                                        ("baseline", "v2", "v3")}
    uptakes, ent_deltas_v3, ent_deltas_v2 = [], [], []
    for concept in exp["concepts"]:
        cids = _concept_candidate_ids(tok, concept, exp.get("concepts_zh"), devs,
                                      policy="single_token_only")
        if not cids:
            devs.append(f"E3: concept '{concept}' has no single-token variant; skipped")
            continue
        concept_ids = sorted(set(cids.values()))
        cmd = plan_write(J, U[concept_ids], wl, concept_ids, alpha=alpha,
                         norm_cap_rel=cap, positions="last")
        texts = {"baseline": [], "v2": [], "v3": []}
        for stub in exp["stubs"]:
            # pre-write state: clean forward -> pre-rank (best across readback layers) + entropy
            lens_clean, model_clean = adapter.read_with_model(hf, tok, stub, positions=[-1],
                                                              layers=rb_layers)
            pre_rank = min(_rank_of(lens_clean[layer][0], concept_ids[0])
                           for layer in rb_layers)
            e_before = entropy(model_clean[0].numpy())
            layer_module = lm.layers[wl]
            with ResidualInjector(layer_module, cmd):
                lens_w, model_w = adapter.read_with_model(hf, tok, stub, positions=[-1],
                                                          layers=rb_layers)
            post_ranks = [min(_rank_of(lens_w[layer][0], cid) for cid in concept_ids)
                          for layer in rb_layers]
            e_after = entropy(model_w[0].numpy())
            uptakes.append(readback_verdict(
                pre_rank, post_ranks, top_m=int(exp["uptake_top_m"]),
                min_rank_gain=int(exp["uptake_min_rank_gain"]),
                entropy_before=e_before, entropy_after=e_after, epsilon=eps))
            ent_deltas_v3.append(e_after - e_before)
            # generations
            texts["baseline"].append(_generate(hf, tok, stub, max_new))
            proc = logit_bias_processor(concept_ids, float(exp["v2_bias"]))
            texts["v2"].append(_generate(hf, tok, stub, max_new, processor=proc))
            with torch.no_grad():
                enc = tok(stub, return_tensors="pt")
                base_logits = hf(enc["input_ids"].to(hf.device)).logits[0, -1]
                b = base_logits.clone()
                b[concept_ids] += float(exp["v2_bias"])
                ent_deltas_v2.append(entropy(b.float().cpu().numpy())
                                     - entropy(base_logits.float().cpu().numpy()))
            with ResidualInjector(layer_module, cmd):
                texts["v3"].append(_generate(hf, tok, stub, max_new))
        row = {"concept": concept, "concept_ids": concept_ids}
        for arm in texts:
            row[f"surface_{arm}"] = concept_surface_rate(texts[arm], concept)
            row[f"camatk_{arm}"] = round(float(np.mean(
                [score_camatk_text(t) for t in texts[arm]])), 4)
            arms[arm]["texts_by_concept"].append(texts[arm])
        results["per_concept"].append(row)

    rows = results["per_concept"]
    agg = {f"{k}_{arm}": round(float(np.mean([r[f"{k}_{arm}"] for r in rows])), 4)
           for k in ("surface", "camatk") for arm in ("baseline", "v2", "v3")}
    agg["uptake_rate"] = round(sum(u.ok for u in uptakes) / len(uptakes), 4)
    agg["malas"] = {m: sum(u.mala == m for u in uptakes)
                    for m in ("anava", "mayiya", "karma", "svatantrya")}
    agg["entropy_delta_v3_mean"] = round(float(np.mean(ent_deltas_v3)), 4)
    agg["entropy_delta_v2_mean"] = round(float(np.mean(ent_deltas_v2)), 4)
    lift_v3 = agg["surface_v3"] - agg["surface_baseline"]
    lift_v2 = agg["surface_v2"] - agg["surface_baseline"]
    agg["lift_v3"], agg["lift_v2"] = round(lift_v3, 4), round(lift_v2, 4)
    agg["camatk_drop_v3"] = round(agg["camatk_baseline"] - agg["camatk_v3"], 4)
    agg["camatk_drop_v2"] = round(agg["camatk_baseline"] - agg["camatk_v2"], 4)

    hyp = exp["hypotheses"]
    h_uptake_pass = agg["uptake_rate"] >= float(hyp["H_uptake"]["threshold_min"])
    hq = hyp["H_quality_per_lift"]
    h_quality_pass = (lift_v3 >= float(hq["min_lift"]) and
                      (agg["camatk_drop_v2"] - agg["camatk_drop_v3"])
                      >= float(hq["min_drop_advantage"]))
    summary = {"H_uptake": {"value": agg["uptake_rate"],
                            "threshold": hyp["H_uptake"]["threshold_min"],
                            "pass": bool(h_uptake_pass)},
               "H_quality_per_lift": {"value": round(
                   agg["camatk_drop_v2"] - agg["camatk_drop_v3"], 4),
                   "threshold": hq["min_drop_advantage"], "pass": bool(h_quality_pass)}}
    report = GateReport(
        loop="L3", status="open",
        code_gate=GateSide(verdict="pass",
                           evidence=f"E3 ran to completion; contention={a.contention}"),
        domain_gate=GateSide(
            verdict="pass" if all(v["pass"] for v in summary.values()) else "fail",
            evidence=json.dumps({"summary": summary, "aggregates": agg,
                                 "per_concept": rows, "contention": a.contention}),
            deviations=list(exp.get("deviations", [])) + devs))
    Path(a.out).write_text(report.model_dump_json(indent=2))
    print(f"gate written: {a.out} (domain={report.domain_gate.verdict}) "
          f"uptake={agg['uptake_rate']} lift v3/v2={lift_v3:.2f}/{lift_v2:.2f} "
          f"camatk drop v3/v2={agg['camatk_drop_v3']:.3f}/{agg['camatk_drop_v2']:.3f}")


if __name__ == "__main__":
    main()
