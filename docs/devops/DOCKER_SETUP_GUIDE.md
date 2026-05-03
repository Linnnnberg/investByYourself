# Docker Setup Guide

**Quick reference for choosing the right Docker setup for your development needs**

---

## Overview

InvestByYourself provides two distinct Docker setups optimized for different development workflows:

1. **Monolithic Development** (`docker-compose.dev.yml`) - Root level
2. **Microservices Development** (`services/docker-compose.yml`) - Services directory

---

## Which Setup Should I Use?

### Use `docker-compose.dev.yml` When:

✅ You're working on **full-stack features** (frontend + API + ETL)  
✅ You want a **simple, unified setup** with minimal configuration  
✅ You're **new to the project** and want to get started quickly  
✅ You're doing **UI/UX development** that needs the full application  
✅ You're **testing end-to-end workflows**

**Best for:** Frontend developers, full-stack features, quick prototyping

### Use `services/docker-compose.yml` When:

✅ You're working on **backend microservices** (ETL, Financial Analysis, Data Service)  
✅ You need **advanced features** like MinIO object storage  
✅ You're developing **new microservices**  
✅ You're working on **service isolation and scaling**  
✅ You're preparing for **production deployment**

**Best for:** Backend developers, microservices architecture, production readiness

---

## Quick Start Guide

### Option 1: Monolithic Development

```bash
# 1. Navigate to project root
cd InvestByYourself

# 2. Set up environment
cp .env.example .env
# Edit .env and add your secure passwords and API keys

# 3. Start all services
docker-compose -f docker-compose.dev.yml up -d

# 4. Verify services are healthy
docker ps

# 5. Access the application
# Frontend: http://localhost:3000
# API: http://localhost:8000
# ETL: http://localhost:8001 (optional, use --profile etl)
```

**Start with ETL service:**
```bash
docker-compose -f docker-compose.dev.yml --profile etl up -d
```

---

### Option 2: Microservices Development

```bash
# 1. Navigate to services directory
cd InvestByYourself/services

# 2. Set up environment (automated)
python setup_env.py
# This generates .env with secure random passwords

# 3. Start all services
docker-compose up -d

# 4. Verify services are healthy
docker ps

# 5. Access the services
# ETL Service: http://localhost:8000
# Financial Analysis: http://localhost:8001
# Data Service: http://localhost:8002
# MinIO Console: http://localhost:9001
# API Gateway: http://localhost:80
```

---

## Detailed Comparison

| Feature | Monolithic (`docker-compose.dev.yml`) | Microservices (`services/docker-compose.yml`) |
|---------|---------------------------------------|-----------------------------------------------|
| **Location** | Project root | `services/` directory |
| **Services** | PostgreSQL, Redis, API, Frontend, ETL (optional) | PostgreSQL, Redis, MinIO, ETL, Financial Analysis, Data Service, API Gateway |
| **Complexity** | Simple | Advanced |
| **Startup Time** | Fast (~30s) | Moderate (~60s) |
| **Resource Usage** | Low-Medium | Medium-High |
| **Configuration** | `.env` in root | `.env` in services/ |
| **Network** | `investbyyourself-dev` (bridge) | `investbyyourself-network` (subnet: 172.20.0.0/16) |
| **Storage** | postgres_data, redis_data | postgres_data, redis_data, minio_data |
| **Health Checks** | Basic | Comprehensive |
| **Object Storage** | ❌ Not included | ✅ MinIO (S3-compatible) |
| **API Gateway** | ❌ Not included | ✅ Nginx |
| **Best For** | Frontend + API development | Backend + Microservices |

---

## Architecture Diagrams

### Monolithic Setup

```
┌─────────────────────────────────────────────┐
│         docker-compose.dev.yml              │
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ Frontend │  │   API    │  │   ETL    │ │
│  │  :3000   │  │  :8000   │  │  :8001   │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘ │
│       │             │              │        │
│       └─────────────┼──────────────┘        │
│                     │                       │
│  ┌──────────┐  ┌────▼─────┐               │
│  │  Redis   │  │ Postgres │               │
│  │  :6379   │  │  :5432   │               │
│  └──────────┘  └──────────┘               │
└─────────────────────────────────────────────┘
```

### Microservices Setup

```
┌───────────────────────────────────────────────────────┐
│           services/docker-compose.yml                 │
│                                                       │
│  ┌────────────────────────────────────────────────┐  │
│  │              API Gateway (Nginx)               │  │
│  │                    :80, :443                   │  │
│  └────────┬────────────┬────────────┬─────────────┘  │
│           │            │            │                 │
│  ┌────────▼───┐  ┌────▼────┐  ┌───▼──────┐         │
│  │ ETL Service│  │Financial│  │   Data   │         │
│  │   :8000    │  │Analysis │  │ Service  │         │
│  │            │  │  :8001  │  │  :8002   │         │
│  └─────┬──────┘  └────┬────┘  └────┬─────┘         │
│        │              │             │                │
│        └──────────────┼─────────────┘                │
│                       │                              │
│  ┌─────────┐  ┌──────▼─────┐  ┌─────────┐         │
│  │  Redis  │  │ PostgreSQL │  │  MinIO  │         │
│  │  :6379  │  │   :5432    │  │ :9000/1 │         │
│  └─────────┘  └────────────┘  └─────────┘         │
└───────────────────────────────────────────────────────┘
```

---

## Common Operations

### Starting Services

```bash
# Monolithic: Start everything
docker-compose -f docker-compose.dev.yml up -d

# Monolithic: Start specific service
docker-compose -f docker-compose.dev.yml up -d api

# Monolithic: Start with ETL
docker-compose -f docker-compose.dev.yml --profile etl up -d

# Microservices: Start everything
cd services && docker-compose up -d

# Microservices: Start specific service
cd services && docker-compose up -d etl-service
```

### Stopping Services

```bash
# Monolithic: Stop all
docker-compose -f docker-compose.dev.yml down

# Microservices: Stop all
cd services && docker-compose down

# Stop and remove volumes (WARNING: Deletes all data!)
docker-compose down -v
```

### Viewing Logs

```bash
# Monolithic: All logs
docker-compose -f docker-compose.dev.yml logs -f

# Monolithic: Specific service
docker-compose -f docker-compose.dev.yml logs -f api

# Microservices: All logs
cd services && docker-compose logs -f

# Microservices: Specific service
cd services && docker-compose logs -f financial-analysis-service
```

### Rebuilding Services

```bash
# Monolithic: Rebuild and restart
docker-compose -f docker-compose.dev.yml up -d --build

# Microservices: Rebuild specific service
cd services && docker-compose up -d --build etl-service

# Force clean rebuild (no cache)
docker-compose build --no-cache
```

### Health Checks

```bash
# Check service status
docker ps

# Check specific service health
docker inspect --format='{{.State.Health.Status}}' investbyyourself-api-dev

# View health check logs
docker inspect --format='{{json .State.Health}}' investbyyourself-api-dev | python -m json.tool
```

---

## Environment Configuration

### Monolithic Setup (`.env`)

Located at: **Project Root** (`InvestByYourself/.env`)

**Required Variables:**
```env
# Database
POSTGRES_PASSWORD=your_secure_postgres_password_here

# Redis
REDIS_PASSWORD=your_secure_redis_password_here

# Security
JWT_SECRET_KEY=your_secure_jwt_secret_key_here

# API Keys (Optional)
ALPHA_VANTAGE_API_KEY=your_api_key_here
FRED_API_KEY=your_api_key_here

# Supabase (Optional)
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url_here
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_key_here
```

**Setup:**
```bash
cp .env.example .env
# Edit .env with your credentials
```

---

### Microservices Setup (`.env`)

Located at: **Services Directory** (`InvestByYourself/services/.env`)

**Required Variables:**
```env
# Build Configuration
BUILD_TARGET=development
ENVIRONMENT=development
DEBUG=true

# Database
POSTGRES_PASSWORD=your_secure_postgres_password_here

# Redis
REDIS_PASSWORD=your_secure_redis_password_here

# MinIO
MINIO_ROOT_USER=your_minio_user_here
MINIO_ROOT_PASSWORD=your_secure_minio_password_here

# Service Configuration
ETL_BATCH_SIZE=100
ANALYSIS_CACHE_TTL=3600
DB_POOL_SIZE=20
```

**Setup (Automated):**
```bash
cd services
python setup_env.py
```

This script automatically generates:
- Secure random passwords (32 characters)
- Proper environment variable structure
- Development-ready configuration

---

## Troubleshooting

### Port Conflicts

**Problem:** Port already in use

```bash
# Check what's using the port
netstat -ano | findstr :8000  # Windows
lsof -i :8000                  # Linux/Mac

# Change ports in docker-compose.yml
ports:
  - "8080:8000"  # Map to different host port
```

### Services Won't Start

**Problem:** Container exits immediately

```bash
# View logs
docker-compose logs service-name

# Check health status
docker ps -a

# Common fixes:
# 1. Check .env file exists and has correct values
# 2. Ensure JWT_SECRET_KEY is set (required!)
# 3. Verify no port conflicts
# 4. Check Docker daemon is running
```

### Database Connection Issues

**Problem:** Can't connect to PostgreSQL

```bash
# Check if postgres is healthy
docker ps | grep postgres

# Test connection manually
docker exec -it investbyyourself-postgres-dev psql -U postgres -d investbyyourself

# Check password in .env matches docker-compose
```

### Volume Permission Issues

**Problem:** Permission denied errors

```bash
# Linux: Fix volume permissions
sudo chown -R $USER:$USER ./data

# Reset volumes (WARNING: Deletes data!)
docker-compose down -v
docker-compose up -d
```

---

## Best Practices

### Development Workflow

1. **Start with Monolithic** if you're new
2. **Use Microservices** when you need specific services
3. **Keep .env secure** - Never commit to git
4. **Run health checks** regularly
5. **Monitor logs** when debugging
6. **Clean up volumes** periodically

### Performance Tips

1. **Use BuildKit** for faster builds:
   ```bash
   export DOCKER_BUILDKIT=1
   ```

2. **Limit resources** in docker-compose:
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '0.5'
         memory: 512M
   ```

3. **Prune unused resources** regularly:
   ```bash
   docker system prune -a
   ```

---

## Migration Guide

### From Monolithic to Microservices

```bash
# 1. Stop monolithic setup
docker-compose -f docker-compose.dev.yml down

# 2. Set up microservices environment
cd services
python setup_env.py

# 3. Start microservices
docker-compose up -d

# 4. Verify migration
docker ps
```

### Data Migration

```bash
# Export from monolithic
docker exec investbyyourself-postgres-dev pg_dump -U postgres investbyyourself > backup.sql

# Import to microservices
docker exec -i investbyyourself-postgres psql -U postgres investbyyourself < backup.sql
```

---

## Related Documentation

- [Docker Integration Improvements](DOCKER_INTEGRATION_IMPROVEMENTS.md) - Detailed analysis
- [Environment File Structure](ENV_FILE_STRUCTURE.md) - Environment configuration guide
- [Volume Backup Strategy](VOLUME_BACKUP_STRATEGY.md) - Data backup procedures (coming soon)

---

## Quick Reference

| Task | Monolithic Command | Microservices Command |
|------|--------------------|-----------------------|
| Start | `docker-compose -f docker-compose.dev.yml up -d` | `cd services && docker-compose up -d` |
| Stop | `docker-compose -f docker-compose.dev.yml down` | `cd services && docker-compose down` |
| Logs | `docker-compose -f docker-compose.dev.yml logs -f` | `cd services && docker-compose logs -f` |
| Rebuild | `docker-compose -f docker-compose.dev.yml up -d --build` | `cd services && docker-compose up -d --build` |
| Status | `docker ps` | `docker ps` |

---

**Need Help?** Check the troubleshooting section or consult the related documentation above.
