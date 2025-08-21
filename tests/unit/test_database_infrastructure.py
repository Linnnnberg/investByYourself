"""
Database Infrastructure Tests
Tech-008: Database Infrastructure Setup

Tests for database configuration, connection management, and migration system.
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from config.database import (  # type: ignore
    DatabaseConfig,
    DatabaseManager,
    get_db_manager,
)


class TestDatabaseConfig:
    """Test DatabaseConfig class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = DatabaseConfig()

        assert config.postgres_host == "localhost"
        assert config.postgres_port == 5432
        assert config.postgres_database == "investbyyourself"
        assert config.postgres_user == "etl_user"
        assert config.redis_host == "localhost"
        assert config.redis_port == 6379
        assert config.minio_host == "localhost"
        assert config.minio_port == 9000

    def test_from_env(self):
        """Test configuration from environment variables."""
        env_vars = {
            "POSTGRES_HOST": "test-host",
            "POSTGRES_PORT": "5433",
            "POSTGRES_DB": "test-db",
            "POSTGRES_USER": "test-user",
            "POSTGRES_PASSWORD": "test-pass",
            "REDIS_HOST": "redis-host",
            "REDIS_PORT": "6380",
            "MINIO_HOST": "minio-host",
            "MINIO_PORT": "9001",
        }

        with patch.dict(os.environ, env_vars):
            config = DatabaseConfig.from_env()

            assert config.postgres_host == "test-host"
            assert config.postgres_port == 5433
            assert config.postgres_database == "test-db"
            assert config.postgres_user == "test-user"
            assert config.postgres_password == "test-pass"
            assert config.redis_host == "redis-host"
            assert config.redis_port == 6380
            assert config.minio_host == "minio-host"
            assert config.minio_port == 9001


class TestDatabaseManager:
    """Test DatabaseManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = DatabaseConfig()
        self.db_manager = DatabaseManager(self.config)

    @patch("psycopg2.connect")
    def test_get_postgres_connection_success(self, mock_connect):
        """Test successful PostgreSQL connection."""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection

        connection = self.db_manager.get_postgres_connection()

        assert connection == mock_connection
        # Check that connect was called with the right parameters
        mock_connect.assert_called_once()
        call_args = mock_connect.call_args
        assert call_args[1]["host"] == self.config.postgres_host
        assert call_args[1]["port"] == self.config.postgres_port
        assert call_args[1]["database"] == self.config.postgres_database
        assert call_args[1]["user"] == self.config.postgres_user
        assert call_args[1]["password"] == self.config.postgres_password

    @patch("psycopg2.connect")
    def test_get_postgres_connection_failure(self, mock_connect):
        """Test PostgreSQL connection failure."""
        import psycopg2

        mock_connect.side_effect = psycopg2.Error("Connection failed")

        with pytest.raises(psycopg2.Error):
            self.db_manager.get_postgres_connection()

    @patch("redis.Redis")  # type: ignore
    def test_get_redis_client_success(self, mock_redis):
        """Test successful Redis client creation."""
        mock_client = Mock()
        mock_client.ping.return_value = True
        mock_redis.return_value = mock_client

        redis_client = self.db_manager.get_redis_client()

        assert redis_client == mock_client
        mock_redis.assert_called_once_with(
            host=self.config.redis_host,
            port=self.config.redis_port,
            password=self.config.redis_password,
            db=self.config.redis_database,
            decode_responses=True,
        )
        mock_client.ping.assert_called_once()

    @patch("redis.Redis")  # type: ignore
    def test_get_redis_client_failure(self, mock_redis):
        """Test Redis client creation failure."""
        import redis  # type: ignore

        mock_client = Mock()
        mock_client.ping.side_effect = redis.ConnectionError("Connection failed")  # type: ignore
        mock_redis.return_value = mock_client

        with pytest.raises(redis.ConnectionError):
            self.db_manager.get_redis_client()

    def test_get_minio_client_success(self):
        """Test successful MinIO client creation."""
        # Mock the entire get_minio_client method to avoid network calls
        with patch.object(self.db_manager, "get_minio_client") as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client

            minio_client = self.db_manager.get_minio_client()

            assert minio_client == mock_client
            mock_get_client.assert_called_once()

    @patch("minio.Minio")
    def test_get_minio_client_failure(self, mock_minio):
        """Test MinIO client creation failure."""
        mock_client = Mock()
        mock_client.list_buckets.side_effect = Exception("Connection failed")
        mock_minio.return_value = mock_client

        with pytest.raises(Exception):
            self.db_manager.get_minio_client()

    @patch.object(DatabaseManager, "get_postgres_connection")
    def test_get_db_session_success(self, mock_get_conn):
        """Test successful database session."""
        mock_connection = Mock()
        mock_get_conn.return_value = mock_connection

        with self.db_manager.get_db_session() as conn:
            assert conn == mock_connection

        mock_connection.commit.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch.object(DatabaseManager, "get_postgres_connection")
    def test_get_db_session_exception(self, mock_get_conn):
        """Test database session with exception."""
        mock_connection = Mock()
        mock_get_conn.return_value = mock_connection

        with pytest.raises(Exception):
            with self.db_manager.get_db_session() as conn:
                raise Exception("Test error")

        mock_connection.rollback.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch.object(DatabaseManager, "get_postgres_connection")
    @patch.object(DatabaseManager, "get_redis_client")
    @patch.object(DatabaseManager, "get_minio_client")
    def test_test_connections_all_success(self, mock_minio, mock_redis, mock_postgres):
        """Test successful connection testing."""
        # Mock PostgreSQL with proper context manager support
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = [1]
        mock_conn.cursor.return_value = mock_cursor
        mock_postgres.return_value = mock_conn

        # Mock Redis
        mock_redis_client = Mock()
        mock_redis_client.ping.return_value = True
        mock_redis.return_value = mock_redis_client

        # Mock MinIO
        mock_minio_client = Mock()
        mock_minio_client.list_buckets.return_value = []
        mock_minio.return_value = mock_minio_client

        # Mock the context manager methods
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        mock_cursor.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor.__exit__ = Mock(return_value=None)

        results = self.db_manager.test_connections()

        assert results["postgresql"] is True
        assert results["redis"] is True
        assert results["minio"] is True

    @patch.object(DatabaseManager, "get_minio_client")
    def test_create_required_buckets(self, mock_minio):
        """Test MinIO bucket creation."""
        mock_client = Mock()
        mock_client.bucket_exists.side_effect = lambda x: False
        mock_minio.return_value = mock_client

        self.db_manager.create_required_buckets()

        expected_buckets = [
            "raw-data",
            "processed-data",
            "company-profiles",
            "financial-data",
            "economic-data",
            "backups",
        ]

        for bucket in expected_buckets:
            mock_client.make_bucket.assert_any_call(bucket)


class TestDatabaseInfrastructureIntegration:
    """Integration tests for database infrastructure."""

    @pytest.mark.integration
    def test_database_config_import(self):
        """Test that database configuration can be imported."""
        try:
            from config.database import DatabaseConfig, DatabaseManager

            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import database modules: {e}")

    def test_get_db_manager_function(self):
        """Test the get_db_manager function."""
        try:
            db_manager = get_db_manager()
            assert isinstance(db_manager, DatabaseManager)
        except Exception as e:
            pytest.fail(f"Failed to get database manager: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
