"""
Unit tests for Strategies API endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestStrategiesAPI:
    """Test suite for strategies API endpoints."""

    def test_create_strategy_success(
        self, client: TestClient, sample_strategy_data: dict
    ):
        """Test successful strategy creation."""
        response = client.post("/api/v1/strategies/", json=sample_strategy_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_strategy_data["name"]
        assert data["strategy_type"] == sample_strategy_data["strategy_type"]
        assert "id" in data

    def test_create_strategy_invalid_data(self, client: TestClient):
        """Test strategy creation with invalid data."""
        invalid_data = {"name": "", "strategy_type": "invalid_type"}
        response = client.post("/api/v1/strategies/", json=invalid_data)
        assert response.status_code == 422

    def test_get_strategies_list(self, client: TestClient):
        """Test retrieving list of strategies."""
        response = client.get("/api/v1/strategies/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_strategy_by_id(self, client: TestClient, sample_strategy_data: dict):
        """Test retrieving strategy by ID."""
        # First create a strategy
        create_response = client.post("/api/v1/strategies/", json=sample_strategy_data)
        strategy_id = create_response.json()["id"]

        # Then retrieve it
        response = client.get(f"/api/v1/strategies/{strategy_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == strategy_id
        assert data["name"] == sample_strategy_data["name"]

    def test_get_strategy_not_found(self, client: TestClient):
        """Test retrieving non-existent strategy."""
        response = client.get("/api/v1/strategies/999")
        assert response.status_code == 404

    def test_update_strategy(self, client: TestClient, sample_strategy_data: dict):
        """Test updating strategy."""
        # First create a strategy
        create_response = client.post("/api/v1/strategies/", json=sample_strategy_data)
        strategy_id = create_response.json()["id"]

        # Update it
        update_data = {
            "name": "Updated Strategy Name",
            "description": "Updated description",
        }
        response = client.put(f"/api/v1/strategies/{strategy_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Strategy Name"
        assert data["description"] == "Updated description"

    def test_delete_strategy(self, client: TestClient, sample_strategy_data: dict):
        """Test deleting strategy."""
        # First create a strategy
        create_response = client.post("/api/v1/strategies/", json=sample_strategy_data)
        strategy_id = create_response.json()["id"]

        # Delete it
        response = client.delete(f"/api/v1/strategies/{strategy_id}")
        assert response.status_code == 204

        # Verify it's deleted
        get_response = client.get(f"/api/v1/strategies/{strategy_id}")
        assert get_response.status_code == 404

    def test_validate_strategy(self, client: TestClient, sample_strategy_data: dict):
        """Test strategy validation endpoint."""
        response = client.post("/api/v1/strategies/validate", json=sample_strategy_data)
        assert response.status_code == 200
        data = response.json()
        assert "valid" in data
        assert "errors" in data
