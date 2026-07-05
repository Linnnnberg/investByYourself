"""
TGA (Treasury General Account) Collector
InvestByYourself Financial Platform

Collects daily Treasury General Account balance data from US Treasury API.
TGA is a key component of market liquidity tracking.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp
import pandas as pd

logger = logging.getLogger(__name__)


class TGACollector:
    """TGA data collector for liquidity tracking."""

    def __init__(self):
        """Initialize TGA collector."""
        self.name = "TGA"
        self.base_url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service"
        self.endpoint = "/v1/accounting/dts/operating_cash_balance"
        self.rate_limit = 0.5  # Conservative: 2 requests per second max
        self.timeout = 30
        self.max_retries = 3

    async def collect_tga_data(
        self, incremental: bool = False, lookback_days: int = 730
    ) -> List[Dict[str, Any]]:
        """
        Collect TGA balance data.

        Args:
            incremental: If True, fetch last 30 days only
            lookback_days: Number of days to look back (default 730 = ~2 years)

        Returns:
            List of TGA data records
        """
        try:
            logger.info(f"Collecting TGA data (incremental={incremental})")

            # Determine date range
            end_date = datetime.now()
            if incremental:
                start_date = end_date - timedelta(days=30)
            else:
                start_date = end_date - timedelta(days=lookback_days)

            # Build request parameters
            params = {
                "fields": "record_date,close_today_bal,open_today_bal,open_month_bal",
                "filter": f"record_date:gte:{start_date.strftime('%Y-%m-%d')},record_date:lte:{end_date.strftime('%Y-%m-%d')}",
                "sort": "record_date",
                "page[size]": 10000,
                "format": "json",
            }

            # Fetch data with retry logic
            data = await self._fetch_with_retry(params)

            # Parse and validate
            tga_records = self._parse_tga_data(data)

            logger.info(f"TGA data collected: {len(tga_records)} records")
            return tga_records

        except Exception as e:
            logger.error(f"Failed to collect TGA data: {e}")
            raise

    async def _fetch_with_retry(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data with exponential backoff retry."""
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.base_url}{self.endpoint}",
                        params=params,
                        timeout=aiohttp.ClientTimeout(total=self.timeout),
                    ) as response:
                        response.raise_for_status()
                        data = await response.json()

                        # Check for API errors
                        if "error" in data:
                            raise Exception(f"Treasury API error: {data['error']}")

                        return data

            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"All {self.max_retries} attempts failed: {e}")

        raise last_exception

    def _parse_tga_data(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse and validate raw TGA data."""
        try:
            records = raw_data.get("data", [])
            parsed_records = []

            for record in records:
                # Validate required fields
                if not record.get("record_date") or not record.get("close_today_bal"):
                    logger.warning(f"Skipping invalid record: {record}")
                    continue

                # Parse numeric values (Treasury API returns strings)
                try:
                    close_bal = float(record["close_today_bal"])
                    open_bal = float(record.get("open_today_bal", 0))
                    open_month_bal = float(record.get("open_month_bal", 0))
                except (ValueError, TypeError) as e:
                    logger.warning(f"Skipping record with invalid numeric data: {e}")
                    continue

                # Create standardized record
                parsed_record = {
                    "record_date": record["record_date"],
                    "close_balance": close_bal,
                    "open_balance": open_bal,
                    "open_month_balance": open_month_bal,
                    "daily_change": close_bal - open_bal if open_bal else None,
                    "source": "treasury.gov",
                    "collected_at": datetime.now().isoformat(),
                }

                parsed_records.append(parsed_record)

            return parsed_records

        except Exception as e:
            logger.error(f"Failed to parse TGA data: {e}")
            raise

    def get_data_quality_metrics(
        self, records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate data quality metrics."""
        if not records:
            return {
                "completeness": 0.0,
                "record_count": 0,
                "date_range": None,
                "missing_days": 0,
            }

        # Convert to DataFrame for analysis
        df = pd.DataFrame(records)
        df["record_date"] = pd.to_datetime(df["record_date"])

        # Calculate metrics
        date_range = (df["record_date"].max() - df["record_date"].min()).days
        expected_records = date_range + 1  # Include both end dates
        actual_records = len(df)

        # TGA data only published on business days
        # Rough estimate: ~252 trading days per year
        expected_business_days = int(date_range * (252 / 365))

        completeness = min(
            1.0, actual_records / expected_business_days if expected_business_days > 0 else 0
        )

        return {
            "completeness": round(completeness, 3),
            "record_count": actual_records,
            "date_range": {
                "start": df["record_date"].min().strftime("%Y-%m-%d"),
                "end": df["record_date"].max().strftime("%Y-%m-%d"),
                "days": date_range,
            },
            "missing_days": max(0, expected_business_days - actual_records),
        }
