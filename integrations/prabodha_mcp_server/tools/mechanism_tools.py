"""Graded hardening mechanism tools — list, recommend, characterize, harden.

Concept: pratyabhijñā (recognition) + krama (graded sequence) steering menu.
Source: prabodha.steering.mechanisms module; L26 recognition-gate branch.
Primitive: prompt_harden, component_restoration_hook, recommend, load_matrix.
"""
from pathlib import Path
from typing import Any
import sys

# Add src to path early for all functions
def _ensure_prabodha_in_path():
    """Ensure prabodha.steering.mechanisms can be imported."""
    # Try canonical path first
    canonical_src = Path(__file__).resolve().parent.parent.parent.parent / "src"
    if canonical_src.exists() and str(canonical_src) not in sys.path:
        sys.path.insert(0, str(canonical_src))
        return

    # Try relative to CWD (for worktree development)
    cwd = Path.cwd()
    for candidate in [cwd] + list(cwd.parents):
        src = candidate / "src"
        if (src / "prabodha" / "steering" / "mechanisms.py").exists():
            if str(src) not in sys.path:
                sys.path.insert(0, str(src))
            return


async def list_mechanisms_impl() -> dict[str, Any]:
    """
    Return the graded library: for each REGISTRY mechanism, its key/name/space/weights/tier/summary.
    Pure library read; must work with zero args.

    Returns: dict with keys:
      - status: "ok" | "error"
      - mechanisms: list of dicts, each with:
        - key: mechanism identifier (e.g., "prompt_refusal_gentle")
        - name: human-readable name
        - space: 'prompt' | 'activation'
        - weights: 'both' (works on any model) | 'open' (needs open weights)
        - tier: 1 (gentle) to 5 (aggressive)
        - summary: description
        - profiles: dict of {model_id: capability_dict} if measured
      - count: total mechanism count
      - error: error message (if status != "ok")
    """
    try:
        # Ensure prabodha is in path
        _ensure_prabodha_in_path()

        # Import here to avoid torch at module level
        from prabodha.steering.mechanisms import REGISTRY

        mechanisms = []
        for key, mech in REGISTRY.items():
            # Build profiles dict: {model_id: {asr_reduction, over_refusal_cost, coherence, ...}}
            profiles = {}
            if mech.profiles:
                for model_id, cap in mech.profiles.items():
                    profiles[model_id] = {
                        "asr_reduction": cap.asr_reduction,
                        "over_refusal_cost": cap.over_refusal_cost,
                        "coherence": cap.coherence,
                        "write_sparsity": cap.write_sparsity,
                        "note": cap.note,
                    }

            mechanisms.append({
                "key": mech.key,
                "name": mech.name,
                "space": mech.space,
                "weights": mech.weights,
                "tier": mech.tier,
                "summary": mech.summary,
                "profiles": profiles,
            })

        return {
            "status": "ok",
            "mechanisms": sorted(mechanisms, key=lambda m: m["tier"]),
            "count": len(mechanisms),
            "error": None,
        }
    except Exception as e:
        return {
            "status": "error",
            "mechanisms": [],
            "count": 0,
            "error": str(e),
        }


async def recommend_mechanism_impl(
    weights: str = "open",
    max_over_refusal: float = 0.3,
    min_coherence: float = 0.6,
) -> dict[str, Any]:
    """
    Return a graded menu of mechanisms by tradeoff constraints.

    Args:
      - weights: 'open' (needs open weights) | 'closed' (prompt-only, works on any model)
      - max_over_refusal: max tolerated benign over-refusal (0–1)
      - min_coherence: min tolerated output coherence (0–1)

    Returns: dict with keys:
      - status: "ok" | "error"
      - recommended: list of mechanism dicts (gentle→aggressive), each with:
        - key, name, space, weights, tier, summary, profiles
      - rationale: brief description of the filter applied
      - count: number of mechanisms matching constraints
      - error: error message (if status != "ok")
    """
    try:
        # Ensure prabodha is in path
        _ensure_prabodha_in_path()

        # Import here to avoid torch at module level
        from prabodha.steering.mechanisms import recommend

        if weights not in ("open", "closed"):
            return {
                "status": "error",
                "recommended": [],
                "rationale": "",
                "count": 0,
                "error": f"weights must be 'open' or 'closed', got {weights}",
            }

        recommended_mechs = recommend(
            weights=weights,
            max_over_refusal=max_over_refusal,
            min_coherence=min_coherence,
        )

        mechanisms = []
        for mech in recommended_mechs:
            profiles = {}
            if mech.profiles:
                for model_id, cap in mech.profiles.items():
                    profiles[model_id] = {
                        "asr_reduction": cap.asr_reduction,
                        "over_refusal_cost": cap.over_refusal_cost,
                        "coherence": cap.coherence,
                        "write_sparsity": cap.write_sparsity,
                        "note": cap.note,
                    }

            mechanisms.append({
                "key": mech.key,
                "name": mech.name,
                "space": mech.space,
                "weights": mech.weights,
                "tier": mech.tier,
                "summary": mech.summary,
                "profiles": profiles,
            })

        # Build rationale
        if weights == "closed":
            rationale = "Prompt-only mechanisms (portable to closed-weight models via OpenRouter). "
        else:
            rationale = "Open-weight mechanisms (may require activation-space access). "

        rationale += (
            f"Filtered by max_over_refusal={max_over_refusal} and min_coherence={min_coherence}. "
            f"Result: {len(mechanisms)} mechanism(s) from gentle(tier 1) to aggressive(tier 5)."
        )

        return {
            "status": "ok",
            "recommended": mechanisms,
            "rationale": rationale,
            "count": len(mechanisms),
            "error": None,
        }
    except Exception as e:
        return {
            "status": "error",
            "recommended": [],
            "rationale": "",
            "count": 0,
            "error": str(e),
        }


async def characterize_model_impl(
    model_id: str,
    mode: str = "prompt",
) -> dict[str, Any]:
    """
    Return characterization data for a model's steering susceptibility.

    Args:
      - model_id: HuggingFace model id (e.g., "Qwen/Qwen3-4B")
      - mode: 'prompt' | 'weight' | 'both'
        - 'prompt': describe prompt-space jailbreak/defense (can run via OpenRouter/BYOK)
        - 'weight': describe white-box weight-space attacks (needs GPU + admin)
        - 'both': return both if available

    Returns: dict with keys:
      - status: "ok" | "error"
      - model: the model_id requested
      - mode_requested: the mode requested
      - characterization_description: plain text describing what WOULD be run
      - measured_data: dict with rows from gate_char_*.json if available, or null
      - data_source: where the data came from (file path or "not yet measured")
      - caveat: if data is from a single seed or is weak signal
      - error: error message (if status != "ok")
    """
    try:
        # Ensure prabodha is in path
        _ensure_prabodha_in_path()

        # Import here to avoid torch at module level
        from prabodha.steering.mechanisms import load_matrix

        if mode not in ("prompt", "weight", "both"):
            return {
                "status": "error",
                "model": model_id,
                "mode_requested": mode,
                "characterization_description": "",
                "measured_data": None,
                "data_source": "",
                "caveat": "",
                "error": f"mode must be 'prompt', 'weight', or 'both', got {mode}",
            }

        # Try to load measured data
        matrix = load_matrix("gates")
        measured_data = None
        data_source = "not yet measured"
        caveat = ""

        if model_id in matrix:
            measured_data = matrix[model_id]
            data_source = f"gates/gate_char_{model_id.replace('/', '_')}.json (inferred)"
            caveat = (
                "Measured data is from a single seed at a snapshot in time. "
                "Multi-seed confirm-tier characterization required for strong claims."
            )

        # Build characterization description
        if mode == "prompt":
            desc = (
                f"Prompt-space characterization of {model_id}:\n"
                f"1. Baseline jailbreak: run adversarial prompts (e.g., DAN, role-play jailbreaks)\n"
                f"   via BYOK (Anthropic, OpenAI) or OpenRouter (closed-weight proxy)\n"
                f"2. Defense experiments: apply prompt_refusal_gentle, firm, constitutional wrappers\n"
                f"3. Measure: attack success rate (ASR), benign over-refusal, coherence\n"
                f"4. Output: metrics for each defense tier (gentle→aggressive)\n"
                f"No GPU required; runs on any machine with BYOK/OpenRouter access."
            )
        elif mode == "weight":
            desc = (
                f"Weight-space (white-box) characterization of {model_id}:\n"
                f"1. Load the model (open-weight HuggingFace only; requires VRAM)\n"
                f"2. Measure the band workspace and harmful concept direction\n"
                f"3. Baseline attack: ablate the harmful concept direction (100% ASR)\n"
                f"4. Defense experiments: apply component_restoration_hook at various β settings\n"
                f"5. Measure: ASR reduction, output coherence, write sparsity\n"
                f"6. Output: ASR curves, prefill vs dense tradeoffs\n"
                f"Requires: GB10 GPU (or equiv VRAM), admin privileges for KILL_SWITCH check."
            )
        else:  # both
            desc = (
                f"Full characterization of {model_id} (prompt + weight space):\n"
                f"1. Run prompt-space jailbreak→defense experiments (no GPU)\n"
                f"2. Run white-box weight-space ablation→restoration experiments (GPU)\n"
                f"3. Cross-validate: compare prompt-space vs weight-space defense effectiveness\n"
                f"4. Output: unified model×mechanism matrix (gate_char_{model_id.replace('/', '_')}.json)\n"
            )

        return {
            "status": "ok",
            "model": model_id,
            "mode_requested": mode,
            "characterization_description": desc,
            "measured_data": measured_data,
            "data_source": data_source,
            "caveat": caveat,
            "error": None,
        }
    except Exception as e:
        return {
            "status": "error",
            "model": model_id,
            "mode_requested": mode,
            "characterization_description": "",
            "measured_data": None,
            "data_source": "",
            "caveat": "",
            "error": str(e),
        }


async def harden_prompt_impl(
    messages: list[dict],
    level: str = "firm",
) -> dict[str, Any]:
    """
    Apply prompt-space hardening to a message list.

    Args:
      - messages: list of dicts with 'role' and 'content' (standard Chat API format)
      - level: 'gentle' | 'firm' | 'constitutional'
        - 'gentle': light nudge to decline harmful requests (weak)
        - 'firm': explicit refusal across role-play/hypotheticals/ignore-instructions (medium)
        - 'constitutional': self-check-before-answer (lowest benign over-refusal)

    Returns: dict with keys:
      - status: "ok" | "error"
      - hardened_messages: list of dicts (messages list with system prompt prepended)
      - level_applied: the level that was applied
      - system_prompt: the system message that was prepended
      - caveat: "Prompt hardening alone does not prevent all jailbreaks; combine with other defenses."
      - error: error message (if status != "ok")
    """
    try:
        # Ensure prabodha is in path
        _ensure_prabodha_in_path()

        # Import here to avoid torch at module level
        from prabodha.steering.mechanisms import prompt_harden

        if level not in ("gentle", "firm", "constitutional"):
            return {
                "status": "error",
                "hardened_messages": [],
                "level_applied": "",
                "system_prompt": "",
                "caveat": "",
                "error": f"level must be 'gentle', 'firm', or 'constitutional', got {level}",
            }

        # Validate messages format
        if not isinstance(messages, list):
            return {
                "status": "error",
                "hardened_messages": [],
                "level_applied": "",
                "system_prompt": "",
                "caveat": "",
                "error": f"messages must be a list, got {type(messages).__name__}",
            }

        for msg in messages:
            if not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                return {
                    "status": "error",
                    "hardened_messages": [],
                    "level_applied": "",
                    "system_prompt": "",
                    "caveat": "",
                    "error": "Each message must be a dict with 'role' and 'content' keys",
                }

        # Apply hardening
        hardened = prompt_harden(messages, level=level)

        # Extract the system prompt for reporting
        system_prompt = ""
        if hardened and hardened[0].get("role") == "system":
            system_prompt = hardened[0].get("content", "")

        return {
            "status": "ok",
            "hardened_messages": hardened,
            "level_applied": level,
            "system_prompt": system_prompt,
            "caveat": (
                "Prompt hardening alone does not prevent all jailbreaks. "
                "Combine with weight-space defenses (activation hooks) for stronger protection. "
                "Always measure on real models before relying on any single defense."
            ),
            "error": None,
        }
    except Exception as e:
        return {
            "status": "error",
            "hardened_messages": [],
            "level_applied": "",
            "system_prompt": "",
            "caveat": "",
            "error": str(e),
        }
