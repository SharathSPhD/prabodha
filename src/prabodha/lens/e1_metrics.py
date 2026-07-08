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
    """Sorted indices of the union of a's and b's top-k sets. CAVEAT (L1 iteration finding,
    verified synthetically): when the two top-k sets are disjoint, rho over the union support
    is structurally ~ -0.72, NOT 0 — each side ranks its own set high and the other's low.
    Kept as secondary evidence; the calibrated primary support is topk_indices(model)."""
    top_a = np.argsort(np.asarray(a))[-k:]
    top_b = np.argsort(np.asarray(b))[-k:]
    return np.unique(np.concatenate([top_a, top_b]))


def topk_indices(a: np.ndarray, k: int) -> np.ndarray:
    """Indices of a's top-k. Used as the H_report comparison support: 'does the lens rank
    the MODEL's report candidates the way the model does' — null (independent lens) ~ 0."""
    return np.argsort(np.asarray(a))[-k:]


def permutation_p_mean_rho(pairs: list[tuple[np.ndarray, np.ndarray]], observed: float,
                           n_resamples: int, seed: int) -> float:
    """One-sided permutation p for a mean Spearman rho over (lens, model) support pairs:
    shuffling each lens vector within its support breaks correspondence while preserving
    marginals. p = P(mean rho_null >= observed). Add-one correction (Phipson & Smyth)."""
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(n_resamples):
        s = float(np.mean([spearman_rho(rng.permutation(lens_v), model_v)
                           for lens_v, model_v in pairs]))
        if s >= observed:
            hits += 1
    return (hits + 1) / (n_resamples + 1)


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


def topk_negentropy(logits: np.ndarray, k: int) -> float:
    """Articulation primitive (E7, scoping §2.5 'top-k concentration'): negentropy of the
    softmax-renormalized top-k readout, normalized to [0, 1]. 0 = uniform over the top-k
    (pre-articulate, paśyantī-like); 1 = a single dominant token (fully uttered, vaikharī)."""
    v = np.asarray(logits, dtype=np.float64)
    top = np.sort(v)[-k:]
    top = top - top.max()
    p = np.exp(top)
    p /= p.sum()
    entropy = float(-(p * np.log(np.maximum(p, 1e-300))).sum())
    return 1.0 - entropy / math.log(k)


def articulation_gradient(scores_by_layer: dict[int, list[float]], *,
                          permutation_resamples: int, seed: int) -> tuple[float, float]:
    """E7 primary statistic: Spearman rho between layer depth and mean articulation score.
    Null: permute the layer labels of the mean-score sequence (does articulation actually
    ORDER by depth, or is any monotony an accident of the values?). Two-sided-strictness is
    not needed — the registered prediction is a RISING gradient, so p is one-sided (>=)."""
    layers = sorted(scores_by_layer)
    means = np.array([float(np.mean(scores_by_layer[layer])) for layer in layers])
    depth = np.array(layers, dtype=np.float64)
    rho = spearman_rho(depth, means)
    rng = np.random.default_rng(seed)
    hits = sum(spearman_rho(depth, rng.permutation(means)) >= rho
               for _ in range(permutation_resamples))
    return rho, (hits + 1) / (permutation_resamples + 1)


def evaluate_h_articulation(hf: Any, tok: Any, lens: Any, prompts: list[str], *,
                            top_k: int, permutation_resamples: int, seed: int) -> dict:
    """H_articulation (E7): progressive articulation across depth. Per prompt, read the lens
    at the final position across all fitted layers; per layer, score top-k negentropy; the
    value is the depth gradient rho (permutation-gated). Purely observational — the
    vāk-hierarchy signature (paśyantī -> madhyamā -> vaikharī) GNW does not predict."""
    scores: dict[int, list[float]] = {}
    for prompt in prompts:
        readout = lens.read(hf, tok, prompt, positions=[-1])
        for layer, t in readout.items():
            scores.setdefault(int(layer), []).append(topk_negentropy(t[0].numpy(), top_k))
    rho, p = articulation_gradient(scores, permutation_resamples=permutation_resamples,
                                   seed=seed)
    layers = sorted(scores)
    return {"articulation_gradient_rho": rho, "permutation_p": p,
            "per_layer_negentropy": {layer: round(float(np.mean(scores[layer])), 4)
                                     for layer in layers},
            "top_k": top_k, "n_prompts": len(prompts)}


# ---------------------------------------------------------------- prompt construction


def concept_prompt_pairs(exp_cfg: dict) -> list[tuple[str, str]]:
    """Deterministic (prompt, concept) pairs: templates x concepts, shuffled by seeds[0].
    The same pool feeds all three evaluators (H_report/H_bands use just the prompt text)."""
    pairs = [(t.format(concept=c), c)
             for t in exp_cfg["templates"] for c in exp_cfg["concepts"]]
    random.Random(exp_cfg["seeds"][0]).shuffle(pairs)
    return pairs


def _token_ids(tok: Any, text: str, *, specials: bool = True) -> list[int]:
    """Token ids via the same __call__ surface jlens's encode uses (BatchEncoding).
    specials=False strips BOS/EOS — REQUIRED for concept-candidate ids on BOS-prepending
    tokenizers (L2 run-1: every candidate's 'first id' was BOS, zeroing all hit rates);
    span positions keep specials=True because jlens encodes prompts with them too."""
    kwargs = {} if specials else {"add_special_tokens": False}
    ids = tok(text, **kwargs)["input_ids"]
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
                      top_k: int, *, permutation_resamples: int = 0,
                      seed: int = 42, window: str = "late_third") -> dict:
    """H_report: verbal-report correspondence. Per prompt, Spearman rho between the lens
    readout at position -1 and the model's actual final next-token logits, per layer.
    PRIMARY support (L1 iteration amendment, adversarial-review driven): the MODEL's top-K
    token set — null (independent lens) ~ 0, so thresholds mean what they say. The union-
    support rho ships as secondary evidence (its null floor is ~ -0.72; see topk_union_indices).
    Value = mean primary rho over the late third of fitted layers; per-prompt late-third
    means and a permutation p (lens shuffled within support) ship as evidence."""
    per_layer_model: dict[int, list[float]] = {}
    per_layer_union: dict[int, list[float]] = {}
    support_pairs: list[tuple[int, np.ndarray, np.ndarray]] = []  # (layer, lens_v, model_v)
    for prompt in prompts:
        lens_logits, model_logits = lens.read_with_model(hf, tok, prompt, positions=[-1])
        m = model_logits[0].numpy()
        m_idx = topk_indices(m, top_k)
        for layer, t in lens_logits.items():
            v = t[0].numpy()
            per_layer_model.setdefault(int(layer), []).append(spearman_rho(v[m_idx], m[m_idx]))
            u_idx = topk_union_indices(v, m, top_k)
            per_layer_union.setdefault(int(layer), []).append(spearman_rho(v[u_idx], m[u_idx]))
            support_pairs.append((int(layer), v[m_idx], m[m_idx]))
    layers = sorted(per_layer_model)
    windows = {"late_third": layers[-max(1, math.ceil(len(layers) / 3)):],
               # L1b review caveat #3: both L1/L1b curves consolidate only in the final
               # layers; last3 is the registered alternative window for L2+.
               "last3": layers[-min(3, len(layers)):]}
    late = windows.get(window)
    if late is None:
        raise ValueError(f"unknown report window: {window!r}")
    curve = {layer: float(np.mean(per_layer_model[layer])) for layer in layers}
    curve_union = {layer: float(np.mean(per_layer_union[layer])) for layer in layers}
    per_prompt = [float(np.mean([per_layer_model[layer][i] for layer in late]))
                  for i in range(len(prompts))]
    value = float(np.mean([curve[layer] for layer in late]))
    other = "last3" if window == "late_third" else "late_third"
    out = {f"spearman_rho_model_topk_{window}": value,
           f"spearman_rho_model_topk_{other}_secondary":
               float(np.mean([curve[layer] for layer in windows[other]])),
           "spearman_rho_union_secondary":
               float(np.mean([curve_union[layer] for layer in late])),
           "per_layer_rho_model_topk": {layer: round(curve[layer], 4) for layer in layers},
           "per_layer_rho_union": {layer: round(curve_union[layer], 4) for layer in layers},
           f"per_prompt_rho_{window}": [round(x, 4) for x in per_prompt],
           "window_layers": late, "window": window, "top_k": top_k,
           "n_prompts": len(prompts)}
    if permutation_resamples:
        late_pairs = [(lv, mv) for layer, lv, mv in support_pairs if layer in set(late)]
        out["permutation_p"] = permutation_p_mean_rho(
            late_pairs, value, permutation_resamples, seed)
        out["permutation_resamples"] = permutation_resamples
    return out


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


def _concept_candidate_ids(tok: Any, concept: str, translations: dict[str, str] | None,
                           deviations: list[str], *,
                           policy: str = "first_id") -> dict[str, int]:
    """First-token ids for the concept's surface variants: English mid-sentence (' fire'),
    English bare ('fire'), and — L1 iteration amendment (CJK meta-token observation:
    Qwen verbalizes concepts in dense Chinese tokens, e.g. fire -> 火) — the configured
    translation. Multi-token variants: policy 'first_id' falls back to the first id (L1/L1b
    behavior); 'single_token_only' DROPS them (L2 review: on large SentencePiece vocabs the
    first piece of a multi-token variant is byte-fallback noise that hits top-5 regardless
    of instruction). Either way, logged once."""
    variants = {"en_mid": " " + concept, "en_bare": concept}
    if translations and concept in translations:
        variants["zh"] = str(translations[concept])
    ids: dict[str, int] = {}
    for name, text in variants.items():
        cids = _token_ids(tok, text, specials=False)
        if len(cids) > 1:
            if policy == "single_token_only":
                deviations.append(f"H_modulation: variant {name} of '{concept}' is "
                                  f"{len(cids)} tokens; DROPPED (single_token_only policy)")
                continue
            deviations.append(f"H_modulation: variant {name} of '{concept}' is "
                              f"{len(cids)} tokens; using first id only (scoping doc #10.3)")
        if cids:
            ids[name] = cids[0]
    return ids


def evaluate_h_modulation(hf: Any, tok: Any, lens: Any,
                          pairs: list[tuple[str, str]], band_layers: list[int],
                          *, translations: dict[str, str] | None = None,
                          null_shuffles: int = 0, seed: int = 42,
                          control_stubs: list[str] | None = None,
                          variant_policy: str = "first_id") -> dict:
    """H_modulation: directed modulation. Hit iff ANY candidate id of the instructed
    concept (English mid/bare + configured translation) is in the lens top-5 at ANY band
    layer, read at the last instruction-span position. Evidence carries the per-prompt
    hit table and a shuffled-concept null baseline (same readouts, deranged concepts) —
    both demanded by the L1 adversarial review."""
    import torch
    deviations: list[str] = []
    all_concepts = sorted({c for _, c in pairs})
    candidate_ids = {c: _concept_candidate_ids(tok, c, translations, deviations,
                                               policy=variant_policy)
                     for c in all_concepts}
    per_prompt: list[dict[str, Any]] = []
    topsets: list[set[int]] = []  # union of band-layer top-5 ids per prompt (for the null)
    hits = 0
    for prompt, concept in pairs:
        pos = instruction_end_position(tok, prompt, concept)
        n_total = len(_token_ids(tok, prompt))
        if pos >= n_total:
            deviations.append(f"H_modulation: clamped span position {pos}->{n_total - 1} "
                              f"for prompt '{prompt[:40]}...'")
            pos = n_total - 1
        readout = lens.read(hf, tok, prompt, positions=[pos], layers=band_layers)
        top = {int(i) for t in readout.values() for i in torch.topk(t[0], k=5).indices.tolist()}
        topsets.append(top)
        matched = sorted(n for n, cid in candidate_ids[concept].items() if cid in top)
        hits += bool(matched)
        per_prompt.append({"concept": concept, "hit": bool(matched), "matched": matched})
    out: dict[str, Any] = {
        "instructed_concept_hit_rate_at5": hits / len(pairs), "n_prompts": len(pairs),
        "band_layers": list(band_layers), "n_hits": hits, "per_prompt": per_prompt,
        "concept_variants": {c: sorted(v) for c, v in candidate_ids.items()},
        "deviations": deviations}
    if null_shuffles:
        import random as _random
        rng = _random.Random(seed)
        concepts = [c for _, c in pairs]
        null_rates = []
        for _ in range(null_shuffles):
            shuffled = concepts[:]
            rng.shuffle(shuffled)
            null_rates.append(sum(
                any(cid in topsets[i] for cid in candidate_ids[c].values())
                for i, c in enumerate(shuffled)) / len(pairs))
        out["null_hit_rate_mean"] = float(np.mean(null_rates))
        out["null_shuffles"] = null_shuffles
    if control_stubs is not None:
        # L1b review caveat #1 (uninstructed-prompt control): does the concept surface in the
        # band WITHOUT the instruction? Distinguishes directed loading from incidental
        # concept-capacity. Stubs deduplicated (one read per unique stub, position -1).
        stub_top: dict[str, set[int]] = {}
        for stub in dict.fromkeys(control_stubs):
            readout = lens.read(hf, tok, stub, positions=[-1], layers=band_layers)
            stub_top[stub] = {int(i) for t in readout.values()
                              for i in torch.topk(t[0], k=5).indices.tolist()}
        control_hits = sum(
            any(cid in stub_top[stub] for cid in candidate_ids[c].values())
            for stub, (_, c) in zip(control_stubs, pairs, strict=True))
        out["uninstructed_control_hit_rate"] = control_hits / len(pairs)
    return out


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


def modulation_band_layers(mode: str, source_layers: list[int],
                           bands_result: dict | None) -> list[int]:
    """H_modulation read-out band, by pre-registered mode (L1 review #2 rule: deriving the
    band from the same run's CKA and then scoring modulation in it is circular; a FIXED
    depth rule breaks the loop):
    - 'depth_middle_third': middle third of fitted layers, decided a priori (L1b default);
    - 'cka_middle': the H_bands middle band (L1 legacy; circularity disclosed)."""
    if mode == "depth_middle_third":
        return _middle_band_layers(source_layers, None)
    if mode == "cka_middle":
        return _middle_band_layers(source_layers, bands_result)
    raise ValueError(f"unknown modulation_band mode: {mode!r}")


def run_e1(hf: Any, tok: Any, lens_adapter: Any, exp_cfg: dict) -> dict:
    """Run all three E1 evaluators; assemble {hypothesis: {value, threshold, pass, evidence}}
    plus a deduplicated deviations list. Thresholds and all knobs come from exp_cfg (R4)."""
    hyp = exp_cfg["hypotheses"]
    pairs = concept_prompt_pairs(exp_cfg)
    prompts = [p for p, _ in pairs]

    stats_cfg = exp_cfg.get("stats", {})
    seed = int(exp_cfg["seeds"][0])
    resamples = int(stats_cfg.get("permutation_resamples", 0))
    r_report = evaluate_h_report(
        hf, tok, lens_adapter, prompts[:int(hyp["H_report"]["n_prompts"])],
        top_k=int(exp_cfg["top_k"]), permutation_resamples=resamples, seed=seed,
        window=exp_cfg.get("report_window", "late_third"))
    r_bands = evaluate_h_bands(hf, tok, prompts[:int(hyp["H_bands"]["n_prompts"])],
                               skip_first=int(exp_cfg["cka_skip_first"]),
                               min_band_size=int(exp_cfg["cka_min_band_size"]))
    band_layers = modulation_band_layers(exp_cfg.get("modulation_band", "cka_middle"),
                                         lens_adapter.source_layers, r_bands)
    mod_pairs = pairs[:int(hyp["H_modulation"]["n_prompts"])]
    control_stubs = None
    if exp_cfg.get("modulation_uninstructed_control"):
        # Stub = the continuation after the instruction sentence ("Think about X. <stub>").
        control_stubs = [p.split(". ", 1)[1] if ". " in p else p for p, _ in mod_pairs]
    r_mod = evaluate_h_modulation(
        hf, tok, lens_adapter, mod_pairs, band_layers,
        translations=exp_cfg.get("concepts_zh"),
        null_shuffles=int(exp_cfg.get("modulation_null_shuffles", 0)), seed=seed,
        control_stubs=control_stubs,
        variant_policy=exp_cfg.get("concept_variant_policy", "first_id"))
    evaluated = [("H_report", r_report), ("H_bands", r_bands), ("H_modulation", r_mod)]
    if "H_articulation" in hyp:
        evaluated.append(("H_articulation", evaluate_h_articulation(
            hf, tok, lens_adapter, prompts[:int(hyp["H_articulation"]["n_prompts"])],
            top_k=int(exp_cfg["top_k"]), permutation_resamples=resamples, seed=seed)))

    results: dict[str, Any] = {}
    deviations: list[str] = []
    for name, r in evaluated:
        value = float(r[hyp[name]["metric"]])
        threshold = float(hyp[name]["threshold_min"])
        ok = value >= threshold
        if "p_max" in hyp[name] and "permutation_p" in r:
            ok = ok and r["permutation_p"] <= float(hyp[name]["p_max"])
        if "control_margin_min" in hyp[name] and "uninstructed_control_hit_rate" in r:
            ok = ok and (value - r["uninstructed_control_hit_rate"]
                         >= float(hyp[name]["control_margin_min"]))
        results[name] = {"value": value, "threshold": threshold,
                         "pass": bool(ok), "evidence": r}
        for d in r.pop("deviations", []):  # hoist into the gate-level list, deduplicated
            if d not in deviations:
                deviations.append(d)
    results["deviations"] = deviations
    return results
