# Financial Analysis Service

**Investment Strategy Module - Microservice**

A FastAPI-based microservice for managing investment strategies, executing backtests, and analyzing financial results.

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.11+
- PostgreSQL (optional, uses in-memory storage by default)
- Redis (optional, for caching)

### **Installation**

1. **Navigate to service directory**:
   ```bash
   cd services/financial-analysis-service
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables** (optional):
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start the service**:
   ```bash
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
   ```

5. **Access the API**:
   - **API Documentation**: http://127.0.0.1:8001/docs
   - **Health Check**: http://127.0.0.1:8001/health
   - **Ready Check**: http://127.0.0.1:8001/ready

## 📊 **API Endpoints**

### **Strategies Management** (`/api/v1/strategies/`)
- `POST /` - Create new investment strategy
- `GET /` - List all strategies
- `GET /{strategy_id}` - Get strategy details
- `PUT /{strategy_id}` - Update strategy
- `DELETE /{strategy_id}` - Delete strategy
- `POST /{strategy_id}/validate` - Validate strategy configuration

### **Backtesting** (`/api/v1/backtesting/`)
- `POST /` - Create new backtest
- `GET /` - List all backtests
- `GET /{backtest_id}` - Get backtest details
- `GET /{backtest_id}/progress` - Get backtest progress
- `DELETE /{backtest_id}` - Cancel backtest
- `POST /{backtest_id}/retry` - Retry failed backtest

### **Results Analysis** (`/api/v1/results/`)
- `GET /{backtest_id}/metrics` - Get performance metrics
- `GET /{backtest_id}/portfolio-values` - Get portfolio values over time
- `GET /{backtest_id}/weights` - Get portfolio weights over time
- `GET /{backtest_id}/trades` - Get trade history
- `GET /{backtest_id}/risk-metrics` - Get risk analysis
- `GET /{backtest_id}/drawdown` - Get drawdown analysis
- `GET /{backtest_id}/rolling-returns` - Get rolling returns
- `POST /{backtest_id}/report` - Generate comprehensive report
- `GET /{backtest_id}/download` - Download results as CSV/JSON

## 🏗️ **Architecture**

```
app/
├── main.py                 # FastAPI application entry point
├── api/                    # API routers
│   ├── strategies.py       # Strategy management endpoints
│   ├── backtesting.py      # Backtest execution endpoints
│   └── results.py          # Results retrieval endpoints
├── core/                   # Core infrastructure
│   ├── config.py           # Configuration management
│   ├── database.py         # Database connection management
│   └── security.py         # Authentication & authorization
└── models/                 # SQLAlchemy data models
    ├── strategy.py         # Strategy model
    ├── backtest.py         # Backtest model
    └── user.py             # User model
```

## 🔧 **Configuration**

### **Environment Variables**

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://user:password@localhost:5432/financial_analysis` | Database connection string |
| `SECRET_KEY` | `your-secret-key-here-change-in-production` | JWT secret key |
| `DEBUG` | `False` | Debug mode flag |
| `HOST` | `0.0.0.0` | Service host address |
| `PORT` | `8001` | Service port number |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |
| `LOG_LEVEL` | `INFO` | Logging level |

### **Database Configuration**

The service supports PostgreSQL with SQLAlchemy ORM. For development, it falls back to in-memory storage if no database is available.

## 🔐 **Security**

- **JWT Authentication**: Token-based authentication
- **Password Hashing**: Secure password storage with `passlib`
- **Role-based Access Control**: User roles and permissions
- **CORS Configuration**: Configurable cross-origin requests
- **Input Validation**: Pydantic models for request validation

## 🧪 **Testing**

### **Service Validation**
```bash
# Test service structure and imports
python -c "from app.main import app; print('Service structure OK')"

# Test configuration
python -c "from app.core.config import get_settings; print(get_settings().service_name)"
```

### **API Testing**
```bash
# Health check
curl http://127.0.0.1:8001/health

# List strategies
curl http://127.0.0.1:8001/api/v1/strategies/
```

## 🚀 **Deployment**

### **Docker Deployment**
```bash
# Build image
docker build -t financial-analysis-service .

# Run container
docker run -p 8001:8001 financial-analysis-service
```

### **Production Considerations**
- Set proper `SECRET_KEY` in production
- Configure production database
- Enable HTTPS
- Set up monitoring and logging
- Configure rate limiting
- Set up backup and recovery

## 📈 **Performance**

- **Startup Time**: < 5 seconds
- **API Response Time**: < 100ms for simple operations
- **Memory Usage**: Optimized for microservice deployment
- **Scalability**: Horizontal scaling ready

## 🔗 **Integration**

### **Microservices Architecture**
This service is part of the InvestByYourself microservices architecture:

- **ETL Service**: Data collection and processing
- **Data Service**: Data storage and retrieval
- **Financial Analysis Service**: Strategy execution and analysis (this service)

### **External Dependencies**
- **PostgreSQL**: Primary database
- **Redis**: Caching and session storage
- **Financial Data APIs**: Yahoo Finance, Alpha Vantage, FRED

## 📚 **Documentation**

- [API Documentation](http://127.0.0.1:8001/docs) - Interactive API docs
- [Week 1 Completion Report](../../docs/story-015-week1-completion-report.md)
- [Microservices Architecture Plan](../../docs/microservices_architecture_plan.md)

## 🤝 **Contributing**

1. Follow the project's coding standards
2. Run pre-commit hooks before committing
3. Add tests for new features
4. Update documentation as needed

## 📄 **License**

This project is part of the InvestByYourself platform.

---

**Service Version**: 1.0.0
**Last Updated**: December 2024
**Status**: Week 1 Complete - Ready for Week 2
