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
              decoding: dict | None = None, seed: int = 42,
              stream_tag: str = "", step_texts: list | None = None) -> str:
    import hashlib
    import torch
    from transformers import LogitsProcessorList
    ids = tok(prompt, return_tensors="pt")["input_ids"].to(hf.device)
    kw = dict(max_new_tokens=max_new, do_sample=False, pad_token_id=tok.eos_token_id,
              logits_processor=LogitsProcessorList(processors))
    if decoding and decoding.get("do_sample"):
        kw.update(do_sample=True, temperature=float(decoding["temperature"]))
        # Reproducible AND independent across generations: hard_seed_probe (L9 cycle 6)
        # found that resetting the SAME seed per generation makes all trajectories in a
        # run share sampling-stream structure (the seed selects a correlated trajectory
        # FAMILY, n_effective << n) — per-generation seeds derive from (seed, stream_tag).
        h = int(hashlib.sha256(f"{seed}|{stream_tag}".encode()).hexdigest()[:8], 16)
        torch.manual_seed(h)
    with torch.no_grad():
        out = hf.generate(ids, **kw)
    gen_ids = out[0, ids.shape[1]:]
    if step_texts is not None:
        step_texts.extend(tok.decode([int(t)]) for t in gen_ids.tolist())
    return tok.decode(gen_ids, skip_special_tokens=True)


def _build_trace_tokens(step_texts: list, entropies: list,
                        write_events: list | None) -> list:
    """Build per-step TraceToken records from one generation's collected evidence.

    step_texts[i] / entropies[i] align by decode step (one logits-processor call per
    generated token). write_events is a TimingPolicy's [(decode_step, gate_entropy)]
    list; a step is gated iff its index appears there. write_norm stays None in v1:
    the injector does not record the applied delta's L2 norm per application — the
    episode-level dose is carried by SteerTrace.alpha.
    """
    from prabodha.contracts.trace import TraceToken
    gated_steps = {int(s) for s, _ in (write_events or [])}
    n = min(len(step_texts), len(entropies))
    return [TraceToken(t=i, token=str(step_texts[i]), entropy=float(entropies[i]),
                       gated=i in gated_steps)
            for i in range(n)]


def main(argv=None) -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    ap = argparse.ArgumentParser()
    for f in ("--model", "--mid-lens", "--exp", "--out"):
        ap.add_argument(f, required=True)
    ap.add_argument("--contention", default="unknown")
    ap.add_argument("--seed", type=int, default=None,
                    help="override exp seeds[0] (multi-seed replications)")
    ap.add_argument("--alpha", type=float, default=None,
                    help="override exp alpha (dose-response grids)")
    ap.add_argument("--write-layer", type=int, default=None,
                    help="override exp write_layer (per-plant site calibration)")
    ap.add_argument("--norm-cap-rel", type=float, default=None,
                    help="override exp norm_cap_rel (raise in lockstep with --alpha; "
                         "pre-dispatch inert-knob checklist)")
    ap.add_argument("--tau-percentile", type=float, default=None,
                    help="override exp tau_percentile (L5 tau-sensitivity sweep)")
    ap.add_argument("--loop", default="L4",
                    help="loop label recorded in the gate (review #11: three relabel "
                         "rounds because this lived in dispatch memory — pass it "
                         "EVERY dispatch)")
    ap.add_argument("--record-readback", action="store_true",
                    help="record raw āgama re-cognition ranks (pre_rank, post_ranks at "
                         "the write port, band lens) per (concept, stub) so acceptance "
                         "thresholds can be calibrated offline (menu-4 "
                         "readback_recalibration)")
    ap.add_argument("--emit-trace", default=None,
                    help="if provided, emit a SteerTrace JSON at this path (per-token "
                         "entropy, gate events, band readouts, readback verdict)")
    ap.add_argument("--readback-lens", default=None,
                    help="optional second lens checkpoint used ONLY for the readback "
                         "decode; the write port still comes from --mid-lens. Enables "
                         "the L22 head-to-head: same writes, same stubs, decoded through "
                         "a band-targeted vs a final-target (jSpace-default) lens. "
                         "Concept: tulanā (weighing two readings of one instrument).")
    a = ap.parse_args(argv)
    import jlens
    exp = load(a.exp, required=("concepts", "stubs", "write_layer", "hypotheses"))
    if a.seed is not None:
        exp["seeds"] = [int(a.seed)]
    hf, tok = build_model(load(a.model))
    adapter = LensAdapter("jacobian").load(a.mid_lens)
    # tulanā: readback may decode through a different lens than the one that plans
    # writes — the L22 jSpace-mode vs prabodha-mode comparison. Defaults to identity.
    rb_adapter = (LensAdapter("jacobian").load(a.readback_lens)
                  if a.readback_lens else adapter)
    lm = jlens.from_hf(hf, tok)
    wl = int(a.write_layer) if a.write_layer is not None else int(exp["write_layer"])
    J = adapter._lens.jacobians[wl].float().cpu().numpy()
    U = hf.get_output_embeddings().weight.detach().float().cpu().numpy()
    alpha = float(a.alpha) if a.alpha is not None else float(exp["alpha"])
    cap = (float(a.norm_cap_rel) if a.norm_cap_rel is not None
           else float(exp["norm_cap_rel"]))
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

    # L20 trained-bridge setup
    citta_store = None
    if "trained_bridge" in exp.get("arms", []):
        try:
            from pwm.memory.citta_store import CittaStore
            hidden_dim = int(hf.config.hidden_size)
            citta_store = CittaStore(
                hidden_dim=hidden_dim,
                n_levels=1,
                beta_episodic=4.0,
                beta_semantic=0.25,
                max_episodic=512,
                max_semantic=256,
            )
            citta_store = citta_store.to(hf.device)
            devs.append(f"L20: CittaStore initialized ({hidden_dim}d, episodic β=4.0)")
        except Exception as e:
            devs.append(f"L20: CittaStore initialization failed: {e}")
            citta_store = None

    # āgama re-cognition raw ranks (opt-in): clean vs injected forward at the write
    # port, band-targeted lens — RAW ranks only; verdict thresholds are the quantity
    # under calibration, so none are applied here.
    readback = {}
    if a.record_readback:
        # rb_adapter (tulanā): the decode instrument; identical to the write-planning
        # adapter unless --readback-lens overrides it (L22 head-to-head).
        rb_layers = [layer for layer in rb_adapter.source_layers
                     if wl < layer <= wl + int(exp.get("readback_span", 4))]
        def _rank_of(row, tid):
            order = np.argsort(-np.asarray(row))
            return int(np.where(order == tid)[0][0]) + 1
        for concept, (ids, cmd) in plans.items():
            for stub in stubs:
                lens_clean, _ = rb_adapter.read_with_model(hf, tok, stub, positions=[-1],
                                                           layers=rb_layers)
                pre = min(_rank_of(lens_clean[layer][0], ids[0]) for layer in rb_layers)
                with ResidualInjector(layer_module, cmd):
                    lens_w, _ = rb_adapter.read_with_model(hf, tok, stub, positions=[-1],
                                                           layers=rb_layers)
                post = [min(_rank_of(lens_w[layer][0], cid) for cid in ids)
                        for layer in rb_layers]
                readback[(concept, stub)] = {"pre_rank": pre, "post_ranks": post,
                                             "rb_layers": list(rb_layers)}

    def run_arm(arm: str, policy_factory, citta_store=None, bridge_writer=None) -> dict:
        texts_by_concept, step_ents, n_writes, records = {}, [], [], []
        baseline_drops: list[float] = []
        episode = None  # first (concept, stub) per-step evidence, for --emit-trace replay
        for concept, (ids, cmd) in plans.items():
            texts = []
            for stub in stubs:
                trace_policy = policy_factory() if policy_factory else None
                trace = EntropyTrace(trace_policy)
                procs = [trace.processor()]
                if trace_policy is None and arm != "baseline" and arm != "trained_bridge":
                    raise AssertionError("non-baseline arm needs a policy")
                tag = f"{arm}|{concept}|{stub}"
                step_texts = [] if (getattr(a, "emit_trace", None) and episode is None) else None
                if arm == "baseline":
                    text = _generate(hf, tok, stub, max_new, procs,
                                     decoding=exp.get("decoding"),
                                     seed=int(exp["seeds"][0]), stream_tag=tag,
                                     step_texts=step_texts)
                elif arm == "trained_bridge":
                    # NEW: trained-bridge arm uses CittaStore-derived direction
                    if bridge_writer is None:
                        raise RuntimeError("trained_bridge arm requires bridge_writer")
                    trained_cmd = bridge_writer.plan_write(
                        u_rows=U[ids],
                        concept_ids=ids,
                        alpha=alpha,
                        norm_cap_rel=cap,
                        positions="last"
                    )
                    with ResidualInjector(layer_module, trained_cmd, policy=trace_policy) as inj:
                        text = _generate(hf, tok, stub, max_new, procs,
                                         decoding=exp.get("decoding"),
                                         seed=int(exp["seeds"][0]), stream_tag=tag,
                                         step_texts=step_texts)
                    n_writes.append(inj.n_applications)
                else:
                    with ResidualInjector(layer_module, cmd, policy=trace_policy) as inj:
                        text = _generate(hf, tok, stub, max_new, procs,
                                         decoding=exp.get("decoding"),
                                         seed=int(exp["seeds"][0]), stream_tag=tag,
                                         step_texts=step_texts)
                    n_writes.append(inj.n_applications)
                if step_texts is not None:
                    episode = {"concept": concept, "stub": stub,
                               "step_texts": step_texts,
                               "entropies": list(trace.entropies),
                               "write_events":
                                   list(getattr(trace_policy, "write_events", []) or [])}
                texts.append(text)
                step_ents.extend(trace.entropies)
                if arm == "baseline":
                    baseline_drops.extend(
                        trace.entropies[i - 1] - trace.entropies[i]
                        for i in range(1, len(trace.entropies))
                        if trace.entropies[i - 1] > trace.entropies[i])
                rec = {"concept": concept, "stub": stub[:24],
                       "mean_step_entropy": round(float(np.mean(trace.entropies)), 4)
                       if trace.entropies else None,
                       "n_writes": n_writes[-1] if arm != "baseline" else 0,
                       "hit": concept_surface_rate([text], concept) > 0,
                       "events": getattr(trace_policy, "write_events", None)}
                if (concept, stub) in readback:
                    rec["readback"] = readback[(concept, stub)]
                records.append(rec)
            texts_by_concept[concept] = texts
        surface = float(np.mean([concept_surface_rate(t, c)
                                 for c, t in texts_by_concept.items()]))
        camatk = float(np.mean([score_camatk_text(x)
                                for t in texts_by_concept.values() for x in t]))
        out = {"arm": arm, "surface": round(surface, 4), "camatk": round(camatk, 4),
               "mean_step_entropy": round(float(np.mean(step_ents)), 4),
               "mean_writes_per_gen": round(float(np.mean(n_writes)), 2) if n_writes else 0.0,
               "records": records}
        if episode is not None:
            out["_episode"] = episode
        if arm == "baseline":
            out["baseline_drops"] = baseline_drops
        return out

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
    drop_tau = None
    if results["baseline"].get("baseline_drops"):
        # commitment-flash threshold: registered percentile of the baseline's own
        # positive step-to-step entropy drops (same self-calibration discipline as tau)
        drop_tau = float(np.percentile(results["baseline"]["baseline_drops"],
                                       float(exp.get("drop_percentile", 60))))
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
    if "entropy_drop_gated" in arms_wanted:
        results["entropy_drop_gated"] = run_arm(
            "entropy_drop_gated",
            lambda: make_policy("entropy_drop_gated", drop=drop_tau, min_gap=min_gap))
    k = 0
    if "every_k" in arms_wanted:
        gated_rate = results["entropy_gated"]["mean_writes_per_gen"]
        k = max(1, round(max_new / max(gated_rate, 1.0)))
        results["every_k"] = run_arm("every_k", lambda: make_policy("every_k", k=k))

    # NEW: trained_bridge arm
    if "trained_bridge" in arms_wanted:
        if citta_store is None:
            devs.append("L20: trained_bridge arm requested but CittaStore not available")
        else:
            from prabodha.steering.bridge_trained import TrainedBridgeWriter
            bridge_writer = TrainedBridgeWriter(citta_store, wl)
            results["trained_bridge"] = run_arm(
                "trained_bridge",
                lambda: make_policy("entropy_gated", tau=tau, min_gap=min_gap),
                citta_store=citta_store,
                bridge_writer=bridge_writer
            )

    base_s, base_c = results["baseline"]["surface"], results["baseline"]["camatk"]
    base_e = results["baseline"]["mean_step_entropy"]
    agg = {"tau": round(tau, 4), "every_k_k": k,
           "drop_tau": round(drop_tau, 4) if drop_tau is not None else None}
    for arm in [x for x in ("continuous", "prefill_only", "entropy_gated",
                            "entropy_drop_gated", "every_k", "trained_bridge") if x in results]:
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
    if "H_flash_vs_uncommitted" in hyp and "entropy_drop_gated" in agg:
        hf_ = hyp["H_flash_vs_uncommitted"]
        adv = agg["entropy_drop_gated"]["lift"] - g["lift"]
        summary["H_flash_vs_uncommitted"] = {"value": round(adv, 4),
                                             "threshold": hf_["min_lift_advantage"],
                                             "pass": bool(adv >= float(hf_["min_lift_advantage"]))}
    if "H_gated_vs_prefill" in hyp and "prefill_only" in agg:
        hp = hyp["H_gated_vs_prefill"]
        adv = g["lift"] - agg["prefill_only"]["lift"]
        summary["H_gated_vs_prefill"] = {"value": round(adv, 4),
                                         "threshold": hp["min_lift_advantage"],
                                         "pass": bool(adv >= float(hp["min_lift_advantage"]))}
    # NEW: Trained-bridge comparator evaluation (L20)
    if "H_trained_bridge" in hyp and "trained_bridge" in agg:
        ht = hyp["H_trained_bridge"]
        tb = agg["trained_bridge"]
        min_lift = float(ht["min_lift"])
        entropy_eps = float(ht["entropy_epsilon"])
        max_gap = float(ht.get("max_gap_vs_analytic", 0.05))

        tb_lift = tb["lift"]
        tb_entropy_delta = tb["step_entropy_delta"]
        gap_vs_analytic = tb_lift - g["lift"]

        # Pass: lift >= min_lift AND entropy within budget AND gap <= max_gap vs analytic
        h_trained_bridge = (tb_lift >= min_lift
                           and abs(tb_entropy_delta) <= entropy_eps
                           and abs(gap_vs_analytic) <= max_gap)

        summary["H_trained_bridge"] = {
            "value": round(tb_lift, 4),
            "entropy_delta": round(tb_entropy_delta, 4),
            "gap_vs_analytic": round(gap_vs_analytic, 4),
            "threshold_lift": min_lift,
            "threshold_entropy": entropy_eps,
            "threshold_gap": max_gap,
            "pass": bool(h_trained_bridge)
        }
    report = GateReport(
        loop=a.loop, status="open",
        code_gate=GateSide(verdict="pass",
                           evidence=f"E4 ran to completion; contention={a.contention}"),
        domain_gate=GateSide(
            verdict="pass" if all(v["pass"] for v in summary.values()) else "fail",
            evidence=json.dumps({"summary": summary, "aggregates": agg,
                                 "arms": {k2: {x: v[x] for x in
                                               ("surface", "camatk", "mean_step_entropy",
                                                "mean_writes_per_gen")}
                                          for k2, v in results.items()},
                                 "drop_tau": agg.get("drop_tau"),
                                 "records": {k2: v["records"] for k2, v in results.items()},
                                 "contention": a.contention}),
            deviations=list(exp.get("deviations", [])) + devs))

    # Emit trace if requested
    if a.emit_trace:
        from datetime import datetime, timezone
        from prabodha.contracts.trace import SteerTrace

        # Extract metadata from the run
        model_cfg = load(a.model)
        prompt = list(exp.get("stubs", [""]))[0] if exp.get("stubs") else ""
        concept = list(exp.get("concepts", [""]))[0] if exp.get("concepts") else ""
        behavioral_hit = None
        if "entropy_gated" in results:
            records = results["entropy_gated"].get("records", [])
            if records:
                behavioral_hit = records[0].get("hit")

        # Per-token replay data from the primary arm's first collected episode
        # (entropy_gated has the best replay value: gate events fire during decode).
        primary_arm = "entropy_gated" if "entropy_gated" in results else "baseline"
        episode = results[primary_arm].get("_episode")
        trace_tokens = []
        if episode:
            trace_tokens = _build_trace_tokens(episode["step_texts"],
                                               episode["entropies"],
                                               episode["write_events"])
            prompt = episode["stub"]
            concept = episode["concept"]

        trace_obj = SteerTrace(
            model_id=model_cfg.get("hf_id", "unknown"),
            prompt=prompt,
            concept=concept,
            arm=primary_arm,
            seed=int(exp["seeds"][0]),
            alpha=alpha,
            tau_percentile=int(a.tau_percentile) if a.tau_percentile is not None else int(exp.get("tau_percentile", 60)),
            site_layer=wl,
            tokens=trace_tokens,
            readback=None,
            behavioral_hit=behavioral_hit,
            gate_ref=None,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        Path(a.emit_trace).parent.mkdir(parents=True, exist_ok=True)
        Path(a.emit_trace).write_text(trace_obj.model_dump_json(indent=2))
        print(f"trace written: {a.emit_trace}")

    Path(a.out).write_text(report.model_dump_json(indent=2))
    print(f"gate written: {a.out} (domain={report.domain_gate.verdict}) tau={tau:.3f} k={k} "
          + " ".join(f"{arm}: lift={agg[arm]['lift']:+.2f} dH={agg[arm]['step_entropy_delta']:+.2f} "
                     f"w={agg[arm]['writes_per_gen']}"
                     for arm in ("continuous", "prefill_only", "entropy_gated",
                                 "entropy_drop_gated", "every_k") if arm in agg))


if __name__ == "__main__":
    main()
