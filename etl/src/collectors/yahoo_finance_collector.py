"""
Yahoo Finance Data Collector
InvestByYourself Financial Platform

Collects market data, company profiles, and financial information from Yahoo Finance.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


class YahooFinanceCollector:
    """Yahoo Finance data collector."""

    def __init__(self):
        """Initialize Yahoo Finance collector."""
        self.name = "Yahoo Finance"
        self.rate_limit = 0.5  # requests per second (slower to avoid rate limits)
        self.timeout = 30
        self.last_request_time = 0
        self.max_retries = 3
        self.retry_delay = 5  # seconds

    async def _rate_limit(self):
        """Apply rate limiting between requests."""
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self.last_request_time
        min_interval = 1.0 / self.rate_limit

        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            await asyncio.sleep(sleep_time)

        self.last_request_time = asyncio.get_event_loop().time()

    async def _retry_with_backoff(self, func, *args, **kwargs):
        """Retry function with exponential backoff for rate limit errors."""
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if "429" in str(e) or "Too Many Requests" in str(e):
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_delay * (2**attempt)
                        logger.warning(
                            f"Rate limited, retrying in {wait_time} seconds (attempt {attempt + 1}/{self.max_retries})"
                        )
                        await asyncio.sleep(wait_time)
                        continue
                raise e
        raise Exception(f"Max retries ({self.max_retries}) exceeded")

    async def collect_company_profile(self, symbol: str) -> Dict[str, Any]:
        """Collect company profile information."""
        try:
            logger.info(f"Collecting company profile for {symbol}")

            # Apply rate limiting
            await self._rate_limit()

            # Use retry wrapper for the actual data collection
            return await self._retry_with_backoff(
                self._collect_company_profile_data, symbol
            )

        except Exception as e:
            logger.error(f"Failed to collect company profile for {symbol}: {e}")
            raise

    async def _collect_company_profile_data(self, symbol: str) -> Dict[str, Any]:
        """Internal method to collect company profile data."""
        # Create ticker object
        ticker = yf.Ticker(symbol)

        # Get company info
        info = ticker.info

        # Extract relevant information
        profile = {
            "symbol": symbol,
            "name": info.get("longName", ""),
            "sector": info.get("sector", ""),
            "industry": info.get("industry", ""),
            "exchange": info.get("exchange", ""),
            "currency": info.get("currency", "USD"),
            "country": info.get("country", ""),
            "website": info.get("website", ""),
            "description": info.get("longBusinessSummary", ""),
            "employee_count": info.get("fullTimeEmployees", 0),
            "market_cap": info.get("marketCap", 0),
            "enterprise_value": info.get("enterpriseValue", 0),
            "ceo": info.get("companyOfficers", [{}])[0].get("name", "")
            if info.get("companyOfficers")
            else "",
            "headquarters": f"{info.get('city', '')}, {info.get('state', '')}, {info.get('country', '')}",
            "founded_year": info.get("founded", 0),
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        logger.info(f"Company profile collected for {symbol}")
        return profile

    async def collect_historical_data(
        self, symbol: str, incremental: bool = False
    ) -> List[Dict[str, Any]]:
        """Collect historical market data."""
        try:
            logger.info(f"Collecting historical data for {symbol}")

            # Apply rate limiting
            await self._rate_limit()

            # Use retry wrapper for the actual data collection
            return await self._retry_with_backoff(
                self._collect_historical_data_data, symbol, incremental
            )

        except Exception as e:
            logger.error(f"Failed to collect historical data for {symbol}: {e}")
            raise

    async def _collect_historical_data_data(
        self, symbol: str, incremental: bool = False
    ) -> List[Dict[str, Any]]:
        """Internal method to collect historical data."""
        # Create ticker object
        ticker = yf.Ticker(symbol)

        # Determine date range
        if incremental:
            # Last 30 days for incremental updates
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
        else:
            # 5 years for full import
            end_date = datetime.now()
            start_date = end_date - timedelta(days=5 * 365)

        # Get historical data
        hist = ticker.history(start=start_date, end=end_date)

        # Convert to list of dictionaries
        historical_data = []
        for date, row in hist.iterrows():
            data_point = {
                "symbol": symbol,
                "date": date.strftime("%Y-%m-%d"),
                "open": float(row["Open"]) if pd.notna(row["Open"]) else None,
                "high": float(row["High"]) if pd.notna(row["High"]) else None,
                "low": float(row["Low"]) if pd.notna(row["Low"]) else None,
                "close": float(row["Close"]) if pd.notna(row["Close"]) else None,
                "volume": int(row["Volume"]) if pd.notna(row["Volume"]) else None,
                "adjusted_close": float(row["Adj Close"])
                if pd.notna(row["Adj Close"])
                else None,
                "source": "yahoo_finance",
                "created_at": datetime.now().isoformat(),
            }
            historical_data.append(data_point)

        logger.info(
            f"Historical data collected for {symbol}: {len(historical_data)} records"
        )
        return historical_data

    async def collect_financial_ratios(self, symbol: str) -> Dict[str, Any]:
        """Collect financial ratios and metrics."""
        try:
            logger.info(f"Collecting financial ratios for {symbol}")

            # Apply rate limiting
            await self._rate_limit()

            # Use retry wrapper for the actual data collection
            return await self._retry_with_backoff(
                self._collect_financial_ratios_data, symbol
            )

        except Exception as e:
            logger.error(f"Failed to collect financial ratios for {symbol}: {e}")
            raise

    async def _collect_financial_ratios_data(self, symbol: str) -> Dict[str, Any]:
        """Internal method to collect financial ratios data."""
        # Create ticker object
        ticker = yf.Ticker(symbol)

        # Get financial info
        info = ticker.info

        # Extract financial ratios
        ratios = {
            "symbol": symbol,
            "period_end_date": datetime.now().strftime("%Y-%m-%d"),
            "current_ratio": info.get("currentRatio", None),
            "quick_ratio": info.get("quickRatio", None),
            "debt_to_equity": info.get("debtToEquity", None),
            "return_on_equity": info.get("returnOnEquity", None),
            "return_on_assets": info.get("returnOnAssets", None),
            "gross_margin": info.get("grossMargins", None),
            "operating_margin": info.get("operatingMargins", None),
            "net_margin": info.get("profitMargins", None),
            "pe_ratio": info.get("trailingPE", None),
            "pb_ratio": info.get("priceToBook", None),
            "ps_ratio": info.get("priceToSalesTrailing12Months", None),
            "dividend_yield": info.get("dividendYield", None),
            "beta": info.get("beta", None),
            "source": "yahoo_finance",
            "created_at": datetime.now().isoformat(),
        }

        logger.info(f"Financial ratios collected for {symbol}")
        return ratios
