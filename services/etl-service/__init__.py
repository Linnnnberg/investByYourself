"""
ETL Service for investByYourself Platform
Tech-021: ETL Service Extraction

This service contains all ETL (Extract, Transform, Load) components
extracted from the monolithic structure into a dedicated microservice.

Features:
- Data collection from financial APIs (Yahoo Finance, Alpha Vantage, FRED)
- Financial data transformation and validation
- Data loading to multiple storage backends
- REST API endpoints for ETL operations
- Service health monitoring and metrics
"""

__version__ = "2.0.0"  # Major version bump for service extraction
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
    "api",
    "models",
]
