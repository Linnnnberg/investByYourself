#!/usr/bin/env python3
"""
InvestByYourself API Router
Tech-028: API Implementation

Main API router that includes all endpoint modules.
"""

from fastapi import APIRouter

from src.api.v1.endpoints import (
    analysis,
    auth,
    etl,
    investment_profile,
    market_data,
    notifications,
    portfolio,
    watchlist,
    websocket,
)

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

api_router.include_router(
    portfolio.router, prefix="/portfolio", tags=["Portfolio Management"]
)

api_router.include_router(
    investment_profile.router, prefix="/investment-profile", tags=["Investment Profile"]
)

api_router.include_router(market_data.router, prefix="/market", tags=["Market Data"])

api_router.include_router(watchlist.router, prefix="/watchlist", tags=["Watchlist"])

api_router.include_router(
    analysis.router, prefix="/analysis", tags=["Financial Analysis"]
)

api_router.include_router(etl.router, prefix="/etl", tags=["ETL Pipeline"])

api_router.include_router(
    notifications.router, prefix="/notifications", tags=["Notifications"]
)

api_router.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])
