"""
FRED (Federal Reserve Economic Data) Collector
InvestByYourself Financial Platform

Collects economic indicators and macroeconomic data from FRED API.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd
import requests

logger = logging.getLogger(__name__)


class FREDCollector:
    """FRED data collector."""

    def __init__(self, api_key: str):
        """Initialize FRED collector."""
        self.name = "FRED"
        self.api_key = api_key
        self.base_url = "https://api.stlouisfed.org/fred"
        self.rate_limit = 2.0  # 120 requests per minute
        self.timeout = 30

    async def collect_economic_data(
        self, indicator: str, incremental: bool = False
    ) -> List[Dict[str, Any]]:
        """Collect economic indicator data."""
        try:
            logger.info(f"Collecting economic data for {indicator}")

            # Determine date range
            if incremental:
                # Last 30 days for incremental updates
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
            else:
                # 5 years for full import
                end_date = datetime.now()
                start_date = end_date - timedelta(days=5 * 365)

            # Get economic data
            params = {
                "series_id": indicator,
                "api_key": self.api_key,
                "file_type": "json",
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
            }

            response = requests.get(
                f"{self.base_url}/series/observations",
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()

            data = response.json()

            # Check for API errors
            if "error_message" in data:
                raise Exception(f"FRED API error: {data['error_message']}")

            # Process observations
            economic_data = []
            for observation in data.get("observations", []):
                if observation.get("value") != ".":
                    data_point = {
                        "indicator_code": indicator,
                        "indicator_name": self._get_indicator_name(indicator),
                        "data_date": observation["date"],
                        "value": float(observation["value"]),
                        "unit": self._get_indicator_unit(indicator),
                        "frequency": "daily",
                        "source": "fred",
                        "created_at": datetime.now().isoformat(),
                    }
                    economic_data.append(data_point)

            logger.info(
                f"Economic data collected for {indicator}: {len(economic_data)} records"
            )
            return economic_data

        except Exception as e:
            logger.error(f"Failed to collect economic data for {indicator}: {e}")
            raise

    def _get_indicator_name(self, indicator: str) -> str:
        """Get human-readable indicator name."""
        names = {
            "CPIAUCSL": "Consumer Price Index",
            "CPILFESL": "Core Consumer Price Index",
            "PPIACO": "Producer Price Index",
            "GDP": "Gross Domestic Product",
            "GDPC1": "Real Gross Domestic Product",
            "FEDFUNDS": "Federal Funds Rate",
            "DGS10": "10-Year Treasury Rate",
            "DGS30": "30-Year Treasury Rate",
            "UNRATE": "Unemployment Rate",
            "PAYEMS": "Total Nonfarm Payrolls",
            "CIVPART": "Labor Force Participation Rate",
            "M1SL": "M1 Money Stock",
            "M2SL": "M2 Money Stock",
            "WALCL": "Fed Balance Sheet",
        }
        return names.get(indicator, indicator)

    def _get_indicator_unit(self, indicator: str) -> str:
        """Get indicator unit."""
        units = {
            "CPIAUCSL": "Index",
            "CPILFESL": "Index",
            "PPIACO": "Index",
            "GDP": "Billions of Dollars",
            "GDPC1": "Billions of Chained 2017 Dollars",
            "FEDFUNDS": "Percent",
            "DGS10": "Percent",
            "DGS30": "Percent",
            "UNRATE": "Percent",
            "PAYEMS": "Thousands of Persons",
            "CIVPART": "Percent",
            "M1SL": "Billions of Dollars",
            "M2SL": "Billions of Dollars",
            "WALCL": "Millions of Dollars",
        }
        return units.get(indicator, "Unknown")
