"""Real steering runtime adapter — wraps prabodha's e4 steering composer.

Concept: the gateway is the app-facing proxy; this module holds the steering logic
reused from e4_cli (model loading, lens, injector, trace emission).

Primitive: SteeringRuntimeAdapter loads model+lens once at startup, exposes
async steer_stream(prompt, concept, alpha, arm) that yields TraceToken per step
then a completed LiveEpisode.
"""
import asyncio
import logging
from datetime import datetime
from typing import AsyncGenerator, Optional

import numpy as np

from prabodha.config import load
from prabodha.contracts.trace import TraceToken, SteerTrace
from prabodha.lens.adapter import LensAdapter, build_model
from prabodha.lens.e1_metrics import _concept_candidate_ids
from prabodha.steering.injector import ResidualInjector, entropy_observer
from prabodha.steering.timing import EntropyGated, Continuous, PrefillOnly, EveryK
from prabodha.steering.writer import plan_write
from steer_gateway.schema import LiveEpisode

logger = logging.getLogger(__name__)


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
    """Generate text, optionally capturing per-step token strings."""
    import hashlib
    import torch
    from transformers import LogitsProcessorList

    ids = tok(prompt, return_tensors="pt")["input_ids"].to(hf.device)
    kw = dict(
        max_new_tokens=max_new, do_sample=False, pad_token_id=tok.eos_token_id,
        logits_processor=LogitsProcessorList(processors)
    )
    if decoding and decoding.get("do_sample"):
        kw.update(do_sample=True, temperature=float(decoding["temperature"]))
        h = int(hashlib.sha256(f"{seed}|{stream_tag}".encode()).hexdigest()[:8], 16)
        torch.manual_seed(h)

    with torch.no_grad():
        out = hf.generate(ids, **kw)

    gen_ids = out[0, ids.shape[1]:]
    if step_texts is not None:
        step_texts.extend(tok.decode([int(t)]) for t in gen_ids.tolist())
    return tok.decode(gen_ids, skip_special_tokens=True)


def _build_trace_tokens(step_texts: list, entropies: list,
                        write_events: list | None) -> list[TraceToken]:
    """Build per-step TraceToken records from collected evidence."""
    gated_steps = {int(s) for s, _ in (write_events or [])}
    n = min(len(step_texts), len(entropies))
    return [
        TraceToken(
            t=i, token=str(step_texts[i]), entropy=float(entropies[i]),
            gated=i in gated_steps
        )
        for i in range(n)
    ]


class SteeringRuntimeAdapter:
    """Real steering runtime: loads model + lens, runs actual steering episodes."""

    def __init__(self, model_config_path: str, lens_file: str, site_layer: int,
                 max_new_tokens: int = 100, min_gap: int = 2, tau_percentile: int = 60):
        """Initialize runtime with model, lens, and steering parameters.

        Args:
            model_config_path: Path to model config YAML (e.g., configs/models/qwen3.yaml)
            lens_file: Path to fitted lens .pt file
            site_layer: Layer index for steering write (e.g., 24)
            max_new_tokens: Max tokens to generate per episode
            min_gap: Min gap between gated writes (temporal hygiene)
            tau_percentile: Entropy percentile threshold for gating
        """
        logger.info("Loading model from %s", model_config_path)
        model_cfg = load(model_config_path)
        self.hf, self.tok = build_model(model_cfg)
        self.model_id = model_cfg.get("hf_id", "unknown-model")

        logger.info("Loading lens from %s", lens_file)
        self.adapter = LensAdapter("jacobian").load(lens_file)

        self.site_layer = int(site_layer)
        self.max_new_tokens = int(max_new_tokens)
        self.min_gap = int(min_gap)
        self.tau_percentile = int(tau_percentile)

        # Precompute lens Jacobian and unembedding for steering
        logger.info("Precomputing Jacobian and unembedding at layer %d", self.site_layer)
        self.J = self.adapter._lens.jacobians[self.site_layer].float().cpu().numpy()
        self.U = self.hf.get_output_embeddings().weight.detach().float().cpu().numpy()

        logger.info("Runtime initialized: model_id=%s, site_layer=%d", self.model_id, self.site_layer)

    async def steer_stream(
        self, prompt: str, concept: str, alpha: Optional[float], arm: str
    ) -> AsyncGenerator[TraceToken | LiveEpisode, None]:
        """Steer an episode: generate baseline, then steered continuation.

        Yields:
            - TraceToken for each decode step of the STEERED arm
            - LiveEpisode with baseline_text, steered_text, and complete trace

        Args:
            prompt: User prompt
            concept: Steering concept (e.g., "fire", "honesty")
            alpha: Steering intensity (None -> use default from lens)
            arm: "baseline", "entropy_gated", "continuous", "prefill_only", or "rate_matched"
        """
        try:
            # Use default alpha if not provided
            if alpha is None:
                alpha = 0.3  # calibrated default from L3/L4

            alpha = float(alpha)

            # Resolve concept to token ids (single-token preference, but graceful fallback)
            logger.info("Resolving concept '%s' to token ids", concept)
            devs = []
            cids = _concept_candidate_ids(
                self.tok, concept, None, devs, policy="single_token_only"
            )

            if not cids:
                # Fallback: try multi-token or report error
                logger.warning("Concept '%s' has no single-token variant; attempting multi-token", concept)
                # For now, we'll encode the concept string directly if it fails
                try:
                    enc = self.tok(concept, return_tensors="pt")
                    concept_ids = [int(cid) for cid in enc["input_ids"][0].tolist() if cid != self.tok.eos_token_id]
                    if not concept_ids:
                        raise ValueError(f"Concept '{concept}' resolves to no token ids")
                except Exception as e:
                    logger.error("Failed to resolve concept '%s': %s", concept, e)
                    raise
            else:
                concept_ids = sorted(set(cids.values()))

            logger.info("Resolved concept to ids: %s", concept_ids)

            # Plan the write command (steering direction + alpha)
            ids = sorted(concept_ids)
            norm_cap_rel = 1.0  # don't cap (alpha already scales)
            cmd = plan_write(self.J, self.U[ids], self.site_layer, ids,
                           alpha=alpha, norm_cap_rel=norm_cap_rel, positions="last")

            # Get the layer module for injection
            import jlens
            lm = jlens.from_hf(self.hf, self.tok)
            layer_module = lm.layers[self.site_layer]

            # Generate baseline (no steering)
            logger.info("Generating baseline continuation")
            baseline_step_texts = []
            baseline_trace = EntropyTrace()
            baseline_procs = [baseline_trace.processor()]
            baseline_text = _generate(
                self.hf, self.tok, prompt, self.max_new_tokens, baseline_procs,
                seed=42, stream_tag="baseline|" + concept,
                step_texts=baseline_step_texts
            )
            logger.info("Baseline: %d tokens", len(baseline_step_texts))

            # Compute tau threshold from baseline entropies (tau_percentile)
            if baseline_trace.entropies:
                tau = float(np.percentile(baseline_trace.entropies, self.tau_percentile))
            else:
                tau = 1.0
            logger.info("Computed tau=%.3f from baseline (percentile %d)", tau, self.tau_percentile)

            # Create timing policy based on arm
            policy_factory = self._make_policy_factory(arm, tau)

            # Generate steered (with steering applied)
            logger.info("Generating steered continuation (arm=%s)", arm)
            steered_step_texts = []
            steered_trace = EntropyTrace(policy_factory() if policy_factory else None)
            steered_procs = [steered_trace.processor()]

            if arm == "baseline":
                # No steering, just reuse baseline
                steered_text = baseline_text
                steered_step_texts = baseline_step_texts
                write_events = []
            else:
                policy = steered_trace._policy
                with ResidualInjector(layer_module, cmd, policy=policy):
                    steered_text = _generate(
                        self.hf, self.tok, prompt, self.max_new_tokens, steered_procs,
                        seed=42, stream_tag="steered|" + concept,
                        step_texts=steered_step_texts
                    )

                write_events = list(getattr(policy, "write_events", []) or [])

            logger.info("Steered: %d tokens, %d writes applied", len(steered_step_texts), len(write_events))

            # Build trace tokens
            trace_tokens = _build_trace_tokens(steered_step_texts, steered_trace.entropies, write_events)

            # Emit trace tokens as SSE events
            for tok_record in trace_tokens:
                yield tok_record
                # Small async yield to let the event stream flow
                await asyncio.sleep(0)

            # Build and emit the final SteerTrace
            now = datetime.utcnow().isoformat() + "Z"
            steer_trace = SteerTrace(
                model_id=self.model_id,
                prompt=prompt,
                concept=concept,
                arm=arm,
                seed=42,
                alpha=alpha,
                tau_percentile=self.tau_percentile,
                site_layer=self.site_layer,
                tokens=trace_tokens,
                readback=None,
                behavioral_hit=None,
                gate_ref=None,
                created_at=now,
            )

            # Yield the complete LiveEpisode
            episode = LiveEpisode(
                model_id=self.model_id,
                prompt=prompt,
                concept=concept,
                arm=arm,
                site_layer=self.site_layer,
                alpha=alpha,
                baseline_text=baseline_text,
                steered_text=steered_text,
                trace=steer_trace,
                readback=None,
                behavioral_hit=None,
                created_at=now,
            )

            logger.info("Episode complete: baseline=%d chars, steered=%d chars",
                       len(baseline_text), len(steered_text))
            yield episode

        except Exception as e:
            logger.error("Steering error: %s", e, exc_info=True)
            raise

    def _make_policy_factory(self, arm: str, tau: float):
        """Factory for timing policies based on arm name."""
        if arm == "baseline":
            return None  # No policy for baseline
        elif arm == "entropy_gated":
            return lambda: EntropyGated(tau, min_gap=self.min_gap)
        elif arm == "continuous":
            return lambda: Continuous()
        elif arm == "prefill_only":
            return lambda: PrefillOnly()
        elif arm.startswith("rate_matched_") or arm == "rate_matched":
            # Parse k from "rate_matched_k" or default to 2
            k = 2
            if "_" in arm:
                try:
                    k = int(arm.split("_")[-1])
                except (ValueError, IndexError):
                    pass
            return lambda: EveryK(k)
        else:
            logger.warning("Unknown arm '%s', defaulting to entropy_gated", arm)
            return lambda: EntropyGated(tau, min_gap=self.min_gap)
