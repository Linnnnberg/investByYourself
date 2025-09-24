#!/usr/bin/env python3
"""
Test script for single DAX company data collection with longer delays.
"""

import asyncio
import os
import sys
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from collectors.yahoo_finance_collector import YahooFinanceCollector

from utils.logger import setup_logging

logger = setup_logging(__name__)


async def test_single_dax():
    """Test single DAX company with longer delays."""
    logger.info("Testing single DAX company data collection...")

    collector = YahooFinanceCollector()

    # Test with just one DAX company
    symbol = "SAP.DE"

    try:
        logger.info(f"Testing {symbol} with 10 second delay...")

        # Wait 10 seconds before starting
        await asyncio.sleep(10)

        # Test company profile
        profile = await collector.collect_company_profile(symbol)
        logger.info(f"✅ {symbol}: {profile['name']}")

        # Wait another 10 seconds
        await asyncio.sleep(10)

        # Test historical data (last 7 days)
        historical = await collector.collect_historical_data(symbol, incremental=True)
        logger.info(f"✅ {symbol}: {len(historical)} historical records")

    except Exception as e:
        logger.error(f"❌ {symbol}: {e}")

    logger.info("Single DAX test completed")


if __name__ == "__main__":
    asyncio.run(test_single_dax())
