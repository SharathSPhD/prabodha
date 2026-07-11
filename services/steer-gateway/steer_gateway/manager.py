"""Dynamic model manager — load the requested model on demand, run, release when idle.

Concept: no persistent holding. The GPU loads whichever model a request names, steers, and
the model is evicted after an idle window (or when a different model is requested and capacity
is exceeded), freeing GPU memory. This is what lets the gateway serve ANY chosen model, not
just one pre-loaded plant.

Robustness note: fitting a Jacobian lens is an hours-long GPU job, so it cannot happen on the
request path. Models that already have a committed lens (see LENS_REGISTRY) use the full
lens+Jacobian steering; every other model uses real contrastive-direction (CAA) steering — a
genuine difference-in-means over actual activations, not a degraded no-op. Both paths are real.
"""
import logging
import os
import threading
import time

from steer_gateway.runtime import SteeringRuntimeAdapter

logger = logging.getLogger(__name__)

# Models that ship with a committed, pre-fitted Jacobian lens (full lens+Jacobian steering).
# Any model NOT listed here is served with real contrastive-direction steering (no lens needed).
LENS_REGISTRY: dict[str, dict] = {
    # Every model the project works on now ships a REAL fitted Jacobian lens (scripts/experiments/
    # fit_lenses.py, wikitext-2 corpus, n_prompts=16). Lenses live under outputs/lenses/ on the GB10
    # host (gitignored; the gateway container mounts /repo so they resolve). site_layer = the band
    # site the lens was fit for (~0.62 depth). These use the full lens+Jacobian steering — the
    # contrastive path only remains as a fallback for models with no fitted lens yet.
    "Qwen/Qwen3-4B-Instruct-2507": {
        "lens_file": os.getenv("PRABODHA_LENS_FILE", "outputs/l10/lens_qwen3_mid30.pt"),
        "site_layer": int(os.getenv("PRABODHA_SITE", "24")),
    },
    "google/gemma-2-2b-it": {"lens_file": "outputs/lenses/gemma-2-2b-it.pt", "site_layer": 16},
    "Qwen/Qwen2.5-1.5B-Instruct": {"lens_file": "outputs/lenses/qwen2.5-1.5b-instruct.pt", "site_layer": 17},
    "meta-llama/Llama-3.2-1B-Instruct": {"lens_file": "outputs/lenses/llama-3.2-1b-instruct.pt", "site_layer": 9},
    "HuggingFaceTB/SmolLM2-1.7B-Instruct": {"lens_file": "outputs/lenses/smollm2-1.7b-instruct.pt", "site_layer": 14},
    "nvidia/Nemotron-Mini-4B-Instruct": {"lens_file": "outputs/lenses/nemotron-mini-4b-instruct.pt", "site_layer": 19},
}


class _Loaded:
    __slots__ = ("runtime", "last_used", "lock")

    def __init__(self, runtime: SteeringRuntimeAdapter):
        self.runtime = runtime
        self.last_used = time.time()
        self.lock = threading.Lock()  # serialize episodes on one model (single GPU)


class ModelManager:
    """Lazy-loads SteeringRuntimeAdapter per model id, with idle eviction.

    capacity: max models resident at once (default 1 — one GB10). Requesting a new model
    beyond capacity evicts the least-recently-used one first.
    idle_ttl_s: a resident model with no request for this many seconds is unloaded by the reaper.
    """

    def __init__(self, capacity: int = 1, idle_ttl_s: int = 600,
                 max_new_tokens: int = 100, min_gap: int = 2, tau_percentile: int = 60):
        self.capacity = max(1, int(capacity))
        self.idle_ttl_s = int(idle_ttl_s)
        self.max_new_tokens = int(max_new_tokens)
        self.min_gap = int(min_gap)
        self.tau_percentile = int(tau_percentile)
        self._models: dict[str, _Loaded] = {}
        self._guard = threading.Lock()  # guards the _models dict + (un)loads
        self._reaper = threading.Thread(target=self._reap_loop, daemon=True)
        self._reaper.start()

    # ----------------------------------------------------------------- loading
    def _load(self, model_id: str) -> _Loaded:
        cfg = LENS_REGISTRY.get(model_id, {})
        lens_file = cfg.get("lens_file")
        site_layer = cfg.get("site_layer")
        logger.info("Loading model %s (lens=%s)", model_id, bool(lens_file))
        runtime = SteeringRuntimeAdapter(
            model_config_path=model_id,          # bare HF id -> default config
            lens_file=lens_file,                 # None -> contrastive-direction steering
            site_layer=site_layer,               # None -> heuristic band layer
            max_new_tokens=self.max_new_tokens,
            min_gap=self.min_gap,
            tau_percentile=self.tau_percentile,
        )
        return _Loaded(runtime)

    def _evict(self, model_id: str) -> None:
        loaded = self._models.pop(model_id, None)
        if loaded is None:
            return
        logger.info("Evicting model %s (idle release)", model_id)
        try:
            loaded.runtime.unload()
        except Exception as e:  # never let eviction crash the server
            logger.warning("Error unloading %s: %s", model_id, e)

    def get(self, model_id: str) -> _Loaded:
        """Return a resident runtime for model_id, loading (and evicting to fit) as needed."""
        with self._guard:
            loaded = self._models.get(model_id)
            if loaded is not None:
                loaded.last_used = time.time()
                return loaded
            # make room (LRU) before loading a new one
            while len(self._models) >= self.capacity:
                lru = min(self._models, key=lambda k: self._models[k].last_used)
                self._evict(lru)
            loaded = self._load(model_id)
            self._models[model_id] = loaded
            loaded.last_used = time.time()
            return loaded

    # ----------------------------------------------------------------- reaper
    def _reap_loop(self) -> None:
        while True:
            time.sleep(30)
            try:
                now = time.time()
                with self._guard:
                    stale = [
                        mid for mid, l in self._models.items()
                        if now - l.last_used > self.idle_ttl_s and not l.lock.locked()
                    ]
                    for mid in stale:
                        self._evict(mid)
            except Exception as e:
                logger.warning("reaper error: %s", e)

    # ----------------------------------------------------------------- status
    def loaded_ids(self) -> list[str]:
        with self._guard:
            return list(self._models.keys())
