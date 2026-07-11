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


def _resolve_corpus(path: str, prayoga_path: str | None) -> str:
    """Resolve a corpus path: literal if it exists, else under the prayoga clone.
    The harmful/benign batteries live in prayoga (dual-use; not vendored into this
    public repo), so `data/prompts/x.txt` resolves to `<prayoga>/data/prompts/x.txt`."""
    from pathlib import Path
    if Path(path).exists():
        return path
    if prayoga_path:
        cand = Path(prayoga_path) / path
        if cand.exists():
            return str(cand)
    return path  # let load_corpus warn


def load_corpus(path: str) -> list[str]:
    """Load a text corpus (one prompt per non-empty line). Returns ALL lines;
    the caller slices disjoint train/test splits (no leakage)."""
    from pathlib import Path
    p = Path(path)
    if not p.exists():
        logger.warning(f"Corpus not found at {path}; using empty list")
        return []
    lines = [ln.rstrip("\n") for ln in p.read_text().splitlines() if ln.strip()]
    logger.info(f"Loaded {len(lines)} texts from {path}")
    return lines


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

    # Load corpora, then slice DISJOINT train/test (no leakage): train = [:n_tr],
    # test = [n_tr : n_tr + n_te]. Corpora live in the prayoga clone (dual-use).
    logger.info("L23: Loading corpora...")
    corp = cfg_dict["corpora"]
    harmful_all = load_corpus(_resolve_corpus(corp["harmful_source"], a.prayoga_path))
    harmless_all = load_corpus(_resolve_corpus(corp["harmless_source"], a.prayoga_path))
    n_htr, n_hte = corp.get("train_harmful_count", 20), corp.get("test_harmful_count", 10)
    n_str, n_ste = corp.get("train_harmless_count", 20), corp.get("test_harmless_count", 10)
    harmful_train, harmful_test = harmful_all[:n_htr], harmful_all[n_htr:n_htr + n_hte]
    harmless_train, harmless_test = harmless_all[:n_str], harmless_all[n_str:n_str + n_ste]
    if not harmful_train or not harmless_train:
        raise SystemExit(f"empty corpora — harmful={len(harmful_all)} harmless={len(harmless_all)}; "
                         f"check --prayoga-path (looked up {corp['harmful_source']})")
    if len(harmful_all) < n_htr + n_hte or len(harmless_all) < n_str + n_ste:
        logger.warning(f"corpus smaller than train+test request; test split may be short "
                       f"(harmful {len(harmful_all)} < {n_htr + n_hte}, "
                       f"harmless {len(harmless_all)} < {n_str + n_ste})")

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
