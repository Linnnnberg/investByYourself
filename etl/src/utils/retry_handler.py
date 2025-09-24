"""
Retry Handler
InvestByYourself Financial Platform

Provides retry logic with exponential backoff for ETL operations.
"""

import asyncio
import logging
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class RetryHandler:
    """Retry handler with exponential backoff."""

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        """Initialize retry handler."""
        self.max_retries = max_retries
        self.base_delay = base_delay

    async def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic."""
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)

                if attempt > 0:
                    logger.info(f"Function succeeded on attempt {attempt + 1}")

                return result

            except Exception as e:
                last_exception = e

                if attempt < self.max_retries:
                    delay = self.base_delay * (2**attempt)
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"All {self.max_retries + 1} attempts failed. Last error: {e}"
                    )

        raise last_exception
