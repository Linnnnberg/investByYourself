#!/usr/bin/env python3
"""
Rate Limiting Middleware for InvestByYourself API
Tech-028: API Implementation

Implements rate limiting to protect the API from over-calling.
"""

import time
from typing import Dict, Optional

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address


# Simple rate limiting configuration for testing
class SimpleSettings:
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_WINDOW = 60


settings = SimpleSettings()

# Create rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[
        f"{settings.RATE_LIMIT_REQUESTS}/{settings.RATE_LIMIT_WINDOW}second"
    ],
)


def setup_rate_limiting(app) -> None:
    """Setup rate limiting middleware."""
    if settings.RATE_LIMIT_ENABLED:
        # Add rate limiting middleware
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        app.add_middleware(SlowAPIMiddleware)

        print(
            f"✅ Rate limiting enabled: {settings.RATE_LIMIT_REQUESTS} requests per {settings.RATE_LIMIT_WINDOW} seconds"
        )
    else:
        print("⚠️  Rate limiting disabled")


def get_rate_limit_info(request: Request) -> Dict[str, any]:
    """Get current rate limit information for a request."""
    if not settings.RATE_LIMIT_ENABLED:
        return {"enabled": False}

    # Get client IP
    client_ip = get_remote_address(request)

    # Get current rate limit status
    # This is a simplified version - in production you'd want to use Redis
    return {
        "enabled": True,
        "client_ip": client_ip,
        "limit": settings.RATE_LIMIT_REQUESTS,
        "window": settings.RATE_LIMIT_WINDOW,
        "remaining": "N/A",  # Would need Redis to track this accurately
    }


def create_rate_limit_response(rate_limit_info: Dict[str, any]) -> JSONResponse:
    """Create a rate limit exceeded response."""
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": f"Too many requests. Limit: {rate_limit_info['limit']} requests per {rate_limit_info['window']} seconds",
            "retry_after": rate_limit_info["window"],
            "limit": rate_limit_info["limit"],
            "window": rate_limit_info["window"],
        },
        headers={
            "Retry-After": str(rate_limit_info["window"]),
            "X-RateLimit-Limit": str(rate_limit_info["limit"]),
            "X-RateLimit-Window": str(rate_limit_info["window"]),
        },
    )
