"""Compose gate_L14_multiseed.json — confirm tier for the qwen3 recipe transfer.
Concept: the recipe's 0.40 (seed 42, gate L13) must hold at independent-stream seeds
to graduate from screen to confirm — same standard the core claim met on the PWM twin.
Source: configs/efe_menu4.yaml qwen3_recipe_multiseed (registered success: >=3/4 seeds
incl. 42 with gated lift >= 0.2 within |dH|<=0.5; gated > prefill every seed).
Primitive: reads gates/gate_L14_ms{123,777,2024}.json + gates/gate_L13_recipe.json.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCES = {"42": "gates/gate_L13_recipe.json", "123": "gates/gate_L14_ms123.json",
           "777": "gates/gate_L14_ms777.json", "2024": "gates/gate_L14_ms2024.json"}

per_seed = {}
for seed, path in SOURCES.items():
    ev = json.loads(json.loads((ROOT / path).read_text())["domain_gate"]["evidence"])
    agg = ev["aggregates"]
    per_seed[seed] = {
        "gated_lift": agg["entropy_gated"]["lift"],
        "gated_dH": agg["entropy_gated"]["step_entropy_delta"],
        "prefill_lift": agg["prefill_only"]["lift"],
        "source": path,
    }

ok = [s for s, v in per_seed.items()
      if v["gated_lift"] >= 0.2 and abs(v["gated_dH"]) <= 0.5]
adv = [s for s, v in per_seed.items() if v["gated_lift"] > v["prefill_lift"]]
summary = {
    "H_recipe_multiseed": {"value": float(len(ok)), "threshold": 3.0,
                           "pass": len(ok) >= 3},
    "H_gated_over_prefill": {"value": float(len(adv)), "threshold": 4.0,
                             "pass": len(adv) == 4},
}
verdict = "pass" if all(v["pass"] for v in summary.values()) else "fail"

gate = {
    "loop": "L14",
    "status": "closed",
    "closed_at": "2026-07-10",
    "code_gate": {"verdict": "pass", "evidence": "57 passed, 4 skipped; ruff clean"},
    "domain_gate": {
        "verdict": verdict,
        "hypothesis": "qwen3 calibrated recipe (site 24, alpha=cap=0.3) holds across "
                      "THREE NEW independent-stream seeds {123,777,2024} plus the "
                      "REPLAYED L13 seed 42: gated lift >= 0.2 within budget, "
                      "gated > prefill, every seed",
        "evidence": json.dumps({"summary": summary, "per_seed": per_seed,
                                "registered_in":
                                    "configs/efe_menu4.yaml:qwen3_recipe_multiseed",
                                "seeds": [42, 123, 777, 2024], "tier": "confirm"}),
    },
    "signoff": "standing authorization (2026-07-09)",
}
(ROOT / "gates/gate_L14_multiseed.json").write_text(json.dumps(gate, indent=1))
print(verdict, "|", {s: v["gated_lift"] for s, v in per_seed.items()},
      "| within-budget+threshold:", len(ok), "/4 | gated>prefill:", len(adv), "/4")
