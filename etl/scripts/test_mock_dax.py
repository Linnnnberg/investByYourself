#!/usr/bin/env python3
"""
Test script for DAX 40 data collection using mock data.
"""

import asyncio
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from collectors.mock_collector import MockCollector

from utils.logger import setup_logging

logger = setup_logging(__name__)


async def test_mock_dax_collection():
    """Test DAX 40 data collection using mock data."""
    logger.info("Testing DAX 40 data collection with mock data...")

    collector = MockCollector()

    # Test with DAX 40 companies
    dax_symbols = [
        "SAP.DE",
        "SIE.DE",
        "ALV.DE",
        "BAS.DE",
        "BAYN.DE",
        "BMW.DE",
        "CON.DE",
        "DAI.DE",
        "DBK.DE",
        "DB1.DE",
    ]

    for symbol in dax_symbols:
        try:
            logger.info(f"Testing {symbol}...")

            # Test company profile
            profile = await collector.collect_company_profile(symbol)
            logger.info(f"✅ {symbol}: {profile['name']} - {profile['sector']}")

            # Test historical data (last 30 days)
            historical = await collector.collect_historical_data(
                symbol, incremental=True
            )
            logger.info(f"✅ {symbol}: {len(historical)} historical records")

            # Test financial ratios
            ratios = await collector.collect_financial_ratios(symbol)
            logger.info(f"✅ {symbol}: PE Ratio {ratios['pe_ratio']}")

        except Exception as e:
            logger.error(f"❌ {symbol}: {e}")

    logger.info("Mock DAX collection test completed")


if __name__ == "__main__":
    asyncio.run(test_mock_dax_collection())
