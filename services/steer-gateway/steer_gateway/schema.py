"""Live episode schema — the contract between gateway and app for live steering.

Concept: sākṣāt-darśana (direct seeing) applied to the steering episode's
behavioral surface — the user sees the actual generated text, baseline vs steered.

Primitive: LiveEpisode carriers the trace + generated text so the app can visualize
the steering effect (alignment shift, jailbreak resistance).
"""
from pydantic import BaseModel
from prabodha.contracts.trace import SteerTrace


class LiveEpisode(BaseModel):
    """Complete steering episode result with generated text.

    I3 gateway contract: the app sends a POST /steer request with prompt/concept/alpha/arm,
    receives token events per TraceToken, then a done event with LiveEpisode JSON.
    This schema ensures the app can display baseline_text and steered_text side-by-side.
    """
    model_id: str                   # e.g. "Qwen/Qwen3-4B"
    prompt: str                     # user-provided prompt
    concept: str                    # steering concept (e.g. "fire", "honesty")
    arm: str                        # baseline|entropy_gated|continuous|prefill_only|rate_matched
    site_layer: int                 # steering write layer (e.g. 24)
    alpha: float | None             # steering intensity (None -> runtime default)
    baseline_text: str              # text generated WITHOUT steering
    steered_text: str               # text generated WITH steering applied
    trace: SteerTrace               # complete per-token trace (entropies, gates, etc.)
    readback: dict | None = None    # optional readback verdict (post-steering concept rank)
    behavioral_hit: bool | None = None  # optional behavioral success signal
    created_at: str                 # ISO-8601 UTC timestamp
