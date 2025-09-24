#!/usr/bin/env python3
"""
ETL Test Script
InvestByYourself Financial Platform

Simple test script to validate ETL system functionality.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from collectors.yahoo_finance_collector import YahooFinanceCollector
from transformers.company_profile_transformer import CompanyProfileTransformer
from transformers.market_data_transformer import MarketDataTransformer

from utils.logger import setup_logging

# Configure logging
logger = setup_logging(__name__)


async def test_yahoo_finance_collector():
    """Test Yahoo Finance collector."""
    try:
        logger.info("Testing Yahoo Finance collector...")

        collector = YahooFinanceCollector()

        # Test company profile collection
        profile = await collector.collect_company_profile("AAPL")
        logger.info(f"Company profile collected: {profile['name']}")

        # Test historical data collection
        historical_data = await collector.collect_historical_data(
            "AAPL", incremental=True
        )
        logger.info(f"Historical data collected: {len(historical_data)} records")

        logger.info("Yahoo Finance collector test: PASSED")
        return True

    except Exception as e:
        logger.error(f"Yahoo Finance collector test failed: {e}")
        return False


async def test_transformers():
    """Test data transformers."""
    try:
        logger.info("Testing data transformers...")

        # Test market data transformer
        market_transformer = MarketDataTransformer()
        test_historical_data = [
            {
                "symbol": "AAPL",
                "date": "2024-01-01",
                "open": 100.0,
                "high": 105.0,
                "low": 99.0,
                "close": 103.0,
                "volume": 1000000,
                "adjusted_close": 103.0,
                "source": "test",
            }
        ]

        transformed_data = market_transformer.transform_historical_data(
            test_historical_data
        )
        logger.info(f"Market data transformed: {len(transformed_data)} records")

        # Test company profile transformer
        profile_transformer = CompanyProfileTransformer()
        test_profile = {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "exchange": "NASDAQ",
            "currency": "USD",
            "country": "United States",
            "website": "https://www.apple.com",
            "description": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide.",
            "employee_count": 164000,
            "market_cap": 3000000000000,
            "enterprise_value": 2900000000000,
            "ceo": "Tim Cook",
            "headquarters": "Cupertino, California, United States",
            "founded_year": 1976,
            "is_active": True,
        }

        transformed_profile = profile_transformer.transform_company_profile(
            test_profile
        )
        logger.info(f"Company profile transformed: {transformed_profile['name']}")

        logger.info("Data transformers test: PASSED")
        return True

    except Exception as e:
        logger.error(f"Data transformers test failed: {e}")
        return False


async def test_health_check():
    """Test health check functionality."""
    try:
        logger.info("Testing health check...")

        # Import and run health check
        from health_check import ETLHealthChecker

        checker = ETLHealthChecker()
        results = await checker.run_all_checks()

        if results["overall_status"]:
            logger.info("Health check test: PASSED")
            return True
        else:
            logger.error("Health check test: FAILED")
            return False

    except Exception as e:
        logger.error(f"Health check test failed: {e}")
        return False


async def main():
    """Run all ETL tests."""
    logger.info("Starting ETL system tests...")

    tests = [
        ("Yahoo Finance Collector", test_yahoo_finance_collector),
        ("Data Transformers", test_transformers),
        ("Health Check", test_health_check),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        logger.info(f"Running {test_name} test...")
        try:
            result = await test_func()
            if result:
                passed += 1
                logger.info(f"✅ {test_name} test: PASSED")
            else:
                logger.error(f"❌ {test_name} test: FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} test: ERROR - {e}")

    logger.info(f"ETL tests completed: {passed}/{total} passed")

    if passed == total:
        logger.info("🎉 All ETL tests passed!")
        return True
    else:
        logger.error(f"💥 {total - passed} ETL tests failed!")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
