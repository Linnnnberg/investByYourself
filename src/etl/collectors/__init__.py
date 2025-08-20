"""
Data Collectors Package - investByYourself
Story-005: ETL & Database Architecture Design

This package contains data collectors for various financial APIs:
- Yahoo Finance collector
- Alpha Vantage collector
- FRED API collector
- API Ninjas collector
"""

from typing import List

__all__: List[str] = [
    "yahoo_finance_collector",
    "alpha_vantage_collector",
    "fred_collector",
    "api_ninjas_collector",
]
