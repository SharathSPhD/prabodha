# prabodha GB10 image — aarch64, CUDA (sm_121), bf16. Build ON the DGX Spark.
# Base: NGC PyTorch (aarch64, CUDA 13 era — same family as prabhasa's nemo-gb10 container).
FROM nvcr.io/nvidia/pytorch:25.06-py3
WORKDIR /workspace/prabodha
COPY pyproject.toml README.md LICENSE NOTICE ./
COPY src ./src
COPY vendor ./vendor
COPY configs ./configs
COPY scripts ./scripts
COPY tests ./tests
COPY contracts ./contracts
COPY gates ./gates
COPY research ./research
RUN pip install --no-cache-dir -e .[dev] && \
    pip install --no-cache-dir transformers && \
    pip install --no-cache-dir -e vendor/jacobian-lens
# HF cache mounted at runtime; models pulled on the Spark, not baked in.
ENV HF_HOME=/workspace/hf_cache
ENTRYPOINT ["bash"]
