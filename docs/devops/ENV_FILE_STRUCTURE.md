# Environment File Structure Guide
**Last Updated**: May 2, 2026
**Purpose**: Standardize .env file locations and naming conventions

---

## Current State Analysis

### Existing Files (Root Level)
```
InvestByYourself/
├── .env.dev                      # ✅ Active development config (gitignored)
├── docker.env.example            # ⚠️  Duplicate - should consolidate
├── env.dev.template              # ⚠️  Duplicate - should consolidate
├── env.template                  # ✅ Good - comprehensive template
└── docker-compose.dev.yml        # Uses environment variables
```

### Existing Files (Services Directory)
```
services/
├── .env                          # ✅ Active config (gitignored)
├── env.production.template       # ✅ Good - production template
└── docker-compose.yml            # Uses environment variables
```

### Existing Files (Config Directory)
```
config/
├── environments/
│   ├── base.env.template         # Base configuration
│   ├── development.env.template  # Development overrides
│   └── production.env.template   # Production overrides
└── services/
    ├── backend.env.template      # Backend service config
    ├── frontend.env.template     # Frontend service config
    └── etl.env.template          # ETL service config
```

### Existing Files (Individual Services)
```
api/env.template                  # API service template
frontend/env.template             # Frontend template
```

---

## Issues Identified

### 1. **Inconsistent Naming**
- Mix of `.env.template`, `env.template`, and `env.*.template`
- Confusing which file to use for what purpose

### 2. **Duplication**
- Multiple templates for same purpose (root level has 3 templates)
- `docker.env.example` vs `env.template` vs `env.dev.template`

### 3. **Unclear Hierarchy**
- Not clear which template to use for which deployment method:
  - Docker Compose development?
  - Microservices development?
  - Production deployment?

---

## Recommended Structure

### Principle: "One Template Per Use Case"

```
InvestByYourself/
│
├── .env                          # ❌ NEVER commit (gitignored)
├── .env.example                  # ✅ Template for docker-compose.dev.yml
├── .gitignore                    # Ensures .env* files ignored
│
├── docker-compose.dev.yml        # Uses .env from root
│
├── api/
│   ├── .env                      # ❌ NEVER commit (gitignored)
│   └── .env.example              # ✅ Template for standalone API
│
├── frontend/
│   ├── .env.local                # ❌ NEVER commit (gitignored)
│   └── .env.example              # ✅ Template for standalone frontend
│
├── etl/
│   ├── .env                      # ❌ NEVER commit (gitignored)
│   └── .env.example              # ✅ Template for standalone ETL
│
└── services/                     # Microservices environment
    ├── .env                      # ❌ NEVER commit (gitignored)
    ├── .env.example              # ✅ Template for development
    ├── .env.production.example   # ✅ Template for production
    └── docker-compose.yml        # Uses .env from services/
```

---

## File Purposes & Usage

### Root Level: Monolithic Development

#### `.env.example` (Recommended Name)
**Purpose**: Template for `docker-compose.dev.yml`

**Usage**:
```bash
# First time setup
cp .env.example .env
# Edit .env with your values
docker-compose -f docker-compose.dev.yml up -d
```

**Content Structure**:
```bash
# =====================================================
# InvestByYourself Development Environment
# For use with: docker-compose.dev.yml
# =====================================================

# Database Configuration
POSTGRES_PASSWORD=your_secure_password_here
REDIS_PASSWORD=your_redis_password_here

# JWT Configuration
# Generate: python -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_SECRET_KEY=your_jwt_secret_here

# External API Keys
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
FRED_API_KEY=your_fred_key

# Supabase (Optional)
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
```

---

### Services Directory: Microservices Architecture

#### `services/.env.example`
**Purpose**: Template for microservices development

**Usage**:
```bash
cd services
cp .env.example .env
# Edit .env with your values
docker-compose up -d
```

**Content Structure**:
```bash
# =====================================================
# InvestByYourself Microservices - Development
# For use with: services/docker-compose.yml
# =====================================================

# Build Configuration
BUILD_TARGET=development
ENVIRONMENT=development
DEBUG=true

# Database
POSTGRES_PASSWORD=your_secure_password
POSTGRES_USER=postgres
POSTGRES_DB=investbyyourself

# Redis
REDIS_PASSWORD=your_redis_password

# MinIO
MINIO_ROOT_USER=your_minio_user
MINIO_ROOT_PASSWORD=your_minio_password

# Service Tuning
ETL_BATCH_SIZE=100
ANALYSIS_CACHE_TTL=3600
DB_POOL_SIZE=20
```

#### `services/.env.production.example`
**Purpose**: Template for production deployment

**Usage**:
```bash
cd services
cp .env.production.example .env.production
# Edit .env.production with SECURE production values
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

**Content Structure**:
```bash
# =====================================================
# InvestByYourself Microservices - PRODUCTION
# For use with: docker-compose.yml + docker-compose.prod.yml
# ⚠️  NEVER use development passwords in production!
# =====================================================

# Build Configuration
BUILD_TARGET=production
ENVIRONMENT=production
DEBUG=false

# Database (REQUIRED)
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:?Required}
POSTGRES_USER=postgres
POSTGRES_DB=investbyyourself

# Redis (REQUIRED)
REDIS_PASSWORD=${REDIS_PASSWORD:?Required}

# MinIO (REQUIRED)
MINIO_ROOT_USER=${MINIO_ROOT_USER:?Required}
MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD:?Required}

# Monitoring (REQUIRED)
GRAFANA_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD:?Required}

# Production Tuning
ETL_BATCH_SIZE=200
ETL_RETRY_ATTEMPTS=5
ANALYSIS_CACHE_TTL=7200
ANALYSIS_MAX_WORKERS=8
DB_POOL_SIZE=50
DB_CONNECTION_TIMEOUT=60
```

---

### Individual Service Directories

#### `api/.env.example`
**Purpose**: Standalone API development (without Docker Compose)

**Usage**:
```bash
cd api
cp .env.example .env
# Edit .env
python -m uvicorn src.main:app --reload
```

#### `frontend/.env.example`
**Purpose**: Standalone frontend development

**Usage**:
```bash
cd frontend
cp .env.example .env.local
# Edit .env.local
npm run dev
```

**Note**: Next.js convention uses `.env.local` for local overrides

#### `etl/.env.example`
**Purpose**: Standalone ETL development

**Usage**:
```bash
cd etl
cp .env.example .env
# Edit .env
python src/main.py
```

---

## Migration Plan

### Phase 1: Consolidate Root Templates
```bash
# Keep the comprehensive one
mv env.template .env.example

# Remove duplicates
rm docker.env.example
rm env.dev.template
rm env.dev.example  # if exists
```

### Phase 2: Rename Services Templates
```bash
cd services
# Rename for consistency
mv env.production.template .env.production.example
# Create development template
cp .env .env.example  # Copy current config as template
# Replace real values with placeholders in .env.example
```

### Phase 3: Create Missing Templates
```bash
# If they don't exist
touch api/.env.example
touch frontend/.env.example
touch etl/.env.example
```

### Phase 4: Update Documentation
- Update README.md with new file names
- Update docker-compose comments
- Add this guide to documentation

---

## Gitignore Configuration

### Current (Good!)
```gitignore
# Environment files
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
.env.*

# Exception: Allow templates
!.env.*.template
!.env.*.example
```

### Recommended Enhancement
```gitignore
# Environment files (NEVER commit actual values!)
.env
.env.local
.env.development
.env.production
.env.*

# Exceptions: Templates and examples are OK
!.env.example
!.env.*.example
!.env.*.template
!.env.template

# Explicitly deny common mistakes
.env.backup
.env.old
.env.save
```

---

## Naming Convention Decision

### Why `.env.example` over `env.template`?

#### Pros of `.env.example`:
✅ Industry standard (Rails, Laravel, Node.js projects)
✅ Clearer intent: "example" is obvious
✅ Shell autocomplete friendly (. prefix groups files)
✅ Consistent with `.env` (same prefix)
✅ Supported by many tools (direnv, etc.)

#### Cons of `env.template`:
⚠️ Less common in modern projects
⚠️ Doesn't match `.env` prefix pattern
⚠️ Could be confused with template engines

**Decision**: Standardize on `.env.example` pattern

---

## Quick Reference Table

| Use Case | File Location | Copy To | Used By |
|----------|--------------|---------|---------|
| Docker Compose Dev | `.env.example` | `.env` | `docker-compose.dev.yml` |
| Microservices Dev | `services/.env.example` | `services/.env` | `services/docker-compose.yml` |
| Microservices Prod | `services/.env.production.example` | `services/.env.production` | `services/docker-compose.prod.yml` |
| Standalone API | `api/.env.example` | `api/.env` | API service directly |
| Standalone Frontend | `frontend/.env.example` | `frontend/.env.local` | Next.js dev server |
| Standalone ETL | `etl/.env.example` | `etl/.env` | ETL service directly |

---

## Security Best Practices

### ✅ DO:
1. **Use templates** with placeholder values
2. **Document requirements** in template comments
3. **Provide examples** for complex values (JWT generation)
4. **Use descriptive placeholders**: `your_secure_password_here`
5. **Add generation instructions**: Show how to create secrets
6. **Version control templates**: Templates should be in git
7. **Link to documentation**: Reference where to get API keys

### ❌ DON'T:
1. **Never commit real passwords**, even development ones
2. **Don't use weak placeholders**: Avoid `password123` or `secret`
3. **Don't skip validation**: Add checks for required values
4. **Don't reuse secrets**: Each environment needs unique secrets
5. **Don't leave defaults**: In production, require explicit values
6. **Don't document sensitive paths**: Keep infrastructure details private

---

## Validation Script

Create `scripts/validate_env.py`:

```python
#!/usr/bin/env python3
"""Validate .env file has all required values."""

import os
import sys
from pathlib import Path

REQUIRED_VARS = [
    "POSTGRES_PASSWORD",
    "REDIS_PASSWORD",
    "JWT_SECRET_KEY",
]

INSECURE_VALUES = [
    "password",
    "123456",
    "your_",
    "replace_",
    "changeme",
]

def validate_env(env_file: Path) -> bool:
    """Validate environment file."""
    if not env_file.exists():
        print(f"❌ {env_file} not found")
        return False

    with open(env_file) as f:
        lines = f.readlines()

    env_vars = {}
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            if '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()

    # Check required vars
    missing = [var for var in REQUIRED_VARS if var not in env_vars]
    if missing:
        print(f"❌ Missing required variables: {', '.join(missing)}")
        return False

    # Check for insecure values
    issues = []
    for key, value in env_vars.items():
        if any(insecure in value.lower() for insecure in INSECURE_VALUES):
            issues.append(f"{key} contains insecure placeholder")

    if issues:
        print(f"⚠️  Security issues found:")
        for issue in issues:
            print(f"   - {issue}")
        return False

    print("✅ Environment file validated successfully")
    return True

if __name__ == "__main__":
    env_file = Path(sys.argv[1] if len(sys.argv) > 1 else ".env")
    sys.exit(0 if validate_env(env_file) else 1)
```

**Usage**:
```bash
# Validate before starting services
python scripts/validate_env.py
docker-compose up -d

# Validate production
python scripts/validate_env.py services/.env.production
```

---

## Docker Compose Best Practices

### Loading .env Files

#### Automatic Loading (Recommended)
```yaml
# docker-compose.yml
# Automatically loads .env from same directory
version: '3.8'
services:
  api:
    environment:
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
```

#### Explicit File (Multiple Environments)
```bash
# Load specific env file
docker-compose --env-file .env.production up -d

# Load multiple
docker-compose --env-file .env --env-file .env.local up -d
```

#### Service-Specific
```yaml
# docker-compose.yml
services:
  api:
    env_file:
      - .env
      - api/.env
```

---

## Common Patterns

### Development + Local Overrides
```
.env.example        → Template (in git)
.env                → Shared dev config (gitignored)
.env.local          → Personal overrides (gitignored)
```

**Usage**:
```bash
cp .env.example .env
# Edit .env with team defaults
echo "DEBUG=true" >> .env.local  # Personal override
```

### Multi-Environment
```
.env.example                → Template
.env.development            → Dev values
.env.staging                → Staging values
.env.production             → Prod values
```

**Usage**:
```bash
docker-compose --env-file .env.staging up -d
```

---

## Implementation Checklist

For Docker Integration Improvements task:

- [ ] Create `/.env.example` (consolidate from templates)
- [ ] Create `/services/.env.example`
- [ ] Rename `/services/env.production.template` to `.env.production.example`
- [ ] Create `/api/.env.example`
- [ ] Create `/frontend/.env.example`
- [ ] Create `/etl/.env.example`
- [ ] Remove duplicate templates (after consolidation)
- [ ] Update `.gitignore` (add explicit patterns)
- [ ] Create validation script
- [ ] Update README.md with new file names
- [ ] Update docker-compose.yml comments
- [ ] Test each environment setup

---

## Documentation References

- **Root README**: Should reference `.env.example`
- **Services README**: Should reference `services/.env.example`
- **Docker Integration Doc**: Should reference this guide
- **Team Setup Guide**: Should include .env setup steps

---

**Document Version**: 1.0
**Maintained By**: DevOps Team
**Related Docs**: DOCKER_INTEGRATION_IMPROVEMENTS.md
