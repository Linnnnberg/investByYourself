"""
Data Collectors Package - investByYourself
Tech-009: ETL Pipeline Implementation - Phase 1

This package contains data collectors for various financial APIs:
- Base collector with common functionality
- Yahoo Finance collector
- Alpha Vantage collector
- FRED API collector
- Collection orchestrator for managing multiple collectors
"""

from typing import List

from .alpha_vantage_collector import AlphaVantageCollector

# Import base classes and configurations
from .base_collector import (
    BaseDataCollector,
    CollectionMetrics,
    DataCollectionError,
    DataQualityLevel,
    DataValidationError,
    RateLimitConfig,
    RateLimitExceededError,
    RetryConfig,
)

# Import orchestrator
from .collection_orchestrator import (
    CollectionResult,
    CollectionTask,
    DataCollectionOrchestrator,
)
from .fred_collector import FREDCollector

# Import specific collectors
from .yahoo_finance_collector import YahooFinanceCollector

__all__: List[str] = [
    # Base classes
    "BaseDataCollector",
    "RateLimitConfig",
    "RetryConfig",
    "CollectionMetrics",
    "DataQualityLevel",
    "DataCollectionError",
    "RateLimitExceededError",
    "DataValidationError",
    # Specific collectors
    "YahooFinanceCollector",
    "AlphaVantageCollector",
    "FREDCollector",
    # Orchestrator
    "DataCollectionOrchestrator",
    "CollectionTask",
    "CollectionResult",
]
