"""
Alpha Vantage Data Collector
InvestByYourself Financial Platform

Collects technical indicators and alternative data from Alpha Vantage API.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import requests

logger = logging.getLogger(__name__)


class AlphaVantageCollector:
    """Alpha Vantage data collector."""

    def __init__(self, api_key: str):
        """Initialize Alpha Vantage collector."""
        self.name = "Alpha Vantage"
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
        self.rate_limit = 0.083  # 5 requests per minute
        self.timeout = 30

    async def collect_technical_indicators(self, symbol: str) -> Dict[str, Any]:
        """Collect technical indicators."""
        try:
            logger.info(f"Collecting technical indicators for {symbol}")

            # Collect RSI
            rsi_data = await self._get_technical_indicator(symbol, "RSI")

            # Collect MACD
            macd_data = await self._get_technical_indicator(symbol, "MACD")

            # Collect SMA
            sma_data = await self._get_technical_indicator(symbol, "SMA")

            # Combine indicators
            indicators = {
                "symbol": symbol,
                "rsi": rsi_data,
                "macd": macd_data,
                "sma": sma_data,
                "source": "alpha_vantage",
                "created_at": datetime.now().isoformat(),
            }

            logger.info(f"Technical indicators collected for {symbol}")
            return indicators

        except Exception as e:
            logger.error(f"Failed to collect technical indicators for {symbol}: {e}")
            raise

    async def _get_technical_indicator(
        self, symbol: str, indicator: str
    ) -> Dict[str, Any]:
        """Get specific technical indicator."""
        try:
            params = {
                "function": indicator,
                "symbol": symbol,
                "apikey": self.api_key,
                "interval": "daily",
                "time_period": 14,
            }

            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            # Check for API errors
            if "Error Message" in data:
                raise Exception(f"Alpha Vantage API error: {data['Error Message']}")

            if "Note" in data:
                raise Exception(f"Alpha Vantage API rate limit: {data['Note']}")

            return data

        except Exception as e:
            logger.error(f"Failed to get {indicator} for {symbol}: {e}")
            raise

    async def collect_fundamental_data(self, symbol: str) -> Dict[str, Any]:
        """Collect fundamental data."""
        try:
            logger.info(f"Collecting fundamental data for {symbol}")

            # Get company overview
            params = {"function": "OVERVIEW", "symbol": symbol, "apikey": self.api_key}

            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            # Check for API errors
            if "Error Message" in data:
                raise Exception(f"Alpha Vantage API error: {data['Error Message']}")

            if "Note" in data:
                raise Exception(f"Alpha Vantage API rate limit: {data['Note']}")

            logger.info(f"Fundamental data collected for {symbol}")
            return data

        except Exception as e:
            logger.error(f"Failed to collect fundamental data for {symbol}: {e}")
            raise
