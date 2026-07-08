"""compare CLI: python -m prabodha.lens.compare_cli --gates <a.json> <b.json> --labels 4B 27B [--out md]
Concept: tulanā — weighing two readings of the same instrument against each other; the
size-matched retry only means something as a COMPARISON, not as another lone verdict.
Source: contracts/L1b_size_matched_retry.md D3; e1b.yaml pre-registered decision rule.
Primitive: two E1-family GateReport JSONs -> markdown comparison table + per-hypothesis deltas.
"""
import argparse
import json
from pathlib import Path


def load_gate(path: str) -> dict:
    g = json.loads(Path(path).read_text(encoding="utf-8"))
    ev = json.loads(g["domain_gate"]["evidence"])
    return {"loop": g["loop"], "domain_verdict": g["domain_gate"]["verdict"],
            "contention": ev.get("contention", "?"), "summary": ev["summary"],
            "detail": ev["detail"]}


def _extra(detail: dict, hyp: str) -> str:
    """Hypothesis-specific context columns beyond value/threshold."""
    d = detail.get(hyp, {})
    if hyp == "H_report":
        p = d.get("permutation_p")
        curve = d.get("per_layer_rho_model_topk") or {}
        last = list(curve.values())[-1] if curve else None
        return f"p={p:.2e}, last-layer ρ={last}" if p is not None else ""
    if hyp == "H_bands":
        return f"bands={d.get('bands')}"
    if hyp == "H_modulation":
        return f"null={d.get('null_hit_rate_mean')}, band n={len(d.get('band_layers', []))}"
    return ""


def compare(a: dict, b: dict, la: str, lb: str) -> str:
    lines = [f"# Gate comparison: {la} ({a['loop']}) vs {lb} ({b['loop']})", "",
             f"- {la}: domain **{a['domain_verdict']}**, contention={a['contention']}",
             f"- {lb}: domain **{b['domain_verdict']}**, contention={b['contention']}", "",
             f"| hypothesis | {la} value | {lb} value | Δ | threshold | "
             f"{la} pass | {lb} pass | context ({lb}) |",
             "|---|---|---|---|---|---|---|---|"]
    for hyp in sorted(set(a["summary"]) | set(b["summary"])):
        sa, sb = a["summary"].get(hyp), b["summary"].get(hyp)
        if sa is None or sb is None:
            lines.append(f"| {hyp} | {'—' if sa is None else round(sa['value'], 4)} "
                         f"| {'—' if sb is None else round(sb['value'], 4)} | — | | | | |")
            continue
        delta = sb["value"] - sa["value"]
        lines.append(f"| {hyp} | {sa['value']:.4f} | {sb['value']:.4f} | {delta:+.4f} "
                     f"| {sb['threshold']} | {sa['pass']} | {sb['pass']} "
                     f"| {_extra(b['detail'], hyp)} |")
    return "\n".join(lines) + "\n"


def main(argv=None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gates", nargs=2, required=True)
    ap.add_argument("--labels", nargs=2, default=["A", "B"])
    ap.add_argument("--out", required=False)
    a = ap.parse_args(argv)
    md = compare(load_gate(a.gates[0]), load_gate(a.gates[1]), *a.labels)
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(md, encoding="utf-8")
        print(f"comparison written: {a.out}")
    else:
        print(md)


if __name__ == "__main__":
    main()
