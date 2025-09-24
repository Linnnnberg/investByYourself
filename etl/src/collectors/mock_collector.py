"""
Mock data collector for testing purposes.

This collector provides mock data when Yahoo Finance rate limits are hit.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MockCollector:
    """Mock data collector for testing."""

    def __init__(self):
        """Initialize mock collector."""
        self.name = "Mock Data Collector"
        self.rate_limit = 0.1  # Very fast for testing

    async def collect_company_profile(self, symbol: str) -> Dict[str, Any]:
        """Collect mock company profile information."""
        try:
            logger.info(f"Collecting mock company profile for {symbol}")

            # Simulate network delay
            await asyncio.sleep(0.1)

            # Mock data based on symbol
            mock_data = {
                "SAP.DE": {
                    "name": "SAP SE",
                    "sector": "Technology",
                    "industry": "Software",
                    "country": "Germany",
                    "market_cap": 150000000000,
                },
                "SIE.DE": {
                    "name": "Siemens AG",
                    "sector": "Industrial",
                    "industry": "Industrial Conglomerates",
                    "country": "Germany",
                    "market_cap": 120000000000,
                },
                "ALV.DE": {
                    "name": "Allianz SE",
                    "sector": "Financial Services",
                    "industry": "Insurance",
                    "country": "Germany",
                    "market_cap": 90000000000,
                },
                "BAS.DE": {
                    "name": "BASF SE",
                    "sector": "Materials",
                    "industry": "Chemicals",
                    "country": "Germany",
                    "market_cap": 80000000000,
                },
                "BAYN.DE": {
                    "name": "Bayer AG",
                    "sector": "Healthcare",
                    "industry": "Pharmaceuticals",
                    "country": "Germany",
                    "market_cap": 70000000000,
                },
            }

            base_data = mock_data.get(
                symbol,
                {
                    "name": f"Company {symbol}",
                    "sector": "Unknown",
                    "industry": "Unknown",
                    "country": "Germany",
                    "market_cap": 50000000000,
                },
            )

            profile = {
                "symbol": symbol,
                "name": base_data["name"],
                "sector": base_data["sector"],
                "industry": base_data["industry"],
                "exchange": "XETRA",
                "currency": "EUR",
                "country": base_data["country"],
                "website": f"https://www.{symbol.lower().replace('.de', '')}.com",
                "description": f"{base_data['name']} is a leading company in the {base_data['industry']} industry.",
                "employee_count": 50000,
                "market_cap": base_data["market_cap"],
                "enterprise_value": base_data["market_cap"] * 0.9,
                "ceo": "CEO Name",
                "headquarters": "Germany",
                "founded_year": 1900,
                "is_active": True,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }

            logger.info(f"Mock company profile collected for {symbol}")
            return profile

        except Exception as e:
            logger.error(f"Failed to collect mock company profile for {symbol}: {e}")
            raise

    async def collect_historical_data(
        self, symbol: str, incremental: bool = False
    ) -> List[Dict[str, Any]]:
        """Collect mock historical market data."""
        try:
            logger.info(f"Collecting mock historical data for {symbol}")

            # Simulate network delay
            await asyncio.sleep(0.1)

            # Generate mock historical data
            historical_data = []
            days = 30 if incremental else 365 * 2  # 2 years for full import

            base_price = 100.0
            for i in range(days):
                date = datetime.now() - timedelta(days=days - i)

                # Simple price movement simulation
                price_change = (i % 10 - 5) * 0.5  # Random walk
                price = base_price + price_change
                base_price = price

                data_point = {
                    "symbol": symbol,
                    "date": date.strftime("%Y-%m-%d"),
                    "open": price * 0.99,
                    "high": price * 1.02,
                    "low": price * 0.98,
                    "close": price,
                    "volume": 1000000 + (i % 100000),
                    "adjusted_close": price,
                    "source": "mock",
                    "created_at": datetime.now().isoformat(),
                }
                historical_data.append(data_point)

            logger.info(
                f"Mock historical data collected for {symbol}: {len(historical_data)} records"
            )
            return historical_data

        except Exception as e:
            logger.error(f"Failed to collect mock historical data for {symbol}: {e}")
            raise

    async def collect_financial_ratios(self, symbol: str) -> Dict[str, Any]:
        """Collect mock financial ratios and metrics."""
        try:
            logger.info(f"Collecting mock financial ratios for {symbol}")

            # Simulate network delay
            await asyncio.sleep(0.1)

            # Mock financial ratios
            ratios = {
                "symbol": symbol,
                "period_end_date": datetime.now().strftime("%Y-%m-%d"),
                "current_ratio": 1.5,
                "quick_ratio": 1.2,
                "debt_to_equity": 0.3,
                "return_on_equity": 0.15,
                "return_on_assets": 0.08,
                "gross_margin": 0.25,
                "operating_margin": 0.12,
                "net_margin": 0.08,
                "pe_ratio": 15.0,
                "pb_ratio": 2.0,
                "ps_ratio": 1.5,
                "dividend_yield": 0.03,
                "beta": 1.0,
                "source": "mock",
                "created_at": datetime.now().isoformat(),
            }

            logger.info(f"Mock financial ratios collected for {symbol}")
            return ratios

        except Exception as e:
            logger.error(f"Failed to collect mock financial ratios for {symbol}: {e}")
            raise
