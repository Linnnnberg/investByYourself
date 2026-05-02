# Docker Integration Improvements
**Feature Branch**: `feature/docker-integration-improvements`
**Created**: May 2, 2026
**Status**: Planning & Documentation Phase

---

## ⚠️ Security Notice

**Password Management Policy**:
- This documentation uses **placeholder values** (e.g., `your_secure_dev_password_here`)
- **NEVER** commit real passwords to version control
- Store actual passwords in:
  - `.env` files (gitignored)
  - Password managers (1Password, LastPass, Bitwarden)
  - Secret management systems (HashiCorp Vault, AWS Secrets Manager)
- The `.env.example` file shows structure only, not real values

---

## Executive Summary

This document outlines critical fixes and improvements for the InvestByYourself Docker integration. The improvements address bugs, security issues, and optimization opportunities identified through comprehensive analysis of the Docker Compose configurations and Dockerfiles.

---

## Table of Contents

1. [Priority 1: Critical Fixes](#priority-1-critical-fixes)
2. [Priority 2: Quality & Documentation](#priority-2-quality--documentation)
3. [Priority 3: Production Readiness](#priority-3-production-readiness)
4. [Implementation Plan](#implementation-plan)
5. [Testing Strategy](#testing-strategy)
6. [Rollback Plan](#rollback-plan)

---

## Priority 1: Critical Fixes

These issues can cause service failures or security vulnerabilities and must be fixed immediately.

### 1.1 Redis Health Check Command

**Issue**: Incorrect Redis health check command in Docker Compose configurations

**Affected Files**:
- `docker-compose.dev.yml` (line 43)
- `services/docker-compose.yml` (line 44)

**Current Implementation**:
```yaml
healthcheck:
  test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
```

**Problem**:
- The command `redis-cli --raw incr ping` is malformed and will fail
- It attempts to use `incr` and `ping` as separate commands
- It doesn't authenticate with the password configured via `--requirepass`
- Health checks will always fail, causing Docker to mark Redis as unhealthy
- Services depending on Redis health (API, ETL) won't start properly

**Solution**:
```yaml
healthcheck:
  test: ["CMD-SHELL", "redis-cli -a ${REDIS_PASSWORD:-YOUR_DEV_PASSWORD} ping || exit 1"]
```

**Note**: Replace `YOUR_DEV_PASSWORD` with your actual development Redis password from `.env` file.

**Explanation**:
- Uses `CMD-SHELL` to allow shell evaluation
- Uses `-a` flag for password authentication
- Properly executes `ping` command to test Redis availability
- Returns exit code 1 on failure for proper health check status

**Impact**: HIGH - Services currently cannot detect Redis health status correctly

---

### 1.2 API and ETL Service Health Checks

**Issue**: Health checks depend on Python `requests` library which may not be available

**Affected Files**:
- `docker-compose.dev.yml` (lines 78, API service)
- Future ETL service health checks

**Current Implementation**:
```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
```

**Problem**:
- Requires `requests` library to be installed and available
- Python import errors will cause health check to fail even if service is healthy
- No error handling if the health endpoint doesn't exist
- Dependency on Python runtime for simple HTTP check

**Solution**:
```yaml
healthcheck:
  test: ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
```

**Alternative** (if curl not available in alpine):
```yaml
healthcheck:
  test: ["CMD-SHELL", "wget --no-verbose --tries=1 --spider http://localhost:8000/health || exit 1"]
```

**Explanation**:
- Uses system utilities (curl/wget) instead of Python dependencies
- `-f` flag (curl) or `--spider` (wget) performs HEAD request
- Proper exit codes for Docker health check evaluation
- More reliable and lightweight

**Prerequisites**:
- Verify curl or wget is available in the Python base image
- May need to add `curl` to system dependencies in Dockerfile if not present

**Impact**: HIGH - Unreliable health checks can cause false negatives

---

### 1.3 Missing .dockerignore Files

**Issue**: No .dockerignore files for most services, causing bloated build contexts

**Affected Services**:
- `api/` - Missing .dockerignore
- `etl/` - Missing .dockerignore
- `services/etl-service/` - Missing .dockerignore
- `services/financial-analysis-service/` - Missing .dockerignore
- `services/data-service/` - Missing .dockerignore

**Current State**:
- Only `frontend/.dockerignore` exists
- All Python cache files, test artifacts, and version control are included in build context

**Problem**:
- Slower Docker builds due to large context
- Unnecessary files copied to build context
- Potential security risk (e.g., .env files, credentials)
- Larger Docker images
- Cache invalidation on irrelevant file changes

**Solution**: Create .dockerignore for each service

**Standard Python Service .dockerignore**:
```dockerignore
# Python artifacts
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/

# Testing & Coverage
.pytest_cache/
.coverage
.coverage.*
htmlcov/
.tox/
.hypothesis/

# Type checking
.mypy_cache/
.dmypy.json
dmypy.json

# Virtual environments
venv/
env/
ENV/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Version control
.git/
.gitignore
.gitattributes

# Environment & secrets
.env
.env.*
*.pem
*.key
credentials.json

# Logs
*.log
logs/

# OS files
.DS_Store
Thumbs.db

# Documentation (if not needed in image)
docs/
*.md
!README.md

# CI/CD
.github/
.gitlab-ci.yml
.travis.yml
```

**Impact**: MEDIUM - Affects build performance and image size

---

### 1.4 JWT Secret Key Security

**Issue**: Weak default JWT secret key in development environment

**Affected Files**:
- `docker-compose.dev.yml` (line 62)

**Current Implementation**:
```yaml
- JWT_SECRET_KEY=${JWT_SECRET_KEY:-dev_jwt_secret_key}
```

**Problem**:
- Default secret `dev_jwt_secret_key` is predictable and insecure
- Anyone can forge JWT tokens if this default is used
- Risk of accidentally using development secret in production
- No warning to developers about security implications

**Solution**:
```yaml
# WARNING: Never use default JWT secret in production!
# Generate a secure secret: python -c "import secrets; print(secrets.token_urlsafe(32))"
- JWT_SECRET_KEY=${JWT_SECRET_KEY:-INSECURE_DEV_KEY_REPLACE_ME}
```

**Additional Improvements**:
1. Add comment warning about security implications
2. Use obviously insecure default to prevent accidental production use
3. Document how to generate secure secrets
4. Add to .env.example with instructions

**Production Solution**:
```yaml
# In production compose file
- JWT_SECRET_KEY=${JWT_SECRET_KEY:?JWT_SECRET_KEY is required}
```

**Impact**: HIGH - Security vulnerability if defaults are used

---

## Priority 2: Quality & Documentation

These improvements enhance maintainability and developer experience.

### 2.1 Create .env.example Files

**Purpose**: Document required environment variables for developers

**Related Documentation**: See [ENV_FILE_STRUCTURE.md](./ENV_FILE_STRUCTURE.md) for complete file structure guide

**Files to Create**:
1. `.env.example` (root, for docker-compose.dev.yml)
2. `services/.env.example` (for services/docker-compose.yml)
3. `services/.env.production.example` (rename from env.production.template)
4. `api/.env.example`, `frontend/.env.example`, `etl/.env.example` (for standalone development)

**Content for Root .env.example**:
```bash
# InvestByYourself Development Environment Variables
# Copy this file to .env and update with your values
# Never commit .env to version control!

# Database Configuration
# For development, use a secure password (not 'password' or '123456')
POSTGRES_PASSWORD=your_secure_dev_password_here

# Redis Configuration
# For development, use a secure password (not 'password' or '123456')
REDIS_PASSWORD=your_secure_dev_password_here

# JWT Configuration (CRITICAL: Generate a secure secret!)
# Generate: python -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_SECRET_KEY=your-secure-jwt-secret-here

# External API Keys
# Get Alpha Vantage key: https://www.alphavantage.co/support/#api-key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key

# Get FRED API key: https://fred.stlouisfed.org/docs/api/api_key.html
FRED_API_KEY=your_fred_api_key

# Supabase Configuration (Optional)
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

**Impact**: MEDIUM - Improves developer onboarding

---

### 2.2 Add Cache Directory Volume Exclusions

**Issue**: Cache directories not excluded in volume mounts

**Affected Files**:
- `docker-compose.dev.yml` (API and ETL services)
- `services/docker-compose.yml` (all microservices)

**Current Implementation**:
```yaml
volumes:
  - ./api:/app
  - /app/__pycache__
```

**Problem**:
- Only excludes `__pycache__`, misses other cache directories
- Test caches, type checker caches persist in containers
- Can cause issues between host and container Python versions

**Solution**:
```yaml
volumes:
  - ./api:/app
  - /app/__pycache__
  - /app/.pytest_cache
  - /app/.mypy_cache
  - /app/.ruff_cache
```

**Impact**: LOW - Prevents minor cache-related issues

---

### 2.3 Verify Frontend Health Endpoint

**Issue**: Frontend Dockerfile assumes /api/health endpoint exists

**Affected Files**:
- `frontend/Dockerfile` (line 74)

**Current Implementation**:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/api/health || exit 1
```

**Action Required**:
1. Verify if `/api/health` endpoint exists in Next.js app
2. If missing, create it: `frontend/src/pages/api/health.ts`
3. If exists, document its purpose and response format

**Proposed Health Endpoint** (if missing):
```typescript
// frontend/src/pages/api/health.ts
import type { NextApiRequest, NextApiResponse } from 'next';

export default function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  res.status(200).json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'frontend'
  });
}
```

**Impact**: MEDIUM - Ensures health checks work correctly

---

### 2.4 Docker Setup Documentation

**Purpose**: Clarify when to use which Docker Compose configuration

**Issue**: Two Docker setups can cause confusion:
- Root: `docker-compose.dev.yml` (monolithic development)
- Services: `services/docker-compose.yml` (microservices)

**Documentation to Add**: Section in README.md or separate DOCKER_SETUP.md

**Content**:
```markdown
## Docker Setup Guide

### Two Docker Environments

InvestByYourself provides two Docker configurations for different use cases:

#### 1. Development Environment (Monolithic)
**File**: `docker-compose.dev.yml` (root directory)

**Use When**:
- Local full-stack development
- Testing frontend-backend integration
- Quick prototyping
- You need all services running together

**Services**:
- API (Port 8000)
- Frontend (Port 3000)
- ETL (Port 8001, optional with --profile etl)
- PostgreSQL (Port 5432)
- Redis (Port 6379)

**Start Command**:
```bash
docker-compose -f docker-compose.dev.yml up -d
```

#### 2. Microservices Environment (Production-like)
**Files**: `services/docker-compose.yml` + overrides

**Use When**:
- Testing microservices architecture
- Production deployment preparation
- Service isolation testing
- Load testing individual services

**Services**:
- ETL Service (Port 8000)
- Financial Analysis Service (Port 8001)
- Data Service (Port 8002)
- PostgreSQL, Redis, MinIO
- API Gateway (Nginx)
- Monitoring (Prometheus, Grafana)

**Start Command**:
```bash
cd services
docker-compose up -d
```

### Choosing the Right Environment

| Scenario | Use |
|----------|-----|
| Frontend development | Monolithic |
| API endpoint development | Monolithic |
| Testing specific microservice | Microservices |
| Production deployment | Microservices |
| Learning the codebase | Monolithic |
```

**Impact**: MEDIUM - Reduces developer confusion

---

## Priority 3: Production Readiness

These optimizations prepare the system for production deployment.

### 3.1 Add Resource Limits to Production Services

**Issue**: No CPU/memory limits defined for production containers

**Affected Files**:
- `services/docker-compose.prod.yml`

**Problem**:
- Services can consume unlimited resources
- No protection against memory leaks
- Difficult to plan infrastructure capacity
- Risk of OOM (Out of Memory) killing containers unexpectedly

**Solution**: Add resource limits based on service requirements

**Proposed Limits**:

```yaml
services:
  postgres:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G

  redis:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M

  etl-service:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M

  financial-analysis-service:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G

  data-service:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

**Tuning Methodology**:
1. Start with conservative limits
2. Monitor actual usage with Prometheus
3. Adjust based on observed patterns
4. Test under load before production

**Impact**: HIGH - Critical for production stability

---

### 3.2 Verify Nginx Configuration Files

**Issue**: API Gateway references nginx configs that may not exist

**Affected Files**:
- `services/docker-compose.yml` (lines 218-219)
- `services/docker-compose.prod.yml` (lines 75-77)

**Referenced Files**:
- `services/nginx/nginx.conf`
- `services/nginx/nginx.prod.conf`
- `services/nginx/conf.d/`
- `services/nginx/ssl/`

**Action Required**:
1. Check if files exist
2. If missing, create basic configurations
3. Document nginx setup and SSL certificate requirements

**Basic Nginx Configuration Template** (if missing):
```nginx
# services/nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream etl_backend {
        server etl-service:8000;
    }

    upstream analysis_backend {
        server financial-analysis-service:8001;
    }

    upstream data_backend {
        server data-service:8002;
    }

    server {
        listen 80;
        server_name localhost;

        location /api/etl/ {
            proxy_pass http://etl_backend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location /api/analysis/ {
            proxy_pass http://analysis_backend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location /api/data/ {
            proxy_pass http://data_backend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
```

**Impact**: HIGH - API Gateway won't start without these files

---

### 3.3 Document Volume Backup Strategy

**Purpose**: Protect critical production data

**Volumes Requiring Backup**:
- `postgres_data` - All database data
- `redis_data` - Cache and session data
- `minio_data` - Object storage

**Documentation to Create**: `docs/devops/BACKUP_RESTORE.md`

**Content Outline**:
1. Backup frequency recommendations
2. Backup procedures for each volume
3. Restore procedures and testing
4. Disaster recovery plan
5. Automated backup scripts

**Example Backup Script**:
```bash
#!/bin/bash
# backup-volumes.sh
BACKUP_DIR="/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup PostgreSQL
docker exec investbyyourself-postgres pg_dump -U postgres investbyyourself | \
    gzip > "$BACKUP_DIR/postgres_backup.sql.gz"

# Backup Redis
docker exec investbyyourself-redis redis-cli -a "$REDIS_PASSWORD" --rdb /data/dump.rdb
docker cp investbyyourself-redis:/data/dump.rdb "$BACKUP_DIR/redis_dump.rdb"

# Backup MinIO (volume copy)
docker run --rm -v minio_data:/data -v "$BACKUP_DIR":/backup alpine \
    tar czf /backup/minio_data.tar.gz -C /data .

echo "Backup completed: $BACKUP_DIR"
```

**Impact**: HIGH - Critical for production data safety

---

### 3.4 Add BuildKit Cache Mounts for Python

**Purpose**: Optimize Docker build times with layer caching

**Affected Files**:
- `api/Dockerfile`
- `etl/Dockerfile`
- `services/shared/Dockerfile.base`
- All microservice Dockerfiles

**Current Implementation**:
```dockerfile
RUN pip install --no-cache-dir -r requirements.txt
```

**Problem**:
- `--no-cache-dir` prevents pip from caching downloads
- Every build re-downloads all packages
- Slow builds, especially with many dependencies
- Wastes bandwidth

**Solution**: Use BuildKit cache mounts

```dockerfile
# syntax=docker/dockerfile:1.4

# Base stage
FROM python:3.11-slim as base

# ... other setup ...

# Install dependencies with cache mount
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install -r requirements.txt
```

**Benefits**:
- Pip cache persists across builds
- Faster builds (can be 3-5x faster)
- Reduced network usage
- Better developer experience

**Prerequisites**:
- Docker BuildKit must be enabled: `export DOCKER_BUILDKIT=1`
- Add syntax directive at top of Dockerfile

**Impact**: MEDIUM - Significantly improves build performance

---

## Implementation Plan

### Phase 1: Critical Fixes (Week 1)
**Goal**: Fix bugs and security issues

1. **Day 1-2**: Fix health checks
   - Update Redis health check in both compose files
   - Update API/ETL health checks to use curl/wget
   - Test health check functionality

2. **Day 3**: Create .dockerignore files
   - Create for all Python services
   - Test build context size reduction
   - Verify builds still work

3. **Day 4**: Fix JWT security
   - Update default JWT secret
   - Add security warnings
   - Create .env.example files

4. **Day 5**: Testing & validation
   - Full integration testing
   - Verify all services start correctly
   - Document any issues found

### Phase 2: Quality Improvements (Week 2)
**Goal**: Enhance maintainability

1. **Day 1**: Volume exclusions
   - Add cache directory exclusions
   - Test hot-reload still works

2. **Day 2**: Frontend health endpoint
   - Verify or create health endpoint
   - Test frontend health checks

3. **Day 3-4**: Documentation
   - Create Docker setup guide
   - Add to README
   - Create diagrams if needed

4. **Day 5**: Review and polish
   - Peer review documentation
   - Address feedback

### Phase 3: Production Readiness (Week 3)
**Goal**: Prepare for production deployment

1. **Day 1-2**: Resource limits
   - Add limits to production compose
   - Test with realistic load
   - Tune based on results

2. **Day 3**: Nginx configuration
   - Verify or create nginx configs
   - Test API gateway routing
   - Document SSL setup

3. **Day 4**: Backup strategy
   - Create backup documentation
   - Write backup scripts
   - Test restore procedures

4. **Day 5**: BuildKit optimization
   - Add cache mounts to Dockerfiles
   - Measure build time improvements
   - Document usage

---

## Testing Strategy

### Unit Testing
- Health check scripts run correctly
- Environment variables properly substituted
- Volume mounts work as expected

### Integration Testing
```bash
# Test development environment
docker-compose -f docker-compose.dev.yml up -d
docker-compose -f docker-compose.dev.yml ps
docker-compose -f docker-compose.dev.yml logs

# Verify health checks
docker ps --format "table {{.Names}}\t{{.Status}}"

# Test service connectivity
curl http://localhost:8000/health
curl http://localhost:3000/api/health
redis-cli -a ${REDIS_PASSWORD} ping  # Use password from your .env file
```

### Production Testing
```bash
# Test production environment
cd services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Verify resource limits
docker stats

# Test API gateway
curl http://localhost/api/etl/health
curl http://localhost/api/analysis/health
```

### Performance Testing
- Measure build times before and after BuildKit optimization
- Load test services under resource limits
- Verify backup/restore procedures

---

## Rollback Plan

### If Critical Issues Occur

1. **Immediate Rollback**:
   ```bash
   git checkout master
   docker-compose down
   docker-compose up -d
   ```

2. **Service-Specific Issues**:
   - Revert specific compose file changes
   - Rebuild affected service only
   - Monitor logs for errors

3. **Data Issues**:
   - Use volume backups to restore
   - Verify data integrity after restore

### Rollback Checklist
- [ ] All services start successfully
- [ ] Health checks pass
- [ ] API endpoints respond correctly
- [ ] Frontend loads properly
- [ ] Database connections work
- [ ] Redis caching functions

---

## Success Metrics

### Immediate Success Indicators
- All health checks passing (was failing)
- Build context size reduced by >50%
- No security warnings from linters
- Clear documentation exists

### Performance Improvements
- Build time reduced by 30-50% (BuildKit)
- Image size reduced by 10-20% (.dockerignore)
- Faster startup times (proper health checks)

### Long-term Goals
- Zero production incidents from Docker misconfigurations
- Developer onboarding time reduced by 30%
- Backup/restore procedures tested quarterly

---

## References

### External Documentation
- Docker Compose documentation: https://docs.docker.com/compose/
- Docker health checks: https://docs.docker.com/engine/reference/builder/#healthcheck
- BuildKit cache mounts: https://docs.docker.com/build/cache/
- Docker security best practices: https://docs.docker.com/develop/security-best-practices/

### Internal Documentation
- **[ENV_FILE_STRUCTURE.md](./ENV_FILE_STRUCTURE.md)** - Complete guide to .env file organization
- **[services/README.md](../../services/README.md)** - Microservices architecture documentation
- **[README.md](../../README.md)** - Project overview and quick start

---

**Document Version**: 1.0
**Last Updated**: May 2, 2026
**Maintained By**: DevOps Team
