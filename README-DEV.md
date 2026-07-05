# InvestByYourself Development Environment

This guide shows you how to start the entire development environment (frontend + API + database) using Docker.

## Quick Start

### Option 1: Using PowerShell (Windows)
```powershell
.\start-dev.ps1
```

### Option 2: Using Bash (Linux/Mac/WSL)
```bash
./start-dev.sh
```

### Option 3: Manual Docker Compose
```bash
# Copy environment template
cp env.dev.template .env.dev

# Start all services
docker-compose -f docker-compose.dev.yml up --build
```

## What Gets Started

When you run the development environment, you'll get:

- **Frontend** (Next.js): http://localhost:3000
- **API** (FastAPI): http://localhost:8000
- **Database** (SQLite via file volume): `api/investbyyourself_dev.db`
- **Cache** (Redis): localhost:6379
- **Database Admin** (Adminer): http://localhost:8080
- **Redis Admin** (Redis Commander): http://localhost:8081

## Services Overview

### Frontend Service
- **Technology**: Next.js 14 with React 18
- **Port**: 3000
- **Hot Reload**: ✅ Enabled
- **API Integration**: Connected to FastAPI backend

### API Service
- **Technology**: FastAPI with Python 3.11
- **Port**: 8000
- **Hot Reload**: ✅ Enabled
- **Database**: Connected to PostgreSQL
- **Cache**: Connected to Redis

### Database Service
- **Technology**: SQLite (file-based)
- **Path**: `api/investbyyourself_dev.db`
- **Data Persistence**: ✅ Enabled (volume-mounted file)

### Cache Service
- **Technology**: Redis 7
- **Port**: 6379
- **Data Persistence**: ✅ Enabled

## Environment Configuration

The development environment uses these default values:

```env
# Database
POSTGRES_PASSWORD=<set_in_.env>
REDIS_PASSWORD=<set_in_.env>

# JWT - SECURITY WARNING: Never use default JWT secrets, even in development!
# Generate a secure key with: python -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_SECRET_KEY=<your_generated_jwt_secret_key_here>

# API Keys (Optional)
ALPHA_VANTAGE_API_KEY=your_api_key_here
YAHOO_FINANCE_API_KEY=your_api_key_here
```

## Development Workflow

1. **Start Environment**: Run `.\start-dev.ps1` or `./start-dev.sh`
2. **Make Changes**: Edit code in `frontend/` or `api/` directories
3. **See Changes**: Frontend and API auto-reload on file changes
4. **Stop Environment**: Press `Ctrl+C` in the terminal

## Troubleshooting

### Port Already in Use
If you get port conflicts, check what's using the ports:
```bash
# Windows
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :3000
lsof -i :8000
```

### Database Connection Issues
1. Wait for PostgreSQL to fully start (takes ~30 seconds)
2. Check database logs: `docker logs investbyyourself_postgres_dev`
3. Verify connection: Visit http://localhost:8080 (Adminer)

### API Not Responding
1. Check API logs: `docker logs investbyyourself_api_dev`
2. Verify API health: Visit http://localhost:8000/health
3. Check database connection

### Frontend Not Loading
1. Check frontend logs: `docker logs investbyyourself_frontend_dev`
2. Verify API connection: Check browser network tab
3. Ensure API is running first

## Stopping the Environment

To stop all services:
- Press `Ctrl+C` in the terminal where you started the environment
- Or run: `docker-compose -f docker-compose.dev.yml down`

To stop and remove all data:
```bash
docker-compose -f docker-compose.dev.yml down -v
```

## Advanced Usage

### View Logs
```bash
# All services
docker-compose -f docker-compose.dev.yml logs

# Specific service
docker-compose -f docker-compose.dev.yml logs api
docker-compose -f docker-compose.dev.yml logs frontend
```

### Rebuild Services
```bash
# Rebuild all
docker-compose -f docker-compose.dev.yml up --build

# Rebuild specific service
docker-compose -f docker-compose.dev.yml up --build api
```

### Access Database
- Use any SQLite client to open `api/investbyyourself_dev.db`

### Access Redis
- **Redis Commander**: http://localhost:8081
  - Password: `<set_in_.env>`

## File Structure

```
├── docker-compose.dev.yml    # Development Docker Compose
├── start-dev.ps1            # Windows startup script
├── start-dev.sh             # Linux/Mac startup script
├── env.dev.template         # Environment variables template
├── api/
│   ├── Dockerfile           # API Docker configuration
│   └── src/                 # API source code
├── frontend/
│   ├── Dockerfile           # Frontend Docker configuration
│   └── src/                 # Frontend source code
└── database/
    └── schema.sql           # Database schema
```

## Next Steps

Once the environment is running:
1. Visit http://localhost:3000 to see the frontend
2. Visit http://localhost:8000/docs to see the API documentation
3. Start developing your features!
4. Check the master todo list for what to work on next
