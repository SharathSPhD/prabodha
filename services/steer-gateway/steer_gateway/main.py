import json
import hmac
import logging
import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from steer_gateway.runtime import SteeringRuntimeAdapter
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

# Global runtime instance
runtime: Optional[SteeringRuntimeAdapter] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    global runtime
    try:
        # Load configuration from environment with defaults
        model_config = os.getenv("PRABODHA_MODEL_CONFIG", "configs/models/qwen3.yaml")
        lens_file = os.getenv("PRABODHA_LENS_FILE", "outputs/l10/lens_qwen3_mid30.pt")
        site_layer = int(os.getenv("PRABODHA_SITE", "24"))
        max_new_tokens = int(os.getenv("PRABODHA_MAX_NEW_TOKENS", "100"))
        min_gap = int(os.getenv("PRABODHA_MIN_GAP", "2"))
        tau_percentile = int(os.getenv("PRABODHA_TAU_PERCENTILE", "60"))

        logger.info("Initializing SteeringRuntimeAdapter with: model_config=%s, lens_file=%s, site_layer=%d",
                   model_config, lens_file, site_layer)

        runtime = SteeringRuntimeAdapter(
            model_config_path=model_config,
            lens_file=lens_file,
            site_layer=site_layer,
            max_new_tokens=max_new_tokens,
            min_gap=min_gap,
            tau_percentile=tau_percentile,
        )
        logger.info("Gateway initialized (model_id: %s, site_layer: %d)", runtime.model_id, runtime.site_layer)
    except Exception as e:
        logger.error("Failed to initialize gateway: %s", e, exc_info=True)
        raise

    yield

    # Cleanup
    if runtime is not None:
        try:
            # Clean up GPU memory if needed
            import torch
            torch.cuda.empty_cache() if torch.cuda.is_available() else None
        except Exception as e:
            logger.warning("Error during cleanup: %s", e)
    runtime = None

app = FastAPI(
    title="prabodha steer gateway",
    description="SSE proxy for steering runtime",
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
    alpha: float | None = None   # None -> runtime uses the plant's calibrated default
    arm: str = "entropy_gated"
    direction_spec: Optional[DirectionSpec] = None  # Optional contrastive or vector steering

@app.get("/health")
async def health_check():
    """Health check endpoint (no auth required). I3: {"ok": true, "model_id": str}."""
    return {"ok": True, "model_id": runtime.model_id if runtime else "uninitialized"}

@app.post("/steer")
async def steer(
    request: SteerRequest,
    authorization: Optional[str] = Header(None),
):
    """Stream a steering episode via SSE.

    I3 framing: named SSE events — one `token` event per TraceToken JSON,
    then a single `done` event carrying the full SteerTrace JSON.
    """
    # Verify bearer token (use timing-safe comparison to prevent side-channel attacks)
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    provided_token = authorization[7:]

    # Use hmac.compare_digest to prevent timing side-channel attacks
    if not hmac.compare_digest(provided_token, STEER_GATEWAY_SECRET):
        raise HTTPException(status_code=403, detail="Invalid token")

    if not runtime:
        raise HTTPException(status_code=500, detail="Runtime not initialized")

    async def generate():
        try:
            # runtime.steer_stream yields TraceToken objects per decode step,
            # then the completed LiveEpisode with generated text + trace.
            episode = None
            async for item in runtime.steer_stream(
                prompt=request.prompt, concept=request.concept,
                alpha=request.alpha, arm=request.arm,
                direction_spec=request.direction_spec,
            ):
                if isinstance(item, LiveEpisode):
                    episode = item
                    break
                # Emit token events as they arrive (streaming transparency)
                yield f"event: token\ndata: {item.model_dump_json()}\n\n"

            # Emit the complete episode as the done event
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
