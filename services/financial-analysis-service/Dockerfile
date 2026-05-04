# syntax=docker/dockerfile:1.7
# Financial Analysis Service Dockerfile
# Tech-020: Microservices Foundation
#
# Build with BuildKit enabled (default in Docker 23+):
#   DOCKER_BUILDKIT=1 docker build -t ibyy-analysis .

# Multi-stage build for optimization
FROM python:3.11-slim as base

# Note: PIP_NO_CACHE_DIR is intentionally NOT set so the cache mount below
# can persist wheels between builds. The cache lives in BuildKit storage,
# not in image layers, so the final image stays slim.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies (cache APT layers across rebuilds)
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    libfreetype6-dev \
    libpng-dev \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies (cached pip wheels)
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    pip install -r requirements.txt

# Development stage
FROM base as development

# Install development dependencies
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    pip install \
    pytest \
    pytest-asyncio \
    pytest-mock \
    black \
    flake8 \
    mypy \
    isort

# Copy source code
COPY . .

# Set development environment
ENV ENVIRONMENT=development
ENV DEBUG=true

# Expose port for development
EXPOSE 8001

# Development command
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]

# Production stage
FROM base as production

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Copy source code
COPY --chown=appuser:appuser . .

# Set production environment
ENV ENVIRONMENT=production
ENV DEBUG=false

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8001/health')" || exit 1

# Production command
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
