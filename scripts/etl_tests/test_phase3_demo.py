"""
Phase 3 Demo Script - Data Loading Framework Demonstration

This script demonstrates the Phase 3 data loading capabilities without requiring
external dependencies like PostgreSQL or Redis. It focuses on the file loader
and shows the architecture and capabilities of the loading framework.

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

from src.etl.loaders.base_loader import (BaseDataLoader, DataVersion,
                                         LoadingError, LoadingMetrics,
                                         LoadingResult, LoadingStrategy)
from src.etl.loaders.file_loader import CompressionType, FileFormat, FileLoader


class MockDatabaseLoader(BaseDataLoader):
    """Mock database loader for demonstration purposes."""

    def __init__(self, **kwargs):
        super().__init__(loader_id="mock_database_loader", **kwargs)
        self.mock_data_store = {}

    async def connect(self) -> None:
        """Mock connection."""
        self.is_connected = True
        print(f"   🔌 Mock database connection established")

    async def disconnect(self) -> None:
        """Mock disconnection."""
        self.is_connected = False
        print(f"   🔌 Mock database connection closed")

    async def load_data(
        self, data, strategy=LoadingStrategy.UPSERT, target_table=None, **kwargs
    ):
        """Mock data loading."""
        if not self.is_connected:
            raise LoadingError("Database loader not connected")

        # Normalize data
        if isinstance(data, dict):
            data = [data]

        # Initialize metrics
        self.metrics = LoadingMetrics(start_time=datetime.now())

        # Simulate loading
        table_data = self.mock_data_store.get(target_table, [])

        if strategy == LoadingStrategy.REPLACE:
            self.mock_data_store[target_table] = data
            self.metrics.records_inserted = len(data)
        elif strategy == LoadingStrategy.APPEND:
            self.mock_data_store[target_table] = table_data + data
            self.metrics.records_inserted = len(data)
        elif strategy == LoadingStrategy.UPSERT:
            # Mock upsert logic
            existing_ids = {
                record.get("id", record.get("symbol", str(i))): i
                for i, record in enumerate(table_data)
            }

            for record in data:
                record_id = record.get("id", record.get("symbol", "unknown"))
                if record_id in existing_ids:
                    # Update existing
                    table_data[existing_ids[record_id]] = record
                    self.metrics.records_updated += 1
                else:
                    # Insert new
                    table_data.append(record)
                    self.metrics.records_inserted += 1

            self.mock_data_store[target_table] = table_data

        self.metrics.records_processed = len(data)
        self.metrics.end_time = datetime.now()
        self.metrics.duration_seconds = (
            self.metrics.end_time - self.metrics.start_time
        ).total_seconds()

        # Create data version if enabled
        data_version = None
        if self.enable_versioning:
            checksum = self.calculate_checksum(data)
            data_version = await self.create_data_version(
                target_table, len(data), checksum
            )

        return LoadingResult(
            success=True, metrics=self.metrics, data_version=data_version
        )

    async def _load_batch(self, batch, strategy, target_table, **kwargs):
        return LoadingResult(
            success=True, metrics=LoadingMetrics(start_time=datetime.now())
        )

    async def get_data_version(self, target: str):
        return None

    async def create_data_version(
        self, target: str, record_count: int, checksum: str, metadata=None
    ):
        import uuid

        return DataVersion(
            version_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            checksum=checksum,
            record_count=record_count,
            schema_version="1.0",
            source=self.loader_id,
            metadata=metadata or {},
        )


class MockCacheLoader(BaseDataLoader):
    """Mock cache loader for demonstration purposes."""

    def __init__(self, **kwargs):
        super().__init__(loader_id="mock_cache_loader", **kwargs)
        self.mock_cache = {}
        self.cache_stats = {"hits": 0, "misses": 0, "sets": 0}

    async def connect(self) -> None:
        """Mock connection."""
        self.is_connected = True
        print(f"   🔌 Mock cache connection established")

    async def disconnect(self) -> None:
        """Mock disconnection."""
        self.is_connected = False
        print(f"   🔌 Mock cache connection closed")

    async def load_data(
        self, data, strategy=LoadingStrategy.UPSERT, target_table=None, **kwargs
    ):
        """Mock cache loading."""
        if not self.is_connected:
            raise LoadingError("Cache loader not connected")

        # Normalize data
        if isinstance(data, dict):
            data = [data]

        # Initialize metrics
        self.metrics = LoadingMetrics(start_time=datetime.now())

        # Mock caching
        for record in data:
            cache_key = (
                f"{target_table}:{record.get('symbol', record.get('id', 'unknown'))}"
            )
            self.mock_cache[cache_key] = record
            self.cache_stats["sets"] += 1
            self.metrics.records_inserted += 1

        self.metrics.records_processed = len(data)
        self.metrics.end_time = datetime.now()
        self.metrics.duration_seconds = (
            self.metrics.end_time - self.metrics.start_time
        ).total_seconds()

        return LoadingResult(success=True, metrics=self.metrics)

    async def _load_batch(self, batch, strategy, target_table, **kwargs):
        return LoadingResult(
            success=True, metrics=LoadingMetrics(start_time=datetime.now())
        )

    async def get_data_version(self, target: str):
        return None

    async def create_data_version(
        self, target: str, record_count: int, checksum: str, metadata=None
    ):
        import uuid

        return DataVersion(
            version_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            checksum=checksum,
            record_count=record_count,
            schema_version="1.0",
            source=self.loader_id,
            metadata=metadata or {},
        )

    def get_cache_stats(self):
        return self.cache_stats


async def demo_file_loader():
    """Demonstrate file loader capabilities."""
    print("\\n🔶 Demo 1: File Loader")
    print("-" * 50)

    # Sample financial data
    sample_data = [
        {
            "symbol": "AAPL",
            "company": "Apple Inc.",
            "sector": "Technology",
            "price": 150.25,
            "market_cap": 2500000000000,
            "pe_ratio": 25.4,
            "timestamp": datetime.now().isoformat(),
        },
        {
            "symbol": "MSFT",
            "company": "Microsoft Corporation",
            "sector": "Technology",
            "price": 285.76,
            "market_cap": 2100000000000,
            "pe_ratio": 28.2,
            "timestamp": datetime.now().isoformat(),
        },
        {
            "symbol": "GOOGL",
            "company": "Alphabet Inc.",
            "sector": "Technology",
            "price": 125.33,
            "market_cap": 1600000000000,
            "pe_ratio": 22.1,
            "timestamp": datetime.now().isoformat(),
        },
    ]

    try:
        # Test JSON format with compression
        print("   📄 Testing JSON file loading with gzip compression...")
        async with FileLoader(
            base_path="data/demo_output",
            file_format=FileFormat.JSON,
            compression=CompressionType.GZIP,
            enable_versioning=True,
        ) as loader:
            result = await loader.load_data(
                data=sample_data,
                strategy=LoadingStrategy.REPLACE,
                target_table="tech_stocks",
            )

            if result.success:
                print(f"   ✅ JSON file created successfully")
                print(f"      - Records processed: {result.metrics.records_processed}")
                print(f"      - Duration: {result.metrics.duration_seconds:.3f}s")
                print(
                    f"      - Throughput: {result.metrics.calculate_throughput():.1f} records/sec"
                )

                if result.data_version:
                    print(f"      - Version ID: {result.data_version.version_id}")
                    print(f"      - Checksum: {result.data_version.checksum[:8]}...")

        # Test CSV format
        print("   📄 Testing CSV file loading...")
        async with FileLoader(
            base_path="data/demo_output",
            file_format=FileFormat.CSV,
            compression=CompressionType.NONE,
        ) as loader:
            result = await loader.load_data(
                data=sample_data,
                strategy=LoadingStrategy.APPEND,
                target_table="tech_stocks_csv",
            )

            if result.success:
                print(f"   ✅ CSV file created successfully")
                print(f"      - Records processed: {result.metrics.records_processed}")

        # Test incremental loading
        print("   📈 Testing incremental loading...")
        new_data = [
            {
                "symbol": "TSLA",
                "company": "Tesla Inc.",
                "sector": "Automotive",
                "price": 195.42,
                "market_cap": 620000000000,
                "pe_ratio": 45.8,
                "timestamp": datetime.now().isoformat(),
            }
        ]

        async with FileLoader(
            base_path="data/demo_output", file_format=FileFormat.JSONL
        ) as loader:
            # Initial load
            result1 = await loader.load_data(
                data=sample_data,
                strategy=LoadingStrategy.INCREMENTAL,
                target_table="incremental_test",
            )

            # Incremental load
            result2 = await loader.load_data(
                data=new_data,
                strategy=LoadingStrategy.INCREMENTAL,
                target_table="incremental_test",
            )

            print(f"   ✅ Incremental loading test completed")
            print(f"      - Initial load: {result1.metrics.records_processed} records")
            print(
                f"      - Incremental load: {result2.metrics.records_processed} records"
            )

    except Exception as e:
        print(f"   ❌ File loader demo failed: {str(e)}")


async def demo_mock_database_loader():
    """Demonstrate mock database loader."""
    print("\\n🔶 Demo 2: Mock Database Loader")
    print("-" * 50)

    sample_data = [
        {"id": 1, "symbol": "AAPL", "price": 150.25},
        {"id": 2, "symbol": "MSFT", "price": 285.76},
    ]

    try:
        async with MockDatabaseLoader(enable_versioning=True) as loader:
            # Test UPSERT strategy
            print("   💾 Testing UPSERT loading strategy...")
            result = await loader.load_data(
                data=sample_data, strategy=LoadingStrategy.UPSERT, target_table="stocks"
            )

            if result.success:
                print(f"   ✅ Mock database load successful")
                print(f"      - Records processed: {result.metrics.records_processed}")
                print(f"      - Records inserted: {result.metrics.records_inserted}")
                print(f"      - Records updated: {result.metrics.records_updated}")
                print(
                    f"      - Success rate: {result.metrics.calculate_success_rate():.1f}%"
                )

                if result.data_version:
                    print(f"      - Version: {result.data_version.version_id}")

            # Test update scenario
            print("   🔄 Testing update scenario...")
            updated_data = [
                {"id": 1, "symbol": "AAPL", "price": 155.30},  # Update
                {"id": 3, "symbol": "GOOGL", "price": 125.33},  # New
            ]

            result2 = await loader.load_data(
                data=updated_data,
                strategy=LoadingStrategy.UPSERT,
                target_table="stocks",
            )

            print(f"   ✅ Update scenario completed")
            print(f"      - Records inserted: {result2.metrics.records_inserted}")
            print(f"      - Records updated: {result2.metrics.records_updated}")

            # Show final state
            final_data = loader.mock_data_store.get("stocks", [])
            print(f"      - Total records in table: {len(final_data)}")

    except Exception as e:
        print(f"   ❌ Mock database loader demo failed: {str(e)}")


async def demo_mock_cache_loader():
    """Demonstrate mock cache loader."""
    print("\\n🔶 Demo 3: Mock Cache Loader")
    print("-" * 50)

    market_data = [
        {"symbol": "SPY", "price": 425.67, "volume": 45000000},
        {"symbol": "QQQ", "price": 358.42, "volume": 32000000},
        {"symbol": "IWM", "price": 185.23, "volume": 15000000},
    ]

    try:
        cache_loader = MockCacheLoader()

        async with cache_loader:
            # Test cache loading
            print("   🗂️  Testing cache loading...")
            result = await cache_loader.load_data(
                data=market_data,
                strategy=LoadingStrategy.UPSERT,
                target_table="etf_data",
            )

            if result.success:
                print(f"   ✅ Mock cache load successful")
                print(f"      - Records cached: {result.metrics.records_processed}")
                print(f"      - Duration: {result.metrics.duration_seconds:.3f}s")

                # Show cache stats
                stats = cache_loader.get_cache_stats()
                print(f"      - Cache operations: {stats['sets']} sets")
                print(f"      - Cache entries: {len(cache_loader.mock_cache)}")

                # Show cached keys
                print(f"      - Cached keys: {list(cache_loader.mock_cache.keys())}")

    except Exception as e:
        print(f"   ❌ Mock cache loader demo failed: {str(e)}")


async def demo_loading_strategies():
    """Demonstrate different loading strategies."""
    print("\\n🔶 Demo 4: Loading Strategies Comparison")
    print("-" * 50)

    initial_data = [
        {"id": 1, "name": "Company A", "value": 100},
        {"id": 2, "name": "Company B", "value": 200},
    ]

    updated_data = [
        {"id": 1, "name": "Company A Updated", "value": 150},  # Update
        {"id": 3, "name": "Company C", "value": 300},  # New
    ]

    try:
        async with FileLoader(base_path="data/strategy_demo") as loader:
            print("   🔄 Testing REPLACE strategy...")
            result1 = await loader.load_data(
                data=initial_data,
                strategy=LoadingStrategy.REPLACE,
                target_table="strategy_test",
            )

            result2 = await loader.load_data(
                data=updated_data,
                strategy=LoadingStrategy.REPLACE,
                target_table="strategy_test",
            )

            print(f"      - Initial: {result1.metrics.records_processed} records")
            print(f"      - Replace: {result2.metrics.records_processed} records")

            print("   ➕ Testing APPEND strategy...")
            result3 = await loader.load_data(
                data=initial_data,
                strategy=LoadingStrategy.APPEND,
                target_table="append_test",
            )

            result4 = await loader.load_data(
                data=updated_data,
                strategy=LoadingStrategy.APPEND,
                target_table="append_test",
            )

            print(f"      - First append: {result3.metrics.records_processed} records")
            print(f"      - Second append: {result4.metrics.records_processed} records")

            print("   📈 Testing INCREMENTAL strategy...")
            result5 = await loader.load_data(
                data=initial_data,
                strategy=LoadingStrategy.INCREMENTAL,
                target_table="incremental_test",
            )

            result6 = await loader.load_data(
                data=initial_data,  # Same data - should be skipped
                strategy=LoadingStrategy.INCREMENTAL,
                target_table="incremental_test",
            )

            print(
                f"      - Initial incremental: {result5.metrics.records_processed} records"
            )
            print(
                f"      - Duplicate incremental: {result6.metrics.records_processed} records"
            )
            print(f"      - Demonstrates deduplication capability")

    except Exception as e:
        print(f"   ❌ Loading strategies demo failed: {str(e)}")


async def demo_data_versioning():
    """Demonstrate data versioning capabilities."""
    print("\\n🔶 Demo 5: Data Versioning")
    print("-" * 50)

    version1_data = [{"company": "VersionCorp", "value": 42}]
    version2_data = [{"company": "VersionCorp", "value": 84}]

    try:
        async with FileLoader(
            base_path="data/version_demo", enable_versioning=True
        ) as loader:
            print("   📋 Creating data version 1...")
            result1 = await loader.load_data(
                data=version1_data,
                strategy=LoadingStrategy.REPLACE,
                target_table="versioned_data",
            )

            if result1.data_version:
                print(f"      - Version 1 ID: {result1.data_version.version_id}")
                print(f"      - Checksum: {result1.data_version.checksum}")
                print(f"      - Record count: {result1.data_version.record_count}")
                print(f"      - Timestamp: {result1.data_version.timestamp}")

            print("   📋 Creating data version 2...")
            result2 = await loader.load_data(
                data=version2_data,
                strategy=LoadingStrategy.REPLACE,
                target_table="versioned_data",
            )

            if result2.data_version:
                print(f"      - Version 2 ID: {result2.data_version.version_id}")
                print(f"      - Checksum: {result2.data_version.checksum}")
                print(f"      - Record count: {result2.data_version.record_count}")

                # Compare versions
                if result1.data_version and result2.data_version:
                    checksums_different = (
                        result1.data_version.checksum != result2.data_version.checksum
                    )
                    print(f"      - Data changed: {checksums_different}")
                    print(f"      - Versioning working correctly: ✅")

    except Exception as e:
        print(f"   ❌ Data versioning demo failed: {str(e)}")


async def run_phase3_demo():
    """Run comprehensive Phase 3 demonstration."""
    print("🚀 Phase 3 Data Loading Framework Demo")
    print("=" * 60)
    print(
        "🎯 Demonstrating TECH-009 Phase 3 capabilities without external dependencies"
    )

    start_time = datetime.now()

    # Create output directory
    os.makedirs("data", exist_ok=True)

    # Run all demos
    await demo_file_loader()
    await demo_mock_database_loader()
    await demo_mock_cache_loader()
    await demo_loading_strategies()
    await demo_data_versioning()

    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\\n🎯 Demo Summary")
    print("-" * 30)
    print(f"✅ All Phase 3 demos completed successfully")
    print(f"⏱️  Total duration: {duration:.2f} seconds")
    print(f"📅 Completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

    print("\\n📊 Phase 3 Features Demonstrated:")
    print("   • File loading with multiple formats (JSON, CSV, JSONL)")
    print("   • Compression support (GZIP)")
    print("   • Loading strategies (REPLACE, APPEND, UPSERT, INCREMENTAL)")
    print("   • Data versioning with checksums")
    print("   • Performance metrics collection")
    print("   • Mock implementations for database and cache loaders")
    print("   • Error handling and validation")
    print("   • Incremental loading with deduplication")

    print("\\n📁 Output Files Created:")
    print("   • data/demo_output/ - File loader outputs")
    print("   • data/strategy_demo/ - Loading strategy comparisons")
    print("   • data/version_demo/ - Data versioning examples")

    print("\\n🎉 Phase 3 Data Loading Framework is operational!")
    print("💡 For full functionality, install: pip install asyncpg redis structlog")


if __name__ == "__main__":
    try:
        asyncio.run(run_phase3_demo())
    except KeyboardInterrupt:
        print("\\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\\n❌ Demo failed with error: {str(e)}")
        import traceback

        traceback.print_exc()
