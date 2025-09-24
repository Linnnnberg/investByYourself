#!/usr/bin/env python3
"""
Historical Data API Endpoints
Story-038: Portfolio Time Series & Data Structure Implementation

API endpoints for historical price data and technical indicators.
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.database.connection import get_db_session
from src.models.database import Company, HistoricalPrice, TechnicalIndicator
from src.services.historical_data_service import HistoricalDataService
from src.services.technical_indicators_service import TechnicalIndicatorsService

router = APIRouter()


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
    db: Session = Depends(get_db_session),
):
    """Get historical price data for a company."""
    try:
        # Find company
        company = db.query(Company).filter(Company.symbol == symbol).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        # Get historical prices
        historical_service = HistoricalDataService(db)
        prices = historical_service.get_historical_prices(
            company.id, start_date, end_date, limit
        )

        return {
            "symbol": symbol,
            "company_name": company.name,
            "prices": [
                {
                    "date": price.date.isoformat(),
                    "open": float(price.open),
                    "high": float(price.high),
                    "low": float(price.low),
                    "close": float(price.close),
                    "volume": int(price.volume),
                    "adjusted_close": float(price.adjusted_close),
                    "dividend_amount": float(price.dividend_amount),
                    "split_coefficient": float(price.split_coefficient),
                }
                for price in prices
            ],
            "total_records": len(prices),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get historical prices: {str(e)}"
        )


@router.get("/companies/{symbol}/technical-indicators")
async def get_technical_indicators(
    symbol: str,
    indicator_type: Optional[str] = Query(None, description="Filter by indicator type"),
    start_date: Optional[date] = Query(None, description="Start date for indicators"),
    end_date: Optional[date] = Query(None, description="End date for indicators"),
    db: Session = Depends(get_db_session),
):
    """Get technical indicators for a company."""
    try:
        # Find company
        company = db.query(Company).filter(Company.symbol == symbol).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        # Get technical indicators
        indicators_service = TechnicalIndicatorsService(db)
        indicators = indicators_service.get_technical_indicators(
            company.id, indicator_type, start_date, end_date
        )

        # Group by indicator type and name
        grouped_indicators = {}
        for indicator in indicators:
            key = f"{indicator.indicator_type}_{indicator.indicator_name}"
            if key not in grouped_indicators:
                grouped_indicators[key] = []

            grouped_indicators[key].append(
                {
                    "date": indicator.date.isoformat(),
                    "value": float(indicator.value) if indicator.value else None,
                    "period": indicator.period,
                }
            )

        return {
            "symbol": symbol,
            "company_name": company.name,
            "indicators": grouped_indicators,
            "total_indicators": len(indicators),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get technical indicators: {str(e)}"
        )


@router.get("/companies/{symbol}/data-quality")
async def get_data_quality(symbol: str, db: Session = Depends(get_db_session)):
    """Get data quality metrics for a company."""
    try:
        # Find company
        company = db.query(Company).filter(Company.symbol == symbol).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        # Get data quality metrics
        historical_service = HistoricalDataService(db)
        quality_metrics = historical_service.validate_data_quality(company.id)

        return {
            "symbol": symbol,
            "company_name": company.name,
            "quality_metrics": quality_metrics,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get data quality metrics: {str(e)}"
        )


@router.post("/companies/{symbol}/collect-data")
async def collect_historical_data(
    symbol: str,
    years: int = Query(
        5, ge=1, le=10, description="Number of years of historical data to collect"
    ),
    db: Session = Depends(get_db_session),
):
    """Collect historical data for a company."""
    try:
        # Find company
        company = db.query(Company).filter(Company.symbol == symbol).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        # Collect historical prices
        historical_service = HistoricalDataService(db)
        prices = await historical_service.collect_historical_prices(company, years)

        # Save prices to database
        historical_service.save_historical_prices(prices)

        # Calculate technical indicators
        indicators_service = TechnicalIndicatorsService(db)
        indicators = indicators_service.calculate_all_indicators(company.id, prices)

        # Save indicators to database
        indicators_service.save_technical_indicators(indicators)

        return {
            "symbol": symbol,
            "company_name": company.name,
            "prices_collected": len(prices),
            "indicators_calculated": len(indicators),
            "message": "Historical data collection completed successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to collect historical data: {str(e)}"
        )


@router.get("/companies/{symbol}/chart-data")
async def get_chart_data(
    symbol: str,
    start_date: Optional[date] = Query(None, description="Start date for chart data"),
    end_date: Optional[date] = Query(None, description="End date for chart data"),
    include_indicators: bool = Query(True, description="Include technical indicators"),
    db: Session = Depends(get_db_session),
):
    """Get formatted chart data for a company."""
    try:
        # Find company
        company = db.query(Company).filter(Company.symbol == symbol).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        # Get historical prices
        historical_service = HistoricalDataService(db)
        prices = historical_service.get_historical_prices(
            company.id, start_date, end_date, 1000
        )

        # Format price data for charts
        chart_data = []
        for price in reversed(prices):  # Reverse to get chronological order
            chart_point = {
                "date": price.date.isoformat(),
                "open": float(price.open),
                "high": float(price.high),
                "low": float(price.low),
                "close": float(price.close),
                "volume": int(price.volume),
                "adjusted_close": float(price.adjusted_close),
            }
            chart_data.append(chart_point)

        result = {
            "symbol": symbol,
            "company_name": company.name,
            "price_data": chart_data,
            "total_records": len(chart_data),
        }

        # Add technical indicators if requested
        if include_indicators:
            indicators_service = TechnicalIndicatorsService(db)
            indicators = indicators_service.get_technical_indicators(
                company.id, start_date=start_date, end_date=end_date
            )

            # Group indicators by date for easy chart integration
            indicators_by_date = {}
            for indicator in indicators:
                if indicator.date not in indicators_by_date:
                    indicators_by_date[indicator.date] = {}
                indicators_by_date[indicator.date][
                    f"{indicator.indicator_type}_{indicator.indicator_name}"
                ] = (float(indicator.value) if indicator.value else None)

            # Add indicators to chart data
            for chart_point in chart_data:
                date_obj = datetime.fromisoformat(chart_point["date"]).date()
                if date_obj in indicators_by_date:
                    chart_point.update(indicators_by_date[date_obj])

            result["indicators_available"] = list(
                set(f"{ind.indicator_type}_{ind.indicator_name}" for ind in indicators)
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get chart data: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for historical data service."""
    return {
        "status": "healthy",
        "service": "historical-data",
        "timestamp": datetime.utcnow().isoformat(),
    }
