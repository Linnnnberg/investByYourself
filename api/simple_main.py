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

    yield

    # Shutdown
    logger.info("Shutting down InvestByYourself API Gateway...")


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

    # Add health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint for monitoring."""
        return {
            "status": "healthy",
            "service": "InvestByYourself API",
            "version": "1.0.0",
            "environment": "development",
        }

    # Add root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "message": "InvestByYourself API Gateway",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health",
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

    @app.get("/api/v1/auth/profile")
    async def get_profile():
        """Simple profile endpoint."""
        return {
            "message": "Profile endpoint - not implemented yet",
            "status": "placeholder",
        }

    return app


# Create the application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "simple_main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
