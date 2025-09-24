#!/usr/bin/env python3
"""
Test script for ETL orchestrator with DAX 40 data collection.
"""

import asyncio
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from etl_orchestrator import ETLOrchestrator

from utils.logger import setup_logging

logger = setup_logging(__name__)


async def test_orchestrator_dax():
    """Test ETL orchestrator with DAX 40 data collection."""
    logger.info("Testing ETL orchestrator with DAX 40 data collection...")

    try:
        # Initialize orchestrator
        orchestrator = ETLOrchestrator()

        # Test company profiles collection
        logger.info("Testing company profiles collection...")
        await orchestrator.collect_company_profiles()

        # Test historical data collection (incremental)
        logger.info("Testing historical data collection...")
        await orchestrator.collect_historical_data(incremental=True)

        logger.info("ETL orchestrator test completed successfully!")

    except Exception as e:
        logger.error(f"ETL orchestrator test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(test_orchestrator_dax())
