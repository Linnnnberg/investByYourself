# ETL Docker Service Technical Specification

*Created: 2025-09-23*
*Status: Technical Design*
*Priority: High*

## 🏗️ **ETL Service Architecture**

### **Container Configuration**
```yaml
# ETL Service Container Specs
etl:
  image: investbyyourself-etl:latest
  container_name: investbyyourself_etl_dev
  environment:
    # Database Configuration
    DATABASE_TYPE: sqlite
    SQLITE_DATABASE: /shared_data/investbyyourself_dev.db
    DATABASE_URL: sqlite+aiosqlite:////shared_data/investbyyourself_dev.db

    # Redis Configuration
    REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0

    # API Keys
    ALPHA_VANTAGE_API_KEY: ${ALPHA_VANTAGE_API_KEY}
    FRED_API_KEY: ${FRED_API_KEY}

    # ETL Configuration
    ETL_MODE: development
    ETL_LOG_LEVEL: INFO
    ETL_BATCH_SIZE: 50
    ETL_RETRY_ATTEMPTS: 3
    ETL_RATE_LIMIT_DELAY: 1.0

    # Data Sources
    ENABLE_YAHOO_FINANCE: true
    ENABLE_ALPHA_VANTAGE: true
    ENABLE_FRED: true

  volumes:
    - etl_data:/app/data
    - shared_data:/shared_data
    - etl_logs:/app/logs
    - ./etl/scripts:/app/scripts:ro

  depends_on:
    - api
    - redis

  networks:
    - investbyyourself_dev_network

  restart: unless-stopped
```

### **Volume Configuration**
```yaml
volumes:
  etl_data:
    driver: local
  shared_data:
    driver: local
  etl_logs:
    driver: local
```

## 📁 **ETL Directory Structure**

```
etl/
├── Dockerfile
├── requirements.txt
├── docker-compose.etl.yml
├── .env.etl.template
├── scripts/
│   ├── __init__.py
│   ├── etl_orchestrator.py
│   ├── collect_historical_data.py
│   ├── collect_company_profiles.py
│   ├── collect_economic_data.py
│   ├── populate_sample_data.py
│   ├── validate_data_quality.py
│   └── backup_data.py
├── config/
│   ├── __init__.py
│   ├── etl_config.yaml
│   ├── data_sources.yaml
│   └── companies_list.yaml
├── src/
│   ├── __init__.py
│   ├── collectors/
│   │   ├── __init__.py
│   │   ├── yahoo_finance_collector.py
│   │   ├── alpha_vantage_collector.py
│   │   └── fred_collector.py
│   ├── transformers/
│   │   ├── __init__.py
│   │   ├── market_data_transformer.py
│   │   ├── company_profile_transformer.py
│   │   └── economic_data_transformer.py
│   ├── loaders/
│   │   ├── __init__.py
│   │   ├── sqlite_loader.py
│   │   └── redis_loader.py
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       ├── retry_handler.py
│       └── rate_limiter.py
└── logs/
    └── etl.log
```

## 🔧 **Dockerfile Specification**

```dockerfile
# ETL Service Dockerfile
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
```

## 📋 **ETL Scripts Specification**

### **1. ETL Orchestrator (`etl_orchestrator.py`)**
```python
"""
ETL Orchestrator - Main entry point for ETL operations
"""
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any

class ETLOrchestrator:
    """Main ETL orchestrator for managing data import operations."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.collectors = {}
        self.transformers = {}
        self.loaders = {}

    async def run_full_import(self):
        """Run complete data import pipeline."""
        pass

    async def run_incremental_import(self):
        """Run incremental data import."""
        pass

    async def run_company_profiles_update(self):
        """Update company profiles."""
        pass

    async def run_historical_data_collection(self):
        """Collect historical market data."""
        pass

    async def run_economic_data_collection(self):
        """Collect economic indicators."""
        pass
```

### **2. Data Collection Scripts**

#### **Historical Data Collection (`collect_historical_data.py`)**
- Collect 5+ years of daily price data
- Calculate technical indicators
- Store in SQLite database
- Update Redis cache

#### **Company Profiles (`collect_company_profiles.py`)**
- Update company information
- Financial statements
- Key metrics and ratios
- Sector and industry data

#### **Economic Data (`collect_economic_data.py`)**
- FRED API integration
- Inflation data (CPI, Core CPI)
- GDP and economic indicators
- Interest rates and monetary policy

### **3. Data Quality & Validation (`validate_data_quality.py`)**
- Data completeness checks
- Data accuracy validation
- Outlier detection
- Data consistency verification

## 🔄 **Scheduling & Automation**

### **Cron-based Scheduling**
```bash
# ETL Cron Jobs
0 6 * * 1-5    # Daily market data collection (weekdays 6 AM)
0 2 * * 1      # Weekly company profiles update (Monday 2 AM)
0 3 1 * *      # Monthly economic data collection (1st of month 3 AM)
0 4 * * 0      # Weekly data quality validation (Sunday 4 AM)
```

### **Manual Triggers**
```bash
# Docker commands for manual ETL operations
docker-compose -f docker-compose.dev.yml exec etl python scripts/collect_historical_data.py
docker-compose -f docker-compose.dev.yml exec etl python scripts/collect_company_profiles.py
docker-compose -f docker-compose.dev.yml exec etl python scripts/collect_economic_data.py
```

## 📊 **Data Flow Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │    │   ETL Service   │    │   Data Storage  │
│                 │    │                 │    │                 │
│ • Yahoo Finance │───▶│ • Collectors    │───▶│ • SQLite DB     │
│ • Alpha Vantage │    │ • Transformers  │    │ • Redis Cache   │
│ • FRED API      │    │ • Loaders       │    │ • Data Files    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   API Service   │
                       │                 │
                       │ • Data Access   │
                       │ • Cache Layer   │
                       │ • Real-time API │
                       └─────────────────┘
```

## 🔐 **Security & Configuration**

### **Environment Variables**
```bash
# ETL Environment Template (.env.etl.template)
# Database Configuration
DATABASE_TYPE=sqlite
SQLITE_DATABASE=investbyyourself_dev.db
DATABASE_URL=sqlite+aiosqlite:////shared_data/investbyyourself_dev.db

# Redis Configuration
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0

# API Keys (Required)
ALPHA_VANTAGE_API_KEY=${ALPHA_VANTAGE_API_KEY}
FRED_API_KEY=${FRED_API_KEY}

# ETL Configuration
ETL_MODE=development
ETL_LOG_LEVEL=INFO
ETL_BATCH_SIZE=50
ETL_RETRY_ATTEMPTS=3
ETL_RATE_LIMIT_DELAY=1.0

# Data Sources (Enable/Disable)
ENABLE_YAHOO_FINANCE=true
ENABLE_ALPHA_VANTAGE=true
ENABLE_FRED=true

# Logging
ETL_LOG_FILE=/app/logs/etl.log
ETL_LOG_MAX_SIZE=10MB
ETL_LOG_BACKUP_COUNT=5
```

### **API Rate Limiting**
```python
# Rate limiting configuration
RATE_LIMITS = {
    'yahoo_finance': {
        'requests_per_second': 1.0,
        'burst_size': 5
    },
    'alpha_vantage': {
        'requests_per_minute': 5,
        'daily_limit': 500
    },
    'fred': {
        'requests_per_second': 0.1,
        'daily_limit': 1000
    }
}
```

## 📈 **Monitoring & Logging**

### **Structured Logging**
```python
# Logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'json': {
            'format': '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/app/logs/etl.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'detailed'
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'detailed'
        }
    },
    'loggers': {
        'etl': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False
        }
    }
}
```

### **Health Checks**
```python
# Health check script
def check_etl_health():
    """Check ETL service health."""
    checks = {
        'database_connection': check_database_connection(),
        'redis_connection': check_redis_connection(),
        'api_keys': check_api_keys(),
        'disk_space': check_disk_space(),
        'last_run': check_last_run_status()
    }
    return all(checks.values()), checks
```

## 🚀 **Deployment Commands**

### **Development Environment**
```bash
# Start ETL service
docker-compose -f docker-compose.dev.yml up etl

# Run specific ETL operations
docker-compose -f docker-compose.dev.yml exec etl python scripts/collect_historical_data.py
docker-compose -f docker-compose.dev.yml exec etl python scripts/collect_company_profiles.py

# View ETL logs
docker-compose -f docker-compose.dev.yml logs -f etl

# Check ETL status
docker-compose -f docker-compose.dev.yml exec etl python scripts/health_check.py
```

### **Production Environment**
```bash
# Build ETL image
docker build -t investbyyourself-etl:latest ./etl

# Run ETL service
docker run -d --name etl-service \
  --env-file .env.production \
  -v etl_data:/app/data \
  -v shared_data:/shared_data \
  investbyyourself-etl:latest
```

## 📋 **Testing Strategy**

### **Unit Tests**
- Individual collector testing
- Transformer validation
- Loader functionality
- Error handling scenarios

### **Integration Tests**
- End-to-end ETL pipeline
- Database integration
- Redis cache integration
- API key validation

### **Performance Tests**
- Data collection speed
- Memory usage optimization
- Database performance
- Network efficiency

## 🔄 **Maintenance Procedures**

### **Daily Operations**
- Monitor ETL logs
- Check data quality
- Verify API key status
- Review error rates

### **Weekly Operations**
- Data backup
- Performance review
- Update company lists
- Clean old logs

### **Monthly Operations**
- Security updates
- Dependency updates
- Performance optimization
- Documentation review

---

**Next Steps:**
1. Review and approve technical specification
2. Create ETL Dockerfile and requirements.txt
3. Implement core ETL scripts
4. Update docker-compose.dev.yml
5. Test ETL pipeline integration
