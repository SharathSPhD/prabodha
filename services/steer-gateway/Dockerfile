FROM pytorch/pytorch:2.1.2-cuda12.1-cudnn8-runtime

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies from pyproject.toml (includes prabodha[lens], torch, transformers)
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy source
COPY steer_gateway/ ./steer_gateway/

# Health check (simple HTTP probe)
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8100/health').read()" || exit 1

# Run the FastAPI app
CMD ["python", "-m", "uvicorn", "steer_gateway.main:app", "--host", "0.0.0.0", "--port", "8100"]
