"""
Pytest configuration and fixtures for Financial Analysis Service tests.
"""

import pytest
from app.core.database import get_db
from app.main import app
from app.models.base import Base
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def client():
    """Test client for FastAPI application."""
    return TestClient(app)


@pytest.fixture
def test_db():
    """Create test database with in-memory SQLite."""
    engine = create_engine(
        "sqlite:///./test.db", connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create tables
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield engine

    # Cleanup
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture
def sample_strategy_data():
    """Sample strategy data for testing."""
    return {
        "name": "Test Momentum Strategy",
        "description": "A test momentum-based investment strategy",
        "strategy_type": "momentum",
        "parameters": {
            "lookback_period": 12,
            "rebalancing_frequency": "monthly",
            "max_positions": 10,
        },
        "is_active": True,
    }


@pytest.fixture
def sample_backtest_data():
    """Sample backtest data for testing."""
    return {
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "initial_investment": 10000.0,
        "strategy_id": 1,
    }
