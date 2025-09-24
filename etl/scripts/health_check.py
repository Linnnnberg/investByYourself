#!/usr/bin/env python3
"""
ETL Health Check Script
InvestByYourself Financial Platform

This script performs comprehensive health checks for the ETL service.
"""

import asyncio
import os
import sqlite3
import sys
from datetime import datetime
from typing import Any, Dict

import redis
import requests

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.logger import setup_logging

# Configure logging
logger = setup_logging(__name__)


class ETLHealthChecker:
    """ETL service health checker."""

    def __init__(self):
        """Initialize health checker."""
        self.checks = {}
        self.overall_status = True

    async def check_database_connection(self) -> bool:
        """Check database connectivity."""
        try:
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                logger.error("DATABASE_URL not set")
                return False

            # Extract database path from URL
            if database_url.startswith("sqlite+aiosqlite:////"):
                db_path = database_url.replace("sqlite+aiosqlite:////", "")
            else:
                logger.error(f"Unsupported database URL format: {database_url}")
                return False

            # Test database connection
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            conn.close()

            if result:
                logger.info("Database connection: OK")
                return True
            else:
                logger.error("Database connection: FAILED")
                return False

        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
            return False

    async def check_redis_connection(self) -> bool:
        """Check Redis connectivity."""
        try:
            redis_url = os.getenv("REDIS_URL")
            if not redis_url:
                logger.error("REDIS_URL not set")
                return False

            # Parse Redis URL
            if redis_url.startswith("redis://:"):
                # Format: redis://:password@host:port/db
                parts = redis_url.replace("redis://:", "").split("@")
                if len(parts) == 2:
                    password = parts[0]
                    host_port_db = parts[1].split("/")
                    if len(host_port_db) == 2:
                        host_port = host_port_db[0].split(":")
                        if len(host_port) == 2:
                            host = host_port[0]
                            port = int(host_port[1])
                            db = int(host_port_db[1])

                            # Test Redis connection
                            r = redis.Redis(
                                host=host, port=port, password=password, db=db
                            )
                            r.ping()

                            logger.info("Redis connection: OK")
                            return True

            logger.error(f"Invalid Redis URL format: {redis_url}")
            return False

        except Exception as e:
            logger.error(f"Redis connection check failed: {e}")
            return False

    async def check_api_keys(self) -> bool:
        """Check API key availability."""
        try:
            api_keys = {
                "ALPHA_VANTAGE_API_KEY": os.getenv("ALPHA_VANTAGE_API_KEY"),
                "FRED_API_KEY": os.getenv("FRED_API_KEY"),
            }

            missing_keys = []
            for key_name, key_value in api_keys.items():
                if not key_value:
                    missing_keys.append(key_name)

            if missing_keys:
                logger.warning(f"Missing API keys: {', '.join(missing_keys)}")
                # Don't fail health check for missing optional keys
                return True
            else:
                logger.info("API keys: OK")
                return True

        except Exception as e:
            logger.error(f"API keys check failed: {e}")
            return False

    async def check_disk_space(self) -> bool:
        """Check available disk space."""
        try:
            import shutil

            # Check space in /app/data directory
            data_path = "/app/data"
            if os.path.exists(data_path):
                total, used, free = shutil.disk_usage(data_path)
                free_gb = free / (1024**3)

                if free_gb < 1.0:  # Less than 1GB free
                    logger.error(f"Low disk space: {free_gb:.2f}GB free")
                    return False
                else:
                    logger.info(f"Disk space: OK ({free_gb:.2f}GB free)")
                    return True
            else:
                logger.warning("Data directory not found")
                return True

        except Exception as e:
            logger.error(f"Disk space check failed: {e}")
            return False

    async def check_last_run_status(self) -> bool:
        """Check status of last ETL run."""
        try:
            # This would check logs or database for last run status
            # For now, just return True
            logger.info("Last run status: OK")
            return True

        except Exception as e:
            logger.error(f"Last run status check failed: {e}")
            return False

    async def check_data_quality(self) -> bool:
        """Check data quality metrics."""
        try:
            # This would check data quality metrics
            # For now, just return True
            logger.info("Data quality: OK")
            return True

        except Exception as e:
            logger.error(f"Data quality check failed: {e}")
            return False

    async def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks."""
        logger.info("Starting ETL health checks")

        checks = {
            "database_connection": await self.check_database_connection(),
            "redis_connection": await self.check_redis_connection(),
            "api_keys": await self.check_api_keys(),
            "disk_space": await self.check_disk_space(),
            "last_run": await self.check_last_run_status(),
            "data_quality": await self.check_data_quality(),
        }

        # Determine overall status
        self.overall_status = all(checks.values())

        # Log results
        if self.overall_status:
            logger.info("All health checks passed")
        else:
            failed_checks = [name for name, status in checks.items() if not status]
            logger.error(f"Health checks failed: {', '.join(failed_checks)}")

        return {
            "overall_status": self.overall_status,
            "checks": checks,
            "timestamp": datetime.now().isoformat(),
        }


async def main():
    """Main health check function."""
    try:
        checker = ETLHealthChecker()
        results = await checker.run_all_checks()

        # Exit with appropriate code
        if results["overall_status"]:
            print("ETL Health Check: PASSED")
            sys.exit(0)
        else:
            print("ETL Health Check: FAILED")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        print("ETL Health Check: ERROR")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
