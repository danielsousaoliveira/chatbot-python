FROM python:3.11-slim

WORKDIR /app

# Point HuggingFace cache to /app/.cache so the same path is used
# during both the build-time model download and at runtime under appuser
ENV HF_HOME=/app/.cache

COPY requirements.txt .

# Install CPU-only torch first to avoid downloading the 420 MB GPU wheel
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt \
    && python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

COPY . .

# Create data directory and non-root user; chown covers /app/.cache too
RUN mkdir -p /app/data \
    && addgroup --system appgroup \
    && adduser --system --ingroup appgroup appuser \
    && chown -R appuser:appgroup /app

USER appuser

EXPOSE 5000

ENTRYPOINT ["bash", "entrypoint.sh"]
