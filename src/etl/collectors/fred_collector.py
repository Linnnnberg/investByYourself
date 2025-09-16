"""
FRED API Data Collector - investByYourself
Tech-009: ETL Pipeline Implementation - Phase 1

This module implements a FRED (Federal Reserve Economic Data) collector with:
- Economic indicators and macro data
- Interest rates and monetary policy data
- Employment and inflation data
- GDP and economic growth metrics
- Rate limiting and error handling
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

from .base_collector import (
    BaseDataCollector,
    DataCollectionError,
    DataValidationError,
    RateLimitConfig,
    RetryConfig,
)

logger = structlog.get_logger(__name__)


class FREDCollector(BaseDataCollector):
    """
    FRED API data collector with rate limiting and error handling.

    Features:
    - Economic indicators and macro data
    - Interest rates and monetary policy
    - Employment and inflation metrics
    - GDP and economic growth data
    - Historical time series data
    """

    def __init__(
        self,
        api_key: str,
        rate_limit_config: Optional[RateLimitConfig] = None,
        retry_config: Optional[RetryConfig] = None,
        session_timeout: int = 30,
        max_concurrent_requests: int = 2,  # FRED has strict limits
    ):
        """Initialize FRED collector."""
        # FRED has rate limits (120 calls per minute for free tier)
        default_rate_limit = RateLimitConfig(
            max_requests_per_minute=120,  # Free tier limit
            max_requests_per_hour=7200,
            max_requests_per_day=100000,
            burst_limit=5,
            cooldown_period=0.5,  # 0.5 seconds between requests
        )

        default_retry = RetryConfig(
            max_retries=3,
            base_delay=2.0,
            max_delay=30.0,
            exponential_backoff=True,
            retry_on_status_codes=[429, 500, 502, 503, 504],
        )

        super().__init__(
            name="fred_collector",
            rate_limit_config=rate_limit_config or default_rate_limit,
            retry_config=retry_config or default_retry,
        )

        self.api_key = api_key
        self.base_url = "https://api.stlouisfed.org/fred"
        self.session_timeout = session_timeout
        self.max_concurrent_requests = max_concurrent_requests
        self.session: Optional[aiohttp.ClientSession] = None
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)

        # Data quality thresholds specific to FRED
        self.quality_thresholds.update(
            {
                "min_records": 1,
                "max_failure_rate": 0.05,  # 5% - FRED is very reliable
                "min_data_completeness": 0.9,  # 90%
                "min_economic_accuracy": 0.99,  # 99% for economic data
            }
        )

        # Common FRED series IDs
        self.common_series = {
            "gdp": "GDP",
            "unemployment_rate": "UNRATE",
            "inflation_cpi": "CPIAUCSL",
            "federal_funds_rate": "FEDFUNDS",
            "treasury_10y": "GS10",
            "treasury_2y": "GS2",
            "treasury_3m": "GS3M",
            "real_gdp": "GDPC1",
            "personal_consumption": "PCE",
            "retail_sales": "RSAFS",
            "industrial_production": "INDPRO",
            "housing_starts": "HOUST",
            "consumer_confidence": "UMCSENT",
            "manufacturing_pmi": "NAPM",
            "trade_balance": "BOPGSTB",
        }

        logger.info(
            "FRED collector initialized",
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
            logger.info("FRED collector session initialized")

    async def cleanup(self):
        """Clean up resources."""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("FRED collector session closed")

    async def collect_data(self, **kwargs) -> Dict[str, Any]:
        """
        Collect data from FRED based on parameters.

        Args:
            **kwargs: Collection parameters including:
                - series_id: FRED series ID (e.g., 'GDP')
                - data_type: Type of data to collect
                - observation_start: Start date for observations
                - observation_end: End date for observations
                - frequency: Data frequency (daily, monthly, quarterly)

        Returns:
            Dict containing collected data and metadata
        """
        series_id = kwargs.get("series_id", "").upper()
        data_type = kwargs.get("data_type", "observations")
        observation_start = kwargs.get("observation_start")
        observation_end = kwargs.get("observation_end")
        frequency = kwargs.get("frequency", "monthly")

        if not series_id:
            raise DataCollectionError("Series ID is required for data collection")

        async with self.semaphore:
            try:
                if data_type == "observations":
                    return await self._collect_series_observations(
                        series_id, observation_start, observation_end, frequency
                    )
                elif data_type == "series_info":
                    return await self._collect_series_info(series_id)
                elif data_type == "category":
                    return await self._collect_category_data(series_id)
                elif data_type == "search":
                    return await self._search_series(kwargs.get("search_text", ""))
                else:
                    raise DataCollectionError(f"Unknown data type: {data_type}")

            except Exception as e:
                logger.error(
                    f"Error collecting {data_type} data for {series_id}", error=str(e)
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

            # Check for FRED specific error messages
            if "error_code" in data:
                return False

            if "error_message" in data:
                return False

            # Check for required metadata
            if "metadata" not in data:
                return False

            metadata = data["metadata"]
            required_metadata = ["source", "collection_time", "series_id", "data_type"]
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

            if data_type == "observations":
                return self._transform_observations_data(data)
            elif data_type == "series_info":
                return self._transform_series_info_data(data)
            elif data_type == "category":
                return self._transform_category_data(data)
            elif data_type == "search":
                return self._transform_search_data(data)
            else:
                return data  # Return as-is if unknown type

        except Exception as e:
            logger.error(f"Data transformation error: {str(e)}")
            raise DataValidationError(f"Failed to transform data: {str(e)}")

    async def _collect_series_observations(
        self,
        series_id: str,
        observation_start: Optional[str] = None,
        observation_end: Optional[str] = None,
        frequency: str = "monthly",
    ) -> Dict[str, Any]:
        """Collect time series observations for a FRED series."""
        try:
            params = {
                "series_id": series_id,
                "api_key": self.api_key,
                "file_type": "json",
            }

            # Add optional parameters
            if observation_start:
                params["observation_start"] = observation_start
            if observation_end:
                params["observation_end"] = observation_end

            # Add frequency parameter
            if frequency != "monthly":
                params["frequency"] = frequency

            url = f"{self.base_url}/series/observations?{urlencode(params)}"

            async with self.session.get(url) as response:
                if response.status != 200:
                    raise DataCollectionError(
                        f"HTTP {response.status}: {response.reason}"
                    )

                data = await response.json()

                # Check for FRED API errors
                if "error_code" in data:
                    raise DataCollectionError(
                        f"FRED API error {data['error_code']}: {data.get('error_message', 'Unknown error')}"
                    )

                if "observations" not in data:
                    raise DataCollectionError("No observations data found in response")

                observations = data["observations"]

                # Transform to standard format
                transformed_data = []
                for obs in observations:
                    if (
                        obs["value"] != "." and obs["value"] != ""
                    ):  # Skip missing values
                        transformed_data.append(
                            {
                                "date": obs["date"],
                                "value": float(obs["value"]),
                                "realtime_start": obs.get("realtime_start"),
                                "realtime_end": obs.get("realtime_end"),
                            }
                        )

                return {
                    "metadata": {
                        "source": "fred",
                        "collection_time": datetime.now().isoformat(),
                        "series_id": series_id,
                        "data_type": "observations",
                        "frequency": frequency,
                        "observation_start": observation_start,
                        "observation_end": observation_end,
                        "completeness": self._calculate_completeness(transformed_data),
                    },
                    "data": {
                        "series_id": series_id,
                        "observations": transformed_data,
                        "data_points": len(transformed_data),
                        "start_date": (
                            transformed_data[-1]["date"] if transformed_data else None
                        ),
                        "end_date": (
                            transformed_data[0]["date"] if transformed_data else None
                        ),
                        "frequency": frequency,
                    },
                    "errors": [],
                }

        except Exception as e:
            logger.error(f"Error collecting observations for {series_id}", error=str(e))
            raise DataCollectionError(f"Failed to collect observations: {str(e)}")

    async def _collect_series_info(self, series_id: str) -> Dict[str, Any]:
        """Collect metadata and information about a FRED series."""
        try:
            params = {
                "series_id": series_id,
                "api_key": self.api_key,
                "file_type": "json",
            }

            url = f"{self.base_url}/series?{urlencode(params)}"

            async with self.session.get(url) as response:
                if response.status != 200:
                    raise DataCollectionError(
                        f"HTTP {response.status}: {response.reason}"
                    )

                data = await response.json()

                # Check for FRED API errors
                if "error_code" in data:
                    raise DataCollectionError(
                        f"FRED API error {data['error_code']}: {data.get('error_message', 'Unknown error')}"
                    )

                if "seriess" not in data or not data["seriess"]:
                    raise DataCollectionError("No series information found")

                series_info = data["seriess"][0]

                return {
                    "metadata": {
                        "source": "fred",
                        "collection_time": datetime.now().isoformat(),
                        "series_id": series_id,
                        "data_type": "series_info",
                        "completeness": self._calculate_completeness(series_info),
                    },
                    "data": {
                        "series_id": series_id,
                        "title": series_info.get("title", ""),
                        "notes": series_info.get("notes", ""),
                        "units": series_info.get("units", ""),
                        "frequency": series_info.get("frequency", ""),
                        "seasonal_adjustment": series_info.get(
                            "seasonal_adjustment", ""
                        ),
                        "last_updated": series_info.get("last_updated", ""),
                        "popularity": series_info.get("popularity", 0),
                        "group_popularity": series_info.get("group_popularity", 0),
                        "observation_start": series_info.get("observation_start", ""),
                        "observation_end": series_info.get("observation_end", ""),
                    },
                    "errors": [],
                }

        except Exception as e:
            logger.error(f"Error collecting series info for {series_id}", error=str(e))
            raise DataCollectionError(f"Failed to collect series info: {str(e)}")

    async def _collect_category_data(self, category_id: str) -> Dict[str, Any]:
        """Collect data for a FRED category."""
        try:
            params = {
                "category_id": category_id,
                "api_key": self.api_key,
                "file_type": "json",
            }

            url = f"{self.base_url}/category?{urlencode(params)}"

            async with self.session.get(url) as response:
                if response.status != 200:
                    raise DataCollectionError(
                        f"HTTP {response.status}: {response.reason}"
                    )

                data = await response.json()

                # Check for FRED API errors
                if "error_code" in data:
                    raise DataCollectionError(
                        f"FRED API error {data['error_code']}: {data.get('error_message', 'Unknown error')}"
                    )

                if "categories" not in data or not data["categories"]:
                    raise DataCollectionError("No category information found")

                category_info = data["categories"][0]

                return {
                    "metadata": {
                        "source": "fred",
                        "collection_time": datetime.now().isoformat(),
                        "category_id": category_id,
                        "data_type": "category",
                        "completeness": self._calculate_completeness(category_info),
                    },
                    "data": {
                        "category_id": category_id,
                        "name": category_info.get("name", ""),
                        "parent_id": category_info.get("parent_id"),
                        "notes": category_info.get("notes", ""),
                    },
                    "errors": [],
                }

        except Exception as e:
            logger.error(
                f"Error collecting category data for {category_id}", error=str(e)
            )
            raise DataCollectionError(f"Failed to collect category data: {str(e)}")

    async def _search_series(self, search_text: str) -> Dict[str, Any]:
        """Search for FRED series by text."""
        try:
            if not search_text:
                raise DataCollectionError("Search text is required")

            params = {
                "search_text": search_text,
                "api_key": self.api_key,
                "file_type": "json",
                "limit": 100,  # Limit results
            }

            url = f"{self.base_url}/series/search?{urlencode(params)}"

            async with self.session.get(url) as response:
                if response.status != 200:
                    raise DataCollectionError(
                        f"HTTP {response.status}: {response.reason}"
                    )

                data = await response.json()

                # Check for FRED API errors
                if "error_code" in data:
                    raise DataCollectionError(
                        f"FRED API error {data['error_code']}: {data.get('error_message', 'Unknown error')}"
                    )

                if "seriess" not in data:
                    raise DataCollectionError("No search results found")

                search_results = data["seriess"]

                # Transform to standard format
                transformed_results = []
                for series in search_results:
                    transformed_results.append(
                        {
                            "series_id": series.get("id", ""),
                            "title": series.get("title", ""),
                            "units": series.get("units", ""),
                            "frequency": series.get("frequency", ""),
                            "seasonal_adjustment": series.get(
                                "seasonal_adjustment", ""
                            ),
                            "last_updated": series.get("last_updated", ""),
                            "observation_start": series.get("observation_start", ""),
                            "observation_end": series.get("observation_end", ""),
                        }
                    )

                return {
                    "metadata": {
                        "source": "fred",
                        "collection_time": datetime.now().isoformat(),
                        "search_text": search_text,
                        "data_type": "search",
                        "total_results": len(transformed_results),
                        "completeness": self._calculate_completeness(
                            transformed_results
                        ),
                    },
                    "data": {
                        "search_text": search_text,
                        "results": transformed_results,
                        "total_results": len(transformed_results),
                    },
                    "errors": [],
                }

        except Exception as e:
            logger.error(
                f"Error searching for series with text: {search_text}", error=str(e)
            )
            raise DataCollectionError(f"Failed to search series: {str(e)}")

    def _transform_observations_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform observations data to standard format."""
        # Observations data is already processed, just ensure consistency
        return data

    def _transform_series_info_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform series info data to standard format."""
        # Series info data is already processed, just ensure consistency
        return data

    def _transform_category_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform category data to standard format."""
        # Category data is already processed, just ensure consistency
        return data

    def _transform_search_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform search data to standard format."""
        # Search data is already processed, just ensure consistency
        return data

    def _calculate_completeness(self, data: Any) -> float:
        """Calculate data completeness score."""
        if not data:
            return 0.0

        if isinstance(data, list):
            if len(data) == 0:
                return 0.0
            # Calculate completeness based on non-empty values in each item
            total_fields = 0
            non_empty_fields = 0
            for item in data:
                if isinstance(item, dict):
                    total_fields += len(item)
                    non_empty_fields += sum(
                        1 for v in item.values() if v is not None and v != ""
                    )
            return non_empty_fields / total_fields if total_fields > 0 else 0.0
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
        return ["series_id", "data_type", "collection_time"]

    async def collect_common_indicators(
        self, indicators: List[str] = None
    ) -> Dict[str, Any]:
        """
        Collect data for common economic indicators.

        Args:
            indicators: List of indicator names to collect (default: all common ones)

        Returns:
            Dict containing collection results for all indicators
        """
        if indicators is None:
            indicators = list(self.common_series.keys())

        results = {
            "metadata": {
                "source": "fred",
                "collection_time": datetime.now().isoformat(),
                "data_type": "common_indicators",
                "total_indicators": len(indicators),
                "batch_size": len(indicators),
            },
            "results": {},
            "errors": [],
            "summary": {"successful": 0, "failed": 0, "total_duration": 0.0},
        }

        start_time = datetime.now()

        # Process indicators with concurrency control and rate limiting
        for indicator in indicators:
            try:
                if indicator not in self.common_series:
                    results["errors"].append(
                        {
                            "indicator": indicator,
                            "error": f"Unknown indicator: {indicator}",
                        }
                    )
                    results["summary"]["failed"] += 1
                    continue

                series_id = self.common_series[indicator]

                # Add delay between requests to respect rate limits
                if len(results["results"]) > 0:
                    await asyncio.sleep(self.rate_limit_config.cooldown_period)

                # Collect both series info and recent observations
                series_info = await self.execute_collection(
                    series_id=series_id, data_type="series_info"
                )

                observations = await self.execute_collection(
                    series_id=series_id,
                    data_type="observations",
                    observation_start=(datetime.now() - timedelta(days=365)).strftime(
                        "%Y-%m-%d"
                    ),
                )

                results["results"][indicator] = {
                    "series_info": series_info,
                    "observations": observations,
                }
                results["summary"]["successful"] += 1

            except Exception as e:
                results["errors"].append({"indicator": indicator, "error": str(e)})
                results["summary"]["failed"] += 1

        end_time = datetime.now()
        results["summary"]["total_duration"] = (end_time - start_time).total_seconds()

        return results

    async def collect_batch(
        self, series_ids: List[str], data_type: str = "observations", **kwargs
    ) -> Dict[str, Any]:
        """
        Collect data for multiple series IDs in batch.

        Args:
            series_ids: List of FRED series IDs
            data_type: Type of data to collect
            **kwargs: Additional parameters for collection

        Returns:
            Dict containing batch collection results
        """
        results = {
            "metadata": {
                "source": "fred",
                "collection_time": datetime.now().isoformat(),
                "data_type": data_type,
                "total_series": len(series_ids),
                "batch_size": len(series_ids),
            },
            "results": {},
            "errors": [],
            "summary": {"successful": 0, "failed": 0, "total_duration": 0.0},
        }

        start_time = datetime.now()

        # Process series with concurrency control and rate limiting
        for series_id in series_ids:
            try:
                # Add delay between requests to respect rate limits
                if len(results["results"]) > 0:
                    await asyncio.sleep(self.rate_limit_config.cooldown_period)

                result = await self.execute_collection(
                    series_id=series_id, data_type=data_type, **kwargs
                )
                results["results"][series_id] = result
                results["summary"]["successful"] += 1

            except Exception as e:
                results["errors"].append({"series_id": series_id, "error": str(e)})
                results["summary"]["failed"] += 1

        end_time = datetime.now()
        results["summary"]["total_duration"] = (end_time - start_time).total_seconds()

        return results
