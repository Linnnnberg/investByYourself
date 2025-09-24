"""
Database Configuration for investByYourself ETL Infrastructure
Tech-008: Database Infrastructure Setup

This module provides database connection configuration and management
for the ETL pipeline and company analysis infrastructure.
"""

import logging
import os
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Dict, Optional

import psycopg2
import redis  # type: ignore
from minio import Minio  # type: ignore
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Database configuration settings."""

    # PostgreSQL Configuration
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_database: str = "investbyyourself"
    postgres_user: str = "etl_user"
    postgres_password: str = ""

    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = None
    redis_database: int = 0

    # MinIO Configuration
    minio_host: str = "localhost"
    minio_port: int = 9000
    minio_access_key: str = "minio_admin"
    minio_secret_key: str = ""
    minio_secure: bool = False

    # Connection Pool Configuration
    max_connections: int = 20
    min_connections: int = 5
    connection_timeout: int = 30
    idle_timeout: int = 300

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Create configuration from environment variables."""
        return cls(
            postgres_host=os.getenv("POSTGRES_HOST", "localhost"),
            postgres_port=int(os.getenv("POSTGRES_PORT", "5432")),
            postgres_database=os.getenv("POSTGRES_DB", "investbyyourself"),
            postgres_user=os.getenv("POSTGRES_USER", "etl_user"),
            postgres_password=os.getenv("POSTGRES_PASSWORD", ""),
            redis_host=os.getenv("REDIS_HOST", "localhost"),
            redis_port=int(os.getenv("REDIS_PORT", "6379")),
            redis_password=os.getenv("REDIS_PASSWORD"),
            minio_host=os.getenv("MINIO_HOST", "localhost"),
            minio_port=int(os.getenv("MINIO_PORT", "9000")),
            minio_access_key=os.getenv("MINIO_ACCESS_KEY", "minio_admin"),
            minio_secret_key=os.getenv("MINIO_SECRET_KEY", ""),
        )


class DatabaseManager:
    """Database connection and management class."""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._postgres_pool: Optional[Any] = None
        self._redis_client: Optional[redis.Redis] = None
        self._minio_client: Optional[Minio] = None

    def get_postgres_connection(self):
        """Get PostgreSQL connection."""
        try:
            connection = psycopg2.connect(
                host=self.config.postgres_host,
                port=self.config.postgres_port,
                database=self.config.postgres_database,
                user=self.config.postgres_user,
                password=self.config.postgres_password,
                cursor_factory=RealDictCursor,
            )
            return connection
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise

    def get_redis_client(self) -> redis.Redis:
        """Get Redis client."""
        if self._redis_client is None:
            try:
                self._redis_client = redis.Redis(
                    host=self.config.redis_host,
                    port=self.config.redis_port,
                    password=self.config.redis_password,
                    db=self.config.redis_database,
                    decode_responses=True,
                )
                # Test connection
                self._redis_client.ping()
                logger.info("Redis connection established successfully")
            except redis.ConnectionError as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise
        return self._redis_client

    def get_minio_client(self) -> Minio:
        """Get MinIO client."""
        if self._minio_client is None:
            try:
                self._minio_client = Minio(
                    f"{self.config.minio_host}:{self.config.minio_port}",
                    access_key=self.config.minio_access_key,
                    secret_key=self.config.minio_secret_key,
                    secure=self.config.minio_secure,
                )
                # Test connection by listing buckets
                self._minio_client.list_buckets()
                logger.info("MinIO connection established successfully")
            except Exception as e:
                logger.error(f"Failed to connect to MinIO: {e}")
                raise
        return self._minio_client

    @contextmanager
    def get_db_session(self):
        """Context manager for database sessions."""
        connection = None
        try:
            connection = self.get_postgres_connection()
            yield connection
            connection.commit()
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            if connection:
                connection.close()

    def test_connections(self) -> Dict[str, bool]:
        """Test all database connections."""
        results = {}

        # Test PostgreSQL
        try:
            with self.get_db_session() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    results["postgresql"] = True
                    logger.info("PostgreSQL connection test: PASSED")
        except Exception as e:
            results["postgresql"] = False
            logger.error(f"PostgreSQL connection test: FAILED - {e}")

        # Test Redis
        try:
            redis_client = self.get_redis_client()
            redis_client.ping()
            results["redis"] = True
            logger.info("Redis connection test: PASSED")
        except Exception as e:
            results["redis"] = False
            logger.error(f"Redis connection test: FAILED - {e}")

        # Test MinIO
        try:
            minio_client = self.get_minio_client()
            minio_client.list_buckets()
            results["minio"] = True
            logger.info("MinIO connection test: PASSED")
        except Exception as e:
            results["minio"] = False
            logger.error(f"MinIO connection test: FAILED - {e}")

        return results

    def create_required_buckets(self):
        """Create required MinIO buckets for data lake."""
        try:
            minio_client = self.get_minio_client()
            required_buckets = [
                "raw-data",
                "processed-data",
                "company-profiles",
                "financial-data",
                "economic-data",
                "backups",
            ]

            for bucket_name in required_buckets:
                if not minio_client.bucket_exists(bucket_name):
                    minio_client.make_bucket(bucket_name)
                    logger.info(f"Created MinIO bucket: {bucket_name}")
                else:
                    logger.info(f"MinIO bucket already exists: {bucket_name}")

        except Exception as e:
            logger.error(f"Failed to create MinIO buckets: {e}")
            raise


# Global database manager instance
db_manager = DatabaseManager(DatabaseConfig.from_env())


def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance."""
    return db_manager
