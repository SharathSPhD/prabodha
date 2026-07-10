FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy source
COPY steer_gateway/ ./steer_gateway/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -m urllib.request.urlopen http://localhost:8100/health || exit 1

# Run
CMD ["python", "-m", "uvicorn", "steer_gateway.main:app", "--host", "0.0.0.0", "--port", "8100"]
