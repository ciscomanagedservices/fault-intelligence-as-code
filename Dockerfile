# Dockerfile for the DEVNET-3171 webhook relay.
# This container runs only the alert_pipeline.py FastAPI relay service.
# The LLM agent runs in OpenCode (on the host or as a separate service).

FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only what the relay needs
COPY pyproject.toml .
COPY app/ app/

# Install the project (relay only needs fastapi, uvicorn, httpx, pydantic)
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e "."

ENV PYTHONPATH="/app"

EXPOSE 8080

ENTRYPOINT ["python", "-m"]
CMD ["app.alert_pipeline"]
