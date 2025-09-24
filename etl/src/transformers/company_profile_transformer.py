"""
Company Profile Transformer
InvestByYourself Financial Platform

Transforms raw company profile data into standardized format.
"""

import logging
from datetime import datetime
from typing import Any, Dict

logger = logging.getLogger(__name__)


class CompanyProfileTransformer:
    """Company profile transformer."""

    def __init__(self):
        """Initialize company profile transformer."""
        self.name = "Company Profile Transformer"

    def transform_company_profile(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform company profile data."""
        try:
            logger.info(
                f"Transforming company profile for {raw_data.get('symbol', 'unknown')}"
            )

            # Validate data
            if not self._validate_company_profile(raw_data):
                raise ValueError("Invalid company profile data")

            # Clean and standardize data
            transformed_data = self._clean_company_profile(raw_data)

            logger.info(
                f"Company profile transformed for {transformed_data.get('symbol', 'unknown')}"
            )
            return transformed_data

        except Exception as e:
            logger.error(f"Failed to transform company profile: {e}")
            raise

    def _validate_company_profile(self, data: Dict[str, Any]) -> bool:
        """Validate company profile data."""
        required_fields = ["symbol", "name"]

        for field in required_fields:
            if field not in data or not data[field]:
                return False

        return True

    def _clean_company_profile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and standardize company profile data."""
        cleaned_data = {
            "symbol": data.get("symbol", "").upper().strip(),
            "name": data.get("name", "").strip(),
            "sector": data.get("sector", "").strip(),
            "industry": data.get("industry", "").strip(),
            "exchange": data.get("exchange", "").strip(),
            "currency": data.get("currency", "USD").strip(),
            "country": data.get("country", "").strip(),
            "website": data.get("website", "").strip(),
            "description": data.get("description", "").strip(),
            "employee_count": self._clean_integer(data.get("employee_count")),
            "market_cap": self._clean_float(data.get("market_cap")),
            "enterprise_value": self._clean_float(data.get("enterprise_value")),
            "ceo": data.get("ceo", "").strip(),
            "headquarters": data.get("headquarters", "").strip(),
            "founded_year": self._clean_integer(data.get("founded_year")),
            "is_active": bool(data.get("is_active", True)),
            "created_at": data.get("created_at", datetime.now().isoformat()),
            "updated_at": data.get("updated_at", datetime.now().isoformat()),
        }

        return cleaned_data

    def _clean_string(self, value: Any) -> str:
        """Clean and convert to string."""
        if value is None:
            return ""

        return str(value).strip()

    def _clean_integer(self, value: Any) -> int:
        """Clean and convert to integer."""
        if value is None:
            return None

        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def _clean_float(self, value: Any) -> float:
        """Clean and convert to float."""
        if value is None:
            return None

        try:
            return float(value)
        except (ValueError, TypeError):
            return None
