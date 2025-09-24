#!/usr/bin/env python3
"""
Historical Data Collection Script
Story-038: Portfolio Time Series & Data Structure Implementation

Script to collect historical price data and calculate technical indicators for all companies.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime

from sqlalchemy.orm import Session

# Add api/src to path
api_src_path = os.path.join(os.path.dirname(__file__), "..", "api", "src")
sys.path.insert(0, api_src_path)

from src.database.connection import get_db_session, init_database
from src.models.database import Company
from src.services.historical_data_service import HistoricalDataService
from src.services.technical_indicators_service import TechnicalIndicatorsService

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def collect_all_historical_data():
    """Collect historical data for all companies."""
    logger.info("Starting historical data collection...")

    try:
        # Initialize database
        logger.info("Initializing database...")
        await init_database()
        logger.info("✅ Database initialized")

        # Get database session
        db_session_factory = await get_db_session()
        async with db_session_factory() as db_session:
            # Get all active companies
            companies = (
                db_session.query(Company).filter(Company.is_active == True).all()
            )
            logger.info(f"Found {len(companies)} active companies")

            if not companies:
                logger.warning("No active companies found")
                return

            # Initialize services
            historical_service = HistoricalDataService(db_session)
            indicators_service = TechnicalIndicatorsService(db_session)

            # Statistics
            total_prices = 0
            total_indicators = 0
            successful_companies = 0
            failed_companies = 0

            for i, company in enumerate(companies, 1):
                logger.info(
                    f"Processing {company.symbol} ({company.name}) - {i}/{len(companies)}"
                )

                try:
                    # Check if data already exists
                    existing_prices = historical_service.get_historical_prices(
                        company.id, limit=1
                    )
                    if existing_prices:
                        logger.info(
                            f"  ⏭️  Skipping {company.symbol} - data already exists ({len(existing_prices)} records)"
                        )
                        continue

                    # Collect historical prices
                    logger.info(
                        f"  📈 Collecting historical prices for {company.symbol}..."
                    )
                    prices = await historical_service.collect_historical_prices(
                        company, years=5
                    )

                    if not prices:
                        logger.warning(
                            f"  ⚠️  No price data collected for {company.symbol}"
                        )
                        failed_companies += 1
                        continue

                    # Save prices to database
                    logger.info(f"  💾 Saving {len(prices)} price records...")
                    historical_service.save_historical_prices(prices)
                    total_prices += len(prices)

                    # Calculate technical indicators
                    logger.info(
                        f"  📊 Calculating technical indicators for {company.symbol}..."
                    )
                    indicators = indicators_service.calculate_all_indicators(
                        company.id, prices
                    )

                    if indicators:
                        # Save indicators to database
                        logger.info(
                            f"  💾 Saving {len(indicators)} indicator records..."
                        )
                        indicators_service.save_technical_indicators(indicators)
                        total_indicators += len(indicators)

                    # Validate data quality
                    quality_metrics = historical_service.validate_data_quality(
                        company.id
                    )
                    quality_score = quality_metrics.get("quality_score", 0)

                    logger.info(
                        f"  ✅ Completed {company.symbol}: {len(prices)} prices, {len(indicators)} indicators, quality: {quality_score:.2f}"
                    )
                    successful_companies += 1

                except Exception as e:
                    logger.error(f"  ❌ Error processing {company.symbol}: {e}")
                    failed_companies += 1
                    continue

            # Summary
            logger.info("\n" + "=" * 60)
            logger.info("HISTORICAL DATA COLLECTION SUMMARY")
            logger.info("=" * 60)
            logger.info(f"Total companies processed: {len(companies)}")
            logger.info(f"Successful: {successful_companies}")
            logger.info(f"Failed: {failed_companies}")
            logger.info(f"Total price records: {total_prices}")
            logger.info(f"Total indicator records: {total_indicators}")
            logger.info("=" * 60)

            if successful_companies > 0:
                logger.info("✅ Historical data collection completed successfully")
            else:
                logger.warning("⚠️  No data was collected successfully")

    except Exception as e:
        logger.error(f"❌ Historical data collection failed: {e}")
        raise


async def collect_single_company(symbol: str, years: int = 5):
    """Collect historical data for a single company."""
    logger.info(f"Collecting historical data for {symbol}...")

    try:
        # Initialize database
        await init_database()

        # Get database session
        db_session_factory = await get_db_session()
        async with db_session_factory() as db_session:
            # Find company
            company = db_session.query(Company).filter(Company.symbol == symbol).first()
            if not company:
                logger.error(f"Company {symbol} not found")
                return

            # Initialize services
            historical_service = HistoricalDataService(db_session)
            indicators_service = TechnicalIndicatorsService(db_session)

            # Collect historical prices
            logger.info(f"Collecting {years} years of historical prices...")
            prices = await historical_service.collect_historical_prices(company, years)

            if not prices:
                logger.error(f"No price data collected for {symbol}")
                return

            # Save prices
            historical_service.save_historical_prices(prices)
            logger.info(f"Saved {len(prices)} price records")

            # Calculate indicators
            logger.info("Calculating technical indicators...")
            indicators = indicators_service.calculate_all_indicators(company.id, prices)

            if indicators:
                indicators_service.save_technical_indicators(indicators)
                logger.info(f"Saved {len(indicators)} indicator records")

            # Quality check
            quality_metrics = historical_service.validate_data_quality(company.id)
            logger.info(
                f"Data quality score: {quality_metrics.get('quality_score', 0):.2f}"
            )

            logger.info(f"✅ Successfully collected data for {symbol}")

    except Exception as e:
        logger.error(f"❌ Failed to collect data for {symbol}: {e}")
        raise


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Collect historical data for companies"
    )
    parser.add_argument("--symbol", help="Collect data for a specific company symbol")
    parser.add_argument(
        "--years", type=int, default=5, help="Number of years of data to collect"
    )
    parser.add_argument(
        "--all", action="store_true", help="Collect data for all companies"
    )

    args = parser.parse_args()

    if args.symbol:
        asyncio.run(collect_single_company(args.symbol, args.years))
    elif args.all:
        asyncio.run(collect_all_historical_data())
    else:
        print("Please specify --symbol or --all")
        parser.print_help()


if __name__ == "__main__":
    main()
