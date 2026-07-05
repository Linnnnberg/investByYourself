# ETL System Quick Reference
## InvestByYourself Financial Platform

*Created: 2025-09-23*
*Status: Quick Reference Guide*

---

## 🚀 **Quick Start Commands**

### **Start ETL Service**

The `etl` service uses Compose **profile `etl`**. It does not start with a plain `docker compose up` unless you name it or enable the profile.

```bash
# Recommended: Postgres + Redis + ETL (ETL stays up and logs to Docker Desktop)
docker compose -f docker-compose.dev.yml --profile etl up -d postgres redis etl

# Enable the profile for the whole session, then start only what you need (api needs JWT_SECRET_KEY in .env)
# CMD: set COMPOSE_PROFILES=etl
# PowerShell: $env:COMPOSE_PROFILES="etl"
docker compose -f docker-compose.dev.yml up -d postgres redis etl

# Start only ETL (Compose starts postgres + redis because of depends_on)
docker compose -f docker-compose.dev.yml up -d etl

# Start ETL in the foreground (see logs immediately)
docker compose -f docker-compose.dev.yml up etl
```

### **Run Data Import**
```bash
# Full data import (one-shot; use while the etl container is running)
docker compose -f docker-compose.dev.yml exec etl python scripts/etl_orchestrator.py --mode=full

# Historical data only
docker compose -f docker-compose.dev.yml exec etl python scripts/collect_historical_data.py

# Company profiles only
docker compose -f docker-compose.dev.yml exec etl python scripts/collect_company_profiles.py

# Economic data only
docker compose -f docker-compose.dev.yml exec etl python scripts/collect_economic_data.py

# One-shot import without a long-running etl container
docker compose -f docker-compose.dev.yml run --rm etl python scripts/etl_orchestrator.py --mode=full
```

### **Monitor ETL Operations**
```bash
# View ETL logs
docker compose -f docker-compose.dev.yml logs -f etl

# Check ETL status
docker compose -f docker-compose.dev.yml exec etl python scripts/health_check.py

# Check container status
docker compose -f docker-compose.dev.yml ps etl
```

---

## 📊 **Data Sources**

| Source | Type | Rate Limit | Coverage | Cost |
|--------|------|------------|----------|------|
| **Yahoo Finance** | Market Data | 1 req/sec | Global | Free |
| **Alpha Vantage** | Technical Indicators | 5 req/min | US Focus | Free (250/day) |
| **FRED API** | Economic Data | 120 req/min | US | Free |

---

## 🗄️ **Database Tables**

### **Core Tables**
- `companies` - Company master data
- `market_data` - Stock prices and market metrics
- `financial_ratios` - Financial ratios and metrics
- `economic_indicators` - Economic data and indicators

### **Data Collection Logs**
- `data_collection_logs` - ETL operation tracking
- `data_quality` - Data quality metrics

---

## ⚙️ **Configuration**

### **Environment Variables**
```bash
# Required API Keys
ALPHA_VANTAGE_API_KEY=your_key_here
FRED_API_KEY=your_key_here

# Database Configuration
DATABASE_TYPE=sqlite
SQLITE_DATABASE=investbyyourself_dev.db
DATABASE_URL=sqlite+aiosqlite:////shared_data/investbyyourself_dev.db

# Redis Configuration
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0

# ETL Configuration
ETL_MODE=development
ETL_LOG_LEVEL=INFO
ETL_BATCH_SIZE=50
ETL_RETRY_ATTEMPTS=3
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
    rate_limit: 1.0
  alpha_vantage:
    enabled: true
    rate_limit: 0.083
    daily_limit: 250
  fred:
    enabled: true
    rate_limit: 2.0
```

---

## 🔧 **Troubleshooting**

### **Common Issues**

#### **Database Connection Error**
```bash
# Check database file
docker-compose -f docker-compose.dev.yml exec etl ls -la /shared_data/

# Test database connection
docker-compose -f docker-compose.dev.yml exec etl python scripts/test_database_connection.py
```

#### **API Rate Limiting**
```bash
# Check API keys
docker-compose -f docker-compose.dev.yml exec etl python scripts/check_api_keys.py

# Monitor rate limiting
docker-compose -f docker-compose.dev.yml logs etl | grep "rate limit"
```

#### **Data Quality Issues**
```bash
# Validate data quality
docker-compose -f docker-compose.dev.yml exec etl python scripts/validate_data_quality.py

# Check data completeness
docker-compose -f docker-compose.dev.yml exec etl python scripts/check_data_completeness.py
```

### **Debug Commands**
```bash
# Access ETL container
docker-compose -f docker-compose.dev.yml exec etl bash

# Check disk usage
docker-compose -f docker-compose.dev.yml exec etl df -h

# Monitor resource usage
docker stats investbyyourself_etl_dev

# View specific logs
docker-compose -f docker-compose.dev.yml logs etl | grep ERROR
```

---

## 📈 **Data Collection Schedule**

### **Automated Schedule**
- **Daily Market Data**: Weekdays 6:00 AM
- **Weekly Company Profiles**: Monday 2:00 AM
- **Monthly Economic Data**: 1st of month 3:00 AM
- **Weekly Data Validation**: Sunday 4:00 AM

### **Manual Triggers**
```bash
# Trigger specific operations
docker-compose -f docker-compose.dev.yml exec etl python scripts/etl_orchestrator.py --mode=incremental

# Update specific company
docker-compose -f docker-compose.dev.yml exec etl python scripts/collect_historical_data.py --symbol=AAPL

# Update date range
docker-compose -f docker-compose.dev.yml exec etl python scripts/collect_historical_data.py --start-date=2024-01-01 --end-date=2024-12-31
```

---

## 📊 **Monitoring & Metrics**

### **Health Checks**
- Database connectivity
- Redis connectivity
- API key validation
- Disk space monitoring
- Last run status

### **Key Metrics**
- Companies processed
- Records collected
- Errors encountered
- Processing time
- API calls made

### **Log Files**
- `/app/logs/etl.log` - Main ETL log
- `/app/logs/collectors.log` - Data collection logs
- `/app/logs/errors.log` - Error logs

---

## 🔄 **Data Flow**

```
Data Sources → ETL Container → Database → API → Frontend
     ↓              ↓            ↓        ↓        ↓
Yahoo Finance   Collectors   SQLite    FastAPI   Next.js
Alpha Vantage   Transformers  Redis    Cache     React
FRED API        Loaders      Files    Real-time  UI
```

---

## 📚 **File Structure**

```
etl/
├── Dockerfile
├── requirements.txt
├── scripts/
│   ├── etl_orchestrator.py
│   ├── collect_historical_data.py
│   ├── collect_company_profiles.py
│   ├── collect_economic_data.py
│   ├── validate_data_quality.py
│   └── health_check.py
├── config/
│   ├── etl_config.yaml
│   └── data_sources.yaml
└── logs/
    └── etl.log
```

---

## 🎯 **Next Steps**

1. **Review Documentation** - Ensure all team members understand ETL system
2. **Set Up API Keys** - Configure Alpha Vantage and FRED API keys
3. **Test ETL Pipeline** - Run initial data collection
4. **Monitor Performance** - Track data quality and processing times
5. **Schedule Operations** - Set up automated data collection

---

**For detailed information, see:**
- [ETL System Documentation](etl-system-documentation.md)
- [Docker ETL Specification](etl-docker-specification.md)
- [Database ETL Implementation Report](../reports/database_etl_implementation_report.md)
