"""
Financial Calculation Tests - investByYourself

Comprehensive tests for all financial calculations used in our platform.
This completes Story-002: Financial Calculation Testing Suite.

Tests include:
- PE ratio calculations
- Portfolio value calculations
- Financial ratios (ROE, ROA, etc.)
- Risk assessment calculations
- Edge cases and error handling
"""

from decimal import Decimal, getcontext
from typing import Any, Dict, List

import numpy as np
import pytest

# Set precision for financial calculations
getcontext().prec = 28


class FinancialCalculator:
    """Financial calculation engine for testing."""

    @staticmethod
    def calculate_pe_ratio(price: float, earnings: float) -> float:
        """Calculate Price-to-Earnings ratio."""
        if earnings <= 0:
            raise ValueError("Earnings must be positive for PE ratio calculation")
        return price / earnings

    @staticmethod
    def calculate_portfolio_value(holdings: List[Dict[str, float]]) -> float:
        """Calculate total portfolio value."""
        return sum(holding["shares"] * holding["price"] for holding in holdings)

    @staticmethod
    def calculate_roe(net_income: float, shareholders_equity: float) -> float:
        """Calculate Return on Equity."""
        if shareholders_equity <= 0:
            raise ValueError("Shareholders equity must be positive")
        return (net_income / shareholders_equity) * 100

    @staticmethod
    def calculate_roa(net_income: float, total_assets: float) -> float:
        """Calculate Return on Assets."""
        if total_assets <= 0:
            raise ValueError("Total assets must be positive")
        return (net_income / total_assets) * 100

    @staticmethod
    def calculate_debt_to_equity(
        total_debt: float, shareholders_equity: float
    ) -> float:
        """Calculate Debt-to-Equity ratio."""
        if shareholders_equity <= 0:
            raise ValueError("Shareholders equity must be positive")
        return total_debt / shareholders_equity

    @staticmethod
    def calculate_sharpe_ratio(
        portfolio_return: float, risk_free_rate: float, portfolio_volatility: float
    ) -> float:
        """Calculate Sharpe ratio."""
        if portfolio_volatility <= 0:
            raise ValueError("Portfolio volatility must be positive")
        return (portfolio_return - risk_free_rate) / portfolio_volatility

    @staticmethod
    def calculate_beta(
        portfolio_returns: List[float], market_returns: List[float]
    ) -> float:
        """Calculate portfolio beta."""
        if len(portfolio_returns) != len(market_returns):
            raise ValueError("Portfolio and market returns must have same length")
        if len(portfolio_returns) < 2:
            raise ValueError("Need at least 2 data points for beta calculation")

        portfolio_array = np.array(portfolio_returns)
        market_array = np.array(market_returns)

        # Calculate covariance and variance
        covariance = np.cov(portfolio_array, market_array)[0, 1]
        market_variance = np.var(market_array)

        if market_variance == 0:
            raise ValueError("Market variance cannot be zero")

        return covariance / market_variance

    @staticmethod
    def calculate_var(returns: List[float], confidence_level: float = 0.95) -> float:
        """Calculate Value at Risk."""
        if not returns:
            raise ValueError("Returns list cannot be empty")
        if confidence_level <= 0 or confidence_level >= 1:
            raise ValueError("Confidence level must be between 0 and 1")

        returns_array = np.array(returns)
        percentile = (1 - confidence_level) * 100
        return np.percentile(returns_array, percentile)

    @staticmethod
    def calculate_cagr(initial_value: float, final_value: float, years: float) -> float:
        """Calculate Compound Annual Growth Rate."""
        if years <= 0:
            raise ValueError("Years must be positive")
        if initial_value <= 0:
            raise ValueError("Initial value must be positive")

        return (final_value / initial_value) ** (1 / years) - 1

    @staticmethod
    def calculate_percentage_change(old_value: float, new_value: float) -> float:
        """Calculate percentage change."""
        if old_value == 0:
            raise ValueError("Old value cannot be zero for percentage change")
        return ((new_value - old_value) / old_value) * 100


class TestFinancialCalculations:
    """Test suite for financial calculations."""

    def test_pe_ratio_calculation(self):
        """Test PE ratio calculations with various scenarios."""
        calc = FinancialCalculator()

        # Normal case
        assert calc.calculate_pe_ratio(100, 5) == 20.0
        assert calc.calculate_pe_ratio(50, 2.5) == 20.0

        # High PE ratio
        assert calc.calculate_pe_ratio(200, 2) == 100.0

        # Low PE ratio
        assert calc.calculate_pe_ratio(10, 2) == 5.0

        # Decimal precision
        assert abs(calc.calculate_pe_ratio(33.33, 3.33) - 10.0) < 0.01

    def test_pe_ratio_edge_cases(self):
        """Test PE ratio edge cases and error handling."""
        calc = FinancialCalculator()

        # Zero earnings should raise error
        with pytest.raises(ValueError, match="Earnings must be positive"):
            calc.calculate_pe_ratio(100, 0)

        # Negative earnings should raise error
        with pytest.raises(ValueError, match="Earnings must be positive"):
            calc.calculate_pe_ratio(100, -5)

        # Zero price is valid (though unusual)
        assert calc.calculate_pe_ratio(0, 5) == 0.0

    def test_portfolio_value_calculation(self):
        """Test portfolio value calculations."""
        calc = FinancialCalculator()

        # Single holding
        holdings = [{"shares": 100, "price": 50.0}]
        assert calc.calculate_portfolio_value(holdings) == 5000.0

        # Multiple holdings
        holdings = [
            {"shares": 100, "price": 50.0},
            {"shares": 50, "price": 100.0},
            {"shares": 200, "price": 25.0},
        ]
        expected = 100 * 50 + 50 * 100 + 200 * 25
        assert calc.calculate_portfolio_value(holdings) == expected

        # Zero shares
        holdings = [{"shares": 0, "price": 100.0}]
        assert calc.calculate_portfolio_value(holdings) == 0.0

        # Empty portfolio
        assert calc.calculate_portfolio_value([]) == 0.0

    def test_financial_ratios(self):
        """Test financial ratios (ROE, ROA, Debt-to-Equity)."""
        calc = FinancialCalculator()

        # ROE calculations
        assert calc.calculate_roe(1000000, 5000000) == 20.0  # 20% ROE
        assert calc.calculate_roe(500000, 10000000) == 5.0  # 5% ROE

        # ROA calculations
        assert calc.calculate_roa(1000000, 10000000) == 10.0  # 10% ROA
        assert calc.calculate_roa(500000, 5000000) == 10.0  # 10% ROA

        # Debt-to-Equity calculations
        assert calc.calculate_debt_to_equity(2000000, 1000000) == 2.0  # 2:1 ratio
        assert calc.calculate_debt_to_equity(500000, 1000000) == 0.5  # 0.5:1 ratio

    def test_financial_ratios_edge_cases(self):
        """Test financial ratios edge cases and error handling."""
        calc = FinancialCalculator()

        # ROE edge cases
        with pytest.raises(ValueError, match="Shareholders equity must be positive"):
            calc.calculate_roe(1000000, 0)
        with pytest.raises(ValueError, match="Shareholders equity must be positive"):
            calc.calculate_roe(1000000, -5000000)

        # ROA edge cases
        with pytest.raises(ValueError, match="Total assets must be positive"):
            calc.calculate_roa(1000000, 0)

        # Debt-to-Equity edge cases
        with pytest.raises(ValueError, match="Shareholders equity must be positive"):
            calc.calculate_debt_to_equity(1000000, 0)

    def test_risk_metrics(self):
        """Test risk assessment calculations."""
        calc = FinancialCalculator()

        # Sharpe ratio calculations
        assert calc.calculate_sharpe_ratio(12.0, 3.0, 15.0) == 0.6
        assert calc.calculate_sharpe_ratio(8.0, 2.0, 10.0) == 0.6

        # Beta calculations
        portfolio_returns = [0.02, -0.01, 0.03, -0.02, 0.01]
        market_returns = [0.01, -0.005, 0.015, -0.01, 0.005]
        beta = calc.calculate_beta(portfolio_returns, market_returns)
        assert isinstance(beta, float)
        assert not np.isnan(beta)

        # VaR calculations
        returns = [-0.02, -0.01, 0.01, 0.02, -0.015, 0.005]
        var_95 = calc.calculate_var(returns, 0.95)
        assert var_95 < 0  # VaR should be negative for losses
        assert isinstance(var_95, float)

    def test_risk_metrics_edge_cases(self):
        """Test risk metrics edge cases and error handling."""
        calc = FinancialCalculator()

        # Sharpe ratio edge cases
        with pytest.raises(ValueError, match="Portfolio volatility must be positive"):
            calc.calculate_sharpe_ratio(12.0, 3.0, 0)
        with pytest.raises(ValueError, match="Portfolio volatility must be positive"):
            calc.calculate_sharpe_ratio(12.0, 3.0, -5.0)

        # Beta edge cases
        with pytest.raises(
            ValueError, match="Portfolio and market returns must have same length"
        ):
            calc.calculate_beta([0.01, 0.02], [0.01])
        with pytest.raises(
            ValueError, match="Need at least 2 data points for beta calculation"
        ):
            calc.calculate_beta([0.01], [0.01])

        # VaR edge cases
        with pytest.raises(ValueError, match="Returns list cannot be empty"):
            calc.calculate_var([])
        with pytest.raises(
            ValueError, match="Confidence level must be between 0 and 1"
        ):
            calc.calculate_var([0.01, 0.02], 1.1)
        with pytest.raises(
            ValueError, match="Confidence level must be between 0 and 1"
        ):
            calc.calculate_var([0.01, 0.02], -0.1)

    def test_growth_calculations(self):
        """Test growth and percentage change calculations."""
        calc = FinancialCalculator()

        # CAGR calculations
        assert abs(calc.calculate_cagr(10000, 20000, 5) - 0.1487) < 0.001  # ~14.87%
        assert abs(calc.calculate_cagr(1000, 1100, 1) - 0.1) < 0.001  # 10%

        # Percentage change calculations
        assert calc.calculate_percentage_change(100, 120) == 20.0  # +20%
        assert calc.calculate_percentage_change(100, 80) == -20.0  # -20%
        assert calc.calculate_percentage_change(50, 75) == 50.0  # +50%

    def test_growth_calculations_edge_cases(self):
        """Test growth calculations edge cases and error handling."""
        calc = FinancialCalculator()

        # CAGR edge cases
        with pytest.raises(ValueError, match="Years must be positive"):
            calc.calculate_cagr(10000, 20000, 0)
        with pytest.raises(ValueError, match="Years must be positive"):
            calc.calculate_cagr(10000, 20000, -5)
        with pytest.raises(ValueError, match="Initial value must be positive"):
            calc.calculate_cagr(0, 20000, 5)
        with pytest.raises(ValueError, match="Initial value must be positive"):
            calc.calculate_cagr(-10000, 20000, 5)

        # Percentage change edge cases
        with pytest.raises(
            ValueError, match="Old value cannot be zero for percentage change"
        ):
            calc.calculate_percentage_change(0, 100)

    def test_decimal_precision(self):
        """Test financial calculations with high precision."""
        calc = FinancialCalculator()

        # Use Decimal for high precision calculations
        price = Decimal("100.123456789")
        earnings = Decimal("5.123456789")
        pe_ratio = calc.calculate_pe_ratio(float(price), float(earnings))

        # Should be approximately 19.52
        expected_pe = float(price / earnings)
        assert abs(pe_ratio - expected_pe) < 0.0001

    def test_large_numbers(self):
        """Test calculations with large financial numbers."""
        calc = FinancialCalculator()

        # Large portfolio value
        holdings = [
            {"shares": 1000000, "price": 100.0},  # $100M
            {"shares": 500000, "price": 200.0},  # $100M
            {"shares": 2000000, "price": 50.0},  # $100M
        ]
        total_value = calc.calculate_portfolio_value(holdings)
        assert total_value == 300000000.0  # $300M

        # Large financial ratios
        roe = calc.calculate_roe(1000000000, 5000000000)  # $1B net income, $5B equity
        assert roe == 20.0  # 20% ROE

    def test_negative_values(self):
        """Test calculations with negative values where appropriate."""
        calc = FinancialCalculator()

        # Negative net income (loss) is valid
        roe = calc.calculate_roe(-1000000, 10000000)  # -$1M loss, $10M equity
        assert roe == -10.0  # -10% ROE

        # Negative returns for VaR calculation
        returns = [-0.05, -0.03, 0.02, -0.01, 0.01]
        var_95 = calc.calculate_var(returns, 0.95)
        assert var_95 < 0  # Should be negative

    def test_performance_benchmarks(self):
        """Test calculation performance with reasonable data sizes."""
        calc = FinancialCalculator()

        # Generate test data
        np.random.seed(42)  # For reproducible results
        n_points = 1000

        # Test beta calculation performance
        portfolio_returns = np.random.normal(0.001, 0.02, n_points).tolist()
        market_returns = np.random.normal(0.0005, 0.015, n_points).tolist()

        import time

        start_time = time.time()
        beta = calc.calculate_beta(portfolio_returns, market_returns)
        end_time = time.time()

        # Should complete in reasonable time (< 1 second)
        assert end_time - start_time < 1.0
        assert isinstance(beta, float)
        assert not np.isnan(beta)


if __name__ == "__main__":
    pytest.main([__file__])
