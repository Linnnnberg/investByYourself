#!/bin/bash
# Bash script to start InvestByYourself development environment
# This script starts the frontend, API, database, and Redis using Docker

echo "🚀 Starting InvestByYourself Development Environment..."

# Check if Docker is running
if ! docker version > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is running"

# Check if .env.dev exists, if not create it from template
if [ ! -f ".env.dev" ]; then
    if [ -f "env.dev.template" ]; then
        echo "📝 Creating .env.dev from template..."
        cp env.dev.template .env.dev
        echo "✅ Created .env.dev - you may need to update API keys"
    else
        echo "⚠️  No .env.dev file found. Using default values."
    fi
fi

# Start the development environment
echo "🐳 Starting Docker containers..."
docker-compose -f docker-compose.dev.yml up --build

echo "🎉 Development environment started!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 API: http://localhost:8000"
echo "🗄️  Database Admin: http://localhost:8080"
echo "📊 Redis Admin: http://localhost:8081"
echo ""
echo "Press Ctrl+C to stop all services"
