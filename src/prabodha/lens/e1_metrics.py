"""E1 evaluators (screen tier): H_report, H_bands, H_modulation.
Concept: pratyabhijna-pariksha (recognition put to the test) -- does the lens's reading of the
residual stream match what the model actually says (H_report), does depth organize into
sensory/workspace/motor bands (H_bands), and can an instruction load a concept into the
workspace band (H_modulation)?
Source: J-space paper + Nanda Qwen replication (docs/jspace_pratyabhijna_scoping.md #7, E1);
linear CKA per Kornblith et al. 2019 "Similarity of Neural Network Representations Revisited";
Spearman rho implemented directly on numpy (rank transform + Pearson), no scipy dependency.
Primitive: evaluate_h_*(...) -> dict(metric + evidence payload); run_e1(hf, tok, lens, exp_cfg)
-> {hypothesis: {value, threshold, pass, evidence}, deviations} with thresholds FROM
configs/experiments/e1.yaml (config over constants -- nothing scientific hardcoded here).

Honest limitations (disclosed per RULES):
- H_bands reads residuals via transformers ``output_hidden_states=True`` on the raw HF model:
  jlens's HFLensModel exposes no hidden-state API (only its ActivationRecorder hook, which
  captures block outputs == hidden_states[1:] for HF decoders). Caveat: HF implementations
  apply the final pre-unembed norm to the LAST hidden_states entry, so the deepest layer is
  post-norm while all others are raw block outputs; acceptable for band structure at screen
  tier, disclosed here.
- H_modulation takes the FIRST token id of the (space-prefixed) tokenized concept; multi-token
  concepts are a known verbalizability-granularity blind spot (scoping doc #10.3) and each
  occurrence is logged as a deviation rather than silently dropped.
- The instruction-span end is located by re-tokenizing the instruction prefix; BPE merges
  across the prefix boundary can shift it by ~1 token (rare at sentence-final punctuation).
  Positions that fall outside the tokenized prompt are clamped and logged as deviations.
"""
from __future__ import annotations

import math
import random
from typing import Any

import numpy as np

# ---------------------------------------------------------------- pure numpy primitives


def _rankdata(x: np.ndarray) -> np.ndarray:
    """Ranks with average tie handling (0-based mean ranks; affine-invariant for Pearson)."""
    x = np.asarray(x, dtype=np.float64)
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty(len(x), dtype=np.float64)
    i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and x[order[j + 1]] == x[order[i]]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2.0
        i = j + 1
    return ranks


def spearman_rho(a: np.ndarray, b: np.ndarray) -> float:
    """Spearman rank correlation = Pearson correlation of the rank transforms.
    Returns 0.0 for degenerate (constant) inputs instead of NaN."""
    ra, rb = _rankdata(a), _rankdata(b)
    ra -= ra.mean()
    rb -= rb.mean()
    denom = float(np.sqrt((ra * ra).sum() * (rb * rb).sum()))
    return float((ra * rb).sum() / denom) if denom > 0 else 0.0


def topk_union_indices(a: np.ndarray, b: np.ndarray, k: int) -> np.ndarray:
    """Sorted indices of the union of a's and b's top-k sets (the comparison support:
    ranking agreement is measured where either side puts mass, not over the full vocab)."""
    top_a = np.argsort(np.asarray(a))[-k:]
    top_b = np.argsort(np.asarray(b))[-k:]
    return np.unique(np.concatenate([top_a, top_b]))


def linear_cka(x: np.ndarray, y: np.ndarray) -> float:
    """Plain (non-debiased) linear CKA between feature matrices [n, d1], [n, d2]
    (Kornblith et al. 2019, eq. 1, Gram/HSIC form). Screen tier: plain is sufficient."""
    xc = np.asarray(x, dtype=np.float64)
    yc = np.asarray(y, dtype=np.float64)
    xc = xc - xc.mean(axis=0)
    yc = yc - yc.mean(axis=0)
    gx, gy = xc @ xc.T, yc @ yc.T
    nx, ny = np.linalg.norm(gx), np.linalg.norm(gy)
    return float(np.sum(gx * gy) / (nx * ny)) if nx > 0 and ny > 0 else 0.0


def cka_matrix(acts: list[np.ndarray]) -> np.ndarray:
    """Pairwise linear CKA over per-layer activation matrices (each [n, d], same n).
    Grams are computed once per layer (n x n), so cost is O(L*n^2*d + L^2*n^2)."""
    grams, norms = [], []
    for x in acts:
        xc = np.asarray(x, dtype=np.float64)
        xc = xc - xc.mean(axis=0)
        g = xc @ xc.T
        grams.append(g)
        norms.append(float(np.linalg.norm(g)))
    n_layers = len(grams)
    c = np.eye(n_layers)
    for i in range(n_layers):
        for j in range(i + 1, n_layers):
            ok = norms[i] > 0 and norms[j] > 0
            c[i, j] = c[j, i] = float(np.sum(grams[i] * grams[j]) / (norms[i] * norms[j])) \
                if ok else 0.0
    return c


def best_band_partition(c: np.ndarray, min_band_size: int = 2) -> tuple[float, tuple[int, int]]:
    """Exhaustive search over 2-boundary segmentations of layers into 3 contiguous bands
    (each >= min_band_size) maximizing mean(within-band CKA) - mean(between-band CKA),
    off-diagonal pairs only. Returns (contrast, (b1, b2)) with bands [0,b1), [b1,b2), [b2,L)."""
    n_layers = c.shape[0]
    if n_layers < 3 * min_band_size:
        raise ValueError(f"need >= {3 * min_band_size} layers for 3 bands of >= "
                         f"{min_band_size}; got {n_layers}")
    iu, ju = np.triu_indices(n_layers, k=1)
    best_contrast, best_bounds = -np.inf, (min_band_size, 2 * min_band_size)
    for b1 in range(min_band_size, n_layers - 2 * min_band_size + 1):
        for b2 in range(b1 + min_band_size, n_layers - min_band_size + 1):
            label = np.digitize(np.arange(n_layers), [b1, b2])
            same = label[iu] == label[ju]
            if not same.any() or same.all():
                continue  # degenerate: no within (or no between) pairs to average
            contrast = float(c[iu, ju][same].mean() - c[iu, ju][~same].mean())
            if contrast > best_contrast:
                best_contrast, best_bounds = contrast, (b1, b2)
    return best_contrast, best_bounds


# ---------------------------------------------------------------- prompt construction


def concept_prompt_pairs(exp_cfg: dict) -> list[tuple[str, str]]:
    """Deterministic (prompt, concept) pairs: templates x concepts, shuffled by seeds[0].
    The same pool feeds all three evaluators (H_report/H_bands use just the prompt text)."""
    pairs = [(t.format(concept=c), c)
             for t in exp_cfg["templates"] for c in exp_cfg["concepts"]]
    random.Random(exp_cfg["seeds"][0]).shuffle(pairs)
    return pairs


def _token_ids(tok: Any, text: str) -> list[int]:
    """Token ids via the same __call__ surface jlens's encode uses (BatchEncoding)."""
    ids = tok(text)["input_ids"]
    if hasattr(ids, "tolist"):
        ids = ids.tolist()
    if ids and isinstance(ids[0], list):
        ids = ids[0]
    return list(ids)


def instruction_end_position(tok: Any, prompt: str, concept: str) -> int:
    """Index of the last token of the instruction span: the prompt prefix up to and
    including the first '.' after the concept (whole prompt if no terminator found).
    Prefix re-tokenization caveat documented in the module docstring."""
    start = prompt.find(concept)
    dot = prompt.find(".", start if start >= 0 else 0)
    prefix = prompt[:dot + 1] if dot >= 0 else prompt
    return len(_token_ids(tok, prefix)) - 1


# ---------------------------------------------------------------- evaluators


def evaluate_h_report(hf: Any, tok: Any, lens: Any, prompts: list[str],
                      top_k: int) -> dict:
    """H_report: verbal-report correspondence. Per prompt, Spearman rho between the lens
    readout at position -1 and the model's actual final next-token logits, computed over
    the union of both top-K token sets, per layer. Value = mean rho over the late third
    of fitted layers; the full per-layer curve (should RISE with depth) ships as evidence."""
    per_layer: dict[int, list[float]] = {}
    for prompt in prompts:
        lens_logits, model_logits = lens.read_with_model(hf, tok, prompt, positions=[-1])
        m = model_logits[0].numpy()
        for layer, t in lens_logits.items():
            v = t[0].numpy()
            idx = topk_union_indices(v, m, top_k)
            per_layer.setdefault(int(layer), []).append(spearman_rho(v[idx], m[idx]))
    layers = sorted(per_layer)
    curve = {layer: float(np.mean(per_layer[layer])) for layer in layers}
    late = layers[-max(1, math.ceil(len(layers) / 3)):]
    value = float(np.mean([curve[layer] for layer in late]))
    return {"spearman_rho_late_third": value,
            "per_layer_rho": {layer: round(curve[layer], 4) for layer in layers},
            "late_third_layers": late, "top_k": top_k, "n_prompts": len(prompts)}


def evaluate_h_bands(hf: Any, tok: Any, prompts: list[str], *,
                     skip_first: int, min_band_size: int) -> dict:
    """H_bands: CKA layer-band structure over residual activations pooled across prompts
    (positions < skip_first dropped: attention-sink residuals, cf. jlens fitting).
    Uses transformers output_hidden_states=True on the raw HF model (see module docstring)."""
    import torch
    deviations: list[str] = []
    acts: list[list[np.ndarray]] = []
    for prompt in prompts:
        ids = tok(prompt, return_tensors="pt").input_ids.to(hf.device)
        with torch.no_grad():
            out = hf(input_ids=ids, output_hidden_states=True, use_cache=False)
        hidden = out.hidden_states[1:]  # block outputs; entry i <-> residual block i
        if not acts:
            acts = [[] for _ in hidden]
        cut = skip_first if ids.shape[1] > skip_first else 0
        for i, h in enumerate(hidden):
            acts[i].append(h[0, cut:].float().cpu().numpy())
    layer_mats = [np.concatenate(a, axis=0) for a in acts]
    c = cka_matrix(layer_mats)
    n_layers = len(layer_mats)
    effective_min = min(min_band_size, max(1, n_layers // 3))
    if effective_min < min_band_size:
        deviations.append(f"H_bands: min_band_size relaxed {min_band_size}->{effective_min} "
                          f"(only {n_layers} layers; shallow-model accommodation)")
    contrast, (b1, b2) = best_band_partition(c, min_band_size=effective_min)
    return {"cka_band_contrast": contrast, "boundaries": [b1, b2],
            "bands": [[0, b1], [b1, b2], [b2, n_layers]],
            "cka_matrix": [[round(float(v), 4) for v in row] for row in c],
            "n_prompts": len(prompts), "deviations": deviations}


def evaluate_h_modulation(hf: Any, tok: Any, lens: Any,
                          pairs: list[tuple[str, str]], band_layers: list[int]) -> dict:
    """H_modulation: directed modulation. Hit iff the instructed concept's token id is in
    the lens top-5 at ANY band layer, read at the last instruction-span position. Concept
    id = first token of ' '+concept (mid-sentence form; single-token limitation disclosed)."""
    import torch
    deviations: list[str] = []
    hits = 0
    for prompt, concept in pairs:
        cids = _token_ids(tok, " " + concept)
        if len(cids) > 1:
            deviations.append(f"H_modulation: concept '{concept}' is {len(cids)} tokens; "
                              "using first id only (scoping doc #10.3)")
        pos = instruction_end_position(tok, prompt, concept)
        n_total = len(_token_ids(tok, prompt))
        if pos >= n_total:
            deviations.append(f"H_modulation: clamped span position {pos}->{n_total - 1} "
                              f"for prompt '{prompt[:40]}...'")
            pos = n_total - 1
        readout = lens.read(hf, tok, prompt, positions=[pos], layers=band_layers)
        if any(cids[0] in torch.topk(t[0], k=5).indices.tolist() for t in readout.values()):
            hits += 1
    return {"instructed_concept_hit_rate_at5": hits / len(pairs), "n_prompts": len(pairs),
            "band_layers": list(band_layers), "n_hits": hits, "deviations": deviations}


# ---------------------------------------------------------------- assembly


def _middle_band_layers(source_layers: list[int], bands_result: dict | None) -> list[int]:
    """Workspace-band layer set: H_bands middle band intersected with the fitted layers,
    falling back to the middle third of fitted layers when the intersection is empty."""
    if bands_result is not None:
        b1, b2 = bands_result["boundaries"]
        mid = [layer for layer in source_layers if b1 <= layer < b2]
        if mid:
            return mid
    n = len(source_layers)
    third = max(1, n // 3)
    return source_layers[third:n - third] or [source_layers[n // 2]]


def run_e1(hf: Any, tok: Any, lens_adapter: Any, exp_cfg: dict) -> dict:
    """Run all three E1 evaluators; assemble {hypothesis: {value, threshold, pass, evidence}}
    plus a deduplicated deviations list. Thresholds and all knobs come from exp_cfg (R4)."""
    hyp = exp_cfg["hypotheses"]
    pairs = concept_prompt_pairs(exp_cfg)
    prompts = [p for p, _ in pairs]

    r_report = evaluate_h_report(hf, tok, lens_adapter,
                                 prompts[:int(hyp["H_report"]["n_prompts"])],
                                 top_k=int(exp_cfg["top_k"]))
    r_bands = evaluate_h_bands(hf, tok, prompts[:int(hyp["H_bands"]["n_prompts"])],
                               skip_first=int(exp_cfg["cka_skip_first"]),
                               min_band_size=int(exp_cfg["cka_min_band_size"]))
    band_layers = _middle_band_layers(lens_adapter.source_layers, r_bands)
    r_mod = evaluate_h_modulation(hf, tok, lens_adapter,
                                  pairs[:int(hyp["H_modulation"]["n_prompts"])], band_layers)

    results: dict[str, Any] = {}
    deviations: list[str] = []
    for name, r in (("H_report", r_report), ("H_bands", r_bands), ("H_modulation", r_mod)):
        value = float(r[hyp[name]["metric"]])
        threshold = float(hyp[name]["threshold_min"])
        results[name] = {"value": value, "threshold": threshold,
                         "pass": bool(value >= threshold), "evidence": r}
        for d in r.pop("deviations", []):  # hoist into the gate-level list, deduplicated
            if d not in deviations:
                deviations.append(d)
    results["deviations"] = deviations
    return results
