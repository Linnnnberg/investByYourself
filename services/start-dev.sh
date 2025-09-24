#!/bin/bash
# Quick Start Script for Development Environment
# Tech-020: Microservices Foundation

echo "🚀 Starting InvestByYourself Microservices Development Environment"
echo "================================================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker environment check passed"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from development template..."
    cp .env.development .env
    echo "✅ .env file created"
else
    echo "✅ .env file already exists"
fi

# Build and start services
echo "🔨 Building and starting services..."
docker-compose up -d --build

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service status
echo "🔍 Checking service status..."
docker-compose ps

echo ""
echo "🎉 Development environment is ready!"
echo ""
echo "📊 Service URLs:"
echo "   ETL Service: http://localhost:8000"
echo "   Financial Analysis: http://localhost:8001"
echo "   Data Service: http://localhost:8002"
echo ""
echo "🛠️  Development Tools:"
echo "   Adminer (Database): http://localhost:8080"
echo "   Redis Commander: http://localhost:8081"
echo "   MinIO Console: http://localhost:9001"
echo ""
echo "📝 Useful Commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart service: docker-compose restart <service-name>"
echo ""
echo "🚀 Happy coding!"
