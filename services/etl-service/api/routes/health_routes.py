"""
Health Check Routes for ETL Service
Tech-021: ETL Service Extraction

Health monitoring and service status endpoints.
"""

from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from models.config import ETLServiceConfig

router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "etl-service",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": "running",
    }


@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """Readiness check for Kubernetes/load balancer health checks."""
    try:
        # Basic readiness check - service is ready to accept requests
        return {
            "status": "ready",
            "service": "etl-service",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service not ready: {str(e)}",
        )


@router.get("/live")
async def liveness_check() -> Dict[str, Any]:
    """Liveness check for Kubernetes health monitoring."""
    try:
        # Basic liveness check - service is alive and responding
        return {
            "status": "alive",
            "service": "etl-service",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service not alive: {str(e)}",
        )


@router.get("/config")
async def config_check(config: ETLServiceConfig = Depends()) -> Dict[str, Any]:
    """Configuration validation check."""
    try:
        # Validate configuration
        config.validate_config()

        return {
            "status": "configured",
            "service": "etl-service",
            "database": "configured" if config.database_url else "not_configured",
            "redis": "configured" if config.redis_host else "not_configured",
            "minio": "configured" if config.minio_host else "not_configured",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Configuration error: {str(e)}",
        )
