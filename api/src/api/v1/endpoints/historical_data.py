#!/usr/bin/env python3
"""
Simple Historical Data API Endpoints
Compatible with current database schema using MarketData table.
"""

from datetime import date, datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import get_db_session
from src.models.database import Company, MarketData

router = APIRouter()


@router.get("/companies/{symbol}/chart-data")
async def get_chart_data(
    symbol: str,
    start_date: Optional[date] = Query(None, description="Start date for chart data"),
    end_date: Optional[date] = Query(None, description="End date for chart data"),
    include_indicators: bool = Query(True, description="Include technical indicators"),
    limit: int = Query(
        1000, le=5000, description="Maximum number of records to return"
    ),
    db: AsyncSession = Depends(get_db_session),
):
    """Get formatted chart data for a company."""
    try:
        # Find company
        result = await db.execute(select(Company).filter(Company.symbol == symbol))
        company = result.scalar_one_or_none()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        # Build query for market data
        query = select(MarketData).filter(MarketData.company_id == company.id)

        # Add date filters if provided
        if start_date:
            query = query.filter(MarketData.data_date >= start_date)
        if end_date:
            query = query.filter(MarketData.data_date <= end_date)

        # Order by date descending and limit
        query = query.order_by(desc(MarketData.data_date)).limit(limit)
        result = await db.execute(query)
        market_data = result.scalars().all()

        if not market_data:
            raise HTTPException(
                status_code=404, detail="No historical data found for this company"
            )

        # Format price data for charts
        chart_data = []
        for data in market_data:
            chart_point = {
                "date": data.data_date.strftime("%Y-%m-%d"),
                "open": float(data.open_price) if data.open_price else None,
                "high": float(data.high_price) if data.high_price else None,
                "low": float(data.low_price) if data.low_price else None,
                "close": float(data.close_price) if data.close_price else None,
                "volume": int(data.volume) if data.volume else None,
                "adjusted_close": float(data.adjusted_close)
                if data.adjusted_close
                else None,
            }
            chart_data.append(chart_point)

        # Sort by date ascending for chart display
        chart_data.sort(key=lambda x: x["date"])

        result = {
            "symbol": symbol,
            "company_name": company.name,
            "price_data": chart_data,
            "total_records": len(chart_data),
        }

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get chart data: {str(e)}"
        )


@router.get("/companies/{symbol}/historical-prices")
async def get_historical_prices(
    symbol: str,
    start_date: Optional[date] = Query(
        None, description="Start date for historical data"
    ),
    end_date: Optional[date] = Query(None, description="End date for historical data"),
    limit: int = Query(
        1000, le=5000, description="Maximum number of records to return"
    ),
    db: AsyncSession = Depends(get_db_session),
):
    """Get historical price data for a company."""
    try:
        # Find company
        result = await db.execute(select(Company).filter(Company.symbol == symbol))
        company = result.scalar_one_or_none()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        # Build query for market data
        query = select(MarketData).filter(MarketData.company_id == company.id)

        # Add date filters if provided
        if start_date:
            query = query.filter(MarketData.data_date >= start_date)
        if end_date:
            query = query.filter(MarketData.data_date <= end_date)

        # Order by date descending and limit
        query = query.order_by(desc(MarketData.data_date)).limit(limit)
        result = await db.execute(query)
        market_data = result.scalars().all()

        if not market_data:
            raise HTTPException(
                status_code=404, detail="No historical data found for this company"
            )

        # Format price data
        prices = []
        for data in market_data:
            price = {
                "date": data.data_date.strftime("%Y-%m-%d"),
                "open": float(data.open_price) if data.open_price else None,
                "high": float(data.high_price) if data.high_price else None,
                "low": float(data.low_price) if data.low_price else None,
                "close": float(data.close_price) if data.close_price else None,
                "volume": int(data.volume) if data.volume else None,
                "adjusted_close": float(data.adjusted_close)
                if data.adjusted_close
                else None,
            }
            prices.append(price)

        return {
            "symbol": symbol,
            "company_name": company.name,
            "prices": prices,
            "total_records": len(prices),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get historical prices: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for historical data service."""
    return {
        "status": "healthy",
        "service": "historical-data-simple",
        "timestamp": datetime.utcnow().isoformat(),
    }
