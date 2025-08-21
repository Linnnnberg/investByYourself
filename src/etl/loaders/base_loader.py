"""
Base Data Loader - Abstract foundation for all data loading operations

This module provides the abstract base class and core data structures for implementing
various data loading strategies in the investByYourself ETL pipeline.

Key Features:
- Abstract interface for consistent loader implementations
- Incremental loading strategies (INSERT, UPDATE, UPSERT)
- Data versioning and change tracking
- Loading metrics and performance monitoring
- Error handling and validation
- Configurable batch processing

Author: investByYourself Development Team
Created: August 2025
Phase: Tech-009 Phase 3 - Data Loading & Storage
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

import structlog

# Configure structured logging
logger = structlog.get_logger(__name__)


class LoadingStrategy(Enum):
    """Enumeration of available data loading strategies."""

    INSERT_ONLY = "insert_only"  # Only insert new records
    UPDATE_ONLY = "update_only"  # Only update existing records
    UPSERT = "upsert"  # Insert new, update existing
    REPLACE = "replace"  # Replace entire dataset
    APPEND = "append"  # Append to existing data
    INCREMENTAL = "incremental"  # Load only changed data


class LoadingError(Exception):
    """Base exception for data loading operations."""

    pass


class ValidationError(LoadingError):
    """Exception raised when data validation fails."""

    pass


class StorageError(LoadingError):
    """Exception raised when storage operations fail."""

    pass


@dataclass
class DataVersion:
    """Data version tracking for change management."""

    version_id: str
    timestamp: datetime
    checksum: str
    record_count: int
    schema_version: str
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LoadingMetrics:
    """Metrics for tracking loading performance and quality."""

    # Performance metrics
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0

    # Data metrics
    records_processed: int = 0
    records_inserted: int = 0
    records_updated: int = 0
    records_skipped: int = 0
    records_failed: int = 0

    # Storage metrics
    bytes_processed: int = 0
    compression_ratio: float = 1.0

    # Quality metrics
    validation_errors: int = 0
    duplicate_records: int = 0
    data_quality_score: float = 0.0

    # System metrics
    memory_peak_mb: float = 0.0
    cpu_usage_percent: float = 0.0

    def calculate_throughput(self) -> float:
        """Calculate records per second throughput."""
        if self.duration_seconds > 0:
            return self.records_processed / self.duration_seconds
        return 0.0

    def calculate_success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.records_processed > 0:
            successful = self.records_processed - self.records_failed
            return (successful / self.records_processed) * 100
        return 0.0


@dataclass
class LoadingResult:
    """Result of a data loading operation."""

    success: bool
    metrics: LoadingMetrics
    data_version: Optional[DataVersion] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_error(self, error: str) -> None:
        """Add an error message to the result."""
        self.errors.append(error)
        self.success = False

    def add_warning(self, warning: str) -> None:
        """Add a warning message to the result."""
        self.warnings.append(warning)


class BaseDataLoader(ABC):
    """
    Abstract base class for all data loaders.

    Provides common functionality for data loading operations including:
    - Connection management
    - Batch processing
    - Error handling
    - Metrics collection
    - Data validation
    """

    def __init__(
        self,
        loader_id: str,
        batch_size: int = 1000,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        enable_versioning: bool = True,
        enable_compression: bool = False,
    ):
        """
        Initialize the base data loader.

        Args:
            loader_id: Unique identifier for this loader instance
            batch_size: Number of records to process in each batch
            max_retries: Maximum number of retry attempts for failed operations
            retry_delay: Delay in seconds between retry attempts
            enable_versioning: Whether to track data versions
            enable_compression: Whether to enable data compression
        """
        self.loader_id = loader_id
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.enable_versioning = enable_versioning
        self.enable_compression = enable_compression

        # State tracking
        self.is_connected = False
        self.current_transaction = None
        self.metrics = LoadingMetrics(start_time=datetime.now())

        # Validation functions
        self.validators: List[Callable[[Any], bool]] = []

        # Logger
        self.logger = logger.bind(loader_id=loader_id)

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the data store."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to the data store."""
        pass

    @abstractmethod
    async def load_data(
        self,
        data: Union[List[Dict[str, Any]], Dict[str, Any]],
        strategy: LoadingStrategy = LoadingStrategy.UPSERT,
        target_table: Optional[str] = None,
        **kwargs,
    ) -> LoadingResult:
        """
        Load data using the specified strategy.

        Args:
            data: Data to load (list of records or single record)
            strategy: Loading strategy to use
            target_table: Target table/collection name
            **kwargs: Additional loader-specific parameters

        Returns:
            LoadingResult with metrics and status
        """
        pass

    @abstractmethod
    async def get_data_version(self, target: str) -> Optional[DataVersion]:
        """Get the current data version for a target."""
        pass

    @abstractmethod
    async def create_data_version(
        self,
        target: str,
        record_count: int,
        checksum: str,
        metadata: Dict[str, Any] = None,
    ) -> DataVersion:
        """Create a new data version entry."""
        pass

    async def validate_data(self, data: Any) -> bool:
        """
        Validate data using registered validators.

        Args:
            data: Data to validate

        Returns:
            True if all validations pass, False otherwise
        """
        for validator in self.validators:
            try:
                if not validator(data):
                    return False
            except Exception as e:
                self.logger.error("Validation error", error=str(e))
                return False
        return True

    def add_validator(self, validator: Callable[[Any], bool]) -> None:
        """Add a custom validation function."""
        self.validators.append(validator)

    async def process_batch(
        self,
        batch: List[Dict[str, Any]],
        strategy: LoadingStrategy,
        target_table: str,
        **kwargs,
    ) -> LoadingResult:
        """
        Process a batch of records with retry logic.

        Args:
            batch: Batch of records to process
            strategy: Loading strategy
            target_table: Target table name
            **kwargs: Additional parameters

        Returns:
            LoadingResult for the batch
        """
        for attempt in range(self.max_retries + 1):
            try:
                # Validate batch data
                for record in batch:
                    if not await self.validate_data(record):
                        raise ValidationError(f"Validation failed for record: {record}")

                # Load the batch
                result = await self._load_batch(batch, strategy, target_table, **kwargs)
                return result

            except Exception as e:
                self.logger.warning(
                    "Batch processing failed",
                    attempt=attempt,
                    error=str(e),
                    batch_size=len(batch),
                )

                if attempt == self.max_retries:
                    # Final attempt failed
                    result = LoadingResult(
                        success=False, metrics=LoadingMetrics(start_time=datetime.now())
                    )
                    result.add_error(
                        f"Failed after {self.max_retries} attempts: {str(e)}"
                    )
                    return result

                # Wait before retry
                await asyncio.sleep(
                    self.retry_delay * (2**attempt)
                )  # Exponential backoff

        # Should never reach here, but for type safety
        return LoadingResult(
            success=False, metrics=LoadingMetrics(start_time=datetime.now())
        )

    @abstractmethod
    async def _load_batch(
        self,
        batch: List[Dict[str, Any]],
        strategy: LoadingStrategy,
        target_table: str,
        **kwargs,
    ) -> LoadingResult:
        """Internal method to load a batch - implemented by subclasses."""
        pass

    def calculate_checksum(self, data: Union[List[Dict[str, Any]], str]) -> str:
        """
        Calculate checksum for data versioning.

        Args:
            data: Data to calculate checksum for

        Returns:
            MD5 checksum string
        """
        import hashlib
        import json

        if isinstance(data, list):
            # Sort and serialize for consistent checksum
            sorted_data = sorted(data, key=lambda x: json.dumps(x, sort_keys=True))
            data_str = json.dumps(sorted_data, sort_keys=True)
        else:
            data_str = str(data)

        return hashlib.md5(data_str.encode("utf-8")).hexdigest()

    async def optimize_storage(self, target: str) -> Dict[str, Any]:
        """
        Optimize storage for the target (e.g., vacuum, analyze, compress).

        Args:
            target: Target to optimize

        Returns:
            Optimization results
        """
        # Default implementation - subclasses can override
        return {"status": "not_implemented", "target": target}

    async def get_statistics(self, target: str) -> Dict[str, Any]:
        """
        Get statistics for the target.

        Args:
            target: Target to get statistics for

        Returns:
            Statistics dictionary
        """
        # Default implementation - subclasses can override
        return {"status": "not_implemented", "target": target}

    def __enter__(self):
        """Context manager entry."""
        return self

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        pass

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
