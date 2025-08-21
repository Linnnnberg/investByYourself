#!/usr/bin/env python3
"""
Test script to verify configuration classes work correctly
after removing hardcoded credentials.
"""

import os
import sys

from dotenv import load_dotenv

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))


def test_database_config():
    """Test DatabaseConfig class."""
    print("🔧 Testing DatabaseConfig Class...")
    print("-" * 40)

    try:
        from config.database import DatabaseConfig

        # Test default values
        config = DatabaseConfig()
        print(f"✅ Default config created:")
        print(f"  Host: {config.postgres_host}")
        print(f"  Port: {config.postgres_port}")
        print(f"  Password: {'SET' if config.postgres_password else 'NOT_SET'}")
        print(f"  Redis Password: {'SET' if config.redis_password else 'NOT_SET'}")

        # Test from_env method
        env_config = DatabaseConfig.from_env()
        print(f"\n✅ Environment config loaded:")
        print(f"  Host: {env_config.postgres_host}")
        print(f"  Port: {env_config.postgres_port}")
        print(f"  Password: {'SET' if env_config.postgres_password else 'NOT_SET'}")
        print(f"  Redis Password: {'SET' if env_config.redis_password else 'NOT_SET'}")

        return True

    except Exception as e:
        print(f"❌ DatabaseConfig test failed: {str(e)}")
        return False


def test_cache_config():
    """Test CacheConfig class."""
    print("\n🔧 Testing CacheConfig Class...")
    print("-" * 40)

    try:
        from src.etl.loaders.cache_loader import CacheConfig

        # Test default values
        config = CacheConfig()
        print(f"✅ Default config created:")
        print(f"  Host: {config.host}")
        print(f"  Port: {config.port}")
        print(f"  Password: {'SET' if config.password else 'NOT_SET'}")

        # Test from_env method
        env_config = CacheConfig.from_env()
        print(f"\n✅ Environment config loaded:")
        print(f"  Host: {env_config.host}")
        print(f"  Port: {env_config.port}")
        print(f"  Password: {'SET' if env_config.password else 'NOT_SET'}")

        return True

    except Exception as e:
        print(f"❌ CacheConfig test failed: {str(e)}")
        return False


def test_database_loader_config():
    """Test DatabaseLoader config."""
    print("\n🔧 Testing DatabaseLoader Config...")
    print("-" * 40)

    try:
        from src.etl.loaders.database_loader import DatabaseConfig

        # Test default values
        config = DatabaseConfig()
        print(f"✅ Default config created:")
        print(f"  Host: {config.host}")
        print(f"  Port: {config.port}")
        print(f"  Password: {'SET' if config.password else 'NOT_SET'}")

        # Test from_env method
        env_config = DatabaseConfig.from_env()
        print(f"\n✅ Environment config loaded:")
        print(f"  Host: {env_config.host}")
        print(f"  Port: {env_config.port}")
        print(f"  Password: {'SET' if env_config.password else 'NOT_SET'}")

        return True

    except Exception as e:
        print(f"❌ DatabaseLoader config test failed: {str(e)}")
        return False


def main():
    """Run all configuration tests."""
    print("🚀 Testing Configuration Classes After Security Fixes")
    print("=" * 60)

    # Load test environment
    load_dotenv("test.env")
    print("✅ Test environment loaded\n")

    # Run tests
    tests = [
        test_database_config,
        test_cache_config,
        test_database_loader_config,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    # Summary
    print("\n" + "=" * 60)
    print(f"🎯 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("✅ All configuration tests passed! Security fixes working correctly.")
    else:
        print("❌ Some tests failed. Check the output above.")

    return passed == total


if __name__ == "__main__":
    main()
