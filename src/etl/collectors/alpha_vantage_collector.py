"""
Alpha Vantage Data Collector - investByYourself
Tech-009: ETL Pipeline Implementation - Phase 1

This module implements an Alpha Vantage data collector with:
- Technical indicators and market data
- Economic indicators and fundamental data
- Alternative data and sentiment analysis
- Rate limiting and error handling
- Data validation and transformation
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode

import aiohttp
import pandas as pd
import structlog

from .base_collector import (BaseDataCollector, DataCollectionError,
                             DataValidationError, RateLimitConfig, RetryConfig)

logger = structlog.get_logger(__name__)


class AlphaVantageCollector(BaseDataCollector):
    """
    Alpha Vantage data collector with rate limiting and error handling.

    Features:
    - Technical indicators (SMA, EMA, RSI, MACD, etc.)
    - Fundamental data (earnings, income statements)
    - Economic indicators
    - Alternative data and sentiment
    - Real-time and historical data
    """

    def __init__(
        self,
        api_key: str,
        rate_limit_config: Optional[RateLimitConfig] = None,
        retry_config: Optional[RetryConfig] = None,
        session_timeout: int = 30,
        max_concurrent_requests: int = 3,  # Alpha Vantage has strict limits
    ):
        """Initialize Alpha Vantage collector."""
        # Alpha Vantage has strict rate limits (5 calls per minute for free tier)
        default_rate_limit = RateLimitConfig(
            max_requests_per_minute=5,  # Free tier limit
            max_requests_per_hour=300,
            max_requests_per_day=5000,
            burst_limit=2,
            cooldown_period=12.0,  # 12 seconds between requests
        )

        default_retry = RetryConfig(
            max_retries=3,
            base_delay=5.0,  # Longer delays for Alpha Vantage
            max_delay=60.0,
            exponential_backoff=True,
            retry_on_status_codes=[429, 500, 502, 503, 504],
        )

        super().__init__(
            name="alpha_vantage_collector",
            rate_limit_config=rate_limit_config or default_rate_limit,
            retry_config=retry_config or default_retry,
        )

        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        self.session_timeout = session_timeout
        self.max_concurrent_requests = max_concurrent_requests
        self.session: Optional[aiohttp.ClientSession] = None
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)

        # Data quality thresholds specific to Alpha Vantage
        self.quality_thresholds.update(
            {
                "min_records": 1,
                "max_failure_rate": 0.1,  # 10% - Alpha Vantage can be less reliable
                "min_data_completeness": 0.8,  # 80%
                "min_technical_accuracy": 0.95,  # 95% for technical indicators
            }
        )

        logger.info(
            "Alpha Vantage collector initialized",
            api_key_length=len(api_key) if api_key else 0,
            rate_limit_config=self.rate_limit_config,
            retry_config=self.retry_config,
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
            logger.info("Alpha Vantage collector session initialized")

    async def cleanup(self):
        """Clean up resources."""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("Alpha Vantage collector session closed")

    async def collect_data(self, **kwargs) -> Dict[str, Any]:
        """
        Collect data from Alpha Vantage based on parameters.

        Args:
            **kwargs: Collection parameters including:
                - symbol: Stock symbol (e.g., 'AAPL')
                - function: Alpha Vantage function (e.g., 'TIME_SERIES_DAILY')
                - data_type: Type of data to collect
                - interval: Data interval for time series

        Returns:
            Dict containing collected data and metadata
        """
        symbol = kwargs.get("symbol", "").upper()
        function = kwargs.get("function", "TIME_SERIES_DAILY")
        data_type = kwargs.get("data_type", "technical")
        interval = kwargs.get("interval", "daily")

        if not symbol:
            raise DataCollectionError("Symbol is required for data collection")

        async with self.semaphore:
            try:
                if function == "TIME_SERIES_DAILY":
                    return await self._collect_daily_time_series(symbol)
                elif function == "TIME_SERIES_INTRADAY":
                    return await self._collect_intraday_time_series(symbol, interval)
                elif function == "TECHNICAL_INDICATORS":
                    return await self._collect_technical_indicators(symbol, data_type)
                elif function == "FUNDAMENTAL_DATA":
                    return await self._collect_fundamental_data(symbol, data_type)
                elif function == "ECONOMIC_INDICATORS":
                    return await self._collect_economic_indicators(data_type)
                else:
                    return await self._collect_custom_function(
                        symbol, function, **kwargs
                    )

            except Exception as e:
                logger.error(
                    f"Error collecting {function} data for {symbol}", error=str(e)
                )
                raise DataCollectionError(
                    f"Failed to collect {function} data: {str(e)}"
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

            # Check for Alpha Vantage specific error messages
            if "Error Message" in data:
                return False

            if "Note" in data and "API call frequency" in data["Note"]:
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

            if data_type == "time_series":
                return self._transform_time_series_data(data)
            elif data_type == "technical_indicators":
                return self._transform_technical_data(data)
            elif data_type == "fundamental":
                return self._transform_fundamental_data(data)
            elif data_type == "economic":
                return self._transform_economic_data(data)
            else:
                return data  # Return as-is if unknown type

        except Exception as e:
            logger.error(f"Data transformation error: {str(e)}")
            raise DataValidationError(f"Failed to transform data: {str(e)}")

    async def _collect_daily_time_series(self, symbol: str) -> Dict[str, Any]:
        """Collect daily time series data."""
        try:
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "apikey": self.api_key,
                "outputsize": "compact",  # Last 100 data points
            }

            url = f"{self.base_url}?{urlencode(params)}"

            async with self.session.get(url) as response:
                if response.status != 200:
                    raise DataCollectionError(
                        f"HTTP {response.status}: {response.reason}"
                    )

                data = await response.json()

                if "Error Message" in data:
                    raise DataCollectionError(
                        f"Alpha Vantage error: {data['Error Message']}"
                    )

                if "Note" in data:
                    raise DataCollectionError(f"Alpha Vantage note: {data['Note']}")

                # Extract time series data
                time_series_key = "Time Series (Daily)"
                if time_series_key not in data:
                    raise DataCollectionError("No time series data found in response")

                time_series_data = data[time_series_key]

                # Transform to standard format
                transformed_data = []
                for date, values in time_series_data.items():
                    transformed_data.append(
                        {
                            "date": date,
                            "open": float(values["1. open"]),
                            "high": float(values["2. high"]),
                            "low": float(values["3. low"]),
                            "close": float(values["4. close"]),
                            "volume": int(values["5. volume"]),
                        }
                    )

                return {
                    "metadata": {
                        "source": "alpha_vantage",
                        "collection_time": datetime.now().isoformat(),
                        "symbol": symbol,
                        "data_type": "time_series",
                        "function": "TIME_SERIES_DAILY",
                        "completeness": self._calculate_completeness(transformed_data),
                    },
                    "data": {
                        "symbol": symbol,
                        "time_series": transformed_data,
                        "data_points": len(transformed_data),
                        "start_date": (
                            transformed_data[-1]["date"] if transformed_data else None
                        ),
                        "end_date": (
                            transformed_data[0]["date"] if transformed_data else None
                        ),
                    },
                    "errors": [],
                }

        except Exception as e:
            logger.error(
                f"Error collecting daily time series for {symbol}", error=str(e)
            )
            raise DataCollectionError(f"Failed to collect daily time series: {str(e)}")

    async def _collect_intraday_time_series(
        self, symbol: str, interval: str
    ) -> Dict[str, Any]:
        """Collect intraday time series data."""
        try:
            # Validate interval
            valid_intervals = ["1min", "5min", "15min", "30min", "60min"]
            if interval not in valid_intervals:
                raise DataCollectionError(
                    f"Invalid interval: {interval}. Must be one of {valid_intervals}"
                )

            params = {
                "function": "TIME_SERIES_INTRADAY",
                "symbol": symbol,
                "interval": interval,
                "apikey": self.api_key,
                "outputsize": "compact",
            }

            url = f"{self.base_url}?{urlencode(params)}"

            async with self.session.get(url) as response:
                if response.status != 200:
                    raise DataCollectionError(
                        f"HTTP {response.status}: {response.reason}"
                    )

                data = await response.json()

                if "Error Message" in data:
                    raise DataCollectionError(
                        f"Alpha Vantage error: {data['Error Message']}"
                    )

                # Extract time series data
                time_series_key = f"Time Series ({interval})"
                if time_series_key not in data:
                    raise DataCollectionError(f"No {interval} time series data found")

                time_series_data = data[time_series_key]

                # Transform to standard format
                transformed_data = []
                for datetime_str, values in time_series_data.items():
                    transformed_data.append(
                        {
                            "datetime": datetime_str,
                            "open": float(values["1. open"]),
                            "high": float(values["2. high"]),
                            "low": float(values["3. low"]),
                            "close": float(values["4. close"]),
                            "volume": int(values["5. volume"]),
                        }
                    )

                return {
                    "metadata": {
                        "source": "alpha_vantage",
                        "collection_time": datetime.now().isoformat(),
                        "symbol": symbol,
                        "data_type": "time_series",
                        "function": "TIME_SERIES_INTRADAY",
                        "interval": interval,
                        "completeness": self._calculate_completeness(transformed_data),
                    },
                    "data": {
                        "symbol": symbol,
                        "interval": interval,
                        "time_series": transformed_data,
                        "data_points": len(transformed_data),
                        "start_datetime": (
                            transformed_data[-1]["datetime"]
                            if transformed_data
                            else None
                        ),
                        "end_datetime": (
                            transformed_data[0]["datetime"]
                            if transformed_data
                            else None
                        ),
                    },
                    "errors": [],
                }

        except Exception as e:
            logger.error(
                f"Error collecting intraday time series for {symbol}", error=str(e)
            )
            raise DataCollectionError(
                f"Failed to collect intraday time series: {str(e)}"
            )

    async def _collect_technical_indicators(
        self, symbol: str, indicator_type: str
    ) -> Dict[str, Any]:
        """Collect technical indicators."""
        try:
            # Map indicator types to Alpha Vantage functions
            indicator_functions = {
                "sma": "SMA",
                "ema": "EMA",
                "rsi": "RSI",
                "macd": "MACD",
                "bbands": "BBANDS",
                "stoch": "STOCH",
                "adx": "ADX",
            }

            if indicator_type not in indicator_functions:
                raise DataCollectionError(f"Unknown indicator type: {indicator_type}")

            function = indicator_functions[indicator_type]

            # Basic parameters for technical indicators
            params = {
                "function": function,
                "symbol": symbol,
                "apikey": self.api_key,
                "interval": "daily",
                "time_period": "20",  # Default period
            }

            # Add indicator-specific parameters
            if function == "MACD":
                params.update(
                    {"fastperiod": "12", "slowperiod": "26", "signalperiod": "9"}
                )
            elif function == "BBANDS":
                params.update({"time_period": "20", "nbdevup": "2", "nbdevdn": "2"})

            url = f"{self.base_url}?{urlencode(params)}"

            async with self.session.get(url) as response:
                if response.status != 200:
                    raise DataCollectionError(
                        f"HTTP {response.status}: {response.reason}"
                    )

                data = await response.json()

                if "Error Message" in data:
                    raise DataCollectionError(
                        f"Alpha Vantage error: {data['Error Message']}"
                    )

                # Extract technical indicator data
                indicator_key = f"Technical Analysis: {function}"
                if indicator_key not in data:
                    raise DataCollectionError(f"No {function} data found")

                indicator_data = data[indicator_key]

                # Transform to standard format
                transformed_data = []
                for date, values in indicator_data.items():
                    transformed_data.append({"date": date, "values": values})

                return {
                    "metadata": {
                        "source": "alpha_vantage",
                        "collection_time": datetime.now().isoformat(),
                        "symbol": symbol,
                        "data_type": "technical_indicators",
                        "function": function,
                        "completeness": self._calculate_completeness(transformed_data),
                    },
                    "data": {
                        "symbol": symbol,
                        "indicator": function,
                        "indicator_data": transformed_data,
                        "data_points": len(transformed_data),
                        "start_date": (
                            transformed_data[-1]["date"] if transformed_data else None
                        ),
                        "end_date": (
                            transformed_data[0]["date"] if transformed_data else None
                        ),
                    },
                    "errors": [],
                }

        except Exception as e:
            logger.error(
                f"Error collecting technical indicators for {symbol}", error=str(e)
            )
            raise DataCollectionError(
                f"Failed to collect technical indicators: {str(e)}"
            )

    async def _collect_fundamental_data(
        self, symbol: str, data_type: str
    ) -> Dict[str, Any]:
        """Collect fundamental data."""
        try:
            # Map data types to Alpha Vantage functions
            fundamental_functions = {
                "earnings": "EARNINGS",
                "income_statement": "INCOME_STATEMENT",
                "balance_sheet": "BALANCE_SHEET",
                "cash_flow": "CASH_FLOW",
                "overview": "OVERVIEW",
            }

            if data_type not in fundamental_functions:
                raise DataCollectionError(f"Unknown fundamental data type: {data_type}")

            function = fundamental_functions[data_type]

            params = {"function": function, "symbol": symbol, "apikey": self.api_key}

            url = f"{self.base_url}?{urlencode(params)}"

            async with self.session.get(url) as response:
                if response.status != 200:
                    raise DataCollectionError(
                        f"HTTP {response.status}: {response.reason}"
                    )

                data = await response.json()

                if "Error Message" in data:
                    raise DataCollectionError(
                        f"Alpha Vantage error: {data['Error Message']}"
                    )

                return {
                    "metadata": {
                        "source": "alpha_vantage",
                        "collection_time": datetime.now().isoformat(),
                        "symbol": symbol,
                        "data_type": "fundamental",
                        "function": function,
                        "completeness": self._calculate_completeness(data),
                    },
                    "data": data,
                    "errors": [],
                }

        except Exception as e:
            logger.error(
                f"Error collecting fundamental data for {symbol}", error=str(e)
            )
            raise DataCollectionError(f"Failed to collect fundamental data: {str(e)}")

    async def _collect_economic_indicators(self, indicator_type: str) -> Dict[str, Any]:
        """Collect economic indicators."""
        try:
            # Map indicator types to Alpha Vantage functions
            economic_functions = {
                "real_gdp": "REAL_GDP",
                "real_gdp_per_capita": "REAL_GDP_PER_CAPITA",
                "treasury_yield": "TREASURY_YIELD",
                "federal_funds_rate": "FEDERAL_FUNDS_RATE",
                "cpi": "CPI",
                "inflation": "INFLATION",
                "retail_sales": "RETAIL_SALES",
                "durable_goods": "DURABLES",
                "unemployment": "UNEMPLOYMENT",
                "nonfarm_payroll": "NONFARM_PAYROLL",
            }

            if indicator_type not in economic_functions:
                raise DataCollectionError(
                    f"Unknown economic indicator: {indicator_type}"
                )

            function = economic_functions[indicator_type]

            params = {"function": function, "apikey": self.api_key}

            url = f"{self.base_url}?{urlencode(params)}"

            async with self.session.get(url) as response:
                if response.status != 200:
                    raise DataCollectionError(
                        f"HTTP {response.status}: {response.reason}"
                    )

                data = await response.json()

                if "Error Message" in data:
                    raise DataCollectionError(
                        f"Alpha Vantage error: {data['Error Message']}"
                    )

                return {
                    "metadata": {
                        "source": "alpha_vantage",
                        "collection_time": datetime.now().isoformat(),
                        "indicator": indicator_type,
                        "data_type": "economic",
                        "function": function,
                        "completeness": self._calculate_completeness(data),
                    },
                    "data": data,
                    "errors": [],
                }

        except Exception as e:
            logger.error(
                f"Error collecting economic indicator {indicator_type}", error=str(e)
            )
            raise DataCollectionError(f"Failed to collect economic indicator: {str(e)}")

    async def _collect_custom_function(
        self, symbol: str, function: str, **kwargs
    ) -> Dict[str, Any]:
        """Collect data using a custom Alpha Vantage function."""
        try:
            params = {"function": function, "symbol": symbol, "apikey": self.api_key}

            # Add any additional parameters
            params.update(kwargs)

            url = f"{self.base_url}?{urlencode(params)}"

            async with self.session.get(url) as response:
                if response.status != 200:
                    raise DataCollectionError(
                        f"HTTP {response.status}: {response.reason}"
                    )

                data = await response.json()

                if "Error Message" in data:
                    raise DataCollectionError(
                        f"Alpha Vantage error: {data['Error Message']}"
                    )

                return {
                    "metadata": {
                        "source": "alpha_vantage",
                        "collection_time": datetime.now().isoformat(),
                        "symbol": symbol,
                        "data_type": "custom",
                        "function": function,
                        "completeness": self._calculate_completeness(data),
                    },
                    "data": data,
                    "errors": [],
                }

        except Exception as e:
            logger.error(
                f"Error collecting custom function {function} for {symbol}",
                error=str(e),
            )
            raise DataCollectionError(
                f"Failed to collect custom function data: {str(e)}"
            )

    def _transform_time_series_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform time series data to standard format."""
        # Time series data is already processed, just ensure consistency
        return data

    def _transform_technical_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform technical indicator data to standard format."""
        # Technical data is already processed, just ensure consistency
        return data

    def _transform_fundamental_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform fundamental data to standard format."""
        # Fundamental data is already processed, just ensure consistency
        return data

    def _transform_economic_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform economic data to standard format."""
        # Economic data is already processed, just ensure consistency
        return data

    def _calculate_completeness(self, data: Any) -> float:
        """Calculate data completeness score."""
        if not data:
            return 0.0

        if isinstance(data, list):
            return 1.0 if len(data) > 0 else 0.0
        elif isinstance(data, dict):
            total_fields = len(data)
            non_empty_fields = sum(
                1 for v in data.values() if v is not None and v != ""
            )
            return non_empty_fields / total_fields if total_fields > 0 else 0.0
        else:
            return 1.0 if data else 0.0

    def _get_required_fields(self) -> List[str]:
        """Get list of required fields for this collector."""
        return ["symbol", "data_type", "collection_time", "function"]

    async def collect_batch(
        self, symbols: List[str], function: str, **kwargs
    ) -> Dict[str, Any]:
        """
        Collect data for multiple symbols in batch.

        Args:
            symbols: List of stock symbols
            function: Alpha Vantage function to call
            **kwargs: Additional parameters for the function

        Returns:
            Dict containing batch collection results
        """
        results = {
            "metadata": {
                "source": "alpha_vantage",
                "collection_time": datetime.now().isoformat(),
                "function": function,
                "total_symbols": len(symbols),
                "batch_size": len(symbols),
            },
            "results": {},
            "errors": [],
            "summary": {"successful": 0, "failed": 0, "total_duration": 0.0},
        }

        start_time = datetime.now()

        # Process symbols with concurrency control and rate limiting
        for symbol in symbols:
            try:
                # Add delay between requests to respect rate limits
                if len(results["results"]) > 0:
                    await asyncio.sleep(self.rate_limit_config.cooldown_period)

                result = await self.execute_collection(
                    symbol=symbol, function=function, **kwargs
                )
                results["results"][symbol] = result
                results["summary"]["successful"] += 1

            except Exception as e:
                results["errors"].append({"symbol": symbol, "error": str(e)})
                results["summary"]["failed"] += 1

        end_time = datetime.now()
        results["summary"]["total_duration"] = (end_time - start_time).total_seconds()

        return results
