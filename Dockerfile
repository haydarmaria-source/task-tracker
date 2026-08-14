# Task Tracker API image.
# Slim base, runtime-only dependencies, non-root user, no secrets baked in.
FROM python:3.11-slim

WORKDIR /app

# Install only what's needed to run the API (not pytest/httpx dev deps).
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code only — no tests, docs, or frontend in the runtime image.
COPY backend/app ./app

# Run as a non-root user.
RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

# SQLite file is written inside the container at runtime; mount a volume
# at /app if you need the data to persist across container restarts.
EXPOSE 8000

# checkov (CKV_DOCKER_2) flagged the missing HEALTHCHECK; added so the
# container reports its own liveness against the real /health endpoint.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
