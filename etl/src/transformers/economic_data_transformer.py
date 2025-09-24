"""
Economic Data Transformer
InvestByYourself Financial Platform

Transforms raw economic data into standardized format.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class EconomicDataTransformer:
    """Economic data transformer."""

    def __init__(self):
        """Initialize economic data transformer."""
        self.name = "Economic Data Transformer"

    def transform_economic_data(
        self, raw_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Transform economic data."""
        try:
            logger.info(f"Transforming {len(raw_data)} economic data records")

            transformed_data = []
            for record in raw_data:
                # Validate and clean data
                if self._validate_economic_record(record):
                    transformed_record = self._clean_economic_record(record)
                    transformed_data.append(transformed_record)
                else:
                    logger.warning(
                        f"Invalid economic record skipped: {record.get('indicator_code', 'unknown')}"
                    )

            logger.info(f"Transformed {len(transformed_data)} economic data records")
            return transformed_data

        except Exception as e:
            logger.error(f"Failed to transform economic data: {e}")
            raise

    def _validate_economic_record(self, record: Dict[str, Any]) -> bool:
        """Validate economic data record."""
        required_fields = ["indicator_code", "data_date", "value"]

        for field in required_fields:
            if field not in record or record[field] is None:
                return False

        return True

    def _clean_economic_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and standardize economic data record."""
        cleaned_record = {
            "indicator_code": record.get("indicator_code", "").strip(),
            "indicator_name": record.get("indicator_name", "").strip(),
            "data_date": record.get("data_date", ""),
            "value": self._clean_float(record.get("value")),
            "unit": record.get("unit", "").strip(),
            "frequency": record.get("frequency", "daily").strip(),
            "source": record.get("source", "unknown"),
            "created_at": record.get("created_at", datetime.now().isoformat()),
        }

        return cleaned_record

    def _clean_float(self, value: Any) -> float:
        """Clean and convert to float."""
        if value is None:
            return None

        try:
            return float(value)
        except (ValueError, TypeError):
            return None
