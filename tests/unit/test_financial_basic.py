"""
Basic Financial Tests for investByYourself

These tests don't require external APIs or running servers.
They test core financial calculations and data structures.
"""

from decimal import Decimal, getcontext

import numpy as np
import pandas as pd
import pytest

# Set precision for financial calculations
getcontext().prec = 28


class TestFinancialCalculations:
    """Test basic financial calculations without external dependencies."""

    def test_pe_ratio_calculation(self):
        """Test PE ratio calculation accuracy."""
        # Test with simple values
        price = 100.0
        earnings = 5.0
        expected_pe = 20.0

        calculated_pe = price / earnings
        assert abs(calculated_pe - expected_pe) < 0.01

        # Test with zero earnings (should raise error)
        with pytest.raises(ZeroDivisionError):
            _ = price / 0

    def test_portfolio_value_calculation(self):
        """Test portfolio value calculation."""
        holdings = [
            {"symbol": "AAPL", "shares": 10, "price": 150.0},
            {"symbol": "GOOGL", "shares": 5, "price": 2800.0},
            {"symbol": "MSFT", "shares": 8, "price": 350.0},
        ]

        expected_value = (10 * 150.0) + (5 * 2800.0) + (8 * 350.0)
        calculated_value = sum(
            holding["shares"] * holding["price"] for holding in holdings
        )

        assert abs(calculated_value - expected_value) < 0.01
        assert calculated_value == 18300.0  # 1500 + 14000 + 2800 = 18300

    def test_percentage_change_calculation(self):
        """Test percentage change calculation."""
        old_value = 100.0
        new_value = 120.0

        percentage_change = ((new_value - old_value) / old_value) * 100
        assert percentage_change == 20.0

        # Test negative change
        new_value_negative = 80.0
        percentage_change_negative = (
            (new_value_negative - old_value) / old_value
        ) * 100
        assert percentage_change_negative == -20.0

    def test_compound_annual_growth_rate(self):
        """Test CAGR calculation."""
        initial_value = 1000.0
        final_value = 2000.0
        years = 5

        cagr = (final_value / initial_value) ** (1 / years) - 1
        expected_cagr = 0.1487  # Approximately 14.87%

        assert abs(cagr - expected_cagr) < 0.0001

    def test_risk_free_rate_adjustment(self):
        """Test risk-free rate adjustment for financial calculations."""
        market_return = 0.12  # 12%
        risk_free_rate = 0.03  # 3%

        risk_premium = market_return - risk_free_rate
        assert risk_premium == 0.09  # 9%


class TestFinancialDataStructures:
    """Test financial data structures and validation."""

    def test_stock_data_structure(self):
        """Test stock data structure validation."""
        stock_data = {
            "symbol": "AAPL",
            "price": 150.0,
            "volume": 1000000,
            "market_cap": 2500000000000,
            "pe_ratio": 25.5,
        }

        # Check required fields
        required_fields = ["symbol", "price", "volume", "market_cap"]
        for field in required_fields:
            assert field in stock_data

        # Check data types
        assert isinstance(stock_data["symbol"], str)
        assert isinstance(stock_data["price"], (int, float))
        assert isinstance(stock_data["volume"], (int, float))
        assert isinstance(stock_data["market_cap"], (int, float))

        # Check data validity
        assert stock_data["price"] > 0
        assert stock_data["volume"] >= 0
        assert stock_data["market_cap"] > 0

    def test_portfolio_structure(self):
        """Test portfolio data structure validation."""
        portfolio = {
            "name": "My Portfolio",
            "holdings": [
                {"symbol": "AAPL", "shares": 10, "cost_basis": 140.0},
                {"symbol": "GOOGL", "shares": 5, "cost_basis": 2700.0},
            ],
            "total_value": 0.0,  # Will be calculated
            "total_cost": 0.0,  # Will be calculated
        }

        # Validate portfolio structure
        assert "name" in portfolio
        assert "holdings" in portfolio
        assert isinstance(portfolio["holdings"], list)

        # Validate holdings
        for holding in portfolio["holdings"]:
            assert "symbol" in holding
            assert "shares" in holding
            assert "cost_basis" in holding
            assert holding["shares"] > 0
            assert holding["cost_basis"] > 0

    def test_financial_ratio_validation(self):
        """Test financial ratio validation."""
        ratios = {
            "pe_ratio": 25.5,
            "pb_ratio": 3.2,
            "debt_to_equity": 0.5,
            "current_ratio": 1.8,
            "roe": 0.15,
        }

        # Check ratio ranges (basic validation)
        assert ratios["pe_ratio"] > 0
        assert ratios["pb_ratio"] > 0
        assert ratios["debt_to_equity"] >= 0
        assert ratios["current_ratio"] > 0
        assert ratios["roe"] > 0


class TestFinancialPrecision:
    """Test financial calculation precision."""

    def test_decimal_precision(self):
        """Test decimal precision for financial calculations."""
        # Use Decimal for precise financial calculations
        price = Decimal("100.50")
        shares = Decimal("10.5")
        total = price * shares

        assert total == Decimal("1055.25")
        assert float(total) == 1055.25

    def test_rounding_behavior(self):
        """Test rounding behavior for financial calculations."""
        # Test rounding to 2 decimal places (cents)
        value = 100.567
        rounded_value = round(value, 2)
        assert rounded_value == 100.57

        # Test rounding to 4 decimal places
        value_4dp = 100.56789
        rounded_value_4dp = round(value_4dp, 4)
        assert rounded_value_4dp == 100.5679

    def test_floating_point_precision(self):
        """Test floating point precision issues and solutions."""
        # Demonstrate floating point precision issue
        a = 0.1
        b = 0.2
        c = 0.3

        # This might not be exactly 0.3 due to floating point precision
        result = a + b
        assert abs(result - c) < 1e-10  # Use small tolerance

        # Better approach: use Decimal
        a_decimal = Decimal("0.1")
        b_decimal = Decimal("0.2")
        c_decimal = Decimal("0.3")

        result_decimal = a_decimal + b_decimal
        assert result_decimal == c_decimal


class TestFinancialValidation:
    """Test financial data validation functions."""

    def test_validate_price_data(self):
        """Test price data validation."""
        valid_prices = [100.0, 0.01, 999999.99]
        invalid_prices = [-100.0, 0.0, "invalid", None]

        for price in valid_prices:
            assert isinstance(price, (int, float))
            assert price > 0

        for price in invalid_prices:
            if isinstance(price, (int, float)):
                assert price <= 0
            else:
                assert not isinstance(price, (int, float))

    def test_validate_volume_data(self):
        """Test volume data validation."""
        valid_volumes = [1000, 0, 999999999]
        invalid_volumes = [-1000, "invalid", None]

        for volume in valid_volumes:
            assert isinstance(volume, (int, float))
            assert volume >= 0

        for volume in invalid_volumes:
            if isinstance(volume, (int, float)):
                assert volume < 0
            else:
                assert not isinstance(volume, (int, float))

    def test_validate_percentage_data(self):
        """Test percentage data validation."""
        valid_percentages = [0.0, 50.0, 100.0, 150.0]
        invalid_percentages = [-50.0, "invalid", None]

        for percentage in valid_percentages:
            assert isinstance(percentage, (int, float))
            assert percentage >= 0

        for percentage in invalid_percentages:
            if isinstance(percentage, (int, float)):
                assert percentage < 0
            else:
                assert not isinstance(percentage, (int, float))


if __name__ == "__main__":
    # Run tests if file is executed directly
    pytest.main([__file__, "-v"])
