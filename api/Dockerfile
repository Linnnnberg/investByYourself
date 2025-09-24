# Multi-stage Dockerfile for InvestByYourself API
# Tech-028: API Implementation

# Base stage with common dependencies
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FINANCIAL_CI=true

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Development stage
FROM base as development

# Install development tools
RUN pip install --no-cache-dir \
    black \
    flake8 \
    mypy \
    pytest \
    pytest-cov \
    pre-commit

# Copy source code
COPY . .

# Install pre-commit hooks (only if in a git repository)
RUN if [ -d ".git" ]; then pre-commit install; else echo "Not in a git repository, skipping pre-commit install"; fi

# Expose port for development server
EXPOSE 8000

# Development command - start the API server
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Testing stage
FROM base as testing

# Install testing dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    pytest-mock \
    pytest-asyncio \
    requests \
    httpx

# Copy source code
COPY . .

# Run tests
CMD ["python", "-m", "pytest", "tests/", "--cov=src", "--cov-report=html"]

# Production stage
FROM base as production

# Copy source code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash financial && \
    chown -R financial:financial /app
USER financial

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Expose port
EXPOSE 8000

# Production command
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
