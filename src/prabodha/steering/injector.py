"""injector — apply a WriteCommand to a live HF decoder via forward hooks (v3 arm), and
the mechanism-matched v2 arm (output logit bias, the 'vaikharī write').
Concept: the v2/v3 contrast IS the experiment — same content, written at the mouth (v2)
vs into the workspace band residual (v3). L3 contract discloses that v2 here is a
mechanism-matched simplification of PWM's trained bridge (which needs the full WM stack).
Source: SPEC §6; PWM bridge_v2.as_logits_processor (mechanism reference).
Primitive: ResidualInjector context manager (hook on the band layer's output hidden state);
logit_bias_processor for generate(logits_processor=...).
"""
from __future__ import annotations

from typing import Any

from prabodha.steering.writer import WriteCommand


class ResidualInjector:
    """Adds the command's capped delta to the layer's output hidden states.
    positions='last' targets only the final position of the current forward (both the
    prefill's last token and each incremental decode step); 'all' targets every position."""

    def __init__(self, layer_module: Any, cmd: WriteCommand, policy: Any = None):
        """policy: optional TimingPolicy — consulted per forward (prefill detected by
        sequence length > 1); None preserves L3 semantics (write every forward)."""
        import numpy as np
        import torch
        self._module = layer_module
        self._cmd = cmd
        self._policy = policy
        self._dir = torch.from_numpy(np.asarray(cmd.direction, dtype=np.float32))
        self._handle = None
        self.n_applications = 0

    def _hook(self, module, args, output):
        hidden = output[0] if isinstance(output, tuple) else output
        if self._policy is not None and not self._policy.should_write(hidden.shape[1] > 1):
            return output
        d = self._dir.to(hidden.device, hidden.dtype)
        if self._cmd.positions == "all":
            idx = slice(None)
        else:  # 'last'
            idx = slice(-1, None)
        h = hidden[:, idx, :]
        h_norm = h.norm(dim=-1, keepdim=True)
        # capped_delta semantics, vectorized: ||delta|| = min(alpha, cap) * ||h|| per position
        scale = min(self._cmd.alpha, self._cmd.norm_cap_rel)
        delta = d * (scale * h_norm)
        new_h = hidden.clone()
        new_h[:, idx, :] = h + delta
        self.n_applications += 1
        if isinstance(output, tuple):
            return (new_h,) + tuple(output[1:])
        return new_h

    def __enter__(self):
        self._handle = self._module.register_forward_hook(self._hook)
        return self

    def __exit__(self, *exc):
        if self._handle is not None:
            self._handle.remove()
        return False


def entropy_observer(policy: Any):
    """LogitsProcessor-shaped observer: feeds each decode step's next-token entropy to the
    timing policy (gates the NEXT forward — the causally clean order). Identity on scores."""
    def _proc(input_ids, scores):
        import torch
        p = torch.softmax(scores[0].float(), dim=-1)
        ent = float(-(p * torch.log(p.clamp_min(1e-30))).sum().item())
        policy.observe(ent)
        return scores
    return _proc


def logit_bias_processor(concept_ids: list[int], bias: float):
    """v2 arm: additive bias on concept token logits at the OUTPUT (vaikharī site).
    Shaped for transformers LogitsProcessor duck-typing (callable(input_ids, scores))."""
    def _proc(input_ids, scores):
        scores[:, list(concept_ids)] = scores[:, list(concept_ids)] + bias
        return scores
    return _proc
