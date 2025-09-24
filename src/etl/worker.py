"""
ETL Worker for investByYourself Platform
Story-005: ETL & Database Architecture Design

Main worker that orchestrates data collection, transformation, and loading.
"""

import asyncio
import logging
import os
import signal
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List

import structlog

# Add src directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.etl.cache.data_cache_manager import DataCacheManager
from src.etl.collectors.yahoo_finance_collector import YahooFinanceCollector
from src.etl.loaders.data_loader import DataLoader
from src.etl.transformers.data_transformer import DataTransformer
from src.etl.utils.pipeline_scheduler import PipelineScheduler
from src.etl.utils.retry_handler import RetryHandler
from src.etl.validators.data_validator import DataValidator

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


class ETLWorker:
    """Main ETL worker that orchestrates the entire data pipeline."""

    def __init__(self):
        """Initialize the ETL worker with all components."""
        self.running = False
        self.scheduler = PipelineScheduler()
        self.retry_handler = RetryHandler()

        # Initialize components
        self.collectors = {}
        self.transformer = None
        self.loader = None
        self.validator = None
        self.cache_manager = None

        # Configuration
        self.batch_size = int(os.getenv("ETL_BATCH_SIZE", 1000))
        self.max_workers = int(os.getenv("ETL_MAX_WORKERS", 4))
        self.retry_attempts = int(os.getenv("ETL_RETRY_ATTEMPTS", 3))
        self.retry_delay = int(os.getenv("ETL_RETRY_DELAY", 5))

        # Data collection state
        self.last_collection_time = {}
        self.collection_stats = {}

        logger.info(
            "ETL Worker initialized",
            batch_size=self.batch_size,
            max_workers=self.max_workers,
        )

    async def initialize(self):
        """Initialize all ETL components."""
        try:
            logger.info("Initializing ETL components...")

            # Initialize data collectors
            await self._initialize_collectors()

            # Initialize data transformer
            self.transformer = DataTransformer()

            # Initialize data loader
            self.loader = DataLoader(database_url=os.getenv("DATABASE_URL"))

            # Initialize data validator
            self.validator = DataValidator()

            # Initialize cache manager
            self.cache_manager = DataCacheManager(redis_url=os.getenv("REDIS_URL"))

            # Set up scheduled tasks
            self._setup_scheduled_tasks()

            logger.info("ETL components initialized successfully")

        except Exception as e:
            logger.error("Failed to initialize ETL components", error=str(e))
            raise

    async def _initialize_collectors(self):
        """Initialize data collectors for different sources."""
        try:
            # Initialize Yahoo Finance collector
            self.collectors["yahoo_finance"] = YahooFinanceCollector()

            # Initialize other collectors as needed
            # self.collectors['alpha_vantage'] = AlphaVantageCollector()
            # self.collectors['fred'] = FredCollector()
            # self.collectors['api_ninjas'] = APINinjasCollector()

            logger.info(
                "Data collectors initialized", sources=list(self.collectors.keys())
            )

        except Exception as e:
            logger.error("Failed to initialize data collectors", error=str(e))
            raise

    def _setup_scheduled_tasks(self):
        """Set up scheduled ETL tasks."""
        try:
            # Add real-time data collection (every 5 minutes during market hours)
            self.scheduler.add_task(
                "real_time_collection", self._collect_real_time_data, "hourly"
            )

            # Add daily data collection (9 AM UTC)
            self.scheduler.add_task(
                "daily_collection", self._collect_daily_data, "daily"
            )

            # Add weekly data collection (Monday 9 AM UTC)
            self.scheduler.add_task(
                "weekly_collection", self._collect_weekly_data, "weekly"
            )

            logger.info("Scheduled tasks configured")

        except Exception as e:
            logger.error("Failed to set up scheduled tasks", error=str(e))
            raise

    async def start(self):
        """Start the ETL worker."""
        try:
            logger.info("Starting ETL worker...")

            # Initialize components
            await self.initialize()

            # Set running flag
            self.running = True

            # Start scheduler
            await self.scheduler.run_scheduled_tasks()

        except Exception as e:
            logger.error("Failed to start ETL worker", error=str(e))
            self.running = False
            raise

    async def stop(self):
        """Stop the ETL worker."""
        logger.info("Stopping ETL worker...")
        self.running = False

        # Clean up resources
        if self.loader:
            await self.loader.__aexit__(None, None, None)

        if self.cache_manager:
            # Close Redis connection
            pass

        logger.info("ETL worker stopped")

    async def _collect_real_time_data(self):
        """Collect real-time market data."""
        try:
            logger.info("Starting real-time data collection")

            # Define symbols to collect (top 100 by market cap)
            symbols = await self._get_top_symbols(100)

            # Collect data in batches
            for i in range(0, len(symbols), self.batch_size):
                batch = symbols[i : i + self.batch_size]
                await self._process_symbol_batch(batch, "real_time")

                # Rate limiting between batches
                await asyncio.sleep(1)

            logger.info(
                "Real-time data collection completed", symbols_processed=len(symbols)
            )

        except Exception as e:
            logger.error("Real-time data collection failed", error=str(e))
            raise

    async def _collect_daily_data(self):
        """Collect daily fundamental and economic data."""
        try:
            logger.info("Starting daily data collection")

            # Collect company fundamentals
            symbols = await self._get_active_symbols()
            await self._collect_company_fundamentals(symbols)

            # Collect economic indicators
            await self._collect_economic_data()

            # Collect earnings data
            await self._collect_earnings_data()

            logger.info("Daily data collection completed")

        except Exception as e:
            logger.error("Daily data collection failed", error=str(e))
            raise

    async def _collect_weekly_data(self):
        """Collect weekly analysis and technical indicators."""
        try:
            logger.info("Starting weekly data collection")

            # Collect technical indicators
            symbols = await self._get_active_symbols()
            await self._collect_technical_indicators(symbols)

            # Update materialized views
            await self._refresh_materialized_views()

            # Generate weekly reports
            await self._generate_weekly_reports()

            logger.info("Weekly data collection completed")

        except Exception as e:
            logger.error("Weekly data collection failed", error=str(e))
            raise

    async def _process_symbol_batch(self, symbols: List[str], data_type: str):
        """Process a batch of symbols for data collection."""
        try:
            logger.info(
                "Processing symbol batch",
                symbols_count=len(symbols),
                data_type=data_type,
            )

            # Collect data from Yahoo Finance
            collector = self.collectors["yahoo_finance"]

            # Use retry handler for data collection
            raw_data = await self.retry_handler.execute_with_retry(
                collector.collect_market_data, symbols
            )

            # Transform data
            transformed_data = []
            for data in raw_data:
                if isinstance(data, Exception):
                    logger.warning("Data collection failed for symbol", error=str(data))
                    continue

                try:
                    transformed = self.transformer.transform_stock_data(data)
                    if self.validator.validate_transformed_data(transformed):
                        transformed_data.append(transformed)
                    else:
                        logger.warning(
                            "Data validation failed",
                            symbol=data.get("symbol", "unknown"),
                        )
                except Exception as e:
                    logger.error(
                        "Data transformation failed",
                        symbol=data.get("symbol", "unknown"),
                        error=str(e),
                    )

            # Load data to database
            if transformed_data:
                await self._load_transformed_data(transformed_data)

                # Update cache
                await self._update_cache(transformed_data)

            # Update collection stats
            self._update_collection_stats(
                data_type, len(symbols), len(transformed_data)
            )

            logger.info(
                "Symbol batch processed",
                symbols_count=len(symbols),
                successful=len(transformed_data),
            )

        except Exception as e:
            logger.error(
                "Failed to process symbol batch",
                symbols_count=len(symbols),
                error=str(e),
            )
            raise

    async def _load_transformed_data(self, transformed_data: List[Dict[str, Any]]):
        """Load transformed data to the database."""
        try:
            async with self.loader:
                for data in transformed_data:
                    # Load company data
                    company_id = await self.loader.load_company_data(data["company"])

                    # Load stock prices
                    if data["prices"]:
                        await self.loader.load_stock_prices(company_id, data["prices"])

            logger.info(
                "Data loaded to database", records_processed=len(transformed_data)
            )

        except Exception as e:
            logger.error("Failed to load data to database", error=str(e))
            raise

    async def _update_cache(self, transformed_data: List[Dict[str, Any]]):
        """Update cache with new data."""
        try:
            for data in transformed_data:
                symbol = data["company"]["symbol"]

                # Cache company data
                self.cache_manager.cache_company_data(symbol, data["company"])

                # Cache latest price
                if data["prices"]:
                    latest_price = data["prices"][-1]
                    self.cache_manager.cache_company_data(
                        f"{symbol}:price",
                        latest_price,
                        ttl=300,  # 5 minutes for price data
                    )

            logger.info("Cache updated", records_processed=len(transformed_data))

        except Exception as e:
            logger.error("Failed to update cache", error=str(e))
            # Don't raise - cache failures shouldn't stop the pipeline

    async def _get_top_symbols(self, limit: int) -> List[str]:
        """Get top symbols by market cap from database."""
        # This would query the database for top symbols
        # For now, return a sample list
        return ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "BRK-B"]

    async def _get_active_symbols(self) -> List[str]:
        """Get all active symbols from database."""
        # This would query the database for active symbols
        # For now, return a sample list
        return ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "BRK-B"]

    async def _collect_company_fundamentals(self, symbols: List[str]):
        """Collect company fundamental data."""
        logger.info("Collecting company fundamentals", symbols_count=len(symbols))
        # Implementation for collecting fundamentals
        pass

    async def _collect_economic_data(self):
        """Collect economic indicator data."""
        logger.info("Collecting economic data")
        # Implementation for collecting economic data
        pass

    async def _collect_earnings_data(self):
        """Collect earnings and transcript data."""
        logger.info("Collecting earnings data")
        # Implementation for collecting earnings data
        pass

    async def _collect_technical_indicators(self, symbols: List[str]):
        """Collect technical analysis indicators."""
        logger.info("Collecting technical indicators", symbols_count=len(symbols))
        # Implementation for collecting technical indicators
        pass

    async def _refresh_materialized_views(self):
        """Refresh database materialized views."""
        logger.info("Refreshing materialized views")
        # Implementation for refreshing views
        pass

    async def _generate_weekly_reports(self):
        """Generate weekly analysis reports."""
        logger.info("Generating weekly reports")
        # Implementation for generating reports
        pass

    def _update_collection_stats(self, data_type: str, total: int, successful: int):
        """Update collection statistics."""
        if data_type not in self.collection_stats:
            self.collection_stats[data_type] = {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "last_collection": None,
            }

        stats = self.collection_stats[data_type]
        stats["total"] += total
        stats["successful"] += successful
        stats["failed"] += total - successful
        stats["last_collection"] = datetime.now()

    def get_status(self) -> Dict[str, Any]:
        """Get current worker status."""
        return {
            "running": self.running,
            "batch_size": self.batch_size,
            "max_workers": self.max_workers,
            "collection_stats": self.collection_stats,
            "last_collection_time": self.last_collection_time,
        }


async def main():
    """Main entry point for the ETL worker."""
    worker = ETLWorker()

    # Set up signal handlers
    def signal_handler(signum, frame):
        logger.info("Received signal, shutting down...", signal=signum)
        asyncio.create_task(worker.stop())

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        await worker.start()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error("ETL worker failed", error=str(e))
        sys.exit(1)
    finally:
        await worker.stop()


if __name__ == "__main__":
    asyncio.run(main())
