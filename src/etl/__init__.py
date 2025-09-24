"""
ETL Package for investByYourself Platform
Tech-009: ETL Pipeline Implementation (Phase 1-3)

This package contains all ETL (Extract, Transform, Load) components:

Phase 1 - Data Collection Framework (✅ COMPLETED):
- Data collectors for various financial APIs (Yahoo Finance, Alpha Vantage, FRED)
- Rate limiting and retry mechanisms
- Data collection orchestration

Phase 2 - Data Processing Engine (✅ COMPLETED):
- Financial data transformers and validators
- Metrics calculation and standardization
- Data quality assessment

Phase 3 - Data Loading & Storage (🚧 IN PROGRESS):
- Database loaders with versioning
- File loaders with compression
- Cache loaders for performance
- Incremental loading strategies
"""

__version__ = "1.3.0"  # Updated for Phase 3
__author__ = "investByYourself Development Team"

from typing import List

__all__: List[str] = [
    "collectors",
    "transformers",
    "loaders",
    "validators",
    "cache",
    "utils",
    "worker",
]
