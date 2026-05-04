# syntax=docker/dockerfile:1.7
# ETL Service Dockerfile
# InvestByYourself Financial Platform
#
# Build with BuildKit enabled (default in Docker 23+):
#   DOCKER_BUILDKIT=1 docker build -t ibyy-etl .

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (cache APT layers across rebuilds)
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    git \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies (cached pip wheels)
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy ETL source code
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY config/ ./config/

# Create necessary directories
RUN mkdir -p /app/data /app/logs /shared_data

# Set permissions
RUN chmod +x scripts/*.py

# Create non-root user
RUN useradd -m -u 1000 etluser && \
    chown -R etluser:etluser /app
USER etluser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python scripts/health_check.py

# Default command
CMD ["python", "scripts/etl_orchestrator.py"]
