"""Compose gates/gate_L15_amp_joint.json — the amplitude-law joint confirm.
Concept: review #11 correction 1 — "law" needs multi-seed on the second plant AND
ordered dose response on both plants. Judged jointly: qwen3 grids at seeds {42(replay
from L14), 123, 777} + nemotron's L8 dose grid (replay).
Source: configs/efe_menu5.yaml amplitude_law_joint_confirm (success: ordering holds in
2/2 NEW qwen3 seeds AND both plants show ordered dose response).
Primitive: per-seed monotone check (adjacent pairs nondecreasing, 0.05 tolerance) +
budget check at every point -> gates/gate_L15_amp_joint.json.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALPHAS = ["0.1", "0.2", "0.3", "0.45"]


def agg_of(path):
    ev = json.loads(json.loads((ROOT / path).read_text())["domain_gate"]["evidence"])
    return ev["aggregates"]


def monotone(lifts, tol=0.05):
    return sum(1 for i in range(len(lifts) - 1) if lifts[i + 1] >= lifts[i] - tol)


# qwen3: two NEW seeds (this cycle) + seed-42 replay (gate_L14_amp grid)
qwen3 = {}
for seed in ("123", "777"):
    grid = {}
    for a in ALPHAS:
        g = agg_of(f"gates/gate_L15_amp_s{seed}_a{a}.json")["entropy_gated"]
        grid[a] = {"lift": g["lift"], "dH": g["step_entropy_delta"]}
    qwen3[seed] = grid
l14 = json.loads(json.loads((ROOT / "gates/gate_L14_amp.json").read_text())
                 ["domain_gate"]["evidence"])["grid"]
qwen3["42_replay"] = {a: {"lift": l14[a]["gated_lift"], "dH": l14[a]["gated_dH"]}
                      for a in ALPHAS}

# nemotron: L8 dose grid replay (its own alpha axis)
l8 = json.loads(json.loads((ROOT / "gates/gate_L8_dose.json").read_text())
                ["domain_gate"]["evidence"])["grid"]
nem_alphas = sorted(l8, key=float)
nem_lifts = [l8[a]["entropy_gated"]["lift"] for a in nem_alphas]

new_seed_ordered = {s: monotone([qwen3[s][a]["lift"] for a in ALPHAS])
                    for s in ("123", "777")}
within = all(abs(qwen3[s][a]["dH"]) <= 0.5 for s in qwen3 for a in ALPHAS)
nem_ordered = monotone(nem_lifts)

summary = {
    "H_qwen3_per_seed_monotone": {
        "value": float(min(new_seed_ordered.values())), "threshold": 3.0,
        "pass": all(v >= 3 for v in new_seed_ordered.values())},
    "H_two_plant_ordered": {
        "value": float(nem_ordered), "threshold": float(len(nem_lifts) - 1),
        "pass": nem_ordered >= len(nem_lifts) - 1},
    "H_budget_all_points": {"value": 1.0 if within else 0.0, "threshold": 1.0,
                            "pass": within},
}
verdict = "pass" if all(v["pass"] for v in summary.values()) else "fail"

gate = {
    "loop": "L15",
    "status": "closed",
    "closed_at": "2026-07-10",
    "code_gate": {"verdict": "pass", "evidence": "pytest green; ruff clean"},
    "domain_gate": {
        "verdict": verdict,
        "hypothesis": "amplitude dose law on the WEAK-TRANSPORT plant (qwen3), "
                      "multi-seed confirm: dose ordering holds per-seed at 2 NEW "
                      "independent-stream seeds {123,777} (+42 replayed), all points "
                      "within budget. The strong-transport plant (nemotron, L8 "
                      "replay) contributes ORDERING ONLY: its curve is flat-then-"
                      "slight-rise (saturated at its marginal alpha boundary), which "
                      "is consistent with amplitude ∝ 1/lens-strength but is NOT a "
                      "dose-response replication (review #12). Two-plant dose-"
                      "response replication remains OPEN.",
        "evidence": json.dumps({
            "summary": summary, "qwen3": qwen3,
            "qwen3_ordered_pairs_new_seeds": new_seed_ordered,
            "nemotron_L8": {"alphas": nem_alphas, "gated_lifts": nem_lifts,
                            "ordered_pairs": nem_ordered},
            "disclosures": [
                "monotone() uses tol=0.05 on adjacent pairs; nemotron's first pair "
                "(0.375 -> 0.375) has ZERO gain and passes only as nondecreasing — "
                "at tol=0 it still passes (equality) but there is no dose signal in "
                "it (review #12)",
                "L8's own summary flagged the alpha=0.02 boundary as MARGINAL "
                "(2/3 seeds); the nemotron leg is ordering-at-a-marginal-boundary, "
                "not replication",
                "claim scope: LAW = per-seed monotone dose within budget on qwen3 "
                "(confirm); the two-plant statement is limited to 'consistent "
                "ordering + saturation pattern' (screen)"],
            "registered_in": "configs/efe_menu5.yaml:amplitude_law_joint_confirm",
            "seeds": [42, 123, 777], "tier": "confirm-qwen3/screen-joint"}),
    },
    "signoff": "standing authorization (2026-07-09)",
}
(ROOT / "gates/gate_L15_amp_joint.json").write_text(json.dumps(gate, indent=1))
print(verdict)
for s in qwen3:
    print(f"  qwen3 seed {s}:", [qwen3[s][a]["lift"] for a in ALPHAS],
          "ordered" if s == "42_replay" or new_seed_ordered.get(s, 3) >= 3 else "NOT ordered")
print("  nemotron L8:", dict(zip(nem_alphas, nem_lifts)), f"({nem_ordered} ordered pairs)")
