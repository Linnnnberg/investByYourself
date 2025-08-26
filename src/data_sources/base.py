#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base Data Source Connector Module

This module provides the base classes and interfaces for data source connectors.
"""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import requests


class DataSourceError(Exception):
    """Base exception for data source errors"""

    pass


class RateLimitError(DataSourceError):
    """Exception raised when rate limit is exceeded"""

    pass


class AuthenticationError(DataSourceError):
    """Exception raised when authentication fails"""

    pass


class DataNotFoundError(DataSourceError):
    """Exception raised when requested data is not found"""

    pass


@dataclass
class DataRequest:
    """Represents a data request"""

    symbols: List[str]
    start_date: datetime
    end_date: datetime
    interval: str = "1d"  # 1m, 5m, 15m, 1h, 1d, 1w, 1M
    fields: List[str] = None  # open, high, low, close, volume, etc.

    def __post_init__(self):
        """Validate request parameters"""
        if not self.symbols:
            raise ValueError("At least one symbol must be specified")
        if self.start_date >= self.end_date:
            raise ValueError("Start date must be before end date")
        if self.interval not in ["1m", "5m", "15m", "1h", "1d", "1w", "1M"]:
            raise ValueError("Invalid interval specified")


@dataclass
class DataResponse:
    """Represents a data response"""

    data: pd.DataFrame
    request: DataRequest
    timestamp: datetime
    source: str
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """Set default metadata if none provided"""
        if self.metadata is None:
            self.metadata = {}


class BaseDataSource(ABC):
    """Base class for all data source connectors"""

    def __init__(self, name: str, api_key: str = None, base_url: str = None):
        self.name = name
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.logger = logging.getLogger(f"DataSource.{name}")

        # Rate limiting
        self.requests_per_minute = 60
        self.last_request_time = 0
        self.min_request_interval = 60 / self.requests_per_minute

        # Authentication
        if api_key:
            self._setup_authentication()

    def _setup_authentication(self) -> None:
        """Setup authentication headers"""
        if self.api_key:
            self.session.headers.update(
                {
                    "Authorization": f"Bearer {self.api_key}",
                    "User-Agent": "InvestByYourself/1.0",
                }
            )

    def _rate_limit_check(self) -> None:
        """Check and enforce rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _make_request(
        self, url: str, method: str = "GET", **kwargs
    ) -> requests.Response:
        """Make HTTP request with rate limiting and error handling"""
        self._rate_limit_check()

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                raise RateLimitError(f"Rate limit exceeded: {e}")
            elif response.status_code == 401:
                raise AuthenticationError(f"Authentication failed: {e}")
            elif response.status_code == 404:
                raise DataNotFoundError(f"Data not found: {e}")
            else:
                raise DataSourceError(f"HTTP error {response.status_code}: {e}")
        except requests.exceptions.RequestException as e:
            raise DataSourceError(f"Request failed: {e}")

    @abstractmethod
    def get_historical_data(self, request: DataRequest) -> DataResponse:
        """Get historical market data"""
        pass

    @abstractmethod
    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Get current quote for a symbol"""
        pass

    @abstractmethod
    def search_symbols(self, query: str) -> List[Dict[str, Any]]:
        """Search for symbols matching query"""
        pass

    def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get current quotes for multiple symbols"""
        quotes = {}
        for symbol in symbols:
            try:
                quotes[symbol] = self.get_quote(symbol)
            except Exception as e:
                self.logger.warning(f"Failed to get quote for {symbol}: {e}")
                quotes[symbol] = None
        return quotes

    def get_daily_data(
        self, symbols: List[str], start_date: datetime, end_date: datetime
    ) -> DataResponse:
        """Get daily data for multiple symbols"""
        request = DataRequest(
            symbols=symbols, start_date=start_date, end_date=end_date, interval="1d"
        )
        return self.get_historical_data(request)

    def get_intraday_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1h",
    ) -> DataResponse:
        """Get intraday data for a single symbol"""
        request = DataRequest(
            symbols=[symbol],
            start_date=start_date,
            end_date=end_date,
            interval=interval,
        )
        return self.get_historical_data(request)

    def validate_symbol(self, symbol: str) -> bool:
        """Validate if a symbol exists"""
        try:
            quote = self.get_quote(symbol)
            return quote is not None
        except Exception:
            return False

    def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """Get detailed information about a symbol"""
        try:
            quote = self.get_quote(symbol)
            if quote:
                return {
                    "symbol": symbol,
                    "name": quote.get("name", ""),
                    "exchange": quote.get("exchange", ""),
                    "currency": quote.get("currency", ""),
                    "asset_type": quote.get("asset_type", ""),
                    "sector": quote.get("sector", ""),
                    "industry": quote.get("industry", ""),
                    "market_cap": quote.get("market_cap", 0),
                    "pe_ratio": quote.get("pe_ratio", 0),
                    "dividend_yield": quote.get("dividend_yield", 0),
                }
        except Exception as e:
            self.logger.warning(f"Failed to get symbol info for {symbol}: {e}")

        return {}

    def test_connection(self) -> bool:
        """Test if the data source is accessible"""
        try:
            # Try to get a simple quote to test connection
            test_symbol = "AAPL"  # Common symbol for testing
            self.get_quote(test_symbol)
            return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get data source status information"""
        return {
            "name": self.name,
            "base_url": self.base_url,
            "api_key_configured": bool(self.api_key),
            "connection_status": self.test_connection(),
            "rate_limit": f"{self.requests_per_minute} requests per minute",
            "last_request": datetime.fromtimestamp(self.last_request_time).isoformat()
            if self.last_request_time > 0
            else "Never",
        }


class DataSourceManager:
    """Manages multiple data sources"""

    def __init__(self):
        self.data_sources: Dict[str, BaseDataSource] = {}
        self.logger = logging.getLogger("DataSourceManager")

    def add_data_source(self, data_source: BaseDataSource) -> None:
        """Add a data source to the manager"""
        if data_source.name in self.data_sources:
            raise ValueError(f"Data source {data_source.name} already exists")

        self.data_sources[data_source.name] = data_source
        self.logger.info(f"Added data source: {data_source.name}")

    def get_data_source(self, name: str) -> BaseDataSource:
        """Get a data source by name"""
        if name not in self.data_sources:
            raise ValueError(f"Data source {name} not found")
        return self.data_sources[name]

    def remove_data_source(self, name: str) -> None:
        """Remove a data source"""
        if name not in self.data_sources:
            raise ValueError(f"Data source {name} not found")

        del self.data_sources[name]
        self.logger.info(f"Removed data source: {name}")

    def list_data_sources(self) -> List[str]:
        """List all data source names"""
        return list(self.data_sources.keys())

    def get_data_source_status(self) -> pd.DataFrame:
        """Get status of all data sources"""
        if not self.data_sources:
            return pd.DataFrame()

        data = []
        for data_source in self.data_sources.values():
            data.append(data_source.get_status())

        return pd.DataFrame(data)

    def get_aggregated_data(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d",
    ) -> pd.DataFrame:
        """Get data from all available sources and aggregate"""
        all_data = []

        for name, data_source in self.data_sources.items():
            try:
                request = DataRequest(
                    symbols=symbols,
                    start_date=start_date,
                    end_date=end_date,
                    interval=interval,
                )

                response = data_source.get_historical_data(request)
                if response.data is not None and not response.data.empty:
                    # Add source column
                    response.data["source"] = name
                    all_data.append(response.data)

            except Exception as e:
                self.logger.warning(f"Failed to get data from {name}: {e}")

        if not all_data:
            return pd.DataFrame()

        # Combine all data sources
        combined_data = pd.concat(all_data, ignore_index=True)

        # Remove duplicates and sort
        combined_data = combined_data.drop_duplicates().sort_values(["date", "symbol"])

        return combined_data

    def get_best_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get the best available quote from all sources"""
        best_quote = None
        best_source = None

        for name, data_source in self.data_sources.items():
            try:
                quote = data_source.get_quote(symbol)
                if quote and quote.get("price", 0) > 0:
                    if best_quote is None or quote.get("price", 0) > best_quote.get(
                        "price", 0
                    ):
                        best_quote = quote
                        best_source = name
            except Exception as e:
                self.logger.warning(f"Failed to get quote from {name}: {e}")

        if best_quote:
            best_quote["source"] = best_source

        return best_quote
