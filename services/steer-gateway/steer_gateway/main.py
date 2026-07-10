import os
import asyncio
import json
from typing import Optional
from fastapi import FastAPI, Header, HTTPException, Response
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
from pydantic import BaseModel

# Load environment
STEER_GATEWAY_SECRET = os.getenv("STEER_GATEWAY_SECRET", "dev-secret")

# Inline trace models (will import from prabodha.contracts.trace in production)
class TraceToken(BaseModel):
    t: int
    token: str
    entropy: float
    gated: bool
    write_norm: Optional[float] = None
    band_topk: Optional[list[str]] = None

class SteerTrace(BaseModel):
    model_id: str
    prompt: str
    concept: str
    arm: str
    seed: int
    alpha: float
    tau_percentile: int
    site_layer: int
    tokens: list[TraceToken]
    created_at: str

class SteeringRuntimeAdapter:
    """Adapter seam to prabodha's steering runtime (real impl wraps the e4 composer;
    the smoke-test fake implements the same generator API, GPU-free)."""

    model_id: str = "Qwen/Qwen3-4B"

    async def steer_stream(self, prompt: str, concept: str,
                           alpha: float | None, arm: str):
        """Yield TraceToken per decode step, then the completed SteerTrace.

        Fake (smoke) implementation shown here; the real adapter (Task: gateway
        runtime wiring) replaces the body by driving the prabodha steering
        composer with --emit-trace semantics and yielding as tokens decode.
        """
        toks = [
            TraceToken(t=0, token=" The", entropy=2.1, gated=False),
            TraceToken(t=1, token=" fire", entropy=1.2, gated=True,
                       write_norm=alpha or 0.3, band_topk=["fire", "flame"]),
        ]
        for tok in toks:
            await asyncio.sleep(0.05)
            yield tok
        yield SteerTrace(
            model_id=self.model_id, prompt=prompt, concept=concept,
            arm=arm, seed=0, alpha=alpha or 0.3, tau_percentile=60,
            site_layer=24, tokens=toks, created_at="1970-01-01T00:00:00Z",
        )

# Global runtime instance
runtime: Optional[SteeringRuntimeAdapter] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    global runtime
    runtime = SteeringRuntimeAdapter()
    yield
    runtime = None

app = FastAPI(
    title="prabodha steer gateway",
    description="SSE proxy for steering runtime",
    lifespan=lifespan,
)

class SteerRequest(BaseModel):
    """Interface I3 (master plan): prompt + concept required; alpha optional; arm fixed default."""
    prompt: str
    concept: str
    alpha: float | None = None   # None -> runtime uses the plant's calibrated default
    arm: str = "entropy_gated"

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
    # Verify bearer token
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = authorization[7:]
    if token != STEER_GATEWAY_SECRET:
        raise HTTPException(status_code=403, detail="Invalid token")

    if not runtime:
        raise HTTPException(status_code=500, detail="Runtime not initialized")

    async def generate():
        try:
            # runtime.steer_stream yields TraceToken objects as they decode,
            # then returns the completed SteerTrace (adapter seam: the fake
            # runtime used in smoke tests implements the same generator API).
            trace = None
            async for tok in runtime.steer_stream(
                prompt=request.prompt, concept=request.concept,
                alpha=request.alpha, arm=request.arm,
            ):
                if isinstance(tok, SteerTrace):
                    trace = tok
                    break
                yield f"event: token\ndata: {tok.model_dump_json()}\n\n"
            if trace is not None:
                yield f"event: done\ndata: {trace.model_dump_json()}\n\n"
        except Exception as e:
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
