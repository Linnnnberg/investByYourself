# ETL Service Dockerfile
# InvestByYourself Financial Platform

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

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
