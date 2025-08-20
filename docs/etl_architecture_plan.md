# ETL Architecture Plan - investByYourself

*Created: January 2025*

## 🎯 **Overview**

This document outlines the comprehensive ETL (Extract, Transform, Load) architecture for the investByYourself platform. The architecture separates external data collection, data parsing/transformation, and internal data storage to create a maintainable, scalable, and reliable data pipeline.

## 🏗️ **Architecture Overview**

### **Three-Layer Architecture:**
```
┌─────────────────────────────────────────────────────────────┐
│                    External Data Sources                     │
│  Yahoo Finance │ Alpha Vantage │ FRED API │ API Ninjas    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    ETL Pipeline Layer                       │
│  Extract │ Transform │ Validate │ Load │ Monitor & Alert  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   Internal Data Structure                   │
│  Database │ Cache │ Analytics │ Export │ Archive          │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 **ETL Process Flow**

### **1. Extract Phase**
```
External API → Rate Limiter → Retry Handler → Data Collector → Raw Data Store
```

### **2. Transform Phase**
```
Raw Data → Parser → Validator → Normalizer → Enricher → Transformed Data
```

### **3. Load Phase**
```
Transformed Data → Quality Check → Conflict Resolution → Database → Cache → Archive
```

## 📊 **Data Sources & Collection Strategy**

### **Primary Data Sources:**
1. **Yahoo Finance (yfinance)**
   - Stock prices, volumes, fundamentals
   - Company profiles and financial statements
   - Real-time and historical data

2. **Alpha Vantage**
   - Technical indicators and analysis
   - Economic data and forex
   - Alternative data sources

3. **FRED API**
   - Economic indicators (CPI, GDP, employment)
   - Interest rates and monetary policy
   - Government and central bank data

4. **API Ninjas (Future)**
   - Earnings data and transcripts
   - Company news and sentiment
   - Market analysis and reports

### **Collection Strategy:**
- **Real-time**: Stock prices, market data (every 1-5 minutes)
- **Daily**: Company fundamentals, economic indicators
- **Weekly**: Portfolio performance, risk metrics
- **Monthly**: Long-term trends, regulatory updates

## 🏛️ **Database Schema Design**

### **Core Entities:**

#### **1. Company Entity**
```sql
CREATE TABLE companies (
    id BIGINT PRIMARY KEY,
    symbol VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap DECIMAL(20,2),
    pe_ratio DECIMAL(10,4),
    dividend_yield DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_source VARCHAR(50),
    data_version INTEGER DEFAULT 1
);
```

#### **2. Stock Price Entity**
```sql
CREATE TABLE stock_prices (
    id BIGINT PRIMARY KEY,
    company_id BIGINT REFERENCES companies(id),
    date DATE NOT NULL,
    open_price DECIMAL(10,4),
    high_price DECIMAL(10,4),
    low_price DECIMAL(10,4),
    close_price DECIMAL(10,4),
    volume BIGINT,
    adjusted_close DECIMAL(10,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_source VARCHAR(50),
    UNIQUE(company_id, date)
);
```

#### **3. Economic Indicator Entity**
```sql
CREATE TABLE economic_indicators (
    id BIGINT PRIMARY KEY,
    indicator_code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    frequency VARCHAR(20),
    unit VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE economic_data (
    id BIGINT PRIMARY KEY,
    indicator_id BIGINT REFERENCES economic_indicators(id),
    date DATE NOT NULL,
    value DECIMAL(15,6),
    change_from_prev DECIMAL(15,6),
    change_percent DECIMAL(8,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(indicator_id, date)
);
```

#### **4. Portfolio Entity**
```sql
CREATE TABLE portfolios (
    id BIGINT PRIMARY KEY,
    user_id BIGINT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE portfolio_holdings (
    id BIGINT PRIMARY KEY,
    portfolio_id BIGINT REFERENCES portfolios(id),
    company_id BIGINT REFERENCES companies(id),
    shares DECIMAL(15,6) NOT NULL,
    average_cost DECIMAL(10,4),
    purchase_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 **Technical Implementation**

### **1. ETL Pipeline Components**

#### **Data Collector Base Class**
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import asyncio
import logging

class DataCollector(ABC):
    """Abstract base class for data collectors."""

    def __init__(self, api_key: str, rate_limit: int = 100):
        self.api_key = api_key
        self.rate_limit = rate_limit
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def collect_data(self, symbol: str) -> Dict[str, Any]:
        """Collect data for a given symbol."""
        pass

    async def collect_batch(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Collect data for multiple symbols with rate limiting."""
        results = []
        for i, symbol in enumerate(symbols):
            if i > 0 and i % self.rate_limit == 0:
                await asyncio.sleep(1)  # Rate limiting
            try:
                data = await self.collect_data(symbol)
                results.append(data)
            except Exception as e:
                self.logger.error(f"Error collecting data for {symbol}: {e}")
        return results
```

#### **Data Transformer**
```python
class DataTransformer:
    """Transform raw data into standardized format."""

    def __init__(self):
        self.transformers = {
            'yahoo_finance': YahooFinanceTransformer(),
            'alpha_vantage': AlphaVantageTransformer(),
            'fred': FredTransformer()
        }

    def transform(self, raw_data: Dict[str, Any], source: str) -> Dict[str, Any]:
        """Transform raw data using appropriate transformer."""
        if source not in self.transformers:
            raise ValueError(f"Unknown data source: {source}")

        transformer = self.transformers[source]
        return transformer.transform(raw_data)

    def validate(self, transformed_data: Dict[str, Any]) -> bool:
        """Validate transformed data."""
        # Implement validation logic
        return True
```

#### **Data Loader**
```python
class DataLoader:
    """Load transformed data into database."""

    def __init__(self, db_session):
        self.db_session = db_session

    async def load_data(self, data: Dict[str, Any], entity_type: str):
        """Load data into appropriate database table."""
        try:
            if entity_type == 'company':
                await self._load_company(data)
            elif entity_type == 'stock_price':
                await self._load_stock_price(data)
            elif entity_type == 'economic_data':
                await self._load_economic_data(data)
            else:
                raise ValueError(f"Unknown entity type: {entity_type}")
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            raise

    async def _load_company(self, data: Dict[str, Any]):
        """Load company data with conflict resolution."""
        # Implementation for company data loading
        pass
```

### **2. Data Quality & Validation**

#### **Validation Rules**
```python
class DataValidator:
    """Validate data quality and integrity."""

    def __init__(self):
        self.rules = {
            'stock_price': [
                self._validate_price_range,
                self._validate_volume_positive,
                self._validate_date_format
            ],
            'company': [
                self._validate_required_fields,
                self._validate_symbol_format,
                self._validate_numeric_ranges
            ]
        }

    def validate(self, data: Dict[str, Any], entity_type: str) -> List[str]:
        """Validate data and return list of errors."""
        errors = []
        if entity_type in self.rules:
            for rule in self.rules[entity_type]:
                try:
                    rule(data)
                except ValidationError as e:
                    errors.append(str(e))
        return errors

    def _validate_price_range(self, data: Dict[str, Any]):
        """Validate stock price is within reasonable range."""
        price = data.get('close_price', 0)
        if price <= 0 or price > 100000:
            raise ValidationError(f"Invalid price: {price}")
```

### **3. Performance Optimization**

#### **Caching Strategy**
```python
class DataCache:
    """Cache frequently accessed data."""

    def __init__(self, redis_client):
        self.redis = redis_client
        self.ttl = {
            'stock_price': 300,      # 5 minutes
            'company_profile': 3600,  # 1 hour
            'economic_data': 86400    # 24 hours
        }

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get data from cache."""
        data = await self.redis.get(key)
        return json.loads(data) if data else None

    async def set(self, key: str, data: Dict[str, Any], entity_type: str):
        """Set data in cache with appropriate TTL."""
        ttl = self.ttl.get(entity_type, 300)
        await self.redis.setex(key, ttl, json.dumps(data))
```

#### **Database Indexing**
```sql
-- Performance indexes
CREATE INDEX idx_stock_prices_company_date ON stock_prices(company_id, date);
CREATE INDEX idx_stock_prices_date ON stock_prices(date);
CREATE INDEX idx_economic_data_indicator_date ON economic_data(indicator_id, date);
CREATE INDEX idx_portfolio_holdings_portfolio ON portfolio_holdings(portfolio_id);

-- Composite indexes for common queries
CREATE INDEX idx_companies_sector_industry ON companies(sector, industry);
CREATE INDEX idx_stock_prices_symbol_date ON stock_prices(company_id, date DESC);
```

## 📈 **Data Pipeline Orchestration**

### **1. Scheduling & Monitoring**

#### **Pipeline Scheduler**
```python
class PipelineScheduler:
    """Schedule and monitor ETL pipeline execution."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.monitor = PipelineMonitor()

    def start(self):
        """Start the ETL pipeline scheduler."""
        # Schedule real-time data collection
        self.scheduler.add_job(
            self._collect_real_time_data,
            'interval',
            minutes=5,
            id='real_time_collection'
        )

        # Schedule daily data collection
        self.scheduler.add_job(
            self._collect_daily_data,
            'cron',
            hour=18,  # 6 PM UTC
            id='daily_collection'
        )

        self.scheduler.start()

    async def _collect_real_time_data(self):
        """Collect real-time market data."""
        try:
            await self.monitor.start_job('real_time_collection')
            # Implementation for real-time collection
            await self.monitor.complete_job('real_time_collection')
        except Exception as e:
            await self.monitor.fail_job('real_time_collection', str(e))
```

### **2. Error Handling & Recovery**

#### **Retry Mechanism**
```python
class RetryHandler:
    """Handle retries for failed API calls."""

    def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    async def execute_with_retry(self, func, *args, **kwargs):
        """Execute function with exponential backoff retry."""
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise e

                wait_time = self.backoff_factor ** attempt
                await asyncio.sleep(wait_time)
```

## 🚀 **Implementation Phases**

### **Phase 1: Foundation (Weeks 4-5)**
- [ ] Design database schema and relationships
- [ ] Create basic ETL pipeline structure
- [ ] Implement data collection base classes
- [ ] Set up database infrastructure

### **Phase 2: Core ETL (Weeks 5-6)**
- [ ] Implement data transformation layer
- [ ] Add data validation and quality checks
- [ ] Create data loading mechanisms
- [ ] Implement basic caching

### **Phase 3: Optimization (Weeks 6-7)**
- [ ] Add performance monitoring
- [ ] Implement advanced caching strategies
- [ ] Optimize database queries
- [ ] Add data archiving

### **Phase 4: Production (Weeks 7-8)**
- [ ] Production deployment
- [ ] Monitoring and alerting
- [ ] Performance testing
- [ ] Documentation and training

## 📊 **Success Metrics**

### **Performance Targets:**
- **Data Collection**: 10,000+ records/hour
- **Data Processing**: <5 seconds per batch
- **Database Queries**: <100ms for standard operations
- **System Uptime**: 99.9% availability

### **Quality Targets:**
- **Data Accuracy**: >99.5% validation success
- **Data Completeness**: <1% missing data
- **Data Freshness**: <5 minutes for real-time data
- **Error Rate**: <0.1% failed operations

## 🔒 **Security & Compliance**

### **Data Security:**
- API key encryption and secure storage
- Data encryption at rest and in transit
- Access control and authentication
- Audit logging and monitoring

### **Compliance:**
- Data retention policies
- Privacy protection measures
- Regulatory compliance (GDPR, etc.)
- Data lineage and traceability

---

## 📝 **Next Steps**

1. **Review and approve this architecture plan**
2. **Start with Phase 1: Foundation**
3. **Create detailed implementation tasks**
4. **Set up development environment**
5. **Begin database schema implementation**

This ETL architecture provides a solid foundation for scalable, maintainable, and reliable financial data processing.
