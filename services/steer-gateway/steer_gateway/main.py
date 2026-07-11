import json
import asyncio
import hmac
import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from steer_gateway.manager import ModelManager
from steer_gateway.schema import LiveEpisode, DirectionSpec

# Secure logging - never log secrets
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Load environment - fail fast if secret not set
STEER_GATEWAY_SECRET = os.getenv("STEER_GATEWAY_SECRET")
if not STEER_GATEWAY_SECRET:
    raise RuntimeError(
        "STEER_GATEWAY_SECRET environment variable is not set. "
        "Gateway cannot start without authentication credentials."
    )

# Default model when a request does not name one.
DEFAULT_MODEL = os.getenv("PRABODHA_DEFAULT_MODEL", "Qwen/Qwen3-4B-Instruct-2507")

# Dynamic model manager: loads the requested model on demand, evicts on idle (no persistent hold).
manager: Optional[ModelManager] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown. No model is loaded at startup — models load on first request and are
    released when idle, so the GPU is only occupied while a chosen model is actually in use."""
    global manager
    manager = ModelManager(
        capacity=int(os.getenv("PRABODHA_MODEL_CAPACITY", "1")),
        idle_ttl_s=int(os.getenv("PRABODHA_MODEL_IDLE_TTL", "600")),
        max_new_tokens=int(os.getenv("PRABODHA_MAX_NEW_TOKENS", "100")),
        min_gap=int(os.getenv("PRABODHA_MIN_GAP", "2")),
        tau_percentile=int(os.getenv("PRABODHA_TAU_PERCENTILE", "60")),
    )
    logger.info("Gateway ready (dynamic model manager; default=%s, no model preloaded)", DEFAULT_MODEL)
    yield
    manager = None

app = FastAPI(
    title="prabodha steer gateway",
    description="SSE proxy for dynamic multi-model steering runtime",
    lifespan=lifespan,
)

class SteerRequest(BaseModel):
    """Interface I3 (master plan): prompt + concept required; alpha optional; arm fixed default.

    Extension: direction_spec allows contrastive or explicit vector steering.
    If direction_spec is provided, concept is still required for identification but not
    used for token-based steering (direction comes from pos/neg activations or vector instead).
    """
    prompt: str
    concept: str
    model: str | None = None     # HF model id to steer; None -> DEFAULT_MODEL. Any model works.
    alpha: float | None = None   # None -> runtime uses the plant's calibrated default
    arm: str = "entropy_gated"
    direction_spec: Optional[DirectionSpec] = None  # Optional contrastive or vector steering

@app.get("/health")
async def health_check():
    """Health check (no auth). Dynamic: reports which models are currently resident (may be none)."""
    loaded = manager.loaded_ids() if manager else []
    return {"ok": manager is not None, "loaded_models": loaded,
            "default_model": DEFAULT_MODEL,
            # Back-compat: model_id = the resident model (first) or the default that would load.
            "model_id": loaded[0] if loaded else DEFAULT_MODEL}

@app.post("/steer")
async def steer(
    request: SteerRequest,
    authorization: Optional[str] = Header(None),
):
    """Stream a steering episode via SSE on the REQUESTED model (loaded on demand).

    Named SSE events — one `token` event per TraceToken JSON, then a single `done` event
    carrying the full LiveEpisode JSON.
    """
    # Verify bearer token (use timing-safe comparison to prevent side-channel attacks)
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    provided_token = authorization[7:]

    # Use hmac.compare_digest to prevent timing side-channel attacks
    if not hmac.compare_digest(provided_token, STEER_GATEWAY_SECRET or ""):
        raise HTTPException(status_code=403, detail="Invalid token")

    if manager is None:
        raise HTTPException(status_code=503, detail="Gateway not ready")

    model_id = (request.model or DEFAULT_MODEL).strip()

    async def generate():
        try:
            # Load the requested model on demand (evicts idle models to free the GPU).
            loop = asyncio.get_event_loop()
            loaded = await loop.run_in_executor(None, manager.get, model_id)
            # Serialize episodes on one model (single GPU) via its lock; run the (sync) steering
            # generation in a thread so the event loop stays responsive.
            with loaded.lock:
                episode = None
                async for item in loaded.runtime.steer_stream(
                    prompt=request.prompt, concept=request.concept,
                    alpha=request.alpha, arm=request.arm,
                    direction_spec=request.direction_spec,
                ):
                    if isinstance(item, LiveEpisode):
                        episode = item
                        break
                    yield f"event: token\ndata: {item.model_dump_json()}\n\n"
                if episode is not None:
                    yield f"event: done\ndata: {episode.model_dump_json()}\n\n"
        except Exception as e:
            logger.error("Streaming error: %s", e, exc_info=True)
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8100)
