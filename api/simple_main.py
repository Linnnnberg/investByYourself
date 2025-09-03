#!/usr/bin/env python3
"""
Simple InvestByYourself API Server
Tech-028: API Implementation

Simplified version to get the server running quickly.
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.v1.endpoints.portfolio import router as portfolio_router
from src.middleware.rate_limiting import limiter, setup_rate_limiting

# Import portfolio models and endpoints
from src.models.portfolio import (
    HoldingCreate,
    PortfolioCreate,
    PortfolioUpdate,
    TransactionCreate,
)
from src.services.database_service import db_service

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting InvestByYourself API Gateway...")
    logger.info("Environment: development")
    logger.info("Debug mode: true")

    # Initialize database service
    try:
        db_service.initialize()
        connection_test = db_service.test_connection()
        if connection_test["status"] == "connected":
            logger.info(
                f"Database connected: {connection_test['database']} on {connection_test['host']}:{connection_test['port']}"
            )
        else:
            logger.error(
                f"Database connection failed: {connection_test.get('error', 'Unknown error')}"
            )
    except Exception as e:
        logger.error(f"Failed to initialize database service: {e}")

    yield

    # Shutdown
    logger.info("Shutting down InvestByYourself API Gateway...")
    db_service.close()


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title="InvestByYourself API",
        description="Comprehensive investment platform API with portfolio management, market data, and financial analysis",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:8000",
            "http://localhost:3001",
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
    )

    # Setup rate limiting
    setup_rate_limiting(app)

    # Include portfolio router
    app.include_router(
        portfolio_router, prefix="/api/v1/portfolio", tags=["Portfolio Management"]
    )

    # Add health check endpoint
    @app.get("/health")
    @limiter.limit("100/minute")  # More lenient for health checks
    async def health_check(request: Request):
        """Health check endpoint for monitoring."""
        # Test database connection
        db_status = db_service.test_connection()

        # Determine status based on database connection
        if db_status["status"] == "connected":
            status = "healthy"
        elif db_status["status"] == "mock_mode":
            status = "healthy (mock data)"
        else:
            status = "degraded"

        return {
            "status": status,
            "service": "InvestByYourself API",
            "version": "1.0.0",
            "environment": "development",
            "database": db_status,
        }

    # Add root endpoint
    @app.get("/")
    @limiter.limit("50/minute")  # Moderate rate limit for root endpoint
    async def root(request: Request):
        """Root endpoint with API information."""
        return {
            "message": "InvestByYourself API Gateway",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health",
            "portfolio_api": "/api/v1/portfolio",
        }

    # Add simple auth endpoints for testing
    @app.post("/api/v1/auth/register")
    async def register_user():
        """Simple registration endpoint."""
        return {
            "message": "Registration endpoint - not implemented yet",
            "status": "placeholder",
        }

    @app.post("/api/v1/auth/login")
    async def login_user():
        """Simple login endpoint."""
        return {
            "message": "Login endpoint - not implemented yet",
            "status": "placeholder",
        }

    # Add portfolio test endpoints
    @app.get("/api/v1/portfolio/test")
    @limiter.limit("30/minute")  # Stricter rate limit for portfolio test
    async def portfolio_test(request: Request):
        """Test portfolio endpoint."""
        return {
            "message": "Portfolio API is working!",
            "endpoints": [
                "POST /api/v1/portfolio/ - Create portfolio",
                "GET /api/v1/portfolio/ - List portfolios",
                "GET /api/v1/portfolio/{id} - Get portfolio details",
                "POST /api/v1/portfolio/{id}/holdings - Add holding",
                "GET /api/v1/portfolio/{id}/analytics - Get analytics",
            ],
        }

    # Add database info endpoint
    @app.get("/api/v1/database/info")
    @limiter.limit("10/minute")  # Very strict rate limit for database info
    async def database_info(request: Request):
        """Get database information and schema."""
        try:
            # Get portfolio tables
            tables = await db_service.get_portfolio_tables()

            # Get schema for first few tables
            table_schemas = {}
            for table in tables[:3]:  # Limit to first 3 tables to avoid large response
                schema = await db_service.get_table_schema(table)
                table_schemas[table] = schema

            return {
                "message": "Database information retrieved successfully",
                "database": db_service.test_connection(),
                "portfolio_tables": tables,
                "table_schemas": table_schemas,
                "total_tables": len(tables),
            }
        except Exception as e:
            return {
                "message": "Failed to retrieve database information",
                "error": str(e),
                "database": db_service.test_connection(),
            }

    return app


# Create the application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "simple_main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
