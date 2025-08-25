# Redis Setup Guide for Microservices

## 🎯 **Configuration Overview**

Since we're building microservices that will communicate with each other inside Docker containers, the correct Redis configuration is:

### **Inside Docker (Microservices Environment)**
```bash
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your_secure_redis_password
REDIS_DB=0
```

### **Outside Docker (Local Development)**
```bash
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_secure_redis_password
REDIS_DB=0
```

## 🐳 **Why REDIS_HOST=redis for Microservices?**

1. **Docker Network**: All services run in the same Docker network
2. **Service Discovery**: Docker Compose creates a network where services can reach each other by name
3. **Container Communication**: `redis` is the service name in docker-compose.yml
4. **Isolation**: Services don't need to know about host machine networking

## 📁 **Creating Your .env File**

1. **Navigate to services directory**:
   ```bash
   cd services/
   ```

2. **Create .env file**:
   ```bash
   cp .env.template .env
   # OR create manually
   touch .env
   ```

3. **Add Redis configuration**:
   ```bash
   # Redis Configuration for Microservices
   REDIS_PASSWORD=your_secure_redis_password_here
   REDIS_HOST=redis
   REDIS_PORT=6379
   REDIS_DB=0
   ```

## 🔧 **Complete .env File Example**

```bash
# ======================================
# Microservices Environment Configuration
# ======================================

# Build & Environment
BUILD_TARGET=development
ENVIRONMENT=development
DEBUG=true

# Database Configuration
POSTGRES_PASSWORD=your_secure_postgres_password
POSTGRES_USER=postgres
POSTGRES_DB=investbyyourself
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis Configuration (Microservices)
REDIS_PASSWORD=your_secure_redis_password
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# MinIO Configuration
MINIO_ROOT_USER=investbyyourself
MINIO_ROOT_PASSWORD=your_secure_minio_password
MINIO_HOST=minio
MINIO_PORT=9000

# Service Configuration
ETL_BATCH_SIZE=100
ETL_MAX_WORKERS=4
ANALYSIS_CACHE_TTL=3600
ANALYSIS_MAX_WORKERS=4

# API Keys
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
FMP_API_KEY=your_fmp_key
FRED_API_KEY=your_fred_key

# Security
JWT_SECRET_KEY=your_jwt_secret_key
```

## 🚀 **Starting Services with Redis**

1. **Start Redis and other services**:
   ```bash
   docker-compose up -d redis postgres minio
   ```

2. **Start your microservices**:
   ```bash
   docker-compose up -d financial-analysis-service
   ```

3. **Verify Redis connection**:
   ```bash
   docker exec -it investbyyourself-redis redis-cli
   # Then test: ping
   ```

## 🔍 **Testing Redis Connection**

### **From Inside a Service Container**
```bash
docker exec -it investbyyourself-financial-analysis redis-cli -h redis -p 6379
```

### **From Host Machine (for debugging)**
```bash
redis-cli -h localhost -p 6379
```

## ⚠️ **Important Notes**

1. **Never commit .env files** to version control
2. **Use strong passwords** for all services
3. **REDIS_HOST=redis** is correct for microservices
4. **REDIS_HOST=localhost** is for local development outside Docker
5. **All services must be in the same Docker network**

## 🐛 **Troubleshooting**

### **Connection Refused**
- Check if Redis container is running: `docker ps | grep redis`
- Verify network: `docker network ls`
- Check logs: `docker logs investbyyourself-redis`

### **Authentication Failed**
- Verify REDIS_PASSWORD in .env matches docker-compose.yml
- Check Redis logs for password errors

### **Service Can't Find Redis**
- Ensure all services are in the same docker-compose.yml
- Verify service names match exactly
- Check Docker network configuration

## 📚 **Related Documentation**

- [Docker Compose Configuration](docker-compose.yml)
- [Microservices Architecture Plan](../docs/microservices_architecture_plan.md)
- [Story-015 Completion Report](../docs/story-015-completion-report.md)
