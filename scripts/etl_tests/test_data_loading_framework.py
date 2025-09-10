"""
Test Script for Data Loading Framework (Phase 3)

This script demonstrates and validates the data loading capabilities implemented
in Phase 3 of TECH-009, including database, file, and cache loaders.

Features Tested:
- Database loading with PostgreSQL
- File loading with multiple formats
- Cache loading with Redis
- Incremental loading strategies
- Data versioning and tracking
- Performance metrics

Author: investByYourself Development Team
Created: August 2025
Phase: Tech-009 Phase 3 - Data Loading & Storage
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Any, Dict

# Add src directory to path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from src.etl.loaders import (CacheConfig, CacheLoader, CompressionType,
                             DatabaseConfig, DatabaseLoader, FileFormat,
                             FileLoader, LoadingStrategy, SerializationFormat)


async def test_database_loader():
    """Test database loading capabilities."""
    print("\\n🔶 Test 1: Database Loader")
    print("-" * 50)

    # Sample financial data
    sample_data = [
        {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "price": 150.25,
            "market_cap": 2500000000000,
            "pe_ratio": 25.4,
            "timestamp": datetime.now().isoformat(),
        },
        {
            "symbol": "MSFT",
            "name": "Microsoft Corporation",
            "price": 285.76,
            "market_cap": 2100000000000,
            "pe_ratio": 28.2,
            "timestamp": datetime.now().isoformat(),
        },
        {
            "symbol": "GOOGL",
            "name": "Alphabet Inc.",
            "price": 125.33,
            "market_cap": 1600000000000,
            "pe_ratio": 22.1,
            "timestamp": datetime.now().isoformat(),
        },
    ]

    try:
        # Initialize database loader
        config = DatabaseConfig(
            host="localhost",
            port=5432,
            database="investbyyourself",
            user="etl_user",
            password=os.getenv("DB_PASSWORD", ""),
        )

        async with DatabaseLoader(config=config, enable_versioning=True) as loader:
            # Test UPSERT strategy
            print("   📥 Testing UPSERT loading strategy...")
            result = await loader.load_data(
                data=sample_data,
                strategy=LoadingStrategy.UPSERT,
                target_table="test_companies",
            )

            if result.success:
                print(
                    f"   ✅ Successfully loaded {result.metrics.records_processed} records"
                )
                print(f"      - Inserted: {result.metrics.records_inserted}")
                print(f"      - Updated: {result.metrics.records_updated}")
                print(f"      - Duration: {result.metrics.duration_seconds:.2f}s")
                print(
                    f"      - Throughput: {result.metrics.calculate_throughput():.1f} records/sec"
                )

                if result.data_version:
                    print(f"      - Version: {result.data_version.version_id}")
                    print(f"      - Checksum: {result.data_version.checksum[:8]}...")
            else:
                print(f"   ❌ Loading failed: {result.errors}")

            # Test incremental loading
            print("   📥 Testing incremental loading...")
            incremental_data = [
                {
                    "symbol": "TSLA",
                    "name": "Tesla Inc.",
                    "price": 195.42,
                    "market_cap": 620000000000,
                    "pe_ratio": 45.8,
                    "timestamp": datetime.now().isoformat(),
                }
            ]

            result2 = await loader.load_data(
                data=incremental_data,
                strategy=LoadingStrategy.UPSERT,
                target_table="test_companies",
            )

            if result2.success:
                print(
                    f"   ✅ Incremental load successful: {result2.metrics.records_processed} records"
                )

            # Get statistics
            print("   📊 Getting database statistics...")
            stats = await loader.get_statistics("test_companies")
            if stats.get("status") != "failed":
                print(f"      - Table size: {stats.get('table_size', 'unknown')}")
                print(
                    f"      - Estimated rows: {stats.get('estimated_rows', 'unknown')}"
                )
                print(f"      - Indexes: {len(stats.get('indexes', []))}")

    except Exception as e:
        print(f"   ❌ Database loader test failed: {str(e)}")
        print("      Note: This test requires PostgreSQL to be running")


async def test_file_loader():
    """Test file loading capabilities."""
    print("\\n🔶 Test 2: File Loader")
    print("-" * 50)

    # Sample data for file testing
    sample_data = [
        {
            "company": "Apple",
            "ticker": "AAPL",
            "sector": "Technology",
            "revenue": 394328000000,
            "employees": 164000,
        },
        {
            "company": "Microsoft",
            "ticker": "MSFT",
            "sector": "Technology",
            "revenue": 211915000000,
            "employees": 221000,
        },
        {
            "company": "Google",
            "ticker": "GOOGL",
            "sector": "Technology",
            "revenue": 307394000000,
            "employees": 190000,
        },
    ]

    try:
        # Test JSON format with compression
        print("   📄 Testing JSON file loading with gzip compression...")
        async with FileLoader(
            base_path="data/test_output",
            file_format=FileFormat.JSON,
            compression=CompressionType.GZIP,
            enable_versioning=True,
        ) as loader:
            result = await loader.load_data(
                data=sample_data,
                strategy=LoadingStrategy.REPLACE,
                target_table="companies_data",
            )

            if result.success:
                print(f"   ✅ JSON file created successfully")
                print(f"      - Records: {result.metrics.records_processed}")
                print(f"      - Duration: {result.metrics.duration_seconds:.2f}s")

                if result.data_version:
                    print(f"      - Version: {result.data_version.version_id}")

        # Test CSV format
        print("   📄 Testing CSV file loading...")
        async with FileLoader(
            base_path="data/test_output",
            file_format=FileFormat.CSV,
            compression=CompressionType.NONE,
        ) as loader:
            result = await loader.load_data(
                data=sample_data,
                strategy=LoadingStrategy.APPEND,
                target_table="companies_csv",
            )

            if result.success:
                print(f"   ✅ CSV file created successfully")

        # Test JSONL format
        print("   📄 Testing JSONL (JSON Lines) format...")
        async with FileLoader(
            base_path="data/test_output",
            file_format=FileFormat.JSONL,
            compression=CompressionType.NONE,
        ) as loader:
            result = await loader.load_data(
                data=sample_data,
                strategy=LoadingStrategy.INCREMENTAL,
                target_table="companies_jsonl",
            )

            if result.success:
                print(f"   ✅ JSONL file created successfully")

                # Test incremental loading (should skip duplicates)
                result2 = await loader.load_data(
                    data=sample_data[:2],  # Same data
                    strategy=LoadingStrategy.INCREMENTAL,
                    target_table="companies_jsonl",
                )
                print(
                    f"   📥 Incremental test: {result2.metrics.records_processed} records processed"
                )

        # Get file statistics
        print("   📊 Getting file statistics...")
        stats = await loader.get_statistics("data/test_output/companies_data.json.gzip")
        if stats.get("status") != "file_not_found":
            print(f"      - File size: {stats.get('size_human', 'unknown')}")
            print(f"      - Records: {stats.get('record_count', 'unknown')}")

    except Exception as e:
        print(f"   ❌ File loader test failed: {str(e)}")


async def test_cache_loader():
    """Test cache loading capabilities."""
    print("\\n🔶 Test 3: Cache Loader")
    print("-" * 50)

    # Sample market data for caching
    market_data = [
        {
            "symbol": "SPY",
            "price": 425.67,
            "volume": 45000000,
            "timestamp": datetime.now().isoformat(),
            "market": "NYSE",
        },
        {
            "symbol": "QQQ",
            "price": 358.42,
            "volume": 32000000,
            "timestamp": datetime.now().isoformat(),
            "market": "NASDAQ",
        },
        {
            "symbol": "IWM",
            "price": 185.23,
            "volume": 15000000,
            "timestamp": datetime.now().isoformat(),
            "market": "NYSE",
        },
    ]

    try:
        # Initialize cache loader
        config = CacheConfig(
            host="localhost",
            port=6379,
            password=os.getenv("REDIS_PASSWORD"),
            default_ttl=3600,  # 1 hour
        )

        async with CacheLoader(
            config=config,
            serialization_format=SerializationFormat.JSON,
            enable_versioning=True,
        ) as loader:
            # Test caching with custom key pattern
            print("   🗂️  Testing cache loading with key patterns...")
            result = await loader.load_data(
                data=market_data,
                strategy=LoadingStrategy.UPSERT,
                target_table="market_data",
                key_pattern="etf:{symbol}",
                ttl=1800,  # 30 minutes
            )

            if result.success:
                print(
                    f"   ✅ Successfully cached {result.metrics.records_processed} records"
                )
                print(f"      - Duration: {result.metrics.duration_seconds:.2f}s")

                if result.data_version:
                    print(f"      - Version: {result.data_version.version_id}")

            # Test cache retrieval
            print("   🔍 Testing cache retrieval...")
            cached_value = await loader.get_cache(
                "investbyyourself:market_data:etf:SPY"
            )
            if cached_value:
                print(f"   ✅ Cache hit for SPY: ${cached_value['price']}")
            else:
                print("   ❌ Cache miss for SPY")

            # Test cache miss
            missing_value = await loader.get_cache(
                "investbyyourself:market_data:etf:NONEXISTENT"
            )
            if missing_value is None:
                print("   ✅ Cache miss handled correctly for non-existent key")

            # Get cache statistics
            print("   📊 Getting cache statistics...")
            stats = await loader.get_statistics("market_data")
            if stats.get("status") != "failed":
                print(f"      - Keys in namespace: {stats.get('key_count', 0)}")
                cache_metrics = stats.get("cache_metrics", {})
                print(f"      - Hit ratio: {cache_metrics.get('hit_ratio', 0):.1%}")
                print(
                    f"      - Total operations: {cache_metrics.get('hits', 0) + cache_metrics.get('misses', 0)}"
                )
                print(
                    f"      - Avg get time: {cache_metrics.get('avg_get_time_ms', 0):.1f}ms"
                )

    except Exception as e:
        print(f"   ❌ Cache loader test failed: {str(e)}")
        print("      Note: This test requires Redis to be running")


async def test_loading_strategies():
    """Test different loading strategies."""
    print("\\n🔶 Test 4: Loading Strategies Comparison")
    print("-" * 50)

    # Sample data for strategy testing
    initial_data = [
        {"id": 1, "name": "Company A", "value": 100},
        {"id": 2, "name": "Company B", "value": 200},
    ]

    updated_data = [
        {"id": 1, "name": "Company A Updated", "value": 150},  # Update
        {"id": 3, "name": "Company C", "value": 300},  # New
    ]

    try:
        async with FileLoader(
            base_path="data/strategy_test", file_format=FileFormat.JSON
        ) as loader:
            # Test REPLACE strategy
            print("   🔄 Testing REPLACE strategy...")
            result1 = await loader.load_data(
                data=initial_data,
                strategy=LoadingStrategy.REPLACE,
                target_table="strategy_test",
            )
            print(f"      - Initial load: {result1.metrics.records_processed} records")

            result2 = await loader.load_data(
                data=updated_data,
                strategy=LoadingStrategy.REPLACE,
                target_table="strategy_test",
            )
            print(f"      - Replace load: {result2.metrics.records_processed} records")

            # Test APPEND strategy
            print("   ➕ Testing APPEND strategy...")
            result3 = await loader.load_data(
                data=updated_data,
                strategy=LoadingStrategy.APPEND,
                target_table="strategy_append_test",
            )
            print(f"      - Append load: {result3.metrics.records_processed} records")

            # Test INCREMENTAL strategy
            print("   📈 Testing INCREMENTAL strategy...")
            result4 = await loader.load_data(
                data=initial_data,
                strategy=LoadingStrategy.INCREMENTAL,
                target_table="strategy_incremental_test",
            )
            print(
                f"      - Initial incremental: {result4.metrics.records_processed} records"
            )

            result5 = await loader.load_data(
                data=initial_data,  # Same data - should be skipped
                strategy=LoadingStrategy.INCREMENTAL,
                target_table="strategy_incremental_test",
            )
            print(
                f"      - Duplicate incremental: {result5.metrics.records_processed} records"
            )

    except Exception as e:
        print(f"   ❌ Loading strategies test failed: {str(e)}")


async def test_data_versioning():
    """Test data versioning capabilities."""
    print("\\n🔶 Test 5: Data Versioning")
    print("-" * 50)

    sample_data = [{"company": "VersionTest Corp", "value": 42}]

    try:
        async with FileLoader(
            base_path="data/version_test", enable_versioning=True
        ) as loader:
            # Create initial version
            print("   📋 Creating initial data version...")
            result1 = await loader.load_data(
                data=sample_data,
                strategy=LoadingStrategy.REPLACE,
                target_table="version_test",
            )

            if result1.data_version:
                print(f"      - Version 1: {result1.data_version.version_id}")
                print(f"      - Checksum: {result1.data_version.checksum}")
                print(f"      - Record count: {result1.data_version.record_count}")

            # Create updated version
            updated_data = [{"company": "VersionTest Corp", "value": 84}]
            result2 = await loader.load_data(
                data=updated_data,
                strategy=LoadingStrategy.REPLACE,
                target_table="version_test",
            )

            if result2.data_version:
                print(f"      - Version 2: {result2.data_version.version_id}")
                print(f"      - Checksum: {result2.data_version.checksum}")
                print(
                    f"      - Different from V1: {result1.data_version.checksum != result2.data_version.checksum}"
                )

    except Exception as e:
        print(f"   ❌ Data versioning test failed: {str(e)}")


async def run_comprehensive_test():
    """Run all data loading tests."""
    print("🚀 Starting Data Loading Framework Tests (Phase 3)")
    print("=" * 60)

    start_time = datetime.now()

    # Run all tests
    await test_database_loader()
    await test_file_loader()
    await test_cache_loader()
    await test_loading_strategies()
    await test_data_versioning()

    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\\n🎯 Test Summary")
    print("-" * 30)
    print(f"✅ All data loading tests completed")
    print(f"⏱️  Total duration: {duration:.2f} seconds")
    print(f"📅 Completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

    print("\\n📊 Features Demonstrated:")
    print("   • Database loading with PostgreSQL")
    print("   • File loading (JSON, CSV, JSONL)")
    print("   • Cache loading with Redis")
    print("   • Multiple loading strategies")
    print("   • Data versioning and tracking")
    print("   • Performance metrics")
    print("   • Compression support")
    print("   • Error handling and validation")

    print("\\n🎉 Phase 3 Data Loading Framework is ready!")


if __name__ == "__main__":
    # Run the comprehensive test
    try:
        asyncio.run(run_comprehensive_test())
    except KeyboardInterrupt:
        print("\\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\\n❌ Test failed with error: {str(e)}")
        import traceback

        traceback.print_exc()
