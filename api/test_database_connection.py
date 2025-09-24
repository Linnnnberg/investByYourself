#!/usr/bin/env python3
"""
Database Connection Test Script
Tech-028: API Implementation

Test script to verify PostgreSQL database connection with environment variables.
"""

import os
import sys

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_environment_variables():
    """Test if required environment variables are set."""
    print("🔍 Checking environment variables...")

    required_vars = [
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DATABASE",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
    ]

    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"❌ {var}: Not set")
        else:
            # Hide password for security
            if "PASSWORD" in var:
                print(f"✅ {var}: {'*' * len(value)}")
            else:
                print(f"✅ {var}: {value}")

    if missing_vars:
        print(f"\n❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False

    print("\n✅ All required environment variables are set!")
    return True


def test_database_connection():
    """Test actual database connection."""
    print("\n🔌 Testing database connection...")

    try:
        from src.services.database_service import db_service

        # Initialize database service
        db_service.initialize()

        # Test connection
        result = db_service.test_connection()

        if result["status"] == "connected":
            print("✅ Database connection successful!")
            print(f"   Database: {result['database']}")
            print(f"   Host: {result['host']}")
            print(f"   Port: {result['port']}")
            return True
        elif result["status"] == "mock_mode":
            print("✅ Mock data mode activated!")
            print(f"   Database: {result['database']}")
            print(f"   Host: {result['host']}")
            print(f"   Port: {result['port']}")
            print("   Note: Using mock data instead of real database")
            return True
        else:
            print(
                f"❌ Database connection failed: {result.get('error', 'Unknown error')}"
            )
            return False

    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False


def main():
    """Main test function."""
    print("=" * 60)
    print("InvestByYourself API - Database Connection Test")
    print("=" * 60)

    # Test environment variables
    env_ok = test_environment_variables()

    if not env_ok:
        print("\n📝 Instructions:")
        print("1. Create a .env file in the api/ directory")
        print("2. Add your PostgreSQL credentials")
        print("3. Run this script again")
        return False

    # Test database connection
    db_ok = test_database_connection()

    if db_ok:
        print("\n🎉 Database connection test completed successfully!")
        print("   Your FastAPI app should now be able to connect to PostgreSQL.")
    else:
        print("\n❌ Database connection test failed.")
        print(
            "   Please check your PostgreSQL credentials and ensure PostgreSQL is running."
        )

    return db_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
