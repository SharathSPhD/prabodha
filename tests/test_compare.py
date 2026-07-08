"""Unit tests for the gate comparison CLI (CPU, pure JSON)."""
import json

from prabodha.lens.compare_cli import compare, load_gate, main


def _gate(tmp_path, name, loop, rho, hit, verdict):
    detail = {
        "H_report": {"spearman_rho_model_topk_late_third": rho, "permutation_p": 1e-4,
                     "per_layer_rho_model_topk": {"0": 0.0, "34": 0.6}},
        "H_bands": {"cka_band_contrast": 0.3, "bands": [[0, 6], [6, 30], [30, 36]]},
        "H_modulation": {"instructed_concept_hit_rate_at5": hit, "null_hit_rate_mean": 0.01,
                         "band_layers": [12, 13]},
    }
    summary = {"H_report": {"value": rho, "threshold": 0.4, "pass": rho >= 0.4},
               "H_bands": {"value": 0.3, "threshold": 0.15, "pass": True},
               "H_modulation": {"value": hit, "threshold": 0.5, "pass": hit >= 0.5}}
    gate = {"loop": loop, "status": "open",
            "code_gate": {"verdict": "pass", "evidence": "ok", "deviations": []},
            "domain_gate": {"verdict": verdict, "deviations": [],
                            "evidence": json.dumps({"summary": summary, "detail": detail,
                                                    "contention": "none"})}}
    p = tmp_path / name
    p.write_text(json.dumps(gate))
    return p


def test_compare_table_carries_values_and_deltas(tmp_path):
    a = _gate(tmp_path, "a.json", "L1", 0.18, 0.10, "fail")
    b = _gate(tmp_path, "b.json", "L1b", 0.45, 0.35, "fail")
    md = compare(load_gate(str(a)), load_gate(str(b)), "4B", "27B")
    assert "| H_report | 0.1800 | 0.4500 | +0.2700 | 0.4 | False | True" in md
    assert "H_modulation" in md and "+0.2500" in md
    assert "bands=[[0, 6], [6, 30], [30, 36]]" in md


def test_compare_cli_writes_file(tmp_path):
    a = _gate(tmp_path, "a.json", "L1", 0.18, 0.10, "fail")
    b = _gate(tmp_path, "b.json", "L1b", 0.20, 0.12, "fail")
    out = tmp_path / "cmp.md"
    main(["--gates", str(a), str(b), "--labels", "4B", "27B", "--out", str(out)])
    assert out.read_text().startswith("# Gate comparison: 4B (L1) vs 27B (L1b)")
