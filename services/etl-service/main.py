"""
ETL Service Main Entry Point
Tech-021: ETL Service Extraction

FastAPI service that provides REST API endpoints for ETL operations.
"""

import asyncio
import logging
import os
import signal
import sys
from contextlib import asynccontextmanager
from typing import Any, Dict

import structlog
import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add service directory to path for imports
sys.path.append(os.path.dirname(__file__))

from models.config import ETLServiceConfig
from worker.etl_worker import ETLWorker

from api.routes import etl_routes, health_routes

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Global ETL worker instance
etl_worker: ETLWorker = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage service lifecycle."""
    global etl_worker

    # Startup
    logger.info("Starting ETL Service...")

    try:
        # Initialize ETL worker
        etl_worker = ETLWorker()
        await etl_worker.initialize()
        logger.info("ETL Service started successfully")

        yield

    except Exception as e:
        logger.error("Failed to start ETL Service", error=str(e))
        raise

    finally:
        # Shutdown
        logger.info("Shutting down ETL Service...")
        if etl_worker:
            await etl_worker.shutdown()
        logger.info("ETL Service shutdown complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    # Load configuration
    config = ETLServiceConfig()

    app = FastAPI(
        title="ETL Service",
        description="Financial data ETL operations for investByYourself platform",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.error(
            "Unhandled exception", error=str(exc), request_path=request.url.path
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )

    # Include routers
    app.include_router(health_routes.router, prefix="/health", tags=["health"])
    app.include_router(etl_routes.router, prefix="/api/v1/etl", tags=["etl"])

    # Add root endpoint
    @app.get("/")
    async def root():
        return {
            "service": "ETL Service",
            "version": "2.0.0",
            "status": "running",
            "docs": "/docs",
        }

    return app


def main():
    """Main entry point for the ETL service."""
    try:
        # Load environment variables
        from dotenv import load_dotenv

        load_dotenv()

        # Create app
        app = create_app()

        # Get configuration
        host = os.getenv("ETL_SERVICE_HOST", "0.0.0.0")
        port = int(os.getenv("ETL_SERVICE_PORT", "8001"))
        reload = os.getenv("ETL_SERVICE_RELOAD", "false").lower() == "true"

        logger.info("Starting ETL Service", host=host, port=port, reload=reload)

        # Start the service
        uvicorn.run("main:app", host=host, port=port, reload=reload, log_level="info")

    except KeyboardInterrupt:
        logger.info("ETL Service stopped by user")
    except Exception as e:
        logger.error("Failed to start ETL Service", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
