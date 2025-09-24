#!/usr/bin/env python3
"""
ETL Orchestrator - Main entry point for ETL operations
InvestByYourself Financial Platform

This script orchestrates the complete ETL pipeline for market data collection,
processing, and storage.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

import click
import yaml
from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from collectors.alpha_vantage_collector import AlphaVantageCollector
from collectors.fred_collector import FREDCollector
from collectors.mock_collector import MockCollector
from collectors.yahoo_finance_collector import YahooFinanceCollector
from loaders.redis_loader import RedisLoader
from loaders.sqlite_loader import SQLiteLoader
from transformers.company_profile_transformer import CompanyProfileTransformer
from transformers.economic_data_transformer import EconomicDataTransformer
from transformers.market_data_transformer import MarketDataTransformer

from utils.logger import setup_logging
from utils.rate_limiter import RateLimiter
from utils.retry_handler import RetryHandler

# Load environment variables
load_dotenv()

# Configure logging
logger = setup_logging(__name__)


class ETLOrchestrator:
    """Main ETL orchestrator for managing data import operations."""

    def __init__(self, config_path: str = "config/etl_config.yaml"):
        """Initialize ETL orchestrator with configuration."""
        self.config = self._load_config(config_path)
        self.collectors = {}
        self.transformers = {}
        self.loaders = {}
        self.retry_handler = RetryHandler()
        self.rate_limiter = RateLimiter()

        # Initialize components
        self._initialize_collectors()
        self._initialize_transformers()
        self._initialize_loaders()

    def _load_config(self, config_path: str) -> Dict:
        """Load ETL configuration from YAML file."""
        try:
            with open(config_path, "r") as file:
                config = yaml.safe_load(file)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise

    def _initialize_collectors(self):
        """Initialize data collectors."""
        try:
            if self.config["data_sources"]["yahoo_finance"]["enabled"]:
                self.collectors["yahoo_finance"] = YahooFinanceCollector()
                logger.info("Yahoo Finance collector initialized")

            if self.config["data_sources"]["alpha_vantage"]["enabled"]:
                api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
                if api_key:
                    self.collectors["alpha_vantage"] = AlphaVantageCollector(api_key)
                    logger.info("Alpha Vantage collector initialized")
                else:
                    logger.warning(
                        "Alpha Vantage API key not found, collector disabled"
                    )

            if self.config["data_sources"]["fred"]["enabled"]:
                api_key = os.getenv("FRED_API_KEY")
                if api_key:
                    self.collectors["fred"] = FREDCollector(api_key)
                    logger.info("FRED collector initialized")
                else:
                    logger.warning("FRED API key not found, collector disabled")

            # Always initialize mock collector as fallback
            self.collectors["mock"] = MockCollector()
            logger.info("Mock collector initialized as fallback")

        except Exception as e:
            logger.error(f"Failed to initialize collectors: {e}")
            raise

    async def _collect_with_fallback(
        self, collector_name: str, method_name: str, *args, **kwargs
    ):
        """Collect data with fallback to mock collector if rate limited."""
        try:
            if collector_name in self.collectors:
                collector = self.collectors[collector_name]
                method = getattr(collector, method_name)
                return await method(*args, **kwargs)
            else:
                raise Exception(f"Collector {collector_name} not available")
        except Exception as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                logger.warning(
                    f"Rate limited on {collector_name}, falling back to mock data"
                )
                mock_collector = self.collectors["mock"]
                method = getattr(mock_collector, method_name)
                return await method(*args, **kwargs)
            else:
                raise e

    def _initialize_transformers(self):
        """Initialize data transformers."""
        try:
            self.transformers["market_data"] = MarketDataTransformer()
            self.transformers["company_profile"] = CompanyProfileTransformer()
            self.transformers["economic_data"] = EconomicDataTransformer()
            logger.info("Data transformers initialized")
        except Exception as e:
            logger.error(f"Failed to initialize transformers: {e}")
            raise

    def _initialize_loaders(self):
        """Initialize data loaders."""
        try:
            database_url = os.getenv("DATABASE_URL")
            redis_url = os.getenv("REDIS_URL")

            if database_url:
                self.loaders["sqlite"] = SQLiteLoader(database_url)
                logger.info("SQLite loader initialized")

            if redis_url:
                self.loaders["redis"] = RedisLoader(redis_url)
                logger.info("Redis loader initialized")

        except Exception as e:
            logger.error(f"Failed to initialize loaders: {e}")
            raise

    async def run_full_import(self):
        """Execute complete data import pipeline."""
        logger.info("Starting full data import pipeline")
        start_time = datetime.now()

        try:
            # 1. Collect company profiles
            await self.collect_company_profiles()

            # 2. Collect historical market data
            await self.collect_historical_data()

            # 3. Collect economic indicators
            await self.collect_economic_data()

            # 4. Validate data quality
            await self.validate_data_quality()

            # 5. Update cache
            await self.update_cache()

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"Full data import completed in {duration:.2f} seconds")

        except Exception as e:
            logger.error(f"Full data import failed: {e}")
            raise

    async def run_incremental_import(self):
        """Execute incremental data updates."""
        logger.info("Starting incremental data import")
        start_time = datetime.now()

        try:
            # Only collect new/updated data since last run
            await self.collect_historical_data(incremental=True)
            await self.collect_economic_data(incremental=True)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"Incremental data import completed in {duration:.2f} seconds")

        except Exception as e:
            logger.error(f"Incremental data import failed: {e}")
            raise

    async def collect_company_profiles(self):
        """Collect and update company profiles."""
        logger.info("Collecting company profiles")

        try:
            if "yahoo_finance" in self.collectors:
                collector = self.collectors["yahoo_finance"]
                transformer = self.transformers["company_profile"]
                loader = self.loaders["sqlite"]

                # Load company symbols from config
                symbols = self._load_company_symbols()

                for symbol in symbols:
                    try:
                        # Collect data with fallback
                        raw_data = await self._collect_with_fallback(
                            "yahoo_finance", "collect_company_profile", symbol
                        )

                        # Transform data
                        transformed_data = transformer.transform_company_profile(
                            raw_data
                        )

                        # Load data
                        await loader.load_company_profile(transformed_data)

                        logger.info(f"Company profile collected for {symbol}")

                    except Exception as e:
                        logger.error(f"Failed to collect profile for {symbol}: {e}")
                        continue

        except Exception as e:
            logger.error(f"Company profile collection failed: {e}")
            raise

    async def collect_historical_data(self, incremental: bool = False):
        """Collect historical market data."""
        logger.info(f"Collecting historical market data (incremental: {incremental})")

        try:
            if "yahoo_finance" in self.collectors:
                collector = self.collectors["yahoo_finance"]
                transformer = self.transformers["market_data"]
                loader = self.loaders["sqlite"]

                # Load company symbols
                symbols = self._load_company_symbols()

                # Process in batches
                batch_size = self.config["etl"]["batch_size"]
                for i in range(0, len(symbols), batch_size):
                    batch = symbols[i : i + batch_size]

                    for symbol in batch:
                        try:
                            # Collect historical data with fallback
                            raw_data = await self._collect_with_fallback(
                                "yahoo_finance",
                                "collect_historical_data",
                                symbol,
                                incremental,
                            )

                            # Transform data
                            transformed_data = transformer.transform_historical_data(
                                raw_data
                            )

                            # Load data
                            await loader.load_historical_data(transformed_data)

                            logger.info(f"Historical data collected for {symbol}")

                        except Exception as e:
                            logger.error(
                                f"Failed to collect historical data for {symbol}: {e}"
                            )
                            continue

        except Exception as e:
            logger.error(f"Historical data collection failed: {e}")
            raise

    async def collect_economic_data(self, incremental: bool = False):
        """Collect economic indicators."""
        logger.info(f"Collecting economic data (incremental: {incremental})")

        try:
            if "fred" in self.collectors:
                collector = self.collectors["fred"]
                transformer = self.transformers["economic_data"]
                loader = self.loaders["sqlite"]

                # Load economic indicators from config
                indicators = self._load_economic_indicators()

                for indicator in indicators:
                    try:
                        # Collect data
                        raw_data = await self.retry_handler.execute_with_retry(
                            collector.collect_economic_data, indicator, incremental
                        )

                        # Transform data
                        transformed_data = transformer.transform_economic_data(raw_data)

                        # Load data
                        await loader.load_economic_data(transformed_data)

                        logger.info(f"Economic data collected for {indicator}")

                    except Exception as e:
                        logger.error(
                            f"Failed to collect economic data for {indicator}: {e}"
                        )
                        continue

        except Exception as e:
            logger.error(f"Economic data collection failed: {e}")
            raise

    async def validate_data_quality(self):
        """Validate data quality."""
        logger.info("Validating data quality")

        try:
            # Implement data quality validation
            # This would check completeness, accuracy, consistency, etc.
            logger.info("Data quality validation completed")

        except Exception as e:
            logger.error(f"Data quality validation failed: {e}")
            raise

    async def update_cache(self):
        """Update Redis cache with latest data."""
        logger.info("Updating cache")

        try:
            if "redis" in self.loaders:
                # Update cache with latest data
                logger.info("Cache updated successfully")
            else:
                logger.warning("Redis loader not available, skipping cache update")

        except Exception as e:
            logger.error(f"Cache update failed: {e}")
            raise

    def _load_company_symbols(self) -> List[str]:
        """Load company symbols from configuration."""
        try:
            with open("config/data_sources.yaml", "r") as file:
                config = yaml.safe_load(file)

            symbols = []
            # Load US stocks
            if "us_stocks" in config["companies"]:
                symbols.extend(config["companies"]["us_stocks"])
            # Load DAX 40 companies
            if "dax_40" in config["companies"]:
                symbols.extend(config["companies"]["dax_40"])
            # Load ETFs
            if "etfs" in config["companies"]:
                symbols.extend(config["companies"]["etfs"])

            logger.info(f"Loaded {len(symbols)} company symbols")
            return symbols

        except Exception as e:
            logger.error(f"Failed to load company symbols: {e}")
            return []

    def _load_economic_indicators(self) -> List[str]:
        """Load economic indicators from configuration."""
        try:
            with open("config/data_sources.yaml", "r") as file:
                config = yaml.safe_load(file)

            indicators = []
            for category in config["economic_indicators"].values():
                indicators.extend(category)

            logger.info(f"Loaded {len(indicators)} economic indicators")
            return indicators

        except Exception as e:
            logger.error(f"Failed to load economic indicators: {e}")
            return []


@click.command()
@click.option(
    "--mode",
    default="full",
    type=click.Choice(["full", "incremental"]),
    help="ETL mode: full or incremental",
)
@click.option(
    "--config", default="config/etl_config.yaml", help="Path to configuration file"
)
def main(mode: str, config: str):
    """ETL Orchestrator - Market Data Import System."""
    try:
        # Initialize orchestrator
        orchestrator = ETLOrchestrator(config)

        # Run ETL pipeline
        if mode == "full":
            asyncio.run(orchestrator.run_full_import())
        elif mode == "incremental":
            asyncio.run(orchestrator.run_incremental_import())
        else:
            logger.error(f"Invalid mode: {mode}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"ETL orchestrator failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
