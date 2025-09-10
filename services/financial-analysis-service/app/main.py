"""
Financial Analysis Service - Main Application
============================================

FastAPI application for investment strategy management and financial analysis.
"""

import os
from datetime import datetime

import uvicorn
# Import API routers
from app.api import backtesting, results, strategies
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Create FastAPI application
app = FastAPI(
    title="Financial Analysis Service",
    description="Investment Strategy Management and Financial Analysis Microservice",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(strategies.router, prefix="/api/v1", tags=["strategies"])
app.include_router(backtesting.router, prefix="/api/v1", tags=["backtesting"])
app.include_router(results.router, prefix="/api/v1", tags=["results"])


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Financial Analysis Service",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "description": "Investment Strategy Management and Financial Analysis",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "financial-analysis-service",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint for deployment."""
    # Add database connection check here when implemented
    return {
        "status": "ready",
        "service": "financial-analysis-service",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected",  # Will be dynamic when DB is implemented
        "dependencies": ["database", "redis", "strategy_framework"],
    }


if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"

    # Run the application
    uvicorn.run("app.main:app", host=host, port=port, reload=debug, log_level="info")
