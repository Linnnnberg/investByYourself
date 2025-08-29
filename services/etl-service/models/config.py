"""
ETL Service Configuration Model
Tech-021: ETL Service Extraction

Configuration settings and environment variable management for the ETL service.
"""

import os
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class ETLServiceConfig(BaseSettings):
    """Configuration for the ETL service."""

    # Service Configuration
    service_name: str = Field(default="etl-service", description="Service name")
    service_version: str = Field(default="2.0.0", description="Service version")
    service_host: str = Field(default="0.0.0.0", description="Service host")
    service_port: int = Field(default=8001, description="Service port")
    service_reload: bool = Field(default=False, description="Enable auto-reload")

    # CORS Configuration
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins",
    )

    # Database Configuration
    database_url: str = Field(
        default="postgresql://etl_user:password@localhost:5432/investbyyourself",
        description="Database connection string",
    )
    database_pool_size: int = Field(
        default=10, description="Database connection pool size"
    )
    database_max_overflow: int = Field(default=20, description="Database max overflow")

    # Redis Configuration
    redis_host: str = Field(default="localhost", description="Redis host")
    redis_port: int = Field(default=6379, description="Redis port")
    redis_db: int = Field(default=0, description="Redis database")
    redis_password: Optional[str] = Field(default=None, description="Redis password")

    # MinIO Configuration
    minio_host: str = Field(default="localhost", description="MinIO host")
    minio_port: int = Field(default=9000, description="MinIO port")
    minio_access_key: str = Field(default="minio_admin", description="MinIO access key")
    minio_secret_key: str = Field(default="password", description="MinIO secret key")
    minio_secure: bool = Field(default=False, description="Use HTTPS for MinIO")

    # ETL Configuration
    etl_batch_size: int = Field(default=1000, description="ETL batch size")
    etl_max_workers: int = Field(default=4, description="ETL max workers")
    etl_retry_attempts: int = Field(default=3, description="ETL retry attempts")
    etl_retry_delay: int = Field(default=5, description="ETL retry delay in seconds")

    # API Configuration
    api_rate_limit: int = Field(default=100, description="API rate limit per minute")
    api_timeout: int = Field(default=30, description="API timeout in seconds")

    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format")

    # Monitoring Configuration
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    metrics_port: int = Field(default=8002, description="Metrics port")

    class Config:
        """Pydantic configuration."""

        env_prefix = "ETL_"
        case_sensitive = False
        env_file = ".env"

    def __init__(self, **kwargs):
        """Initialize configuration with environment variables."""
        super().__init__(**kwargs)

        # Override with environment variables if not set
        if (
            not self.database_url
            or self.database_url
            == "postgresql://etl_user:password@localhost:5432/investbyyourself"
        ):
            self.database_url = os.getenv("DATABASE_URL", self.database_url)

        if not self.redis_host or self.redis_host == "localhost":
            self.redis_host = os.getenv("REDIS_HOST", self.redis_host)
            self.redis_port = int(os.getenv("REDIS_PORT", str(self.redis_port)))
            self.redis_password = os.getenv("REDIS_PASSWORD", self.redis_password)

        if not self.minio_host or self.minio_host == "localhost":
            self.minio_host = os.getenv("MINIO_HOST", self.minio_host)
            self.minio_port = int(os.getenv("MINIO_PORT", str(self.minio_port)))
            self.minio_access_key = os.getenv("MINIO_ACCESS_KEY", self.minio_access_key)
            self.minio_secret_key = os.getenv("MINIO_SECRET_KEY", self.minio_secret_key)

    @property
    def redis_url(self) -> str:
        """Get Redis connection URL."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def minio_endpoint(self) -> str:
        """Get MinIO endpoint URL."""
        protocol = "https" if self.minio_secure else "http"
        return f"{protocol}://{self.minio_host}:{self.minio_port}"

    def validate_config(self) -> bool:
        """Validate the configuration."""
        required_vars = [
            "database_url",
            "redis_host",
            "minio_host",
            "minio_access_key",
            "minio_secret_key",
        ]

        for var in required_vars:
            if not getattr(self, var):
                raise ValueError(f"Required configuration variable {var} is not set")

        return True
