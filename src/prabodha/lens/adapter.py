"""LensAdapter — Adapter over vendor jacobian-lens; Strategy for backends (RULES R7).
Concept: vimarśa-darpaṇa (the mirror of reflexive awareness) — the instrument that reads
what an activation is disposed to make the model say.
Source: anthropics/jacobian-lens (Apache-2.0, vendored); scoping doc §1 (actuator role).
Primitive: fit/read/save/load over HF decoders; 'jacobian' backend = vendor jlens;
'logit' backend = identity-transport baseline (control arm).

Vendor API facts this adapter is aligned to (jlens source, not its README):
- jlens.from_hf(hf_model, tokenizer) -> HFLensModel; auto-detects GPT-2 layout
  Layout("transformer", layers="h", norm="ln_f", embed="wte") (jlens/hf.py:_LAYOUTS).
- HFLensModel.encode() calls tokenizer(text, return_tensors="pt", truncation=True,
  max_length=...) and reads `.input_ids` as an ATTRIBUTE (jlens/hf.py), so any
  tokenizer must return a BatchEncoding-like object, not a plain dict.
- jlens.fit(model, prompts, *, skip_first=16, checkpoint_path=None, ...):
  skip_first defaults to fitting.SKIP_FIRST_N_POSITIONS == 16 and each prompt
  needs seq_len > skip_first + 1 tokens or it is skipped (jlens/fitting.py:
  valid_position_mask); checkpoint_path stores resumable fit STATE
  ({"jacobian_sum", ...}), a different format from JacobianLens.save()
  ({"J", ...}), so the two must not share a path.
- JacobianLens.apply(model, prompt, positions=[...]) returns
  (lens_logits: {layer: [n_positions, vocab]}, model_logits, input_ids).
"""
from __future__ import annotations
from pathlib import Path
from typing import Any

def build_model(model_cfg: dict):
    """Model factory. Strategy: hf_id download OR random_tiny_decoder (CPU smoke, no network)."""
    import torch
    import transformers
    if model_cfg.get("builder") == "random_tiny_decoder":
        cfg = transformers.GPT2Config(
            n_layer=model_cfg["n_layers"], n_embd=model_cfg["d_model"],
            n_head=model_cfg["n_heads"], vocab_size=model_cfg["vocab_size"],
            n_positions=model_cfg["seq_len"],
            # bos/eos must be in-vocab for transformers>=5 config validation.
            bos_token_id=0, eos_token_id=0)
        hf = transformers.GPT2LMHeadModel(cfg)
        tok = _tiny_tokenizer(model_cfg["vocab_size"], model_cfg["seq_len"])
        return hf.to(model_cfg.get("device", "cpu")), tok
    hf = transformers.AutoModelForCausalLM.from_pretrained(
        model_cfg["hf_id"],
        torch_dtype=getattr(torch, model_cfg.get("dtype", "bfloat16").replace("bf16", "bfloat16")),
        trust_remote_code=model_cfg.get("trust_remote_code", False))
    tok = transformers.AutoTokenizer.from_pretrained(model_cfg["hf_id"])
    return hf.to(model_cfg.get("device", "cuda")), tok

def _tiny_tokenizer(vocab_size: int, model_max_length: int):
    """Whitespace toy tokenizer exposing the HF surface jlens actually touches:
    __call__(text, return_tensors="pt", truncation=..., max_length=...) returning a
    BatchEncoding whose .input_ids is attribute-accessible (HFLensModel.encode), plus
    decode() for the vis helpers (jlens/protocol.py LensModel.tokenizer contract)."""
    class TinyTok:
        def __init__(self, n, max_len):
            self.vocab_size = n
            self.model_max_length = max_len
            self.eos_token_id = 0
            self.pad_token_id = 0
            self.bos_token_id = None  # from_hf(force_bos=True) then leaves us alone
        def __call__(self, text, return_tensors=None, truncation=False,
                     max_length=None, **kw):
            import torch
            import transformers
            limit = min(max_length or self.model_max_length, self.model_max_length)
            ids = [abs(hash(w)) % self.vocab_size for w in str(text).split()][:limit] or [1]
            t = torch.tensor([ids])
            return transformers.BatchEncoding(
                {"input_ids": t, "attention_mask": t.new_ones(t.shape)})
        def encode(self, text, **kw): return self(text)["input_ids"][0].tolist()
        def decode(self, ids, **kw): return " ".join(f"<{i}>" for i in
                    (ids.tolist() if hasattr(ids, "tolist") else list(ids)))
    return TinyTok(vocab_size, model_max_length)

class LensAdapter:
    def __init__(self, backend: str = "jacobian"):
        assert backend in ("jacobian", "logit")
        self.backend = backend
        self._lens = None

    def fit(self, hf, tok, lens_cfg: dict, out: str | Path | None = None):
        import jlens
        model = jlens.from_hf(hf, tok)
        prompts = _prompts(lens_cfg)
        # Vendor fit() checkpoint (resumable {"jacobian_sum", ...} state) must not
        # share a path with the saved lens ({"J", ...}); resume=True would choke.
        kwargs: dict[str, Any] = {}
        if out:
            kwargs["checkpoint_path"] = f"{out}.fit-ckpt"
        # Config over constants: vendor skip_first defaults to 16 (attention-sink
        # exclusion, jlens/fitting.py) — short smoke prompts must override it.
        for key, jlens_kw in (("skip_first", "skip_first"), ("seq_len", "max_seq_len"),
                              ("dim_batch", "dim_batch"), ("checkpoint_every", "checkpoint_every"),
                              # L2b: intermediate-target lenses (each band its own decoder;
                              # vendor default target = final layer)
                              ("target_layer", "target_layer")):
            if key in lens_cfg:
                kwargs[jlens_kw] = lens_cfg[key]
        self._lens = jlens.fit(model, prompts, **kwargs)
        if out:
            self._lens.save(str(out))
        return self

    def read(self, hf, tok, prompt: str, positions=(-1,), layers=None) -> dict[int, Any]:
        """Returns {layer: [n_positions, vocab] logits} per vendor apply();
        'logit' backend = final unembed only (identity-transport control)."""
        if self.backend == "logit":
            import torch
            enc = {k: v.to(hf.device) for k, v in dict(tok(prompt, return_tensors="pt")).items()}
            with torch.no_grad():
                out = hf(**enc)
            return {-1: out.logits[0, -1]}
        assert self._lens is not None, "fit or load first"
        import jlens
        model = jlens.from_hf(hf, tok)
        lens_logits, _model_logits, _ = self._lens.apply(
            model, prompt, layers=layers, positions=list(positions))
        return lens_logits

    @property
    def source_layers(self) -> list[int]:
        """Fitted layer indices (vendor JacobianLens.source_layers). Requires fit/load."""
        assert self._lens is not None, "fit or load first"
        return list(self._lens.source_layers)

    def read_with_model(self, hf, tok, prompt: str, positions=(-1,), layers=None):
        """Like read(), but also returns the model's ACTUAL final logits at the same
        positions -- vendor apply() computes both in one forward pass (E1 H_report needs
        the lens/model pair; jacobian backend only)."""
        assert self._lens is not None, "fit or load first"
        import jlens
        model = jlens.from_hf(hf, tok)
        lens_logits, model_logits, _ = self._lens.apply(
            model, prompt, layers=layers, positions=list(positions))
        return lens_logits, model_logits

    def load(self, path: str | Path):
        import jlens
        self._lens = jlens.JacobianLens.from_pretrained(str(Path(path).parent),
                                                        filename=Path(path).name) \
            if not Path(path).exists() else _load_local(path)
        return self

def _load_local(path):
    import jlens
    import torch
    return jlens.JacobianLens.load(str(path)) if hasattr(jlens.JacobianLens, "load") \
        else torch.load(path, weights_only=False)

def _prompts(lens_cfg: dict) -> list[str]:
    n = int(lens_cfg.get("n_prompts", 8))
    if lens_cfg.get("corpus") == "synthetic_smoke":
        # prompt_len must exceed skip_first + 1 (vendor valid_position_mask) and fit
        # inside the model's n_positions; both come from config, not constants.
        k = int(lens_cfg.get("prompt_len", 24))
        words = ["nadī", "agni", "vāyu", "soma", "gauḥ", "aśvaḥ", "sūrya", "candra"]
        import random
        rng = random.Random(lens_cfg.get("seed", 42))
        return [" ".join(rng.choices(words, k=k)) for _ in range(n)]
    if lens_cfg.get("corpus") == "pretraining_like":
        # One prompt per line, generated once by scripts/tools/make_fit_corpus.py from a
        # local pretraining-like corpus (seeded, non-overlapping windows). Reading a flat
        # file keeps the runtime image free of dataset libraries and the fit inspectable.
        path = Path(lens_cfg["corpus_file"])
        lines = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines()
                 if ln.strip()]
        if len(lines) < n:
            raise ValueError(f"corpus_file {path} has {len(lines)} prompts < n_prompts={n}")
        return lines[:n]
    raise NotImplementedError(f"unknown corpus: {lens_cfg.get('corpus')!r}")
