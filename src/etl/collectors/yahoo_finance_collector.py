"""
Yahoo Finance Data Collector - investByYourself
Tech-009: ETL Pipeline Implementation - Phase 1

This module implements a Yahoo Finance data collector with:
- Company profile and fundamentals collection
- Financial statements (income, balance sheet, cash flow)
- Market data and technical indicators
- Rate limiting and error handling
- Data validation and transformation
"""

import asyncio
import json
import logging
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from urllib.parse import quote

import aiohttp
import pandas as pd
import structlog
import yfinance as yf

from .base_collector import (BaseDataCollector, DataCollectionError,
                             DataValidationError, RateLimitConfig, RetryConfig)

logger = structlog.get_logger(__name__)


class YahooFinanceCollector(BaseDataCollector):
    """
    Yahoo Finance data collector with rate limiting and error handling.

    Features:
    - Company profile and fundamentals
    - Financial statements (income, balance sheet, cash flow)
    - Market data and technical indicators
    - Historical price data
    - Options and dividend data
    """

    def __init__(
        self,
        rate_limit_config: Optional[RateLimitConfig] = None,
        retry_config: Optional[RetryConfig] = None,
        session_timeout: int = 30,
        max_concurrent_requests: int = 5,
    ):
        """Initialize Yahoo Finance collector."""
        # Yahoo Finance has generous rate limits, but we'll be conservative
        default_rate_limit = RateLimitConfig(
            max_requests_per_minute=30,  # Conservative limit
            max_requests_per_hour=500,
            max_requests_per_day=5000,
            burst_limit=5,
            cooldown_period=0.5,
        )

        default_retry = RetryConfig(
            max_retries=3,
            base_delay=2.0,
            max_delay=30.0,
            exponential_backoff=True,
            retry_on_status_codes=[429, 500, 502, 503, 504, 503],
        )

        super().__init__(
            name="yahoo_finance_collector",
            rate_limit_config=rate_limit_config or default_rate_limit,
            retry_config=retry_config or default_retry,
        )

        self.session_timeout = session_timeout
        self.max_concurrent_requests = max_concurrent_requests
        self.session: Optional[aiohttp.ClientSession] = None
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)

        # Data quality thresholds specific to Yahoo Finance
        self.quality_thresholds.update(
            {
                "min_records": 1,
                "max_failure_rate": 0.05,  # 5% - Yahoo Finance is generally reliable
                "min_data_completeness": 0.85,  # 85%
                "min_price_accuracy": 0.99,  # 99% for price data
            }
        )

        logger.info(
            "Yahoo Finance collector initialized",
            rate_limit_config=self.rate_limit_config,
            retry_config=self.retry_config,
            session_timeout=session_timeout,
            max_concurrent_requests=max_concurrent_requests,
        )

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()

    async def initialize(self):
        """Initialize the collector session."""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=self.session_timeout)
            connector = aiohttp.TCPConnector(limit=self.max_concurrent_requests)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                },
            )
            logger.info("Yahoo Finance collector session initialized")

    async def cleanup(self):
        """Clean up resources."""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("Yahoo Finance collector session closed")

    async def collect_data(self, **kwargs) -> Dict[str, Any]:
        """
        Collect data from Yahoo Finance based on parameters.

        Args:
            **kwargs: Collection parameters including:
                - symbol: Stock symbol (e.g., 'AAPL')
                - data_type: Type of data to collect
                - period: Time period for historical data
                - interval: Data interval for historical data

        Returns:
            Dict containing collected data and metadata
        """
        symbol = kwargs.get("symbol", "").upper()
        data_type = kwargs.get("data_type", "profile")
        period = kwargs.get("period", "1y")
        interval = kwargs.get("interval", "1d")

        if not symbol:
            raise DataCollectionError("Symbol is required for data collection")

        async with self.semaphore:
            try:
                if data_type == "profile":
                    return await self._collect_company_profile(symbol)
                elif data_type == "financials":
                    return await self._collect_financial_statements(symbol)
                elif data_type == "market_data":
                    return await self._collect_market_data(symbol, period, interval)
                elif data_type == "fundamentals":
                    return await self._collect_fundamentals(symbol)
                elif data_type == "options":
                    return await self._collect_options_data(symbol)
                elif data_type == "dividends":
                    return await self._collect_dividend_data(symbol)
                else:
                    raise DataCollectionError(f"Unknown data type: {data_type}")

            except Exception as e:
                logger.error(
                    f"Error collecting {data_type} data for {symbol}", error=str(e)
                )
                raise DataCollectionError(
                    f"Failed to collect {data_type} data: {str(e)}"
                )

    async def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate collected data quality and completeness.

        Args:
            data: Collected data to validate

        Returns:
            True if data is valid, False otherwise
        """
        try:
            if not data or not isinstance(data, dict):
                return False

            # Check for required metadata
            if "metadata" not in data:
                return False

            metadata = data["metadata"]
            required_metadata = ["source", "collection_time", "symbol", "data_type"]
            if not all(field in metadata for field in required_metadata):
                return False

            # Check data completeness
            if "data" not in data or not data["data"]:
                return False

            # Check for errors
            if "errors" in data and data["errors"]:
                return False

            # Data type specific validation
            data_type = metadata.get("data_type")
            if data_type == "profile":
                return self._validate_profile_data(data["data"])
            elif data_type == "financials":
                return self._validate_financial_data(data["data"])
            elif data_type == "market_data":
                return self._validate_market_data(data["data"])

            return True

        except Exception as e:
            logger.error(f"Data validation error: {str(e)}")
            return False

    async def transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform collected data into standard format.

        Args:
            data: Raw collected data

        Returns:
            Transformed data in standard format
        """
        try:
            data_type = data.get("metadata", {}).get("data_type", "unknown")

            if data_type == "profile":
                return self._transform_profile_data(data)
            elif data_type == "financials":
                return self._transform_financial_data(data)
            elif data_type == "market_data":
                return self._transform_market_data(data)
            elif data_type == "fundamentals":
                return self._transform_fundamentals_data(data)
            else:
                return data  # Return as-is if unknown type

        except Exception as e:
            logger.error(f"Data transformation error: {str(e)}")
            raise DataValidationError(f"Failed to transform data: {str(e)}")

    async def _collect_options_data(self, symbol: str) -> Dict[str, Any]:
        """Collect options data for a symbol."""
        try:
            ticker = yf.Ticker(symbol)
            options = ticker.options

            if not options:
                return {
                    "symbol": symbol,
                    "options_data": [],
                    "message": "No options data available",
                }

            # Get the nearest expiration date options
            nearest_expiry = options[0] if options else None
            if nearest_expiry:
                calls = ticker.option_chain(nearest_expiry).calls
                puts = ticker.option_chain(nearest_expiry).puts

                return {
                    "symbol": symbol,
                    "expiration_date": nearest_expiry,
                    "calls_count": len(calls) if calls is not None else 0,
                    "puts_count": len(puts) if puts is not None else 0,
                    "options_data": {
                        "calls": calls.to_dict("records") if calls is not None else [],
                        "puts": puts.to_dict("records") if puts is not None else [],
                    },
                }
            else:
                return {
                    "symbol": symbol,
                    "options_data": [],
                    "message": "No options expiration dates available",
                }

        except Exception as e:
            logger.error(f"Error collecting options data for {symbol}: {str(e)}")
            raise DataCollectionError(f"Failed to collect options data: {str(e)}")

    async def _collect_dividend_data(self, symbol: str) -> Dict[str, Any]:
        """Collect dividend data for a symbol."""
        try:
            ticker = yf.Ticker(symbol)
            dividends = ticker.dividends

            if dividends is None or dividends.empty:
                return {
                    "symbol": symbol,
                    "dividends_data": [],
                    "message": "No dividend data available",
                }

            # Convert to list of records
            dividends_list = dividends.reset_index().to_dict("records")

            return {
                "symbol": symbol,
                "dividends_count": len(dividends_list),
                "dividends_data": dividends_list,
                "total_dividends": (
                    float(dividends.sum()) if dividends.sum() is not None else 0.0
                ),
            }

        except Exception as e:
            logger.error(f"Error collecting dividend data for {symbol}: {str(e)}")
            raise DataCollectionError(f"Failed to collect dividend data: {str(e)}")

    async def _collect_company_profile(self, symbol: str) -> Dict[str, Any]:
        """Collect company profile information."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Extract key profile information
            profile_data = {
                "symbol": symbol,
                "company_name": info.get("longName", ""),
                "sector": info.get("sector", ""),
                "industry": info.get("industry", ""),
                "market_cap": info.get("marketCap", 0),
                "enterprise_value": info.get("enterpriseValue", 0),
                "pe_ratio": info.get("trailingPE", None),
                "forward_pe": info.get("forwardPE", None),
                "price_to_book": info.get("priceToBook", None),
                "price_to_sales": info.get("priceToSalesTrailing12Months", None),
                "dividend_yield": info.get("dividendYield", 0),
                "beta": info.get("beta", None),
                "fifty_two_week_high": info.get("fiftyTwoWeekHigh", None),
                "fifty_two_week_low": info.get("fiftyTwoWeekLow", None),
                "fifty_day_average": info.get("fiftyDayAverage", None),
                "two_hundred_day_average": info.get("twoHundredDayAverage", None),
                "volume": info.get("volume", 0),
                "avg_volume": info.get("averageVolume", 0),
                "currency": info.get("currency", "USD"),
                "exchange": info.get("exchange", ""),
                "country": info.get("country", ""),
                "website": info.get("website", ""),
                "business_summary": info.get("longBusinessSummary", ""),
                "employees": info.get("fullTimeEmployees", None),
                "founded_year": info.get("founded", None),
            }

            return {
                "metadata": {
                    "source": "yahoo_finance",
                    "collection_time": datetime.now().isoformat(),
                    "symbol": symbol,
                    "data_type": "profile",
                    "completeness": self._calculate_completeness(profile_data),
                },
                "data": profile_data,
                "errors": [],
            }

        except Exception as e:
            logger.error(f"Error collecting company profile for {symbol}", error=str(e))
            raise DataCollectionError(f"Failed to collect company profile: {str(e)}")

    async def _collect_financial_statements(self, symbol: str) -> Dict[str, Any]:
        """Collect financial statements (income, balance sheet, cash flow)."""
        try:
            ticker = yf.Ticker(symbol)

            # Collect financial statements
            income_stmt = ticker.income_stmt
            balance_sheet = ticker.balance_sheet
            cash_flow = ticker.cashflow

            financial_data = {
                "symbol": symbol,
                "income_statement": self._process_financial_statement(
                    income_stmt, "income"
                ),
                "balance_sheet": self._process_financial_statement(
                    balance_sheet, "balance"
                ),
                "cash_flow": self._process_financial_statement(cash_flow, "cash_flow"),
                "collection_date": datetime.now().isoformat(),
            }

            return {
                "metadata": {
                    "source": "yahoo_finance",
                    "collection_time": datetime.now().isoformat(),
                    "symbol": symbol,
                    "data_type": "financials",
                    "completeness": self._calculate_completeness(financial_data),
                },
                "data": financial_data,
                "errors": [],
            }

        except Exception as e:
            logger.error(
                f"Error collecting financial statements for {symbol}", error=str(e)
            )
            raise DataCollectionError(
                f"Failed to collect financial statements: {str(e)}"
            )

    async def _collect_market_data(
        self, symbol: str, period: str, interval: str
    ) -> Dict[str, Any]:
        """Collect historical market data."""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)

            if hist.empty:
                raise DataCollectionError(f"No historical data available for {symbol}")

            # Convert to standard format
            market_data = {
                "symbol": symbol,
                "period": period,
                "interval": interval,
                "data_points": len(hist),
                "start_date": hist.index[0].isoformat(),
                "end_date": hist.index[-1].isoformat(),
                "ohlcv_data": hist.to_dict("records"),
                "summary_stats": {
                    "open": hist["Open"].tolist(),
                    "high": hist["High"].tolist(),
                    "low": hist["Low"].tolist(),
                    "close": hist["Close"].tolist(),
                    "volume": hist["Volume"].tolist(),
                    "dates": [d.isoformat() for d in hist.index],
                },
            }

            return {
                "metadata": {
                    "source": "yahoo_finance",
                    "collection_time": datetime.now().isoformat(),
                    "symbol": symbol,
                    "data_type": "market_data",
                    "completeness": self._calculate_completeness(market_data),
                },
                "data": market_data,
                "errors": [],
            }

        except Exception as e:
            logger.error(f"Error collecting market data for {symbol}", error=str(e))
            raise DataCollectionError(f"Failed to collect market data: {str(e)}")

    async def _collect_fundamentals(self, symbol: str) -> Dict[str, Any]:
        """Collect fundamental analysis data."""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Extract fundamental metrics
            fundamentals = {
                "symbol": symbol,
                "valuation_metrics": {
                    "market_cap": info.get("marketCap", 0),
                    "enterprise_value": info.get("enterpriseValue", 0),
                    "pe_ratio": info.get("trailingPE", None),
                    "forward_pe": info.get("forwardPE", None),
                    "peg_ratio": info.get("pegRatio", None),
                    "price_to_book": info.get("priceToBook", None),
                    "price_to_sales": info.get("priceToSalesTrailing12Months", None),
                    "price_to_cash_flow": info.get("priceToCashflow", None),
                    "ev_to_ebitda": info.get("enterpriseToEbitda", None),
                    "ev_to_revenue": info.get("enterpriseToRevenue", None),
                },
                "profitability_metrics": {
                    "gross_margin": info.get("grossMargins", None),
                    "operating_margin": info.get("operatingMargins", None),
                    "net_margin": info.get("profitMargins", None),
                    "roa": info.get("returnOnAssets", None),
                    "roe": info.get("returnOnEquity", None),
                    "roic": info.get("returnOnInvestmentCapital", None),
                },
                "growth_metrics": {
                    "revenue_growth": info.get("revenueGrowth", None),
                    "earnings_growth": info.get("earningsGrowth", None),
                    "revenue_per_share": info.get("revenuePerShare", None),
                    "book_value_per_share": info.get("bookValue", None),
                    "cash_per_share": info.get("totalCashPerShare", None),
                },
            }

            return {
                "metadata": {
                    "source": "yahoo_finance",
                    "collection_time": datetime.now().isoformat(),
                    "symbol": symbol,
                    "data_type": "fundamentals",
                    "completeness": self._calculate_completeness(fundamentals),
                },
                "data": fundamentals,
                "errors": [],
            }

        except Exception as e:
            logger.error(f"Error collecting fundamentals for {symbol}", error=str(e))
            raise DataCollectionError(f"Failed to collect fundamentals: {str(e)}")

    def _process_financial_statement(
        self, statement: pd.DataFrame, stmt_type: str
    ) -> Dict[str, Any]:
        """Process financial statement DataFrame into standard format."""
        if statement is None or statement.empty:
            return {}

        try:
            # Convert to standard format
            processed_data = {
                "type": stmt_type,
                "periods": statement.columns.tolist(),
                "metrics": {},
            }

            for index, row in statement.iterrows():
                metric_name = str(index)
                values = row.tolist()
                processed_data["metrics"][metric_name] = values

            return processed_data

        except Exception as e:
            logger.error(f"Error processing {stmt_type} statement", error=str(e))
            return {}

    def _calculate_completeness(self, data: Dict[str, Any]) -> float:
        """Calculate data completeness score."""
        if not data:
            return 0.0

        total_fields = len(data)
        non_empty_fields = sum(1 for v in data.values() if v is not None and v != "")

        return non_empty_fields / total_fields if total_fields > 0 else 0.0

    def _validate_profile_data(self, data: Dict[str, Any]) -> bool:
        """Validate company profile data."""
        required_fields = ["symbol", "company_name", "sector", "market_cap"]
        return all(field in data and data[field] for field in required_fields)

    def _validate_financial_data(self, data: Dict[str, Any]) -> bool:
        """Validate financial statement data."""
        required_fields = ["income_statement", "balance_sheet", "cash_flow"]
        return all(field in data for field in required_fields)

    def _validate_market_data(self, data: Dict[str, Any]) -> bool:
        """Validate market data."""
        required_fields = ["symbol", "data_points", "ohlcv_data"]
        return all(field in data and data[field] for field in required_fields)

    def _transform_profile_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform profile data to standard format."""
        # Profile data is already in good format, just ensure consistency
        return data

    def _transform_financial_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform financial data to standard format."""
        # Financial data is already processed, just ensure consistency
        return data

    def _transform_market_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform market data to standard format."""
        # Market data is already processed, just ensure consistency
        return data

    def _transform_fundamentals_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform fundamentals data to standard format."""
        # Fundamentals data is already processed, just ensure consistency
        return data

    def _get_required_fields(self) -> List[str]:
        """Get list of required fields for this collector."""
        return ["symbol", "data_type", "collection_time"]

    async def collect_batch(
        self, symbols: List[str], data_type: str = "profile"
    ) -> Dict[str, Any]:
        """
        Collect data for multiple symbols in batch.

        Args:
            symbols: List of stock symbols
            data_type: Type of data to collect

        Returns:
            Dict containing batch collection results
        """
        results = {
            "metadata": {
                "source": "yahoo_finance",
                "collection_time": datetime.now().isoformat(),
                "data_type": data_type,
                "total_symbols": len(symbols),
                "batch_size": len(symbols),
            },
            "results": {},
            "errors": [],
            "summary": {"successful": 0, "failed": 0, "total_duration": 0.0},
        }

        start_time = datetime.now()

        # Process symbols with concurrency control
        tasks = []
        for symbol in symbols:
            task = self._collect_single_symbol(symbol, data_type)
            tasks.append(task)

        # Execute tasks with semaphore control
        completed_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for i, result in enumerate(completed_results):
            symbol = symbols[i]
            if isinstance(result, Exception):
                results["errors"].append({"symbol": symbol, "error": str(result)})
                results["summary"]["failed"] += 1
            else:
                results["results"][symbol] = result
                results["summary"]["successful"] += 1

        end_time = datetime.now()
        results["summary"]["total_duration"] = (end_time - start_time).total_seconds()

        return results

    async def _collect_single_symbol(
        self, symbol: str, data_type: str
    ) -> Dict[str, Any]:
        """Collect data for a single symbol."""
        async with self.semaphore:
            return await self.execute_collection(symbol=symbol, data_type=data_type)
