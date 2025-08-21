"""
Financial Data Validation Tests for investByYourself

This module tests data quality validation, API response formats,
financial calculation accuracy, and data source consistency.

Part of Story-001: Financial Data Testing Framework
"""

from datetime import datetime, timedelta
from decimal import Decimal, getcontext
from typing import Any, Dict, List

import numpy as np
import pandas as pd
import pytest

# Set precision for financial calculations
getcontext().prec = 28


class TestDataQualityValidation:
    """Test data quality validation functions."""

    def test_validate_stock_price_data(self):
        """Test stock price data validation."""
        # Valid price data
        valid_prices = pd.DataFrame(
            {
                "symbol": ["AAPL", "GOOGL", "MSFT"],
                "price": [150.25, 2800.50, 350.75],
                "volume": [1000000, 500000, 750000],
                "timestamp": [datetime.now(), datetime.now(), datetime.now()],
            }
        )

        # Test validation
        assert self._validate_price_data(valid_prices) is True

        # Invalid price data (negative price)
        invalid_prices = valid_prices.copy()
        invalid_prices.loc[0, "price"] = -150.25

        assert self._validate_price_data(invalid_prices) is False

    def test_validate_financial_ratios(self):
        """Test financial ratio validation."""
        # Valid ratios
        valid_ratios = {
            "pe_ratio": 15.5,
            "pb_ratio": 2.1,
            "roe": 0.18,
            "debt_to_equity": 0.45,
        }

        assert self._validate_financial_ratios(valid_ratios) is True

        # Invalid ratios (negative PE ratio)
        invalid_ratios = valid_ratios.copy()
        invalid_ratios["pe_ratio"] = -15.5

        assert self._validate_financial_ratios(invalid_ratios) is False

    def test_validate_portfolio_data(self):
        """Test portfolio data validation."""
        # Valid portfolio
        valid_portfolio = {
            "total_value": 100000.00,
            "cash": 15000.00,
            "positions": [
                {"symbol": "AAPL", "shares": 100, "value": 15025.00},
                {"symbol": "GOOGL", "shares": 5, "value": 14002.50},
            ],
        }

        assert self._validate_portfolio_data(valid_portfolio) is True

        # Invalid portfolio (negative cash)
        invalid_portfolio = valid_portfolio.copy()
        invalid_portfolio["cash"] = -15000.00

        assert self._validate_portfolio_data(invalid_portfolio) is False

    def _validate_price_data(self, df: pd.DataFrame) -> bool:
        """Validate price data quality."""
        try:
            # Check for required columns
            required_cols = ["symbol", "price", "volume", "timestamp"]
            if not all(col in df.columns for col in required_cols):
                return False

            # Check for valid prices (positive)
            if (df["price"] <= 0).any():
                return False

            # Check for valid volumes (non-negative)
            if (df["volume"] < 0).any():
                return False

            # Check for valid timestamps
            if df["timestamp"].isna().any():
                return False

            return True
        except Exception:
            return False

    def _validate_financial_ratios(self, ratios: Dict[str, float]) -> bool:
        """Validate financial ratios."""
        try:
            # PE ratio should be positive
            if ratios.get("pe_ratio", 0) <= 0:
                return False

            # PB ratio should be positive
            if ratios.get("pb_ratio", 0) <= 0:
                return False

            # ROE should be reasonable (-100% to 100%)
            if not -1 <= ratios.get("roe", 0) <= 1:
                return False

            # Debt to equity should be reasonable
            if ratios.get("debt_to_equity", 0) < 0:
                return False

            return True
        except Exception:
            return False

    def _validate_portfolio_data(self, portfolio: Dict[str, Any]) -> bool:
        """Validate portfolio data."""
        try:
            # Check total value is positive
            if portfolio.get("total_value", 0) <= 0:
                return False

            # Check cash is non-negative
            if portfolio.get("cash", 0) < 0:
                return False

            # Check positions
            positions = portfolio.get("positions", [])
            for position in positions:
                if position.get("shares", 0) <= 0:
                    return False
                if position.get("value", 0) <= 0:
                    return False

            return True
        except Exception:
            return False


class TestAPIResponseFormat:
    """Test API response format validation."""

    def test_validate_yahoo_finance_response(self):
        """Test Yahoo Finance API response format."""
        # Mock valid response
        valid_response = {
            "symbol": "AAPL",
            "price": 150.25,
            "volume": 1000000,
            "market_cap": 2500000000000,
            "pe_ratio": 15.5,
            "timestamp": datetime.now().isoformat(),
        }

        assert self._validate_yahoo_response(valid_response) is True

        # Invalid response (missing required fields)
        invalid_response = {
            "symbol": "AAPL",
            "price": 150.25,
            # Missing other required fields
        }

        assert self._validate_yahoo_response(invalid_response) is False

    def test_validate_alpha_vantage_response(self):
        """Test Alpha Vantage API response format."""
        # Mock valid response
        valid_response = {
            "Meta Data": {
                "1. Information": "Daily Prices (open, high, low, close) and Volumes",
                "2. Symbol": "AAPL",
                "3. Last Refreshed": "2024-01-15",
            },
            "Time Series (Daily)": {
                "2024-01-15": {
                    "1. open": "150.25",
                    "2. high": "152.50",
                    "3. low": "149.75",
                    "4. close": "151.00",
                    "5. volume": "1000000",
                }
            },
        }

        assert self._validate_alpha_vantage_response(valid_response) is True

    def _validate_yahoo_response(self, response: Dict[str, Any]) -> bool:
        """Validate Yahoo Finance API response."""
        required_fields = ["symbol", "price", "volume", "timestamp"]
        return all(field in response for field in required_fields)

    def _validate_alpha_vantage_response(self, response: Dict[str, Any]) -> bool:
        """Validate Alpha Vantage API response."""
        required_sections = ["Meta Data", "Time Series (Daily)"]
        if not all(section in response for section in required_sections):
            return False

        # Check meta data
        meta = response["Meta Data"]
        if "2. Symbol" not in meta:
            return False

        # Check time series data
        time_series = response["Time Series (Daily)"]
        if not time_series:
            return False

        # Check first data point
        first_date = list(time_series.keys())[0]
        first_data = time_series[first_date]
        required_fields = ["1. open", "2. high", "3. low", "4. close", "5. volume"]

        return all(field in first_data for field in required_fields)


class TestFinancialCalculationAccuracy:
    """Test financial calculation accuracy."""

    def test_pe_ratio_calculation_accuracy(self):
        """Test PE ratio calculation accuracy."""
        # Test data
        price = 150.25
        earnings_per_share = 9.69

        # Calculate PE ratio
        calculated_pe = price / earnings_per_share
        expected_pe = 15.51

        # Check accuracy within 0.01
        assert abs(calculated_pe - expected_pe) < 0.01

    def test_portfolio_value_calculation_accuracy(self):
        """Test portfolio value calculation accuracy."""
        # Test portfolio
        positions = [
            {"symbol": "AAPL", "shares": 100, "price": 150.25},
            {"symbol": "GOOGL", "shares": 5, "price": 2800.50},
            {"symbol": "MSFT", "shares": 50, "price": 350.75},
        ]

        # Calculate total value
        total_value = sum(pos["shares"] * pos["price"] for pos in positions)
        expected_value = (100 * 150.25) + (5 * 2800.50) + (50 * 350.75)

        assert abs(total_value - expected_value) < 0.01

    def test_percentage_change_calculation_accuracy(self):
        """Test percentage change calculation accuracy."""
        # Test data
        old_value = 100.00
        new_value = 110.00

        # Calculate percentage change
        percentage_change = ((new_value - old_value) / old_value) * 100
        expected_change = 10.0

        assert abs(percentage_change - expected_change) < 0.01

    def test_compound_annual_growth_rate_accuracy(self):
        """Test CAGR calculation accuracy."""
        # Test data
        initial_value = 10000.00
        final_value = 15000.00
        years = 5

        # Calculate CAGR
        cagr = (final_value / initial_value) ** (1 / years) - 1
        expected_cagr = 0.0845  # 8.45%

        # Check accuracy within 0.001
        assert abs(cagr - expected_cagr) < 0.001


class TestDataSourceConsistency:
    """Test data source consistency checks."""

    def test_symbol_consistency_across_sources(self):
        """Test symbol consistency across different data sources."""
        # Mock data from different sources
        yahoo_data = {"AAPL": 150.25, "GOOGL": 2800.50}
        alpha_vantage_data = {"AAPL": 150.25, "GOOGL": 2800.50}

        # Check consistency
        assert self._check_symbol_consistency(yahoo_data, alpha_vantage_data) is True

        # Inconsistent data
        inconsistent_data = {"AAPL": 150.25, "GOOGL": 2801.00}
        assert self._check_symbol_consistency(yahoo_data, inconsistent_data) is False

    def test_price_tolerance_check(self):
        """Test price tolerance checking."""
        # Same price from different sources
        price1 = 150.25
        price2 = 150.26
        tolerance = 0.01

        assert self._check_price_tolerance(price1, price2, tolerance) is True

        # Price difference exceeds tolerance
        price3 = 150.30
        assert self._check_price_tolerance(price1, price3, tolerance) is False

    def test_timestamp_consistency(self):
        """Test timestamp consistency."""
        # Recent timestamps
        now = datetime.now()
        timestamp1 = now - timedelta(minutes=1)
        timestamp2 = now - timedelta(minutes=2)

        # Check if timestamps are within reasonable range
        max_delay = timedelta(minutes=5)
        assert (
            self._check_timestamp_consistency(timestamp1, timestamp2, max_delay) is True
        )

        # Old timestamp
        old_timestamp = now - timedelta(hours=1)
        assert (
            self._check_timestamp_consistency(timestamp1, old_timestamp, max_delay)
            is False
        )

    def _check_symbol_consistency(
        self, data1: Dict[str, float], data2: Dict[str, float]
    ) -> bool:
        """Check symbol consistency between data sources."""
        if set(data1.keys()) != set(data2.keys()):
            return False

        for symbol in data1:
            if abs(data1[symbol] - data2[symbol]) > 0.01:
                return False

        return True

    def _check_price_tolerance(
        self, price1: float, price2: float, tolerance: float
    ) -> bool:
        """Check if price difference is within tolerance."""
        return abs(price1 - price2) <= tolerance

    def _check_timestamp_consistency(
        self, ts1: datetime, ts2: datetime, max_delay: timedelta
    ) -> bool:
        """Check if timestamps are within acceptable delay."""
        return abs(ts1 - ts2) <= max_delay


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
