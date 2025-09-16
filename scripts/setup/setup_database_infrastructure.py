#!/usr/bin/env python3
"""
Database Infrastructure Setup Script
Tech-008: Database Infrastructure Setup

This script sets up and tests the database infrastructure for the ETL pipeline:
- Tests database connections (PostgreSQL, Redis, MinIO)
- Creates required MinIO buckets for data lake
- Validates database schema
- Sets up initial monitoring and health checks
"""

import os
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

import logging

from config.database import DatabaseConfig, get_db_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_database_connections():
    """Test all database connections."""
    logger.info("🔍 Testing database connections...")

    try:
        db_manager = get_db_manager()
        results = db_manager.test_connections()

        # Display results
        logger.info("📊 Connection Test Results:")
        for service, status in results.items():
            status_icon = "✅" if status else "❌"
            logger.info(
                f"  {status_icon} {service.upper()}: {'PASSED' if status else 'FAILED'}"
            )

        # Check if all connections passed
        all_passed = all(results.values())
        if all_passed:
            logger.info("🎉 All database connections are working!")
        else:
            logger.error("❌ Some database connections failed!")

        return all_passed

    except Exception as e:
        logger.error(f"❌ Failed to test database connections: {e}")
        return False


def setup_minio_buckets():
    """Set up required MinIO buckets for data lake."""
    logger.info("🪣 Setting up MinIO buckets for data lake...")

    try:
        db_manager = get_db_manager()
        db_manager.create_required_buckets()
        logger.info("✅ MinIO buckets setup completed successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to setup MinIO buckets: {e}")
        return False


def validate_database_schema():
    """Validate that the database schema is properly set up."""
    logger.info("🏗️ Validating database schema...")

    try:
        db_manager = get_db_manager()

        with db_manager.get_db_session() as conn:
            with conn.cursor() as cur:
                # Check if core tables exist
                required_tables = [
                    "companies",
                    "stock_prices",
                    "economic_indicators",
                    "economic_data",
                    "portfolios",
                    "portfolio_holdings",
                ]

                existing_tables = []
                for table in required_tables:
                    cur.execute(
                        """
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables
                            WHERE table_schema = 'public'
                            AND table_name = %s
                        );
                    """,
                        (table,),
                    )
                    exists = cur.fetchone()[0]
                    existing_tables.append((table, exists))

                # Display results
                logger.info("📋 Schema Validation Results:")
                all_tables_exist = True
                for table, exists in existing_tables:
                    status_icon = "✅" if exists else "❌"
                    status_text = "EXISTS" if exists else "MISSING"
                    logger.info(f"  {status_icon} {table}: {status_text}")
                    if not exists:
                        all_tables_exist = False

                if all_tables_exist:
                    logger.info("✅ All required tables exist!")
                else:
                    logger.warning("⚠️ Some required tables are missing!")

                # Check table row counts
                logger.info("📊 Table Row Counts:")
                for table, exists in existing_tables:
                    if exists:
                        cur.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cur.fetchone()[0]
                        logger.info(f"  📈 {table}: {count:,} rows")

                return all_tables_exist

    except Exception as e:
        logger.error(f"❌ Failed to validate database schema: {e}")
        return False


def setup_monitoring():
    """Set up basic monitoring and health checks."""
    logger.info("📊 Setting up database monitoring...")

    try:
        db_manager = get_db_manager()

        # Set up Redis monitoring keys
        redis_client = db_manager.get_redis_client()
        redis_client.set("db_health:last_check", time.time())
        redis_client.set("db_health:status", "healthy")
        redis_client.set("db_health:postgres", "connected")
        redis_client.set("db_health:redis", "connected")
        redis_client.set("db_health:minio", "connected")

        # Set up MinIO monitoring
        minio_client = db_manager.get_minio_client()

        # Create monitoring bucket if it doesn't exist
        if not minio_client.bucket_exists("monitoring"):
            minio_client.make_bucket("monitoring")
            logger.info("✅ Created monitoring bucket")

        logger.info("✅ Database monitoring setup completed!")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to setup monitoring: {e}")
        return False


def run_health_check():
    """Run a comprehensive health check of the database infrastructure."""
    logger.info("🏥 Running comprehensive health check...")

    try:
        db_manager = get_db_manager()

        # Test PostgreSQL performance
        with db_manager.get_db_session() as conn:
            with conn.cursor() as cur:
                start_time = time.time()
                cur.execute("SELECT COUNT(*) FROM companies")
                count = cur.fetchone()[0]
                query_time = time.time() - start_time

                logger.info(
                    f"📊 PostgreSQL Performance: {query_time:.3f}s for companies count query"
                )

                if query_time < 0.1:
                    logger.info("✅ PostgreSQL performance: EXCELLENT")
                elif query_time < 0.5:
                    logger.info("✅ PostgreSQL performance: GOOD")
                else:
                    logger.warning("⚠️ PostgreSQL performance: SLOW")

        # Test Redis performance
        redis_client = db_manager.get_redis_client()
        start_time = time.time()
        redis_client.ping()
        redis_time = time.time() - start_time

        logger.info(f"📊 Redis Performance: {redis_time:.3f}s for ping")

        if redis_time < 0.01:
            logger.info("✅ Redis performance: EXCELLENT")
        elif redis_time < 0.05:
            logger.info("✅ Redis performance: GOOD")
        else:
            logger.warning("⚠️ Redis performance: SLOW")

        # Test MinIO performance
        minio_client = db_manager.get_minio_client()
        start_time = time.time()
        minio_client.list_buckets()
        minio_time = time.time() - start_time

        logger.info(f"📊 MinIO Performance: {minio_time:.3f}s for bucket listing")

        if minio_time < 0.1:
            logger.info("✅ MinIO performance: EXCELLENT")
        elif minio_time < 0.5:
            logger.info("✅ MinIO performance: GOOD")
        else:
            logger.warning("⚠️ MinIO performance: SLOW")

        logger.info("✅ Health check completed successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return False


def main():
    """Main setup function."""
    logger.info("🚀 Starting Database Infrastructure Setup (Tech-008)")
    logger.info("=" * 60)

    # Step 1: Test connections
    if not test_database_connections():
        logger.error(
            "❌ Database connection test failed. Please check your Docker services."
        )
        return False

    # Step 2: Setup MinIO buckets
    if not setup_minio_buckets():
        logger.error("❌ MinIO bucket setup failed.")
        return False

    # Step 3: Validate schema
    if not validate_database_schema():
        logger.warning("⚠️ Schema validation failed. Some tables may be missing.")

    # Step 4: Setup monitoring
    if not setup_monitoring():
        logger.error("❌ Monitoring setup failed.")
        return False

    # Step 5: Run health check
    if not run_health_check():
        logger.error("❌ Health check failed.")
        return False

    logger.info("=" * 60)
    logger.info("🎉 Database Infrastructure Setup Completed Successfully!")
    logger.info("✅ All systems are operational and ready for ETL pipeline")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
