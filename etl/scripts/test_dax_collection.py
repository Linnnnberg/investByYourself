#!/usr/bin/env python3
"""
Test script for DAX 40 data collection.
"""

import asyncio
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from collectors.yahoo_finance_collector import YahooFinanceCollector

from utils.logger import setup_logging

logger = setup_logging(__name__)


async def test_dax_collection():
    """Test DAX 40 data collection."""
    logger.info("Testing DAX 40 data collection...")

    collector = YahooFinanceCollector()

    # Test with a few DAX companies
    test_symbols = ["SAP.DE", "SIE.DE", "ALV.DE", "BAS.DE", "BAYN.DE"]

    for symbol in test_symbols:
        try:
            logger.info(f"Testing {symbol}...")

            # Test company profile
            profile = await collector.collect_company_profile(symbol)
            logger.info(f"✅ {symbol}: {profile['name']}")

            # Test historical data (last 7 days)
            historical = await collector.collect_historical_data(
                symbol, incremental=True
            )
            logger.info(f"✅ {symbol}: {len(historical)} historical records")

        except Exception as e:
            logger.error(f"❌ {symbol}: {e}")

    logger.info("DAX collection test completed")


if __name__ == "__main__":
    asyncio.run(test_dax_collection())
