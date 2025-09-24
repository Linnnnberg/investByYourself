"""
Unit tests for Backtesting API endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestBacktestingAPI:
    """Test suite for backtesting API endpoints."""

    def test_create_backtest_success(
        self, client: TestClient, sample_backtest_data: dict
    ):
        """Test successful backtest creation."""
        response = client.post("/api/v1/backtesting/", json=sample_backtest_data)
        assert response.status_code == 201
        data = response.json()
        assert data["initial_investment"] == sample_backtest_data["initial_investment"]
        assert data["strategy_id"] == sample_backtest_data["strategy_id"]
        assert "id" in data
        assert "status" in data

    def test_create_backtest_invalid_data(self, client: TestClient):
        """Test backtest creation with invalid data."""
        invalid_data = {
            "start_date": "invalid-date",
            "end_date": "2023-12-31",
            "initial_investment": -1000,
        }
        response = client.post("/api/v1/backtesting/", json=invalid_data)
        assert response.status_code == 422

    def test_get_backtests_list(self, client: TestClient):
        """Test retrieving list of backtests."""
        response = client.get("/api/v1/backtesting/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_backtest_by_id(self, client: TestClient, sample_backtest_data: dict):
        """Test retrieving backtest by ID."""
        # First create a backtest
        create_response = client.post("/api/v1/backtesting/", json=sample_backtest_data)
        backtest_id = create_response.json()["id"]

        # Then retrieve it
        response = client.get(f"/api/v1/backtesting/{backtest_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == backtest_id
        assert data["initial_investment"] == sample_backtest_data["initial_investment"]

    def test_get_backtest_not_found(self, client: TestClient):
        """Test retrieving non-existent backtest."""
        response = client.get("/api/v1/backtesting/999")
        assert response.status_code == 404

    def test_get_backtest_progress(
        self, client: TestClient, sample_backtest_data: dict
    ):
        """Test retrieving backtest progress."""
        # First create a backtest
        create_response = client.post("/api/v1/backtesting/", json=sample_backtest_data)
        backtest_id = create_response.json()["id"]

        # Get progress
        response = client.get(f"/api/v1/backtesting/{backtest_id}/progress")
        assert response.status_code == 200
        data = response.json()
        assert "progress" in data
        assert "current_step" in data
        assert "status" in data

    def test_cancel_backtest(self, client: TestClient, sample_backtest_data: dict):
        """Test canceling backtest."""
        # First create a backtest
        create_response = client.post("/api/v1/backtesting/", json=sample_backtest_data)
        backtest_id = create_response.json()["id"]

        # Cancel it
        response = client.delete(f"/api/v1/backtesting/{backtest_id}")
        assert response.status_code == 204

        # Verify it's canceled
        get_response = client.get(f"/api/v1/backtesting/{backtest_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["status"] == "canceled"

    def test_retry_backtest(self, client: TestClient, sample_backtest_data: dict):
        """Test retrying failed backtest."""
        # First create a backtest
        create_response = client.post("/api/v1/backtesting/", json=sample_backtest_data)
        backtest_id = create_response.json()["id"]

        # Retry it
        response = client.post(f"/api/v1/backtesting/{backtest_id}/retry")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["status"] == "pending"

    def test_backtest_date_validation(self, client: TestClient):
        """Test backtest date validation."""
        invalid_dates = {
            "start_date": "2023-12-31",
            "end_date": "2023-01-01",  # End before start
            "initial_investment": 10000.0,
            "strategy_id": 1,
        }
        response = client.post("/api/v1/backtesting/", json=invalid_dates)
        assert response.status_code == 422

    def test_backtest_investment_validation(self, client: TestClient):
        """Test backtest investment amount validation."""
        invalid_investment = {
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "initial_investment": 0,  # Zero investment
            "strategy_id": 1,
        }
        response = client.post("/api/v1/backtesting/", json=invalid_investment)
        assert response.status_code == 422
