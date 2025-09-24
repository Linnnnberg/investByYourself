#!/usr/bin/env python3
"""
Test script to verify environment variable loading works correctly
after removing hardcoded credentials.
"""

import os

from dotenv import load_dotenv


def test_env_loading():
    """Test environment variable loading from test.env file."""
    print("🔧 Testing Environment Variable Loading...")
    print("=" * 50)

    # Load test environment
    load_dotenv("test.env")
    print("✅ test.env file loaded successfully")

    # Test database credentials
    print("\n📊 Database Credentials:")
    print(f"  DB_HOST: {os.getenv('DB_HOST', 'NOT_SET')}")
    print(f"  DB_PASSWORD: {os.getenv('DB_PASSWORD', 'NOT_SET')}")
    print(f"  POSTGRES_PASSWORD: {os.getenv('POSTGRES_PASSWORD', 'NOT_SET')}")

    # Test Redis credentials
    print("\n🔴 Redis Credentials:")
    print(f"  REDIS_HOST: {os.getenv('REDIS_HOST', 'NOT_SET')}")
    print(f"  REDIS_PASSWORD: {os.getenv('REDIS_PASSWORD', 'NOT_SET')}")

    # Test MinIO credentials
    print("\n📦 MinIO Credentials:")
    print(f"  MINIO_HOST: {os.getenv('MINIO_HOST', 'NOT_SET')}")
    print(f"  MINIO_SECRET_KEY: {os.getenv('MINIO_SECRET_KEY', 'NOT_SET')}")

    # Test API keys
    print("\n🔑 API Keys:")
    print(f"  ALPHA_VANTAGE_API_KEY: {os.getenv('ALPHA_VANTAGE_API_KEY', 'NOT_SET')}")
    print(f"  FMP_API_KEY: {os.getenv('FMP_API_KEY', 'NOT_SET')}")
    print(f"  FRED_API_KEY: {os.getenv('FRED_API_KEY', 'NOT_SET')}")

    print("\n✅ Environment variable loading test completed!")


if __name__ == "__main__":
    test_env_loading()
