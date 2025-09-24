# ETL System Documentation
## InvestByYourself Financial Platform

*Created: 2025-09-23*
*Status: Active Development*
*Version: 2.0*

---

## 📋 **Table of Contents**

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Data Sources](#data-sources)
4. [ETL Pipeline](#etl-pipeline)
5. [Docker Integration](#docker-integration)
6. [Data Models](#data-models)
7. [Configuration](#configuration)
8. [Operations](#operations)
9. [Monitoring](#monitoring)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 **Overview**

The InvestByYourself ETL (Extract, Transform, Load) system is a comprehensive data pipeline designed to collect, process, and store financial market data from multiple sources. The system is fully containerized using Docker and integrates seamlessly with our development and production environments.

### **Key Features**
- **Multi-source Data Collection**: Yahoo Finance, Alpha Vantage, FRED API
- **Real-time & Historical Data**: Market prices, company profiles, economic indicators
- **Docker Containerization**: Fully containerized ETL operations
- **Data Quality Assurance**: Validation, cleaning, and quality scoring
- **Scalable Architecture**: Designed for high-volume data processing
- **Monitoring & Logging**: Comprehensive observability and debugging

### **Current Status**
- ✅ **Core ETL Pipeline**: Complete with collectors, transformers, loaders
- ✅ **Docker Integration**: Containerized ETL service
- ✅ **Database Models**: SQLite/PostgreSQL data models
- ✅ **Data Sources**: Yahoo Finance, Alpha Vantage, FRED integration
- 🔄 **Scheduling**: Automated data collection (in progress)
- 🔄 **Monitoring**: Enhanced logging and metrics (in progress)

---

## 🏗️ **Architecture**

### **High-Level Architecture**
```
┌─────────────────────────────────────────────────────────────┐
│                    ETL System Architecture                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Data      │    │   ETL       │    │   Data      │     │
│  │  Sources    │───▶│  Pipeline   │───▶│  Storage    │     │
│  │             │    │             │    │             │     │
│  │ • Yahoo     │    │ • Collect   │    │ • SQLite    │     │
│  │   Finance   │    │ • Transform │    │ • Redis     │     │
│  │ • Alpha     │    │ • Load      │    │ • Files     │     │
│  │   Vantage   │    │ • Validate  │    │             │     │
│  │ • FRED API  │    │ • Schedule  │    │             │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Docker Container Environment              │ │
│  │  • ETL Service Container  • Shared Volumes            │ │
│  │  • API Integration       • Redis Cache                │ │
│  │  • Scheduled Jobs        • Health Monitoring          │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### **ETL Pipeline Components**

#### **1. Data Collectors**
- **`yahoo_finance_collector.py`**: Stock prices, company profiles, market data
- **`alpha_vantage_collector.py`**: Technical indicators, alternative data
- **`fred_collector.py`**: Economic indicators, macroeconomic data
- **`base_collector.py`**: Abstract base class with common functionality

#### **2. Data Transformers**
- **`market_data_transformer.py`**: Price data processing and validation
- **`company_profile_transformer.py`**: Company information processing
- **`economic_data_transformer.py`**: Economic indicator processing
- **`base_transformer.py`**: Common transformation utilities

#### **3. Data Loaders**
- **`sqlite_loader.py`**: SQLite database operations
- **`redis_loader.py`**: Redis cache management
- **`file_loader.py`**: File-based data storage
- **`base_loader.py`**: Abstract loading interface

#### **4. ETL Orchestration**
- **`etl_orchestrator.py`**: Main ETL coordination and scheduling
- **`worker.py`**: Individual ETL job execution
- **`retry_handler.py`**: Error handling and retry logic
- **`rate_limiter.py`**: API rate limiting and throttling

---

## 📊 **Data Sources**

### **1. Yahoo Finance (yfinance)**
```python
# Primary data source for market data
YAHOO_FINANCE = {
    "rate_limit": "1 request/second",
    "data_types": [
        "stock_prices",      # OHLCV data
        "company_profiles",  # Basic company info
        "financials",        # Income statements, balance sheets
        "market_cap",        # Market capitalization
        "dividends"          # Dividend history
    ],
    "coverage": "Global markets",
    "cost": "Free",
    "reliability": "High"
}
```

**Data Collected:**
- Daily OHLCV price data (5+ years)
- Company profiles and metadata
- Financial statements (quarterly/annual)
- Market capitalization and ratios
- Dividend and split history

### **2. Alpha Vantage**
```python
# Secondary source for technical indicators
ALPHA_VANTAGE = {
    "rate_limit": "5 requests/minute (free tier)",
    "data_types": [
        "technical_indicators",  # RSI, MACD, Bollinger Bands
        "fundamental_data",      # Enhanced financial metrics
        "news_sentiment",        # News and sentiment analysis
        "cryptocurrency"         # Crypto market data
    ],
    "coverage": "US markets focus",
    "cost": "Free tier: 250 calls/day",
    "reliability": "High"
}
```

**Data Collected:**
- Technical indicators (RSI, MACD, SMA, EMA)
- Enhanced fundamental data
- News sentiment scores
- Alternative market data

### **3. FRED API (Federal Reserve)**
```python
# Economic indicators and macroeconomic data
FRED_API = {
    "rate_limit": "120 requests/minute",
    "data_types": [
        "inflation",           # CPI, Core CPI, PPI
        "gdp",                 # Gross Domestic Product
        "interest_rates",      # Federal funds rate, Treasury yields
        "employment",          # Unemployment rate, job data
        "monetary_policy"      # Money supply, Fed balance sheet
    ],
    "coverage": "US economic data",
    "cost": "Free",
    "reliability": "Very High"
}
```

**Data Collected:**
- Consumer Price Index (CPI)
- Gross Domestic Product (GDP)
- Federal funds rate
- Unemployment rate
- Treasury bond yields

---

## 🔄 **ETL Pipeline**

### **Data Flow Process**
```
1. EXTRACT    → 2. TRANSFORM  → 3. VALIDATE  → 4. LOAD
   ↓              ↓              ↓              ↓
Data Sources   Data Cleaning   Quality Check   Database
   ↓              ↓              ↓              ↓
API Calls     Format Convert   Validation     SQLite/Redis
   ↓              ↓              ↓              ↓
Rate Limit    Data Enrich     Error Handle   Cache Update
```

### **ETL Orchestrator**
```python
class ETLOrchestrator:
    """Main ETL coordination and management."""

    async def run_full_import(self):
        """Execute complete data import pipeline."""
        # 1. Collect company profiles
        await self.collect_company_profiles()

        # 2. Collect historical market data
        await self.collect_historical_data()

        # 3. Collect economic indicators
        await self.collect_economic_data()

        # 4. Validate data quality
        await self.validate_data_quality()

        # 5. Update cache
        await self.update_cache()

    async def run_incremental_import(self):
        """Execute incremental data updates."""
        # Only collect new/updated data
        pass
```

### **Data Collection Strategies**

#### **Batch Processing**
- Process multiple companies simultaneously
- Optimize API calls and reduce rate limiting
- Implement retry logic for failed requests
- Progress tracking and error reporting

#### **Incremental Updates**
- Only collect new data since last run
- Track last update timestamps
- Efficient resource utilization
- Faster execution times

#### **Error Handling**
- Retry failed requests with exponential backoff
- Log errors for debugging and monitoring
- Continue processing other data on failures
- Alert on critical errors

---

## 🐳 **Docker Integration**

### **ETL Service Container**
```yaml
# docker-compose.dev.yml
etl:
  build:
    context: ./etl
    dockerfile: Dockerfile
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

  volumes:
    - etl_data:/app/data
    - shared_data:/shared_data
    - etl_logs:/app/logs

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
    driver_opts:
      type: none
      o: bind
      device: ./data/etl
  shared_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./data/shared
  etl_logs:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ./logs/etl
```

### **Docker Commands**
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

---

## 🗄️ **Data Models**

### **Core Data Tables**

#### **Companies Table**
```sql
CREATE TABLE companies (
    id TEXT PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    exchange VARCHAR(20),
    currency VARCHAR(3) DEFAULT 'USD',
    country VARCHAR(100),
    website VARCHAR(255),
    description TEXT,
    employee_count INTEGER,
    market_cap DECIMAL(20,2),
    enterprise_value DECIMAL(20,2),
    ceo VARCHAR(255),
    headquarters VARCHAR(255),
    founded_year INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **Market Data Table**
```sql
CREATE TABLE market_data (
    id TEXT PRIMARY KEY,
    company_id TEXT REFERENCES companies(id),
    data_date DATE NOT NULL,
    open_price DECIMAL(10,4),
    high_price DECIMAL(10,4),
    low_price DECIMAL(10,4),
    close_price DECIMAL(10,4),
    adjusted_close DECIMAL(10,4),
    volume BIGINT,
    market_cap DECIMAL(20,2),
    enterprise_value DECIMAL(20,2),
    pe_ratio DECIMAL(8,4),
    pb_ratio DECIMAL(8,4),
    ps_ratio DECIMAL(8,4),
    dividend_yield DECIMAL(6,4),
    beta DECIMAL(6,4),
    source VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **Financial Ratios Table**
```sql
CREATE TABLE financial_ratios (
    id TEXT PRIMARY KEY,
    company_id TEXT REFERENCES companies(id),
    period_end_date DATE,
    current_ratio DECIMAL(8,4),
    quick_ratio DECIMAL(8,4),
    debt_to_equity DECIMAL(8,4),
    return_on_equity DECIMAL(8,4),
    return_on_assets DECIMAL(8,4),
    gross_margin DECIMAL(8,4),
    operating_margin DECIMAL(8,4),
    net_margin DECIMAL(8,4),
    source VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **Economic Indicators Table**
```sql
CREATE TABLE economic_indicators (
    id TEXT PRIMARY KEY,
    indicator_code VARCHAR(20) NOT NULL,
    indicator_name VARCHAR(255) NOT NULL,
    data_date DATE NOT NULL,
    value DECIMAL(15,6),
    unit VARCHAR(50),
    frequency VARCHAR(20),
    source VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## ⚙️ **Configuration**

### **Environment Variables**
```bash
# .env.etl.template
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

### **ETL Configuration File**
```yaml
# config/etl_config.yaml
etl:
  mode: development
  batch_size: 50
  retry_attempts: 3
  rate_limit_delay: 1.0

data_sources:
  yahoo_finance:
    enabled: true
    rate_limit: 1.0  # requests per second
    timeout: 30

  alpha_vantage:
    enabled: true
    rate_limit: 0.083  # 5 requests per minute
    timeout: 30
    daily_limit: 250

  fred:
    enabled: true
    rate_limit: 2.0  # 120 requests per minute
    timeout: 30

logging:
  level: INFO
  file: /app/logs/etl.log
  max_size: 10MB
  backup_count: 5
  format: detailed
```

---

## 🚀 **Operations**

### **Manual ETL Operations**

#### **Full Data Import**
```bash
# Run complete data import
docker-compose -f docker-compose.dev.yml exec etl python scripts/etl_orchestrator.py --mode=full

# Collect historical data only
docker-compose -f docker-compose.dev.yml exec etl python scripts/collect_historical_data.py

# Update company profiles
docker-compose -f docker-compose.dev.yml exec etl python scripts/collect_company_profiles.py

# Collect economic data
docker-compose -f docker-compose.dev.yml exec etl python scripts/collect_economic_data.py
```

#### **Incremental Updates**
```bash
# Run incremental update
docker-compose -f docker-compose.dev.yml exec etl python scripts/etl_orchestrator.py --mode=incremental

# Update specific company
docker-compose -f docker-compose.dev.yml exec etl python scripts/collect_historical_data.py --symbol=AAPL

# Update specific date range
docker-compose -f docker-compose.dev.yml exec etl python scripts/collect_historical_data.py --start-date=2024-01-01 --end-date=2024-12-31
```

### **Scheduled Operations**

#### **Cron-based Scheduling**
```bash
# ETL Cron Jobs (in container)
0 6 * * 1-5    # Daily market data collection (weekdays 6 AM)
0 2 * * 1      # Weekly company profiles update (Monday 2 AM)
0 3 1 * *      # Monthly economic data collection (1st of month 3 AM)
0 4 * * 0      # Weekly data quality validation (Sunday 4 AM)
```

#### **Docker Compose Scheduling**
```yaml
# Add to docker-compose.dev.yml
etl-scheduler:
  image: investbyyourself-etl:latest
  command: python scripts/scheduler.py
  environment:
    - ETL_SCHEDULE_MODE=cron
  volumes:
    - etl_data:/app/data
    - shared_data:/shared_data
  depends_on:
    - etl
    - redis
```

---

## 📊 **Monitoring**

### **Health Checks**
```python
# scripts/health_check.py
def check_etl_health():
    """Comprehensive ETL health check."""
    checks = {
        'database_connection': check_database_connection(),
        'redis_connection': check_redis_connection(),
        'api_keys': check_api_keys(),
        'disk_space': check_disk_space(),
        'last_run': check_last_run_status(),
        'data_quality': check_data_quality()
    }

    status = all(checks.values())
    return status, checks
```

### **Logging Configuration**
```python
# Structured logging setup
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

### **Metrics Collection**
```python
# ETL metrics tracking
class ETLMetrics:
    def __init__(self):
        self.collection_stats = {
            'companies_processed': 0,
            'records_collected': 0,
            'errors_encountered': 0,
            'processing_time': 0,
            'api_calls_made': 0
        }

    def update_metrics(self, **kwargs):
        """Update ETL metrics."""
        for key, value in kwargs.items():
            if key in self.collection_stats:
                self.collection_stats[key] += value
```

---

## 🔧 **Troubleshooting**

### **Common Issues**

#### **1. Database Connection Errors**
```bash
# Check database file permissions
docker-compose -f docker-compose.dev.yml exec etl ls -la /shared_data/

# Verify database URL
docker-compose -f docker-compose.dev.yml exec etl python -c "import os; print(os.getenv('DATABASE_URL'))"

# Test database connection
docker-compose -f docker-compose.dev.yml exec etl python scripts/test_database_connection.py
```

#### **2. API Rate Limiting**
```bash
# Check API key status
docker-compose -f docker-compose.dev.yml exec etl python scripts/check_api_keys.py

# Monitor rate limiting
docker-compose -f docker-compose.dev.yml logs etl | grep "rate limit"

# Adjust rate limiting settings
# Edit config/etl_config.yaml and restart container
```

#### **3. Data Quality Issues**
```bash
# Run data quality validation
docker-compose -f docker-compose.dev.yml exec etl python scripts/validate_data_quality.py

# Check data completeness
docker-compose -f docker-compose.dev.yml exec etl python scripts/check_data_completeness.py

# Review data quality logs
docker-compose -f docker-compose.dev.yml logs etl | grep "quality"
```

### **Debug Commands**
```bash
# View ETL logs
docker-compose -f docker-compose.dev.yml logs -f etl

# Check container status
docker-compose -f docker-compose.dev.yml ps etl

# Access ETL container shell
docker-compose -f docker-compose.dev.yml exec etl bash

# Check disk usage
docker-compose -f docker-compose.dev.yml exec etl df -h

# Monitor resource usage
docker stats investbyyourself_etl_dev
```

---

## 📚 **API Reference**

### **ETL Scripts**

#### **`etl_orchestrator.py`**
```python
# Main ETL orchestration script
python scripts/etl_orchestrator.py [options]

Options:
  --mode {full,incremental}    ETL mode (default: full)
  --batch-size INTEGER         Batch size for processing (default: 50)
  --retry-attempts INTEGER     Number of retry attempts (default: 3)
  --log-level {DEBUG,INFO,WARNING,ERROR}  Log level (default: INFO)
```

#### **`collect_historical_data.py`**
```python
# Historical data collection script
python scripts/collect_historical_data.py [options]

Options:
  --symbol TEXT               Specific company symbol
  --start-date DATE           Start date (YYYY-MM-DD)
  --end-date DATE             End date (YYYY-MM-DD)
  --years INTEGER             Number of years to collect (default: 5)
```

#### **`collect_company_profiles.py`**
```python
# Company profile collection script
python scripts/collect_company_profiles.py [options]

Options:
  --symbol TEXT               Specific company symbol
  --update-existing           Update existing profiles
  --validate-data             Validate collected data
```

---

## 🎯 **Future Enhancements**

### **Planned Features**
1. **Real-time Data Streaming**: WebSocket integration for live data
2. **Advanced Analytics**: Machine learning-based data analysis
3. **Data Visualization**: ETL pipeline monitoring dashboard
4. **Cloud Integration**: AWS/Azure data storage options
5. **API Gateway**: RESTful API for ETL operations

### **Performance Optimizations**
1. **Parallel Processing**: Multi-threaded data collection
2. **Caching Strategy**: Enhanced Redis caching
3. **Database Optimization**: Query performance tuning
4. **Resource Management**: Memory and CPU optimization

---

**Document Version**: 2.0
**Last Updated**: 2025-09-23
**Next Review**: 2025-10-23
**Maintained By**: Development Team
