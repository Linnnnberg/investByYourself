"""
Market Data Transformer
InvestByYourself Financial Platform

Transforms raw market data into standardized format.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class MarketDataTransformer:
    """Market data transformer."""

    def __init__(self):
        """Initialize market data transformer."""
        self.name = "Market Data Transformer"

    def transform_historical_data(
        self, raw_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Transform historical market data."""
        try:
            logger.info(f"Transforming {len(raw_data)} historical data records")

            transformed_data = []
            for record in raw_data:
                # Validate and clean data
                if self._validate_historical_record(record):
                    transformed_record = self._clean_historical_record(record)
                    transformed_data.append(transformed_record)
                else:
                    logger.warning(
                        f"Invalid historical record skipped: {record.get('symbol', 'unknown')}"
                    )

            logger.info(f"Transformed {len(transformed_data)} historical data records")
            return transformed_data

        except Exception as e:
            logger.error(f"Failed to transform historical data: {e}")
            raise

    def _validate_historical_record(self, record: Dict[str, Any]) -> bool:
        """Validate historical data record."""
        required_fields = ["symbol", "date", "close"]

        for field in required_fields:
            if field not in record or record[field] is None:
                return False

        # Validate price data
        if record.get("close", 0) <= 0:
            return False

        return True

    def _clean_historical_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and standardize historical data record."""
        cleaned_record = {
            "symbol": record.get("symbol", "").upper(),
            "date": record.get("date", ""),
            "open": self._clean_price(record.get("open")),
            "high": self._clean_price(record.get("high")),
            "low": self._clean_price(record.get("low")),
            "close": self._clean_price(record.get("close")),
            "volume": self._clean_volume(record.get("volume")),
            "adjusted_close": self._clean_price(record.get("adjusted_close")),
            "source": record.get("source", "unknown"),
            "created_at": record.get("created_at", datetime.now().isoformat()),
        }

        return cleaned_record

    def _clean_price(self, price: Any) -> float:
        """Clean and convert price to float."""
        if price is None:
            return None

        try:
            return float(price)
        except (ValueError, TypeError):
            return None

    def _clean_volume(self, volume: Any) -> int:
        """Clean and convert volume to int."""
        if volume is None:
            return None

        try:
            return int(volume)
        except (ValueError, TypeError):
            return None
