"""Real steering runtime adapter — wraps prabodha's e4 steering composer.

Concept: the gateway is the app-facing proxy; this module holds the steering logic
reused from e4_cli (model loading, lens, injector, trace emission).

Primitive: SteeringRuntimeAdapter loads model+lens once at startup, exposes
async steer_stream(prompt, concept, alpha, arm, direction_spec) that yields TraceToken per step
then a completed LiveEpisode. Supports concept-based, contrastive, and vector steering modes.

Extension: direction_spec enables contrastive (CAA-style) and explicit vector steering modes.
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
from prabodha.steering.direction import contrastive_direction, apply_direction_write
from steer_gateway.schema import LiveEpisode, DirectionSpec

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

    def __init__(self, model_config_path: str, lens_file: str | None = None,
                 site_layer: int | None = None,
                 max_new_tokens: int = 100, min_gap: int = 2, tau_percentile: int = 60):
        """Initialize a real steering runtime for a chosen model.

        Args:
            model_config_path: EITHER a model-config YAML path OR a bare HuggingFace model id
                (e.g. "google/gemma-2-2b-it"). A bare id builds a default config — this is what
                lets the gateway serve ANY chosen model, not only the pre-configured plant.
            lens_file: Path to a committed, pre-fitted Jacobian lens. Present ONLY for models
                that already have one (see manager.LENS_REGISTRY); fitting a lens is an hours-long
                GPU job that cannot run on the request path. When a lens is present, concept
                steering uses the full lens+Jacobian method. When it is absent, steering uses
                REAL contrastive-direction (CAA) writes — a genuine difference-in-means over
                actual activations. Both are real steering; neither is a stub.
            site_layer: Steering write layer. When None, the workspace-band heuristic (~62% depth).
        """
        import os as _os
        if isinstance(model_config_path, str) and model_config_path.endswith((".yaml", ".yml")) and _os.path.exists(model_config_path):
            model_cfg = load(model_config_path)
        else:
            model_cfg = {"hf_id": model_config_path, "dtype": "bf16", "device": "cuda", "trust_remote_code": False}
        logger.info("Loading model %s", model_cfg["hf_id"])
        self.hf, self.tok = build_model(model_cfg)
        self.model_id = model_cfg.get("hf_id", "unknown-model")

        n_layers = int(self.hf.config.num_hidden_layers)
        # Resolve the lens path robustly: registry paths are repo-relative, but the working
        # directory varies by container. Try the path as-is and under known roots.
        resolved_lens = None
        if lens_file:
            roots = ["", _os.environ.get("PRABODHA_ROOT", "/repo"), "/repo", _os.getcwd(), "/lens"]
            for r in roots:
                cand = lens_file if not r else _os.path.join(r, lens_file)
                if _os.path.exists(cand):
                    resolved_lens = cand
                    break
            if resolved_lens is None:
                logger.warning("Lens file %s not found under any known root; falling back to contrastive steering", lens_file)
        lens_file = resolved_lens
        self.has_lens = bool(lens_file) and _os.path.exists(lens_file)
        # Workspace-band heuristic when no explicit site_layer is given (lensless models).
        self.site_layer = int(site_layer) if site_layer is not None else int(0.62 * n_layers)
        self.max_new_tokens = int(max_new_tokens)
        self.min_gap = int(min_gap)
        self.tau_percentile = int(tau_percentile)

        if self.has_lens:
            logger.info("Loading pre-fitted lens from %s; precomputing Jacobian at layer %d", lens_file, self.site_layer)
            self.adapter = LensAdapter("jacobian").load(lens_file)
            self.J = self.adapter._lens.jacobians[self.site_layer].float().cpu().numpy()
            self.U = self.hf.get_output_embeddings().weight.detach().float().cpu().numpy()
        else:
            self.adapter = None
            self.J = None
            self.U = None

        logger.info("Runtime ready: model_id=%s site_layer=%d method=%s",
                    self.model_id, self.site_layer, "lens+jacobian" if self.has_lens else "contrastive")

    def unload(self) -> None:
        """Release the model + lens from GPU memory (dynamic, no persistent holding)."""
        try:
            import torch
            for attr in ("hf", "adapter", "J", "U"):
                if getattr(self, attr, None) is not None:
                    setattr(self, attr, None)
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
        except Exception as e:
            logger.warning("unload error for %s: %s", getattr(self, "model_id", "?"), e)

    def _extract_residuals_at_site(self, texts: list[str]) -> np.ndarray:
        """Extract residual activations at site_layer for a batch of texts.

        Args:
            texts: List of text strings.

        Returns:
            Activations array of shape [len(texts), hidden_dim] (float32, CPU numpy).

        This method forward-passes each text through the model with hooks attached
        to the site_layer, capturing the residual stream at the last token position.
        Used for contrastive direction computation.
        """
        import torch
        import jlens

        activations_list = []
        lm = jlens.from_hf(self.hf, self.tok)
        layer_module = lm.layers[self.site_layer]

        # Hook to capture residual activations at the site layer (last token only)
        captured_acts = None

        def hook_fn(module, input, output):
            nonlocal captured_acts
            # output is the residual stream tensor [batch, seq_len, hidden_dim]
            if isinstance(output, tuple):
                output = output[0]
            # Capture activations at the last token position
            captured_acts = output[:, -1, :].detach().float().cpu()

        hook_handle = layer_module.register_forward_hook(hook_fn)

        try:
            with torch.no_grad():
                for text in texts:
                    ids = self.tok(text, return_tensors="pt")["input_ids"].to(self.hf.device)
                    if ids.shape[-1] == 0:
                        # A text that tokenizes to zero tokens (e.g. empty string) would crash the
                        # forward pass; skip it — contrastive_direction averages, so counts may differ.
                        continue
                    _ = self.hf(ids)
                    if captured_acts is not None:
                        # Flatten to a 1D [hidden_dim] vector regardless of the captured tensor's
                        # rank (some model layers emit [1, d] or [1, 1, d] at the last position).
                        activations_list.append(np.asarray(captured_acts).reshape(-1))
                    captured_acts = None
        finally:
            hook_handle.remove()

        if not activations_list:
            raise ValueError("No activations captured; check text encoding")

        # Guarantee a 2D [n, hidden_dim] array for contrastive_direction (never [n, 1, d]).
        arr = np.asarray(activations_list, dtype=np.float32)
        if arr.ndim != 2:
            arr = arr.reshape(arr.shape[0], -1)
        return arr

    async def steer_stream(
        self, prompt: str, concept: str, alpha: Optional[float], arm: str,
        direction_spec: Optional[DirectionSpec] = None
    ) -> AsyncGenerator[TraceToken | LiveEpisode, None]:
        """Steer an episode: generate baseline, then steered continuation.

        Yields:
            - TraceToken for each decode step of the STEERED arm
            - LiveEpisode with baseline_text, steered_text, and complete trace

        Args:
            prompt: User prompt
            concept: Steering concept (e.g., "fire", "honesty") — used for identification
            alpha: Steering intensity (None -> use default from lens)
            arm: "baseline", "entropy_gated", "continuous", "prefill_only", or "rate_matched"
            direction_spec: Optional DirectionSpec for contrastive or vector steering.
                           If None, uses concept-based steering (legacy mode).
        """
        try:
            # Use default alpha if not provided
            if alpha is None:
                alpha = 0.3  # calibrated default from L3/L4

            alpha = float(alpha)

            # Determine steering direction and source
            direction_source = None
            cmd = None

            if direction_spec is not None and direction_spec.mode != "concept":
                # CONTRASTIVE or VECTOR steering mode
                if direction_spec.mode == "contrastive":
                    logger.info("Computing contrastive direction from %d positive and %d negative exemplars",
                               len(direction_spec.pos_texts or []), len(direction_spec.neg_texts or []))
                    if not direction_spec.pos_texts or not direction_spec.neg_texts:
                        raise ValueError("Contrastive mode requires both pos_texts and neg_texts")

                    # Extract residual activations
                    pos_acts = self._extract_residuals_at_site(direction_spec.pos_texts)
                    neg_acts = self._extract_residuals_at_site(direction_spec.neg_texts)

                    # Compute direction via contrastive_direction
                    direction = contrastive_direction(pos_acts, neg_acts, normalize=True)
                    logger.info("Computed contrastive direction (dim=%d, norm=%.3f)",
                               len(direction), float(np.linalg.norm(direction)))

                    # Create WriteCommand via apply_direction_write
                    cmd = apply_direction_write(
                        direction, layer=self.site_layer, alpha=alpha,
                        norm_cap_rel=1.0, positions="last",
                        meta={"concept": concept, "n_pos": len(direction_spec.pos_texts),
                              "n_neg": len(direction_spec.neg_texts)}
                    )
                    direction_source = f"contrastive:{concept}({len(direction_spec.pos_texts)}+/{len(direction_spec.neg_texts)}-)"

                elif direction_spec.mode == "vector":
                    logger.info("Using explicit vector steering (dim=%d)", len(direction_spec.vector or []))
                    if not direction_spec.vector:
                        raise ValueError("Vector mode requires a vector field")

                    # Normalize the provided vector
                    vector_array = np.asarray(direction_spec.vector, dtype=np.float64)
                    vector_norm = float(np.linalg.norm(vector_array))
                    if vector_norm == 0:
                        raise ValueError("Provided vector has zero norm")
                    direction = vector_array / vector_norm

                    # Create WriteCommand
                    cmd = apply_direction_write(
                        direction, layer=self.site_layer, alpha=alpha,
                        norm_cap_rel=1.0, positions="last",
                        meta={"concept": concept, "type": "vector"}
                    )
                    direction_source = "vector"

                else:
                    raise ValueError(f"Unknown direction_spec.mode: {direction_spec.mode}")
            elif not self.has_lens:
                # CONCEPT steering, lens-free: derive a REAL contrastive direction for the concept.
                # pos = the concept in carrier templates, neg = neutral templates. The direction is
                # a genuine difference-in-means over actual model activations (CAA) — not fabricated.
                logger.info("Concept '%s' via lens-free contrastive direction", concept)
                pos_texts = [f"The topic is {concept}.", f"This text is about {concept}.", f"Everything here concerns {concept}."]
                neg_texts = ["The topic is unspecified.", "This text is about nothing in particular.", "Everything here concerns ordinary matters."]
                pos_acts = self._extract_residuals_at_site(pos_texts)
                neg_acts = self._extract_residuals_at_site(neg_texts)
                direction = contrastive_direction(pos_acts, neg_acts, normalize=True)
                cmd = apply_direction_write(
                    direction, layer=self.site_layer, alpha=alpha,
                    norm_cap_rel=1.0, positions="last",
                    meta={"concept": concept, "type": "concept-contrastive"}
                )
                direction_source = f"concept-contrastive:{concept}"

            else:
                # CONCEPT steering mode via the pre-fitted lens + Jacobian (models with a lens).
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
                direction_source = f"concept:{concept}"

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
                direction_source=direction_source,
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
