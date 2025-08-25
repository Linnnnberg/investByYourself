"""
Unit tests for Results API endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestResultsAPI:
    """Test suite for results API endpoints."""

    def test_get_performance_metrics(self, client: TestClient):
        """Test retrieving performance metrics."""
        response = client.get("/api/v1/results/1/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "total_return" in data
        assert "annualized_return" in data
        assert "sharpe_ratio" in data
        assert "max_drawdown" in data

    def test_get_portfolio_values(self, client: TestClient):
        """Test retrieving portfolio values over time."""
        response = client.get("/api/v1/results/1/portfolio-values")
        assert response.status_code == 200
        data = response.json()
        assert "dates" in data
        assert "values" in data
        assert "benchmark_values" in data
        assert len(data["dates"]) == len(data["values"])

    def test_get_portfolio_weights(self, client: TestClient):
        """Test retrieving portfolio weights over time."""
        response = client.get("/api/v1/results/1/weights")
        assert response.status_code == 200
        data = response.json()
        assert "dates" in data
        assert "weights" in data
        assert "assets" in data
        assert len(data["dates"]) == len(data["weights"])

    def test_get_trade_history(self, client: TestClient):
        """Test retrieving trade history."""
        response = client.get("/api/v1/results/1/trades")
        assert response.status_code == 200
        data = response.json()
        assert "trades" in data
        assert isinstance(data["trades"], list)
        if data["trades"]:
            trade = data["trades"][0]
            assert "date" in trade
            assert "action" in trade
            assert "symbol" in trade
            assert "quantity" in trade
            assert "price" in trade

    def test_get_risk_metrics(self, client: TestClient):
        """Test retrieving risk metrics."""
        response = client.get("/api/v1/results/1/risk-metrics")
        assert response.status_code == 200
        data = response.json()
        assert "volatility" in data
        assert "var_95" in data
        assert "cvar_95" in data
        assert "beta" in data
        assert "correlation" in data

    def test_get_drawdown_analysis(self, client: TestClient):
        """Test retrieving drawdown analysis."""
        response = client.get("/api/v1/results/1/drawdown")
        assert response.status_code == 200
        data = response.json()
        assert "drawdowns" in data
        assert "max_drawdown" in data
        assert "max_drawdown_duration" in data
        assert "recovery_time" in data

    def test_get_rolling_returns(self, client: TestClient):
        """Test retrieving rolling returns."""
        response = client.get("/api/v1/results/1/rolling-returns")
        assert response.status_code == 200
        data = response.json()
        assert "periods" in data
        assert "returns" in data
        assert "benchmark_returns" in data
        assert len(data["periods"]) == len(data["returns"])

    def test_generate_comprehensive_report(self, client: TestClient):
        """Test generating comprehensive report."""
        response = client.post("/api/v1/results/1/report")
        assert response.status_code == 200
        data = response.json()
        assert "report_id" in data
        assert "status" in data
        assert "generated_at" in data

    def test_download_results(self, client: TestClient):
        """Test downloading results."""
        response = client.get("/api/v1/results/1/download")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/zip"
        assert "attachment" in response.headers["content-disposition"]

    def test_export_data(self, client: TestClient):
        """Test exporting data."""
        export_request = {
            "format": "csv",
            "include_metrics": True,
            "include_trades": True,
            "include_portfolio": True,
        }
        response = client.post("/api/v1/results/1/export", json=export_request)
        assert response.status_code == 200
        data = response.json()
        assert "export_id" in data
        assert "status" in data
        assert "format" in data

    def test_results_not_found(self, client: TestClient):
        """Test retrieving results for non-existent backtest."""
        response = client.get("/api/v1/results/999/metrics")
        assert response.status_code == 404

    def test_invalid_export_format(self, client: TestClient):
        """Test export with invalid format."""
        export_request = {"format": "invalid_format", "include_metrics": True}
        response = client.post("/api/v1/results/1/export", json=export_request)
        assert response.status_code == 422
