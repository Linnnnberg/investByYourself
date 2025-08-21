# 🔄 ETL Service - InvestByYourself

*Data collection, transformation, and loading service*

## 🎯 **Purpose**

The ETL Service handles all data pipeline operations including:
- **Data Collection**: Yahoo Finance, Alpha Vantage, FRED APIs
- **Data Transformation**: Financial data processing and validation
- **Data Loading**: Database, file, and cache storage operations

## 🏗️ **Architecture**

### **Components**
- **Collectors**: Data collection from external APIs
- **Transformers**: Data processing and validation
- **Loaders**: Data storage and retrieval
- **Orchestrator**: Pipeline coordination and monitoring

### **Data Flow**
```
External APIs → Collectors → Transformers → Loaders → Storage
     ↓              ↓           ↓           ↓         ↓
  Rate Limit   Validation   Processing   Storage   Monitoring
```

## 🚀 **Quick Start**

### **Local Development**
```bash
# Install dependencies
pip install -r requirements.txt

# Run service
python -m uvicorn main:app --reload --port 8000
```

### **Docker**
```bash
# Build image
docker build -t etl-service .

# Run container
docker run -p 8000:8000 etl-service
```

## 📡 **API Endpoints**

### **Health Check**
- `GET /health` - Service health status

### **Data Collection**
- `POST /collect/{source}` - Trigger data collection
- `GET /collect/status/{job_id}` - Collection job status

### **Data Transformation**
- `POST /transform` - Transform collected data
- `GET /transform/status/{job_id}` - Transformation status

### **Data Loading**
- `POST /load` - Load transformed data
- `GET /load/status/{job_id}` - Loading status

## ⚙️ **Configuration**

### **Environment Variables**
```bash
# API Keys
FRED_API_KEY=your_fred_api_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key

# Database
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379

# Service Settings
SERVICE_PORT=8000
LOG_LEVEL=INFO
```

## 🧪 **Testing**

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=.

# Run specific tests
pytest tests/test_collectors.py
```

## 📊 **Monitoring**

- **Health Checks**: `/health` endpoint
- **Metrics**: Prometheus metrics available
- **Logging**: Structured logging with structlog
- **Performance**: Response time and throughput metrics

## 🔗 **Dependencies**

- **External APIs**: Yahoo Finance, Alpha Vantage, FRED
- **Databases**: PostgreSQL, Redis
- **Frameworks**: FastAPI, asyncio, aiohttp
- **Data Processing**: pandas, numpy, pydantic

---

*This service is part of the InvestByYourself microservices architecture*
