#!/usr/bin/env python3
"""
ETL Scheduler
InvestByYourself Financial Platform

Schedules and manages ETL operations using cron-like functionality.
"""

import asyncio
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List

import schedule

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from etl_orchestrator import ETLOrchestrator

from utils.logger import setup_logging

# Configure logging
logger = setup_logging(__name__)


class ETLScheduler:
    """ETL scheduler for automated data import."""

    def __init__(self, config_path: str = "config/etl_config.yaml"):
        """Initialize ETL scheduler."""
        self.orchestrator = ETLOrchestrator(config_path)
        self.schedule_config = self._load_schedule_config()
        self.running = False

    def _load_schedule_config(self) -> Dict[str, Any]:
        """Load scheduling configuration."""
        try:
            import yaml

            with open("config/etl_config.yaml", "r") as file:
                config = yaml.safe_load(file)
            return config.get("scheduling", {})
        except Exception as e:
            logger.error(f"Failed to load schedule config: {e}")
            return {}

    def setup_schedules(self):
        """Set up scheduled ETL jobs."""
        try:
            if not self.schedule_config.get("enabled", False):
                logger.info("ETL scheduling is disabled")
                return

            jobs = self.schedule_config.get("jobs", {})

            # Daily market data collection
            if jobs.get("daily_market_data", {}).get("enabled", False):
                schedule_time = jobs["daily_market_data"]["schedule"]
                schedule.every().monday.at("06:00").do(self._run_daily_market_data)
                schedule.every().tuesday.at("06:00").do(self._run_daily_market_data)
                schedule.every().wednesday.at("06:00").do(self._run_daily_market_data)
                schedule.every().thursday.at("06:00").do(self._run_daily_market_data)
                schedule.every().friday.at("06:00").do(self._run_daily_market_data)
                logger.info("Daily market data collection scheduled")

            # Weekly company profiles
            if jobs.get("weekly_company_profiles", {}).get("enabled", False):
                schedule.every().monday.at("02:00").do(
                    self._run_weekly_company_profiles
                )
                logger.info("Weekly company profiles collection scheduled")

            # Monthly economic data
            if jobs.get("monthly_economic_data", {}).get("enabled", False):
                schedule.every().day.at("03:00").do(self._run_monthly_economic_data)
                logger.info("Monthly economic data collection scheduled")

            # Weekly data validation
            if jobs.get("weekly_data_validation", {}).get("enabled", False):
                schedule.every().sunday.at("04:00").do(self._run_weekly_data_validation)
                logger.info("Weekly data validation scheduled")

            logger.info("ETL schedules configured successfully")

        except Exception as e:
            logger.error(f"Failed to setup schedules: {e}")
            raise

    def _run_daily_market_data(self):
        """Run daily market data collection."""
        try:
            logger.info("Starting scheduled daily market data collection")
            asyncio.run(self.orchestrator.collect_historical_data(incremental=True))
            logger.info("Scheduled daily market data collection completed")
        except Exception as e:
            logger.error(f"Scheduled daily market data collection failed: {e}")

    def _run_weekly_company_profiles(self):
        """Run weekly company profiles collection."""
        try:
            logger.info("Starting scheduled weekly company profiles collection")
            asyncio.run(self.orchestrator.collect_company_profiles())
            logger.info("Scheduled weekly company profiles collection completed")
        except Exception as e:
            logger.error(f"Scheduled weekly company profiles collection failed: {e}")

    def _run_monthly_economic_data(self):
        """Run monthly economic data collection."""
        try:
            logger.info("Starting scheduled monthly economic data collection")
            asyncio.run(self.orchestrator.collect_economic_data(incremental=True))
            logger.info("Scheduled monthly economic data collection completed")
        except Exception as e:
            logger.error(f"Scheduled monthly economic data collection failed: {e}")

    def _run_weekly_data_validation(self):
        """Run weekly data validation."""
        try:
            logger.info("Starting scheduled weekly data validation")
            asyncio.run(self.orchestrator.validate_data_quality())
            logger.info("Scheduled weekly data validation completed")
        except Exception as e:
            logger.error(f"Scheduled weekly data validation failed: {e}")

    def start(self):
        """Start the ETL scheduler."""
        try:
            logger.info("Starting ETL scheduler...")
            self.setup_schedules()
            self.running = True

            logger.info("ETL scheduler started successfully")
            logger.info("Press Ctrl+C to stop the scheduler")

            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            logger.info("ETL scheduler stopped by user")
            self.running = False
        except Exception as e:
            logger.error(f"ETL scheduler failed: {e}")
            self.running = False
            raise

    def stop(self):
        """Stop the ETL scheduler."""
        logger.info("Stopping ETL scheduler...")
        self.running = False


def main():
    """Main scheduler function."""
    try:
        scheduler = ETLScheduler()
        scheduler.start()
    except Exception as e:
        logger.error(f"ETL scheduler failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
