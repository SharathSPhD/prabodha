"""LensAdapter — Adapter over vendor jacobian-lens; Strategy for backends (RULES R7).
Concept: vimarśa-darpaṇa (the mirror of reflexive awareness) — the instrument that reads
what an activation is disposed to make the model say.
Source: anthropics/jacobian-lens (Apache-2.0, vendored); scoping doc §1 (actuator role).
Primitive: fit/read/save/load over HF decoders; 'jacobian' backend = vendor jlens;
'logit' backend = identity-transport baseline (control arm).
"""
from __future__ import annotations
from pathlib import Path
from typing import Any
from prabodha.config import load as load_cfg

def build_model(model_cfg: dict):
    """Model factory. Strategy: hf_id download OR random_tiny_decoder (CPU smoke, no network)."""
    import torch, transformers
    if model_cfg.get("builder") == "random_tiny_decoder":
        cfg = transformers.GPT2Config(
            n_layer=model_cfg["n_layers"], n_embd=model_cfg["d_model"],
            n_head=model_cfg["n_heads"], vocab_size=model_cfg["vocab_size"],
            n_positions=model_cfg["seq_len"], n_ctx=model_cfg["seq_len"])
        hf = transformers.GPT2LMHeadModel(cfg)
        tok = _tiny_tokenizer(model_cfg["vocab_size"])
        return hf.to(model_cfg.get("device", "cpu")), tok
    hf = transformers.AutoModelForCausalLM.from_pretrained(
        model_cfg["hf_id"],
        torch_dtype=getattr(torch, model_cfg.get("dtype", "bfloat16").replace("bf16", "bfloat16")),
        trust_remote_code=model_cfg.get("trust_remote_code", False))
    tok = transformers.AutoTokenizer.from_pretrained(model_cfg["hf_id"])
    return hf.to(model_cfg.get("device", "cuda")), tok

def _tiny_tokenizer(vocab_size: int):
    """Whitespace toy tokenizer exposing the minimal HF surface jlens/apply needs."""
    class TinyTok:
        def __init__(self, n): self.vocab_size = n; self.eos_token_id = 0; self.pad_token_id = 0
        def __call__(self, text, return_tensors=None, **kw):
            import torch
            ids = [min(abs(hash(w)) % self.vocab_size, self.vocab_size - 1)
                   for w in str(text).split()][:31] or [1]
            t = torch.tensor([ids])
            return {"input_ids": t, "attention_mask": t.new_ones(t.shape)}
        def encode(self, text, **kw): return self(text)["input_ids"][0].tolist()
        def decode(self, ids, **kw): return " ".join(f"<{i}>" for i in
                    (ids.tolist() if hasattr(ids, "tolist") else list(ids)))
    return TinyTok(vocab_size)

class LensAdapter:
    def __init__(self, backend: str = "jacobian"):
        assert backend in ("jacobian", "logit")
        self.backend = backend
        self._lens = None

    def fit(self, hf, tok, lens_cfg: dict, out: str | Path | None = None):
        import jlens
        model = jlens.from_hf(hf, tok)
        prompts = _prompts(lens_cfg)
        ckpt = str(out) if out else None
        self._lens = jlens.fit(model, prompts=prompts, checkpoint_path=ckpt)
        if out:
            self._lens.save(str(out))
        return self

    def read(self, hf, tok, prompt: str, positions=(-1,), layers=None) -> dict[int, Any]:
        """Returns {layer: top-token logits} per vendor apply(); 'logit' backend = final unembed only."""
        import jlens
        model = jlens.from_hf(hf, tok)
        if self.backend == "logit":
            import torch
            with torch.no_grad():
                out = hf(**tok(prompt, return_tensors="pt").to(hf.device) if hasattr(tok(prompt), "to")
                         else hf(**{k: v.to(hf.device) for k, v in tok(prompt, return_tensors="pt").items()}))
            return {-1: out.logits[0, -1]}
        assert self._lens is not None, "fit or load first"
        lens_logits, model_logits, _ = self._lens.apply(model, prompt, positions=list(positions))
        return lens_logits

    def load(self, path: str | Path):
        import jlens
        self._lens = jlens.JacobianLens.from_pretrained(str(Path(path).parent),
                                                        filename=Path(path).name) \
            if not Path(path).exists() else _load_local(path)
        return self

def _load_local(path):
    import jlens, torch
    return jlens.JacobianLens.load(str(path)) if hasattr(jlens.JacobianLens, "load") \
        else torch.load(path, weights_only=False)

def _prompts(lens_cfg: dict) -> list[str]:
    n = int(lens_cfg.get("n_prompts", 8))
    if lens_cfg.get("corpus") == "synthetic_smoke":
        words = ["nadī", "agni", "vāyu", "soma", "gauḥ", "aśvaḥ", "sūrya", "candra"]
        import random
        rng = random.Random(lens_cfg.get("seed", 42))
        return [" ".join(rng.choices(words, k=16)) for _ in range(n)]
    raise NotImplementedError("pretraining_like corpus resolver lands with L1 GB10 pack "
                              "(uses local text corpus on the Spark; R4: declared here)")
