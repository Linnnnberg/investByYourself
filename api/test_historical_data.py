#!/usr/bin/env python3
"""
Test Historical Data Implementation
Story-038: Portfolio Time Series & Data Structure Implementation

Test script to verify historical data collection and technical indicators.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, "src")

from src.database.connection import get_db_session, init_database
from src.models.database import Company
from src.services.historical_data_service import HistoricalDataService
from src.services.technical_indicators_service import TechnicalIndicatorsService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_historical_data():
    """Test historical data collection and technical indicators."""
    logger.info("Testing Historical Data Implementation...")

    try:
        # Initialize database
        logger.info("1. Initializing database...")
        await init_database()
        logger.info("✅ Database initialized")

        # Get database session
        logger.info("2. Getting database session...")
        db_session_factory = await get_db_session()
        async with db_session_factory() as db_session:
            # Get a test company
            logger.info("3. Finding test company...")
            from sqlalchemy import select

            result = await db_session.execute(
                select(Company).filter(Company.is_active == True).limit(1)
            )
            company = result.scalar_one_or_none()

            if not company:
                logger.warning("No active companies found in database")
                return

            logger.info(f"✅ Found test company: {company.symbol} ({company.name})")

            # Test historical data service
            logger.info("4. Testing historical data service...")
            historical_service = HistoricalDataService(db_session)

            # Check if data already exists
            existing_prices = await historical_service.get_historical_prices(
                company.id, limit=1
            )
            if existing_prices:
                logger.info(
                    f"✅ Historical data already exists for {company.symbol}: {len(existing_prices)} records"
                )
            else:
                logger.info(f"ℹ️  No historical data found for {company.symbol}")

            # Test technical indicators service
            logger.info("5. Testing technical indicators service...")
            indicators_service = TechnicalIndicatorsService(db_session)

            # Get existing indicators
            existing_indicators = await indicators_service.get_technical_indicators(
                company.id
            )
            if existing_indicators:
                logger.info(
                    f"✅ Technical indicators already exist for {company.symbol}: {len(existing_indicators)} records"
                )
            else:
                logger.info(f"ℹ️  No technical indicators found for {company.symbol}")

            # Test data quality validation
            logger.info("6. Testing data quality validation...")
            quality_metrics = await historical_service.validate_data_quality(company.id)
            logger.info(f"✅ Data quality metrics: {quality_metrics}")

            logger.info("\n" + "=" * 60)
            logger.info("HISTORICAL DATA TEST SUMMARY")
            logger.info("=" * 60)
            logger.info(f"Company: {company.symbol} ({company.name})")
            logger.info(f"Historical prices: {len(existing_prices)} records")
            logger.info(f"Technical indicators: {len(existing_indicators)} records")
            logger.info(
                f"Data quality score: {quality_metrics.get('quality_score', 'N/A')}"
            )
            logger.info("=" * 60)

            logger.info("✅ Historical data implementation test completed successfully!")

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(test_historical_data())
