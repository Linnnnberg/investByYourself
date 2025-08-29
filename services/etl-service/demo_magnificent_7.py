"""
Magnificent 7 Stocks ETL Service Demo
Tech-021: ETL Service Extraction

Comprehensive demonstration of the ETL service functionality using the Magnificent 7 stocks as a test universe.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Any, Dict

from collectors.demo_collector import DemoDataCollector
from models.test_universe import get_test_symbols, get_universe_manager
from worker.etl_worker import ETLWorker


class Magnificent7Demo:
    """Comprehensive demo of ETL service functionality with Magnificent 7 stocks."""

    def __init__(self):
        """Initialize the demo."""
        self.universe_manager = get_universe_manager()
        self.collector = DemoDataCollector()
        self.etl_worker = None

    async def run_full_demo(self):
        """Run the complete demo showcasing all ETL functionality."""
        print("🚀 Magnificent 7 Stocks ETL Service Demo")
        print("=" * 70)
        print()

        # Phase 1: Universe Overview
        await self.show_universe_overview()

        # Phase 2: Data Collection Demo
        await self.demo_data_collection()

        # Phase 3: ETL Worker Demo
        await self.demo_etl_worker()

        # Phase 4: Data Quality Analysis
        await self.demo_data_quality_analysis()

        # Phase 5: Performance Metrics
        await self.demo_performance_metrics()

        print("\n🎉 Demo completed successfully!")
        print(
            "The ETL service is ready for production use with the Magnificent 7 stocks test universe."
        )

    async def show_universe_overview(self):
        """Show an overview of the test universe."""
        print("📊 Phase 1: Test Universe Overview")
        print("-" * 40)

        universe_summary = self.universe_manager.get_universe_summary()

        print(f"Universe Name: {universe_summary['name']}")
        print(f"Description: {universe_summary['description']}")
        print(f"Total Stocks: {universe_summary['total_stocks']}")
        print(f"Version: {universe_summary['version']}")
        print(f"Created: {universe_summary['created_at']}")
        print()

        print("📈 Stock Composition:")
        print(f"  Sectors: {', '.join(universe_summary['sectors'])}")
        print(f"  Industries: {', '.join(universe_summary['industries'])}")
        print(f"  Exchanges: {', '.join(universe_summary['exchanges'])}")
        print(f"  Countries: {', '.join(universe_summary['countries'])}")
        print(
            f"  Market Cap Categories: {', '.join(universe_summary['market_cap_categories'])}"
        )
        print()

        print("🔍 Individual Stock Details:")
        for stock in self.universe_manager.universe.stocks:
            print(f"  {stock.symbol}: {stock.company_name}")
            print(f"    Sector: {stock.sector} | Industry: {stock.industry}")
            print(
                f"    Priority: {stock.priority} | Data Types: {', '.join(stock.data_types)}"
            )
            print(
                f"    Expected Profile Completeness: {stock.expected_profile_completeness:.1%}"
            )
            print()

        print("✅ Universe overview completed")
        print()

    async def demo_data_collection(self):
        """Demonstrate data collection functionality."""
        print("📡 Phase 2: Data Collection Demo")
        print("-" * 40)

        print("Starting comprehensive data collection for Magnificent 7 stocks...")
        start_time = time.time()

        # Collect comprehensive data
        data = await self.collector.collect_comprehensive_data()

        end_time = time.time()
        collection_time = end_time - start_time

        # Show collection summary
        summary = data["collection_summary"]
        print(f"\n📊 Collection Summary:")
        print(f"  Total Symbols: {summary['total_symbols']}")
        print(
            f"  Successful Profiles: {summary['successful_profiles']}/{summary['total_symbols']}"
        )
        print(
            f"  Successful Financials: {summary['successful_financials']}/{summary['total_symbols']}"
        )
        print(
            f"  Successful Market Data: {summary['successful_market_data']}/{summary['total_symbols']}"
        )
        print(f"  Collection Time: {summary['collection_time_seconds']} seconds")
        print(
            f"  Average Time per Symbol: {summary['average_time_per_symbol']} seconds"
        )

        # Show sample data for first stock
        first_symbol = list(data["data"].keys())[0]
        first_stock_data = data["data"][first_symbol]

        print(f"\n📋 Sample Data for {first_symbol}:")
        if "profile" in first_stock_data and "error" not in first_stock_data["profile"]:
            profile = first_stock_data["profile"]
            print(f"  Company: {profile.get('company_name', 'N/A')}")
            print(f"  Sector: {profile.get('sector', 'N/A')}")
            print(
                f"  Market Cap: {profile.get('market_cap', 'N/A'):,}"
                if profile.get("market_cap")
                else "  Market Cap: N/A"
            )
            print(f"  Website: {profile.get('website', 'N/A')}")

        if (
            "financials" in first_stock_data
            and "error" not in first_stock_data["financials"]
        ):
            financials = first_stock_data["financials"]
            if "key_metrics" in financials:
                metrics = financials["key_metrics"]
                print(f"  P/E Ratio: {metrics.get('pe_ratio', 'N/A')}")
                print(f"  Price to Book: {metrics.get('price_to_book', 'N/A')}")
                print(f"  Return on Equity: {metrics.get('return_on_equity', 'N/A')}")

        if (
            "market_data" in first_stock_data
            and "error" not in first_stock_data["market_data"]
        ):
            market = first_stock_data["market_data"]
            print(f"  Current Price: ${market.get('current_price', 'N/A')}")
            print(
                f"  Volume: {market.get('volume', 'N/A'):,}"
                if market.get("volume")
                else "  Volume: N/A"
            )
            print(
                f"  52-Week Range: ${market.get('52_week_low', 'N/A')} - ${market.get('52_week_high', 'N/A')}"
            )

        print(f"\n✅ Data collection demo completed in {collection_time:.2f} seconds")
        print()

        # Store data for later use
        self.collected_data = data

    async def demo_etl_worker(self):
        """Demonstrate ETL worker functionality."""
        print("⚙️ Phase 3: ETL Worker Demo")
        print("-" * 40)

        print("Initializing ETL Worker...")

        # Initialize ETL worker
        self.etl_worker = ETLWorker()
        await self.etl_worker.initialize()

        print("✅ ETL Worker initialized successfully")

        # Test job creation
        print("\n🔄 Testing ETL Job Creation:")

        # Start a data collection job
        job_id = await self.etl_worker.start_data_collection(
            source="yahoo_finance",
            symbols=get_test_symbols(),
            data_types=["profile", "financials", "market_data"],
        )
        print(f"  Created collection job: {job_id}")

        # Start a transformation job
        transform_job_id = await self.etl_worker.start_data_transformation(
            source_data="collected",
            transformation_rules=["standardize", "validate", "enrich"],
            output_format="standardized",
        )
        print(f"  Created transformation job: {transform_job_id}")

        # Start a loading job
        load_job_id = await self.etl_worker.start_data_loading(
            target="database",
            data_source="transformed",
            compression=True,
            backup_existing=True,
        )
        print(f"  Created loading job: {load_job_id}")

        # Start a full pipeline job
        pipeline_job_id = await self.etl_worker.start_full_pipeline(
            collection_params={
                "source": "yahoo_finance",
                "symbols": get_test_symbols(),
            },
            transformation_params={"rules": ["standardize", "validate"]},
            loading_params={"target": "database"},
        )
        print(f"  Created full pipeline job: {pipeline_job_id}")

        # Wait for jobs to complete
        print("\n⏳ Waiting for jobs to complete...")
        await asyncio.sleep(8)  # Wait for all jobs to complete

        # Check job statuses
        print("\n📋 Job Status Check:")
        for job_id in [job_id, transform_job_id, load_job_id, pipeline_job_id]:
            status = await self.etl_worker.get_job_status(job_id)
            if status:
                print(f"  {job_id}: {status['status']} ({status['progress']:.1f}%)")
            else:
                print(f"  {job_id}: Status not found")

        # Get service status
        service_status = self.etl_worker.get_service_status()
        print(f"\n📊 Service Status:")
        print(f"  Active Jobs: {service_status['active_jobs']}")
        print(f"  Completed Today: {service_status['completed_jobs_today']}")
        print(f"  Failed Today: {service_status['failed_jobs_today']}")

        print(f"\n✅ ETL Worker demo completed")
        print()

    async def demo_data_quality_analysis(self):
        """Demonstrate data quality analysis."""
        print("🔍 Phase 4: Data Quality Analysis")
        print("-" * 40)

        if not hasattr(self, "collected_data"):
            print("❌ No collected data available for quality analysis")
            return

        print("Analyzing data quality for collected data...")

        # Validate collected data
        validation_results = self.collector.validate_collected_data(self.collected_data)

        print(f"\n📊 Data Quality Results:")
        print(f"  Total Stocks Analyzed: {len(validation_results)}")

        # Calculate overall quality metrics
        total_quality_score = 0
        profile_completeness_met = 0
        financials_met = 0
        market_data_met = 0

        for symbol, results in validation_results.items():
            total_quality_score += results["overall_quality_score"]
            if results["profile_completeness_met"]:
                profile_completeness_met += 1
            if results["financials_met"]:
                financials_met += 1
            if results["market_data_met"]:
                market_data_met += 1

        avg_quality_score = (
            total_quality_score / len(validation_results) if validation_results else 0
        )

        print(f"  Average Quality Score: {avg_quality_score:.1%}")
        print(
            f"  Profile Completeness Met: {profile_completeness_met}/{len(validation_results)}"
        )
        print(f"  Financials Met: {financials_met}/{len(validation_results)}")
        print(f"  Market Data Met: {market_data_met}/{len(validation_results)}")

        print(f"\n📋 Individual Stock Quality Scores:")
        for symbol, results in validation_results.items():
            print(f"  {symbol}:")
            print(
                f"    Profile: {'✅' if results['profile_completeness_met'] else '❌'} ({results['actual_profile_completeness']:.1%})"
            )
            print(f"    Financials: {'✅' if results['financials_met'] else '❌'}")
            print(f"    Market Data: {'✅' if results['market_data_met'] else '❌'}")
            print(f"    Overall Quality: {results['overall_quality_score']:.1%}")

        print(f"\n✅ Data quality analysis completed")
        print()

    async def demo_performance_metrics(self):
        """Demonstrate performance metrics and benchmarking."""
        print("⚡ Phase 5: Performance Metrics & Benchmarking")
        print("-" * 40)

        print("Running performance benchmarks...")

        # Benchmark data collection performance
        print("\n📊 Data Collection Performance:")

        if hasattr(self, "collected_data"):
            summary = self.collected_data["collection_summary"]
            print(
                f"  Total Collection Time: {summary['collection_time_seconds']} seconds"
            )
            print(
                f"  Average Time per Symbol: {summary['average_time_per_symbol']} seconds"
            )
            print(
                f"  Symbols per Second: {summary['total_symbols'] / summary['collection_time_seconds']:.2f}"
            )
            print(
                f"  Data Points Collected: {summary['successful_profiles'] + summary['successful_financials'] + summary['successful_market_data']}"
            )
            print(
                f"  Data Points per Second: {(summary['successful_profiles'] + summary['successful_financials'] + summary['successful_market_data']) / summary['collection_time_seconds']:.2f}"
            )

        # Benchmark ETL worker performance
        print("\n⚙️ ETL Worker Performance:")
        if self.etl_worker:
            service_status = self.etl_worker.get_service_status()
            print(f"  Jobs Processed Today: {service_status['completed_jobs_today']}")
            print(f"  Failed Jobs Today: {service_status['failed_jobs_today']}")
            print(
                f"  Success Rate: {service_status['completed_jobs_today'] / (service_status['completed_jobs_today'] + service_status['failed_jobs_today']) * 100:.1f}%"
                if (
                    service_status["completed_jobs_today"]
                    + service_status["failed_jobs_today"]
                )
                > 0
                else "  Success Rate: N/A"
            )

        # System performance metrics
        print("\n💻 System Performance:")
        import psutil

        memory = psutil.virtual_memory()
        print(f"  Memory Usage: {memory.percent:.1f}%")
        print(f"  Available Memory: {memory.available / (1024**3):.1f} GB")

        # Data quality performance
        print("\n🎯 Data Quality Performance:")
        if hasattr(self, "collected_data"):
            validation_results = self.collector.validate_collected_data(
                self.collected_data
            )
            total_quality_score = sum(
                r["overall_quality_score"] for r in validation_results.values()
            )
            avg_quality_score = (
                total_quality_score / len(validation_results)
                if validation_results
                else 0
            )

            print(f"  Average Data Quality: {avg_quality_score:.1%}")
            print(
                f"  Quality Threshold Met: {'✅' if avg_quality_score >= 0.8 else '❌'}"
            )
            print(
                f"  Data Completeness: {len([r for r in validation_results.values() if r['profile_completeness_met']]) / len(validation_results):.1%}"
            )

        print(f"\n✅ Performance metrics demo completed")
        print()

    async def cleanup(self):
        """Clean up resources."""
        if self.etl_worker:
            await self.etl_worker.shutdown()


async def main():
    """Main demo function."""
    demo = Magnificent7Demo()

    try:
        await demo.run_full_demo()
    finally:
        await demo.cleanup()


if __name__ == "__main__":
    print("🚀 Starting Magnificent 7 Stocks ETL Service Demo...")
    print("This demo will showcase all ETL functionality with real data collection.")
    print()

    # Run the demo
    asyncio.run(main())
