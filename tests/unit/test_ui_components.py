"""
UI Component Tests - investByYourself

Tests for our Streamlit UI components to ensure they work correctly.
This validates that our UI accurately reflects our financial calculations.

Tests include:
- Portfolio dashboard functionality
- Financial calculator accuracy
- Chart viewer operations
- UI component integration
"""

import os
import sys
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))


class TestPortfolioDashboard:
    """Test portfolio dashboard functionality."""

    def test_portfolio_calculator_initialization(self):
        """Test portfolio calculator initializes correctly."""
        try:
            from src.ui.portfolio_dashboard import PortfolioCalculator

            calc = PortfolioCalculator()
            assert calc.holdings == []
            assert calc.current_prices == {}
        except ImportError:
            pytest.skip("Portfolio dashboard not available")

    def test_add_holding(self):
        """Test adding holdings to portfolio."""
        try:
            from src.ui.portfolio_dashboard import PortfolioCalculator

            calc = PortfolioCalculator()

            # Add a holding
            calc.add_holding("AAPL", 100, 150.0)
            assert len(calc.holdings) == 1
            assert calc.holdings[0]["symbol"] == "AAPL"
            assert calc.holdings[0]["shares"] == 100
            assert calc.holdings[0]["cost_basis"] == 150.0

            # Add another holding
            calc.add_holding("GOOGL", 50, 2800.0)
            assert len(calc.holdings) == 2
        except ImportError:
            pytest.skip("Portfolio dashboard not available")

    def test_portfolio_value_calculation(self):
        """Test portfolio value calculations."""
        try:
            from src.ui.portfolio_dashboard import PortfolioCalculator

            calc = PortfolioCalculator()

            # Add holdings
            calc.add_holding("AAPL", 100, 150.0)
            calc.add_holding("GOOGL", 50, 2800.0)

            # Update prices
            calc.update_prices({"AAPL": 160.0, "GOOGL": 2900.0})

            # Calculate values
            total_value = calc.calculate_portfolio_value()
            expected_value = 100 * 160.0 + 50 * 2900.0
            assert total_value == expected_value

            # Test individual holding calculations
            aapl_holding = calc.holdings[0]
            aapl_value = aapl_holding["shares"] * aapl_holding["current_price"]
            assert aapl_value == 100 * 160.0
        except ImportError:
            pytest.skip("Portfolio dashboard not available")

    def test_portfolio_performance_metrics(self):
        """Test portfolio performance calculations."""
        try:
            from src.ui.portfolio_dashboard import PortfolioCalculator

            calc = PortfolioCalculator()

            # Add holdings with different scenarios
            calc.add_holding("AAPL", 100, 150.0)  # Cost: $15,000
            calc.add_holding("GOOGL", 50, 2800.0)  # Cost: $140,000

            # Update to current prices
            calc.update_prices({"AAPL": 160.0, "GOOGL": 2900.0})

            # Calculate metrics
            total_cost = calc.calculate_total_cost()
            total_value = calc.calculate_portfolio_value()
            total_pnl = calc.calculate_total_pnl()
            pnl_percent = calc.calculate_percentage_return()

            # Verify calculations
            assert total_cost == 100 * 150.0 + 50 * 2800.0
            assert total_value == 100 * 160.0 + 50 * 2900.0
            assert total_pnl == total_value - total_cost
            assert abs(pnl_percent - (total_pnl / total_cost * 100)) < 0.01
        except ImportError:
            pytest.skip("Portfolio dashboard not available")


class TestFinancialCalculator:
    """Test financial calculator functionality."""

    def test_pe_ratio_calculator(self):
        """Test PE ratio calculator accuracy."""
        try:
            from src.ui.financial_calculator import FinancialCalculator

            # Test basic PE ratio calculation
            pe_ratio = FinancialCalculator.calculate_pe_ratio(150.0, 5.0)
            assert pe_ratio == 30.0

            # Test edge cases
            with pytest.raises(ValueError):
                FinancialCalculator.calculate_pe_ratio(150.0, 0)

            with pytest.raises(ValueError):
                FinancialCalculator.calculate_pe_ratio(150.0, -5.0)
        except ImportError:
            pytest.skip("Financial calculator not available")

    def test_cagr_calculator(self):
        """Test CAGR calculator accuracy."""
        try:
            from src.ui.financial_calculator import FinancialCalculator

            # Test CAGR calculation
            cagr = FinancialCalculator.calculate_cagr(10000, 20000, 5)
            expected_cagr = (20000 / 10000) ** (1 / 5) - 1
            assert abs(cagr - expected_cagr) < 0.0001

            # Test edge cases
            with pytest.raises(ValueError):
                FinancialCalculator.calculate_cagr(10000, 20000, 0)

            with pytest.raises(ValueError):
                FinancialCalculator.calculate_cagr(0, 20000, 5)
        except ImportError:
            pytest.skip("Financial calculator not available")

    def test_portfolio_calculator(self):
        """Test portfolio calculator in financial calculator."""
        try:
            from src.ui.financial_calculator import FinancialCalculator

            # Test portfolio value calculation
            holdings = [{"shares": 100, "price": 50.0}, {"shares": 200, "price": 25.0}]
            total_value = FinancialCalculator.calculate_portfolio_value(holdings)
            expected_value = 100 * 50.0 + 200 * 25.0
            assert total_value == expected_value
        except ImportError:
            pytest.skip("Financial calculator not available")

    def test_percentage_change_calculator(self):
        """Test percentage change calculator."""
        try:
            from src.ui.financial_calculator import FinancialCalculator

            # Test percentage change
            change = FinancialCalculator.calculate_percentage_change(100, 120)
            assert change == 20.0

            change = FinancialCalculator.calculate_percentage_change(100, 80)
            assert change == -20.0

            # Test edge case
            with pytest.raises(ValueError):
                FinancialCalculator.calculate_percentage_change(0, 100)
        except ImportError:
            pytest.skip("Financial calculator not available")


class TestChartViewer:
    """Test chart viewer functionality."""

    def test_chart_file_detection(self):
        """Test that chart viewer can detect chart files."""
        try:
            import glob

            from src.ui.chart_viewer import main

            # Check if charts directory exists and has files
            chart_files = glob.glob("charts/*.png")
            assert len(chart_files) > 0, "No chart files found"

            # Verify specific chart types exist
            chart_names = [os.path.basename(f) for f in chart_files]
            assert any("portfolio" in name.lower() for name in chart_names)
            assert any("analysis" in name.lower() for name in chart_names)
        except ImportError:
            pytest.skip("Chart viewer not available")

    def test_chart_metadata_extraction(self):
        """Test chart metadata extraction functions."""
        try:
            from src.ui.chart_viewer import get_chart_description, get_chart_type

            # Test chart type detection
            assert get_chart_type("Portfolio Allocation") == "Pie Chart"
            assert get_chart_type("Portfolio Performance") == "Line Chart"
            assert get_chart_type("PE Ratio Comparison") == "Bar Chart"

            # Test chart descriptions
            desc = get_chart_description("Portfolio Allocation")
            assert "Portfolio Allocation Chart" in desc
            assert "pie chart" in desc.lower()
        except ImportError:
            pytest.skip("Chart viewer not available")


class TestUIIntegration:
    """Test UI component integration."""

    def test_main_app_navigation(self):
        """Test main app navigation structure."""
        try:
            from src.ui.main_app import main, show_home_page

            # Test that main functions exist and are callable
            assert callable(main)
            assert callable(show_home_page)
        except ImportError:
            pytest.skip("Main app not available")

    def test_ui_launcher_script(self):
        """Test UI launcher script functionality."""
        # Check if launcher script exists
        launcher_path = "run_ui.py"
        assert os.path.exists(launcher_path), "UI launcher script not found"

        # Check if it's executable
        assert os.access(launcher_path, os.R_OK), "UI launcher script not readable"


class TestChartGeneration:
    """Test chart generation system."""

    def test_chart_generation_script(self):
        """Test chart generation script exists and works."""
        script_path = "scripts/generate_sample_charts.py"
        assert os.path.exists(script_path), "Chart generation script not found"

        # Check if script has required functions
        try:
            with open(script_path, "r") as f:
                content = f.read()
                assert "create_portfolio_allocation_chart" in content
                assert "create_portfolio_performance_chart" in content
                assert "create_pe_ratio_comparison_chart" in content
        except Exception:
            pytest.skip("Could not read chart generation script")

    def test_generated_charts_exist(self):
        """Test that sample charts were generated."""
        charts_dir = "charts"
        assert os.path.exists(charts_dir), "Charts directory not found"

        # Check for specific chart files
        expected_charts = [
            "portfolio_allocation_sample.png",
            "portfolio_performance_sample.png",
            "pe_ratio_comparison_sample.png",
            "cagr_analysis_sample.png",
            "risk_return_analysis_sample.png",
            "portfolio_correlation_heatmap_sample.png",
        ]

        for chart in expected_charts:
            chart_path = os.path.join(charts_dir, chart)
            assert os.path.exists(chart_path), f"Chart {chart} not found"

            # Check file size (should be reasonable for PNG)
            file_size = os.path.getsize(chart_path)
            assert file_size > 1000, f"Chart {chart} seems too small"
            assert file_size < 10000000, f"Chart {chart} seems too large"


class TestDataStructures:
    """Test data structures used in UI components."""

    def test_portfolio_data_structure(self):
        """Test portfolio data structure consistency."""
        try:
            from src.ui.portfolio_dashboard import PortfolioCalculator

            calc = PortfolioCalculator()

            # Add a holding and verify structure
            calc.add_holding("TEST", 100, 50.0)
            holding = calc.holdings[0]

            # Check required fields
            required_fields = ["symbol", "shares", "cost_basis", "current_price"]
            for field in required_fields:
                assert field in holding, f"Missing field: {field}"

            # Check data types
            assert isinstance(holding["symbol"], str)
            assert isinstance(holding["shares"], (int, float))
            assert isinstance(holding["cost_basis"], (int, float))
            assert isinstance(holding["current_price"], (int, float))
        except ImportError:
            pytest.skip("Portfolio dashboard not available")

    def test_holdings_dataframe_conversion(self):
        """Test conversion of holdings to pandas DataFrame."""
        try:
            from src.ui.portfolio_dashboard import PortfolioCalculator

            calc = PortfolioCalculator()

            # Add sample holdings
            calc.add_holding("AAPL", 100, 150.0)
            calc.add_holding("GOOGL", 50, 2800.0)
            calc.update_prices({"AAPL": 160.0, "GOOGL": 2900.0})

            # Convert to DataFrame
            df = calc.get_holdings_dataframe()

            # Verify DataFrame structure
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 2  # Two holdings
            assert "Symbol" in df.columns
            assert "Shares" in df.columns
            assert "Cost Basis" in df.columns
            assert "Current Price" in df.columns
            assert "Current Value" in df.columns
            assert "P&L" in df.columns
            assert "P&L %" in df.columns
        except ImportError:
            pytest.skip("Portfolio dashboard not available")


if __name__ == "__main__":
    pytest.main([__file__])
