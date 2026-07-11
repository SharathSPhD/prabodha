"""CLI entry point for L23 hardening loop.

Concept: pratirodha (hardening/resistance). Orchestrates the fused prayoga↔prabodha loop:
  1. Load config (PRE-REGISTERED hypotheses, corpora sizes, hyperparameters).
  2. Load harmful and harmless corpora from disk.
  3. Run the hardening loop (direction extraction, layer scan, four arms, hypothesis verification).
  4. Emit gates/gate_L23_harden.json.

Source: L23 worklist; dispatch scripts/dispatch/l23/run.sh.
"""
import argparse
import json
import logging
from pathlib import Path

import yaml

from prabodha.hardening.harden_loop import (
    HardeningConfig,
    run_hardening_loop,
    result_to_gate_json,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger(__name__)


def load_corpus(path: str, max_lines: int | None = None) -> list[str]:
    """Load text corpus from file (one line per prompt)."""
    lines = []
    try:
        with open(path, "r") as f:
            for i, line in enumerate(f):
                if max_lines and i >= max_lines:
                    break
                stripped = line.rstrip("\n")
                if stripped:
                    lines.append(stripped)
        logger.info(f"Loaded {len(lines)} texts from {path}")
        return lines
    except FileNotFoundError:
        logger.warning(f"Corpus not found at {path}; using empty list")
        return []


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(
        description="L23: prayoga↔prabodha jailbreak→harden loop"
    )
    ap.add_argument("--model", required=True,
                    help="HF model ID (e.g., 'Qwen/Qwen3-4B-Instruct-2507')")
    ap.add_argument("--config", required=True,
                    help="Path to e_l23_harden.yaml config")
    ap.add_argument("--prayoga-path", default=None,
                    help="Path to prayoga clone (for soft import)")
    ap.add_argument("--out", required=True,
                    help="Output path for gate_L23_harden.json")
    ap.add_argument("--seed", type=int, default=None,
                    help="Override config seed (for parameter sweeps)")
    ap.add_argument("--write-layer", type=int, default=None,
                    help="Override config write_layer (for manual calibration)")
    a = ap.parse_args(argv)

    logger.info("L23: Loading configuration...")
    with open(a.config, "r") as f:
        cfg_dict = yaml.safe_load(f)

    # Load corpora
    logger.info("L23: Loading corpora...")
    harmful_train = load_corpus(
        cfg_dict["corpora"]["harmful_source"],
        max_lines=cfg_dict["corpora"].get("train_harmful_count")
    )
    harmless_train = load_corpus(
        cfg_dict["corpora"]["harmless_source"],
        max_lines=cfg_dict["corpora"].get("train_harmless_count")
    )
    harmful_test = load_corpus(
        cfg_dict["corpora"]["harmful_source"],
        max_lines=cfg_dict["corpora"].get("test_harmful_count")
    )
    harmless_test = load_corpus(
        cfg_dict["corpora"]["harmless_source"],
        max_lines=cfg_dict["corpora"].get("test_harmless_count")
    )

    # Build HardeningConfig
    write_layer = (a.write_layer if a.write_layer is not None
                   else cfg_dict["injection"].get("write_layer"))
    seed = a.seed if a.seed is not None else cfg_dict.get("random_seed", 42)

    config = HardeningConfig(
        model_id=a.model,
        harmful_texts=harmful_train,
        harmless_texts=harmless_train,
        test_harmful_texts=harmful_test,
        test_harmless_texts=harmless_test,
        candidate_layers=cfg_dict["direction"]["candidate_layers"],
        write_layer=write_layer,
        coeff=float(cfg_dict["injection"]["coeff"]),
        tau_percentile=float(cfg_dict["entropy_gating"]["tau_percentile"]),
        min_gap=int(cfg_dict["entropy_gating"]["min_gap"]),
        max_new_tokens=int(cfg_dict["injection"]["max_new_tokens"]),
        seed=seed,
        hypotheses=cfg_dict.get("hypotheses"),
    )

    logger.info(f"L23: Configuration loaded: model={config.model_id}, "
                f"harmful_train={len(config.harmful_texts)}, "
                f"harmful_test={len(config.test_harmful_texts)}")

    # Run loop
    logger.info("L23: Starting hardening loop...")
    result = run_hardening_loop(config, prayoga_path=a.prayoga_path)

    # Convert to gate JSON
    gate_json = result_to_gate_json(result, loop_label="L23")

    # Write output
    Path(a.out).write_text(json.dumps(gate_json, indent=2))
    logger.info(f"L23: Gate written to {a.out}")

    # Print summary
    domain_verdict = gate_json["domain_gate"]["verdict"]
    evidence = json.loads(gate_json["domain_gate"]["evidence"])
    logger.info(f"L23: Domain gate verdict: {domain_verdict}")
    logger.info(f"L23: Hypotheses verdicts: {evidence['hypotheses']}")
    logger.info(f"L23: tau = {evidence['tau']:.4f}")

    print(json.dumps(gate_json, indent=2))


if __name__ == "__main__":
    main()
