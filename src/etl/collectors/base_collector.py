"""
Abstract Base Classes for Data Collectors - investByYourself
Tech-009: ETL Pipeline Implementation - Phase 1

This module provides abstract base classes for implementing data collectors
with rate limiting, retry mechanisms, and data quality monitoring.
"""

import abc
import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import structlog

logger = structlog.get_logger(__name__)


class DataQualityLevel(Enum):
    """Data quality levels for monitoring and alerting."""

    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    FAILED = "failed"


@dataclass
class CollectionMetrics:
    """Metrics for data collection monitoring."""

    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    records_collected: int = 0
    records_failed: int = 0
    api_calls: int = 0
    rate_limit_hits: int = 0
    retry_attempts: int = 0
    total_duration: float = 0.0
    data_quality_score: float = 0.0
    errors: List[str] = field(default_factory=list)

    def finalize(self):
        """Finalize metrics calculation."""
        self.end_time = datetime.now()
        self.total_duration = (self.end_time - self.start_time).total_seconds()

    @property
    def success_rate(self) -> float:
        """Calculate success rate of data collection."""
        total = self.records_collected + self.records_failed
        return (self.records_collected / total * 100) if total > 0 else 0.0


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""

    max_requests_per_minute: int = 60
    max_requests_per_hour: int = 1000
    max_requests_per_day: int = 10000
    burst_limit: int = 10
    cooldown_period: float = 1.0  # seconds


@dataclass
class RetryConfig:
    """Configuration for retry mechanisms."""

    max_retries: int = 3
    base_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    exponential_backoff: bool = True
    retry_on_status_codes: List[int] = field(
        default_factory=lambda: [429, 500, 502, 503, 504]
    )


class BaseDataCollector(abc.ABC):
    """
    Abstract base class for data collectors.

    Provides common functionality for:
    - Rate limiting and API quota management
    - Retry mechanisms with exponential backoff
    - Data quality monitoring and validation
    - Error handling and logging
    - Metrics collection and reporting
    """

    def __init__(
        self,
        name: str,
        rate_limit_config: Optional[RateLimitConfig] = None,
        retry_config: Optional[RetryConfig] = None,
        enable_logging: bool = True,
    ):
        """Initialize the base collector."""
        self.name = name
        self.rate_limit_config = rate_limit_config or RateLimitConfig()
        self.retry_config = retry_config or RetryConfig()
        self.enable_logging = enable_logging

        # Rate limiting state
        self.request_timestamps: List[float] = []
        self.last_request_time: float = 0.0

        # Metrics and monitoring
        self.collection_metrics = CollectionMetrics()
        self.total_metrics = CollectionMetrics()

        # Data quality thresholds
        self.quality_thresholds = {
            "min_records": 1,
            "max_failure_rate": 0.1,  # 10%
            "min_data_completeness": 0.8,  # 80%
        }

        logger.info(
            f"Initialized {self.name} collector",
            rate_limit_config=self.rate_limit_config,
            retry_config=self.retry_config,
        )

    @abc.abstractmethod
    async def collect_data(self, **kwargs) -> Dict[str, Any]:
        """
        Abstract method for collecting data from the source.

        Args:
            **kwargs: Source-specific parameters for data collection

        Returns:
            Dict containing collected data and metadata
        """
        pass

    @abc.abstractmethod
    async def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Abstract method for validating collected data.

        Args:
            data: Collected data to validate

        Returns:
            True if data is valid, False otherwise
        """
        pass

    @abc.abstractmethod
    async def transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Abstract method for transforming collected data into standard format.

        Args:
            data: Raw collected data

        Returns:
            Transformed data in standard format
        """
        pass

    async def execute_collection(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the complete data collection process with monitoring.

        Args:
            **kwargs: Parameters for data collection

        Returns:
            Collected and processed data
        """
        self.collection_metrics = CollectionMetrics()

        try:
            logger.info(f"Starting data collection for {self.name}", **kwargs)

            # Check rate limits
            await self._check_rate_limits()

            # Collect data with retry mechanism
            raw_data = await self._collect_with_retry(**kwargs)

            # Validate data
            if not await self.validate_data(raw_data):
                raise ValueError(f"Data validation failed for {self.name}")

            # Transform data
            transformed_data = await self.transform_data(raw_data)

            # Update metrics
            self.collection_metrics.records_collected = self._count_records(
                transformed_data
            )
            self.collection_metrics.data_quality_score = self._calculate_quality_score(
                transformed_data
            )

            logger.info(
                f"Data collection completed for {self.name}",
                records_collected=self.collection_metrics.records_collected,
                quality_score=self.collection_metrics.data_quality_score,
            )

            return transformed_data

        except Exception as e:
            self.collection_metrics.records_failed += 1
            self.collection_metrics.errors.append(str(e))
            logger.error(f"Data collection failed for {self.name}", error=str(e))
            raise
        finally:
            self.collection_metrics.finalize()
            self._update_total_metrics()

    async def _check_rate_limits(self):
        """Check and enforce rate limits."""
        current_time = time.time()

        # Clean old timestamps
        cutoff_time = current_time - 3600  # 1 hour
        self.request_timestamps = [
            ts for ts in self.request_timestamps if ts > cutoff_time
        ]

        # Check minute limit
        minute_cutoff = current_time - 60
        minute_requests = len(
            [ts for ts in self.request_timestamps if ts > minute_cutoff]
        )

        if minute_requests >= self.rate_limit_config.max_requests_per_minute:
            wait_time = 60 - (current_time - self.request_timestamps[0])
            logger.warning(
                f"Rate limit hit for {self.name}, waiting {wait_time:.2f} seconds"
            )
            await asyncio.sleep(wait_time)
            self.collection_metrics.rate_limit_hits += 1

        # Check hour limit
        hour_requests = len(self.request_timestamps)
        if hour_requests >= self.rate_limit_config.max_requests_per_hour:
            wait_time = 3600 - (current_time - self.request_timestamps[0])
            logger.warning(
                f"Hourly rate limit hit for {self.name}, waiting {wait_time:.2f} seconds"
            )
            await asyncio.sleep(wait_time)
            self.collection_metrics.rate_limit_hits += 1

        # Add current request timestamp
        self.request_timestamps.append(current_time)
        self.last_request_time = current_time

    async def _collect_with_retry(self, **kwargs) -> Dict[str, Any]:
        """Collect data with retry mechanism."""
        last_exception = None

        for attempt in range(self.retry_config.max_retries + 1):
            try:
                self.collection_metrics.api_calls += 1
                return await self.collect_data(**kwargs)

            except Exception as e:
                last_exception = e
                self.collection_metrics.retry_attempts += 1

                if attempt < self.retry_config.max_retries:
                    delay = self._calculate_retry_delay(attempt)
                    logger.warning(
                        f"Collection attempt {attempt + 1} failed for {self.name}, "
                        f"retrying in {delay:.2f} seconds",
                        error=str(e),
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"All retry attempts failed for {self.name}", error=str(e)
                    )

        raise last_exception

    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempts."""
        if self.retry_config.exponential_backoff:
            delay = self.retry_config.base_delay * (2**attempt)
        else:
            delay = self.retry_config.base_delay * (attempt + 1)

        return min(delay, self.retry_config.max_delay)

    def _count_records(self, data: Dict[str, Any]) -> int:
        """Count the number of records in collected data."""
        if isinstance(data, dict):
            if "records" in data:
                return len(data["records"])
            elif "data" in data:
                return len(data["data"])
            elif "results" in data:
                return len(data["results"])
            else:
                return 1
        elif isinstance(data, list):
            return len(data)
        else:
            return 1

    def _calculate_quality_score(self, data: Dict[str, Any]) -> float:
        """Calculate data quality score based on various factors."""
        score = 1.0

        # Check data completeness
        if "metadata" in data and "completeness" in data["metadata"]:
            score *= data["metadata"]["completeness"]

        # Check for required fields
        required_fields = self._get_required_fields()
        if required_fields:
            present_fields = sum(1 for field in required_fields if field in data)
            score *= present_fields / len(required_fields)

        # Penalize for errors
        if self.collection_metrics.errors:
            score *= 0.8

        return max(0.0, min(1.0, score))

    def _get_required_fields(self) -> List[str]:
        """Get list of required fields for this collector."""
        return []

    def _update_total_metrics(self):
        """Update total metrics with current collection metrics."""
        self.total_metrics.records_collected += (
            self.collection_metrics.records_collected
        )
        self.total_metrics.records_failed += self.collection_metrics.records_failed
        self.total_metrics.api_calls += self.collection_metrics.api_calls
        self.total_metrics.rate_limit_hits += self.collection_metrics.rate_limit_hits
        self.total_metrics.retry_attempts += self.collection_metrics.retry_attempts
        self.total_metrics.errors.extend(self.collection_metrics.errors)

    def get_metrics(self) -> Dict[str, Any]:
        """Get current collection metrics."""
        return {
            "collector_name": self.name,
            "current_collection": {
                "start_time": self.collection_metrics.start_time.isoformat(),
                "end_time": (
                    self.collection_metrics.end_time.isoformat()
                    if self.collection_metrics.end_time
                    else None
                ),
                "records_collected": self.collection_metrics.records_collected,
                "records_failed": self.collection_metrics.records_failed,
                "success_rate": self.collection_metrics.success_rate,
                "api_calls": self.collection_metrics.api_calls,
                "rate_limit_hits": self.collection_metrics.rate_limit_hits,
                "retry_attempts": self.collection_metrics.retry_attempts,
                "total_duration": self.collection_metrics.total_duration,
                "data_quality_score": self.collection_metrics.data_quality_score,
                "errors": self.collection_metrics.errors,
            },
            "total_metrics": {
                "records_collected": self.total_metrics.records_collected,
                "records_failed": self.total_metrics.records_failed,
                "api_calls": self.total_metrics.api_calls,
                "rate_limit_hits": self.total_metrics.rate_limit_hits,
                "retry_attempts": self.total_metrics.retry_attempts,
                "total_errors": len(self.total_metrics.errors),
            },
        }

    def reset_metrics(self):
        """Reset all metrics."""
        self.collection_metrics = CollectionMetrics()
        self.total_metrics = CollectionMetrics()
        logger.info(f"Metrics reset for {self.name}")


class DataCollectionError(Exception):
    """Custom exception for data collection errors."""

    pass


class RateLimitExceededError(DataCollectionError):
    """Exception raised when rate limits are exceeded."""

    pass


class DataValidationError(DataCollectionError):
    """Exception raised when data validation fails."""

    pass
