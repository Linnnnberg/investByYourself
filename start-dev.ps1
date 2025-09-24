# PowerShell script to start InvestByYourself development environment
# This script starts the frontend, API, database, and Redis using Docker

Write-Host "Starting InvestByYourself Development Environment..." -ForegroundColor Green

# Check if Docker is running
try {
    docker version | Out-Null
    Write-Host "Docker is running" -ForegroundColor Green
} catch {
    Write-Host "Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check if .env.dev exists, if not create it from template
if (-not (Test-Path ".env.dev")) {
    if (Test-Path "env.dev.template") {
        Write-Host "Creating .env.dev from template..." -ForegroundColor Yellow
        Copy-Item "env.dev.template" ".env.dev"
        Write-Host "Created .env.dev - you may need to update API keys" -ForegroundColor Green
    } else {
        Write-Host "No .env.dev file found. Using default values." -ForegroundColor Yellow
    }
}

# Start the development environment
Write-Host "Starting Docker containers..." -ForegroundColor Blue
docker-compose -f docker-compose.dev.yml up --build

Write-Host "Development environment started!" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Redis Admin: http://localhost:8081" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
