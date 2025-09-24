#!/usr/bin/env python3
"""
Historical Data Service
Story-038: Portfolio Time Series & Data Structure Implementation

Service for collecting and managing historical price data and technical indicators.
"""

import asyncio
import logging
import uuid
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from ..core.config import settings
from ..models.database import (
    Company,
    DataQualityMetrics,
    HistoricalPrice,
    TechnicalIndicator,
)

logger = logging.getLogger(__name__)


class HistoricalDataService:
    """Service for historical data collection and management."""

    def __init__(self, db: Session):
        self.db = db
        self.alpha_vantage_key = getattr(settings, "ALPHA_VANTAGE_API_KEY", None)
        self.yahoo_finance_enabled = getattr(settings, "YAHOO_FINANCE_ENABLED", True)

    async def collect_historical_prices(
        self, company: Company, years: int = 5
    ) -> List[HistoricalPrice]:
        """Collect 5 years of historical price data for a company."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years * 365)

        logger.info(
            f"Collecting historical prices for {company.symbol} from {start_date.date()} to {end_date.date()}"
        )

        # Try Alpha Vantage first, fallback to Yahoo Finance
        try:
            if self.alpha_vantage_key:
                data = await self._fetch_alpha_vantage_data(
                    company.symbol, start_date, end_date
                )
                logger.info(
                    f"Successfully fetched data from Alpha Vantage for {company.symbol}"
                )
            else:
                raise Exception("Alpha Vantage API key not configured")
        except Exception as e:
            logger.warning(f"Alpha Vantage failed for {company.symbol}: {e}")
            if self.yahoo_finance_enabled:
                data = await self._fetch_yahoo_finance_data(
                    company.symbol, start_date, end_date
                )
                logger.info(
                    f"Successfully fetched data from Yahoo Finance for {company.symbol}"
                )
            else:
                raise Exception(f"All data sources failed for {company.symbol}: {e}")

        return self._process_price_data(company.id, data)

    async def _fetch_alpha_vantage_data(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> pd.DataFrame:
        """Fetch data from Alpha Vantage API."""
        import aiohttp

        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": symbol,
            "outputsize": "full",
            "apikey": self.alpha_vantage_key,
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()

        if "Error Message" in data:
            raise Exception(f"Alpha Vantage error: {data['Error Message']}")

        if "Note" in data:
            raise Exception(f"Alpha Vantage rate limit: {data['Note']}")

        # Convert to DataFrame
        time_series = data.get("Time Series (Daily)", {})
        if not time_series:
            raise Exception("No time series data found in Alpha Vantage response")

        df = pd.DataFrame.from_dict(time_series, orient="index")
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()

        # Rename columns to standard format
        df.columns = [
            "open",
            "high",
            "low",
            "close",
            "adjusted_close",
            "volume",
            "dividend_amount",
            "split_coefficient",
        ]

        # Convert to numeric
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Filter by date range
        df = df[(df.index >= start_date) & (df.index <= end_date)]

        return df

    async def _fetch_yahoo_finance_data(
        self, symbol: str, start_date: datetime, end_date: datetime
    ) -> pd.DataFrame:
        """Fetch data from Yahoo Finance (backup)."""
        try:
            import yfinance as yf
        except ImportError:
            raise Exception(
                "yfinance package not installed. Install with: pip install yfinance"
            )

        ticker = yf.Ticker(symbol)
        data = ticker.history(start=start_date, end=end_date)

        if data.empty:
            raise Exception(f"No data found for symbol {symbol}")

        # Rename columns to match our schema
        data.columns = data.columns.str.lower()
        data = data.rename(columns={"adj close": "adjusted_close"})

        # Add missing columns with default values
        if "dividend_amount" not in data.columns:
            data["dividend_amount"] = 0
        if "split_coefficient" not in data.columns:
            data["split_coefficient"] = 1.0

        return data

    def _process_price_data(
        self, company_id: str, data: pd.DataFrame
    ) -> List[HistoricalPrice]:
        """Process and validate price data."""
        prices = []

        for date, row in data.iterrows():
            # Skip rows with NaN values
            if row.isnull().any():
                logger.warning(
                    f"Skipping row with NaN values for {company_id} on {date}"
                )
                continue

            price = HistoricalPrice(
                id=str(uuid.uuid4()),
                company_id=company_id,
                date=date.date(),
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                volume=int(row["volume"]),
                adjusted_close=float(row.get("adjusted_close", row["close"])),
                dividend_amount=float(row.get("dividend_amount", 0)),
                split_coefficient=float(row.get("split_coefficient", 1.0)),
            )
            prices.append(price)

        logger.info(f"Processed {len(prices)} price records for company {company_id}")
        return prices

    def save_historical_prices(self, prices: List[HistoricalPrice]) -> None:
        """Save historical prices to database."""
        try:
            for price in prices:
                self.db.add(price)
            self.db.commit()
            logger.info(f"Saved {len(prices)} historical price records")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving historical prices: {e}")
            raise

    async def get_historical_prices(
        self,
        company_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 1000,
    ) -> List[HistoricalPrice]:
        """Get historical prices for a company."""
        query = select(HistoricalPrice).where(HistoricalPrice.company_id == company_id)

        if start_date:
            query = query.where(HistoricalPrice.date >= start_date)
        if end_date:
            query = query.where(HistoricalPrice.date <= end_date)

        query = query.order_by(HistoricalPrice.date.desc()).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_companies_with_historical_data(self) -> List[Company]:
        """Get companies that have historical data."""
        query = select(Company).join(HistoricalPrice).distinct()
        result = await self.db.execute(query)
        return result.scalars().all()

    async def validate_data_quality(self, company_id: str) -> Dict[str, any]:
        """Validate data quality for a company."""
        prices = await self.get_historical_prices(company_id)

        if not prices:
            return {"error": "No price data found"}

        # Check for missing dates
        expected_dates = self._get_expected_trading_dates(
            prices[-1].date, prices[0].date
        )
        actual_dates = {price.date for price in prices}
        missing_dates = expected_dates - actual_dates

        # Check for data anomalies
        anomalies = self._detect_price_anomalies(prices)

        # Calculate quality score
        quality_score = self._calculate_quality_score(
            len(prices), len(missing_dates), len(anomalies)
        )

        return {
            "total_records": len(prices),
            "missing_dates": len(missing_dates),
            "anomalies": len(anomalies),
            "quality_score": quality_score,
            "date_range": {
                "start": prices[-1].date.isoformat(),
                "end": prices[0].date.isoformat(),
            },
        }

    def _get_expected_trading_dates(self, start_date: date, end_date: date) -> set:
        """Get expected trading dates (weekdays only)."""
        dates = set()
        current = start_date

        while current <= end_date:
            # Skip weekends
            if current.weekday() < 5:
                dates.add(current)
            current += timedelta(days=1)

        return dates

    def _detect_price_anomalies(self, prices: List[HistoricalPrice]) -> List[Dict]:
        """Detect price anomalies (gaps, spikes, etc.)."""
        anomalies = []

        for i in range(1, len(prices)):
            prev_price = prices[i - 1]
            curr_price = prices[i]

            # Check for large price gaps (>20% change)
            price_change = abs(curr_price.close - prev_price.close) / prev_price.close
            if price_change > 0.2:
                anomalies.append(
                    {
                        "date": curr_price.date,
                        "type": "large_price_gap",
                        "change_percent": price_change * 100,
                    }
                )

            # Check for volume spikes (>5x average)
            if i >= 20:  # Need some history for average
                avg_volume = sum(p.volume for p in prices[i - 20 : i]) / 20
                if curr_price.volume > avg_volume * 5:
                    anomalies.append(
                        {
                            "date": curr_price.date,
                            "type": "volume_spike",
                            "volume_ratio": curr_price.volume / avg_volume,
                        }
                    )

        return anomalies

    def _calculate_quality_score(
        self, total_records: int, missing_dates: int, anomalies: int
    ) -> float:
        """Calculate data quality score (0.0 to 1.0)."""
        if total_records == 0:
            return 0.0

        # Base score from completeness
        completeness_score = 1.0 - (missing_dates / total_records)

        # Penalty for anomalies
        anomaly_penalty = min(anomalies / total_records, 0.2)  # Max 20% penalty

        return max(0.0, completeness_score - anomaly_penalty)
