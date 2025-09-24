"""
Rate Limiter
InvestByYourself Financial Platform

Provides rate limiting functionality for API calls.
"""

import asyncio
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter for API calls."""

    def __init__(self):
        """Initialize rate limiter."""
        self.limits = {
            "yahoo_finance": 1.0,  # requests per second
            "alpha_vantage": 0.083,  # 5 requests per minute
            "fred": 2.0,  # 120 requests per minute
        }
        self.last_calls = {}

    async def wait_if_needed(self, source: str):
        """Wait if necessary to respect rate limits."""
        if source not in self.limits:
            return

        rate_limit = self.limits[source]
        min_interval = 1.0 / rate_limit

        if source in self.last_calls:
            time_since_last = asyncio.get_event_loop().time() - self.last_calls[source]
            if time_since_last < min_interval:
                wait_time = min_interval - time_since_last
                logger.debug(f"Rate limiting {source}: waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)

        self.last_calls[source] = asyncio.get_event_loop().time()
