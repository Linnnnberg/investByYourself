"""
Redis Data Loader
InvestByYourself Financial Platform

Loads data into Redis cache for fast access.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List

import redis

logger = logging.getLogger(__name__)


class RedisLoader:
    """Redis data loader."""

    def __init__(self, redis_url: str):
        """Initialize Redis loader."""
        self.redis_url = redis_url
        self.redis_client = self._create_redis_client()
        self.name = "Redis Loader"

    def _create_redis_client(self):
        """Create Redis client from URL."""
        try:
            # Parse Redis URL
            if self.redis_url.startswith("redis://:"):
                # Format: redis://:password@host:port/db
                parts = self.redis_url.replace("redis://:", "").split("@")
                if len(parts) == 2:
                    password = parts[0]
                    host_port_db = parts[1].split("/")
                    if len(host_port_db) == 2:
                        host_port = host_port_db[0].split(":")
                        if len(host_port) == 2:
                            host = host_port[0]
                            port = int(host_port[1])
                            db = int(host_port_db[1])

                            return redis.Redis(
                                host=host,
                                port=port,
                                password=password,
                                db=db,
                                decode_responses=True,
                            )

            raise ValueError(f"Invalid Redis URL format: {self.redis_url}")

        except Exception as e:
            logger.error(f"Failed to create Redis client: {e}")
            raise

    async def load_company_profile(self, data: Dict[str, Any]):
        """Load company profile to Redis cache."""
        try:
            symbol = data.get("symbol", "unknown")
            logger.info(f"Loading company profile to cache for {symbol}")

            # Cache company profile
            cache_key = f"company_profile:{symbol}"
            self.redis_client.setex(
                cache_key, 3600, json.dumps(data, default=str)  # 1 hour TTL
            )

            logger.info(f"Company profile cached for {symbol}")

        except Exception as e:
            logger.error(
                f"Failed to cache company profile for {data.get('symbol', 'unknown')}: {e}"
            )
            raise

    async def load_historical_data(self, data: List[Dict[str, Any]]):
        """Load historical data to Redis cache."""
        try:
            logger.info(f"Loading {len(data)} historical data records to cache")

            # Group data by symbol
            symbol_data = {}
            for record in data:
                symbol = record["symbol"]
                if symbol not in symbol_data:
                    symbol_data[symbol] = []
                symbol_data[symbol].append(record)

            # Cache data for each symbol
            for symbol, records in symbol_data.items():
                cache_key = f"historical_data:{symbol}"
                self.redis_client.setex(
                    cache_key, 1800, json.dumps(records, default=str)  # 30 minutes TTL
                )

            logger.info(f"Historical data cached for {len(symbol_data)} symbols")

        except Exception as e:
            logger.error(f"Failed to cache historical data: {e}")
            raise

    async def load_economic_data(self, data: List[Dict[str, Any]]):
        """Load economic data to Redis cache."""
        try:
            logger.info(f"Loading {len(data)} economic data records to cache")

            # Group data by indicator
            indicator_data = {}
            for record in data:
                indicator = record["indicator_code"]
                if indicator not in indicator_data:
                    indicator_data[indicator] = []
                indicator_data[indicator].append(record)

            # Cache data for each indicator
            for indicator, records in indicator_data.items():
                cache_key = f"economic_data:{indicator}"
                self.redis_client.setex(
                    cache_key, 3600, json.dumps(records, default=str)  # 1 hour TTL
                )

            logger.info(f"Economic data cached for {len(indicator_data)} indicators")

        except Exception as e:
            logger.error(f"Failed to cache economic data: {e}")
            raise
