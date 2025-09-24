# Development Setup Guide

## Quick Start

### 1. Environment Setup

1. **Copy environment template:**
   ```bash
   cp env.dev.example .env.dev
   ```

2. **Update environment variables:**
   Edit `.env.dev` and set your actual values:
   ```bash
   # Required for Docker
   REDIS_PASSWORD=your_secure_redis_password
   JWT_SECRET_KEY=your_secure_jwt_secret_key

   # Optional API keys
   ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
   YAHOO_FINANCE_API_KEY=your_yahoo_finance_key
   FRED_API_KEY=your_fred_api_key
   ```

### 2. Start Development Environment

```bash
# Start all services
docker-compose -f docker-compose.dev.yml up

# Or start in background
docker-compose -f docker-compose.dev.yml up -d
```

### 3. Access Services

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Redis Commander**: http://localhost:8081

## Security Notes

### Environment Variables
- **Never commit `.env.dev`** - it contains sensitive information
- **Use strong passwords** for Redis and JWT secrets
- **Rotate API keys** regularly
- **Use different keys** for development and production

### Docker Security
- All services use environment variables for configuration
- No hardcoded passwords in Docker files
- Redis requires authentication
- Database connections use environment variables

## Troubleshooting

### Common Issues

1. **Redis connection failed:**
   - Check `REDIS_PASSWORD` in `.env.dev`
   - Ensure Redis service is running

2. **API authentication failed:**
   - Check `JWT_SECRET_KEY` in `.env.dev`
   - Restart API service after changing JWT secret

3. **Database connection failed:**
   - Check `DATABASE_URL` in `.env.dev`
   - Ensure database service is running

### Reset Environment

```bash
# Stop all services
docker-compose -f docker-compose.dev.yml down

# Remove volumes (WARNING: This deletes all data)
docker-compose -f docker-compose.dev.yml down -v

# Start fresh
docker-compose -f docker-compose.dev.yml up
```

## Development Workflow

1. **Make changes** to source code
2. **Test locally** with Docker
3. **Commit changes** (without secrets)
4. **Push to repository**

## Security Checklist

- [ ] `.env.dev` is in `.gitignore`
- [ ] No hardcoded passwords in code
- [ ] All secrets use environment variables
- [ ] Strong passwords for Redis and JWT
- [ ] API keys are optional for development
- [ ] Docker services use environment variables
