"""
Configuration Management - Financial Analysis Service
===================================================

Configuration settings and environment variable management.
"""

import os
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Service Configuration
    service_name: str = "financial-analysis-service"
    service_version: str = "1.0.0"
    debug: bool = Field(default=False, env="DEBUG")

    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")

    # Database Configuration
    database_url: str = Field(
        default="postgresql://user:password@localhost:5432/financial_analysis",
        env="DATABASE_URL",
    )
    database_pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")

    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_pool_size: int = Field(default=10, env="REDIS_POOL_SIZE")

    # API Configuration
    api_prefix: str = "/api/v1"
    cors_origins: list = Field(default=["*"], env="CORS_ORIGINS")
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")

    # Security Configuration
    secret_key: str = Field(
        default="your-secret-key-here-change-in-production", env="SECRET_KEY"
    )
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    # Strategy Framework Configuration
    strategy_cache_ttl: int = Field(default=3600, env="STRATEGY_CACHE_TTL")  # 1 hour
    backtest_timeout: int = Field(default=300, env="BACKTEST_TIMEOUT")  # 5 minutes
    max_concurrent_backtests: int = Field(default=5, env="MAX_CONCURRENT_BACKTESTS")

    # Data Source Configuration
    yahoo_finance_api_key: Optional[str] = Field(
        default=None, env="YAHOO_FINANCE_API_KEY"
    )
    alpha_vantage_api_key: Optional[str] = Field(
        default=None, env="ALPHA_VANTAGE_API_KEY"
    )
    fred_api_key: Optional[str] = Field(default=None, env="FRED_API_KEY")

    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT"
    )

    # Monitoring Configuration
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings


# Environment-specific configurations
def is_development() -> bool:
    """Check if running in development mode."""
    return settings.debug or os.getenv("ENVIRONMENT", "").lower() == "development"


def is_production() -> bool:
    """Check if running in production mode."""
    return os.getenv("ENVIRONMENT", "").lower() == "production"


def is_testing() -> bool:
    """Check if running in testing mode."""
    return os.getenv("ENVIRONMENT", "").lower() == "testing"


# Configuration validation
def validate_config():
    """Validate critical configuration settings."""
    errors = []

    # Check required API keys for production
    if is_production():
        if (
            not settings.secret_key
            or settings.secret_key == "your-secret-key-here-change-in-production"
        ):
            errors.append("SECRET_KEY must be set in production")

        if not settings.database_url or "localhost" in settings.database_url:
            errors.append("DATABASE_URL must point to production database")

    # Check database URL format
    if not settings.database_url.startswith(("postgresql://", "postgres://")):
        errors.append("DATABASE_URL must be a valid PostgreSQL connection string")

    # Check Redis URL format
    if not settings.redis_url.startswith("redis://"):
        errors.append("REDIS_URL must be a valid Redis connection string")

    if errors:
        raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")


# Validate configuration on import
try:
    validate_config()
except ValueError as e:
    print(f"Warning: {e}")
    # In production, this should raise an error and prevent startup
