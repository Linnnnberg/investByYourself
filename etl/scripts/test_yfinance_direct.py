#!/usr/bin/env python3
"""
Test script for direct yfinance usage.
"""

import asyncio
import os
import sys
import time

import yfinance as yf

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.logger import setup_logging

logger = setup_logging(__name__)


async def test_yfinance_direct():
    """Test direct yfinance usage."""
    logger.info("Testing direct yfinance usage...")

    try:
        # Test with a simple US stock first
        logger.info("Testing AAPL (US stock)...")
        ticker = yf.Ticker("AAPL")
        info = ticker.info
        logger.info(f"✅ AAPL: {info.get('longName', 'Unknown')}")

        # Wait 5 seconds
        await asyncio.sleep(5)

        # Test with a DAX stock
        logger.info("Testing SAP.DE (DAX stock)...")
        ticker = yf.Ticker("SAP.DE")
        info = ticker.info
        logger.info(f"✅ SAP.DE: {info.get('longName', 'Unknown')}")

    except Exception as e:
        logger.error(f"❌ Error: {e}")

    logger.info("Direct yfinance test completed")


if __name__ == "__main__":
    asyncio.run(test_yfinance_direct())
