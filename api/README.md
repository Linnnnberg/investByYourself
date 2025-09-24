# InvestByYourself API Gateway

## Tech-028: API Implementation

Comprehensive investment platform API with portfolio management, market data, and financial analysis capabilities.

## 🚀 Features

- **Authentication & Authorization**: JWT-based user authentication
- **Portfolio Management**: Complete CRUD operations for portfolios and holdings
- **Market Data**: Real-time quotes, charts, and market information
- **Watchlist & Alerts**: User watchlists with price alerts
- **Financial Analysis**: Technical and fundamental analysis tools
- **ETL Pipeline Management**: Data pipeline monitoring and control
- **Real-time Updates**: WebSocket connections for live data
- **Notifications**: User communication and alert system

## 📋 API Modules

### Authentication (`/api/v1/auth`)
- User registration and login
- JWT token management
- Password reset functionality
- User profile management

### Portfolio Management (`/api/v1/portfolio`)
- Portfolio CRUD operations
- Holdings management
- Transaction tracking
- Performance analytics

### Market Data (`/api/v1/market`)
- Real-time stock quotes
- Market indices and sectors
- Chart data and historical prices
- Stock search functionality

### Watchlist (`/api/v1/watchlist`)
- User watchlist management
- Price alerts and notifications
- Performance tracking

### Financial Analysis (`/api/v1/analysis`)
- Technical analysis indicators
- Fundamental analysis metrics
- Risk assessment tools
- Portfolio optimization

### ETL Pipeline (`/api/v1/etl`)
- Pipeline status monitoring
- Job management
- Data source configuration

### Notifications (`/api/v1/notifications`)
- User notification management
- Preference settings
- Alert subscriptions

### WebSocket (`/api/v1/ws`)
- Real-time data streaming
- Live portfolio updates
- Market data feeds

## 🛠️ Setup

### Prerequisites
- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- Node.js 18+ (for frontend integration)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd InvestByYourself/api
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Database setup**
   ```bash
   # Create database
   createdb investbyyourself

   # Run migrations
   alembic upgrade head
   ```

6. **Start the server**
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

## 🔧 Configuration

The API uses environment variables for configuration. See `src/core/config.py` for all available settings.

### Required Environment Variables
```bash
# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_here

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=investbyyourself
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# External APIs
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
FRED_API_KEY=your_fred_key
FMP_API_KEY=your_fmp_key

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_key
```

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_auth.py
```

## 🔒 Security

- JWT-based authentication
- Rate limiting on all endpoints
- CORS configuration
- Input validation and sanitization
- Secure password hashing
- Environment variable protection

## 📊 Monitoring

- Structured logging with JSON format
- Health check endpoint (`/health`)
- Prometheus metrics (optional)
- Sentry error tracking (optional)

## 🚀 Deployment

### Docker
```bash
docker build -t investbyyourself-api .
docker run -p 8000:8000 investbyyourself-api
```

### Production
- Use a production ASGI server (Gunicorn with Uvicorn workers)
- Configure reverse proxy (Nginx)
- Set up SSL/TLS certificates
- Configure monitoring and logging

## 📝 Development

### Code Style
- Black for code formatting
- isort for import sorting
- flake8 for linting
- mypy for type checking

### Pre-commit Hooks
```bash
pre-commit install
pre-commit run --all-files
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation
- Review the troubleshooting guide

---

**Built with FastAPI, SQLAlchemy, and Redis for the InvestByYourself platform.**
