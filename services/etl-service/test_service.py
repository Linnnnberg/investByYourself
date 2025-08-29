"""
Test Script for ETL Service
Tech-021: ETL Service Extraction

Simple test to verify the ETL service can start and basic functionality works.
"""

import asyncio
import os
import sys

# Add service directory to path
sys.path.append(os.path.dirname(__file__))

from models.config import ETLServiceConfig
from worker.etl_worker import ETLWorker


async def test_etl_worker():
    """Test the ETL worker functionality."""
    print("Testing ETL Worker...")

    try:
        # Test configuration
        print("1. Testing configuration...")
        config = ETLServiceConfig()
        print(f"   - Service name: {config.service_name}")
        print(f"   - Service port: {config.service_port}")
        print(f"   - Database URL: {config.database_url[:50]}...")
        print(f"   - Redis host: {config.redis_host}")
        print(f"   - MinIO host: {config.minio_host}")

        # Test configuration validation
        print("2. Testing configuration validation...")
        config.validate_config()
        print("   - Configuration validation passed")

        # Test ETL worker initialization
        print("3. Testing ETL worker initialization...")
        worker = ETLWorker(config)
        await worker.initialize()
        print("   - ETL worker initialized successfully")

        # Test service status
        print("4. Testing service status...")
        status = worker.get_service_status()
        print(f"   - Service status: {status['service_status']}")
        print(f"   - Active jobs: {status['active_jobs']}")

        # Test job creation
        print("5. Testing job creation...")
        job_id = await worker.start_data_collection(
            source="yahoo_finance",
            symbols=["AAPL", "MSFT"],
            data_types=["profile", "financials"],
        )
        print(f"   - Collection job created: {job_id}")

        # Wait a bit for job to complete
        await asyncio.sleep(3)

        # Test job status
        print("6. Testing job status...")
        job_status = await worker.get_job_status(job_id)
        if job_status:
            print(f"   - Job status: {job_status['status']}")
            print(f"   - Job progress: {job_status['progress']}%")

        # Test final status
        print("7. Testing final status...")
        final_status = worker.get_service_status()
        print(f"   - Final active jobs: {final_status['active_jobs']}")
        print(f"   - Completed jobs today: {final_status['completed_jobs_today']}")

        # Test shutdown
        print("8. Testing shutdown...")
        await worker.shutdown()
        print("   - ETL worker shutdown successfully")

        print("\n✅ All tests passed! ETL service is working correctly.")

    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback

        traceback.print_exc()
        return False

    return True


def test_config_imports():
    """Test that all configuration imports work."""
    print("Testing configuration imports...")

    try:
        from models.config import ETLServiceConfig

        print("   - ETLServiceConfig imported successfully")

        config = ETLServiceConfig()
        print("   - Configuration instance created successfully")

        return True

    except Exception as e:
        print(f"   - Configuration import failed: {str(e)}")
        return False


def test_worker_imports():
    """Test that all worker imports work."""
    print("Testing worker imports...")

    try:
        from worker.etl_worker import ETLWorker

        print("   - ETLWorker imported successfully")

        worker = ETLWorker()
        print("   - Worker instance created successfully")

        return True

    except Exception as e:
        print(f"   - Worker import failed: {str(e)}")
        return False


def main():
    """Main test function."""
    print("🚀 ETL Service Test Suite")
    print("=" * 50)

    # Test imports first
    print("\n📦 Testing imports...")
    config_ok = test_config_imports()
    worker_ok = test_worker_imports()

    if not (config_ok and worker_ok):
        print("\n❌ Import tests failed. Cannot proceed with functional tests.")
        return False

    # Test async functionality
    print("\n🔧 Testing async functionality...")
    try:
        asyncio.run(test_etl_worker())
        return True
    except Exception as e:
        print(f"\n❌ Async test failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
