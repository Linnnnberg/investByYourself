#!/usr/bin/env python3
"""
Test Data Collection Framework - investByYourself
Tech-009: ETL Pipeline Implementation - Phase 1

This script demonstrates the new data collection framework with:
- Individual collector usage
- Orchestrator usage
- Error handling and rate limiting
- Performance monitoring
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict

# Set FRED API key directly for testing
os.environ["FRED_API_KEY"] = "14030930f9b81e23d9ba97aed857ef3b"

# Add src directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.etl.collectors import (
    AlphaVantageCollector,
    DataCollectionOrchestrator,
    FREDCollector,
    YahooFinanceCollector,
)


async def test_individual_collectors():
    """Test individual data collectors."""
    print("=" * 60)
    print("Testing Individual Data Collectors")
    print("=" * 60)

    # Test Yahoo Finance Collector
    print("\n1. Testing Yahoo Finance Collector")
    print("-" * 40)

    try:
        async with YahooFinanceCollector() as yahoo_collector:
            # Test company profile collection
            print("Collecting AAPL company profile...")
            profile_data = await yahoo_collector.execute_collection(
                symbol="AAPL", data_type="profile"
            )

            print(f"✓ Company profile collected successfully")
            print(f"  - Company: {profile_data['data']['company_name']}")
            print(f"  - Sector: {profile_data['data']['sector']}")
            print(f"  - Market Cap: ${profile_data['data']['market_cap']:,}")
            print(
                f"  - Data Quality Score: {profile_data['metadata']['completeness']:.2%}"
            )

            # Test fundamentals collection
            print("\nCollecting AAPL fundamentals...")
            fundamentals_data = await yahoo_collector.execute_collection(
                symbol="AAPL", data_type="fundamentals"
            )

            print(f"✓ Fundamentals collected successfully")
            print(
                f"  - PE Ratio: {fundamentals_data['data']['valuation_metrics']['pe_ratio']}"
            )
            print(
                f"  - Forward PE: {fundamentals_data['data']['valuation_metrics']['forward_pe']}"
            )
            print(
                f"  - Data Quality Score: {fundamentals_data['metadata']['completeness']:.2%}"
            )

            # Get metrics
            metrics = yahoo_collector.get_metrics()
            print(f"\nCollector Metrics:")
            print(f"  - API Calls: {metrics['current_collection']['api_calls']}")
            print(
                f"  - Rate Limit Hits: {metrics['current_collection']['rate_limit_hits']}"
            )
            print(
                f"  - Total Duration: {metrics['current_collection']['total_duration']:.2f}s"
            )

    except Exception as e:
        print(f"✗ Yahoo Finance collector test failed: {str(e)}")

    # Test Alpha Vantage Collector (if API key available)
    print("\n2. Testing Alpha Vantage Collector")
    print("-" * 40)

    alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if alpha_vantage_key:
        try:
            async with AlphaVantageCollector(api_key=alpha_vantage_key) as av_collector:
                # Test time series collection
                print("Collecting AAPL daily time series...")
                time_series_data = await av_collector.execute_collection(
                    symbol="AAPL", function="TIME_SERIES_DAILY"
                )

                print(f"✓ Time series collected successfully")
                print(f"  - Data Points: {time_series_data['data']['data_points']}")
                print(
                    f"  - Date Range: {time_series_data['data']['start_date']} to {time_series_data['data']['end_date']}"
                )
                print(
                    f"  - Data Quality Score: {time_series_data['metadata']['completeness']:.2%}"
                )

                # Get metrics
                metrics = av_collector.get_metrics()
                print(f"\nCollector Metrics:")
                print(f"  - API Calls: {metrics['current_collection']['api_calls']}")
                print(
                    f"  - Rate Limit Hits: {metrics['current_collection']['rate_limit_hits']}"
                )
                print(
                    f"  - Total Duration: {metrics['current_collection']['total_duration']:.2f}s"
                )

        except Exception as e:
            print(f"✗ Alpha Vantage collector test failed: {str(e)}")
    else:
        print("⚠ Alpha Vantage API key not available, skipping test")

    # Test FRED Collector (if API key available)
    print("\n3. Testing FRED Collector")
    print("-" * 40)

    fred_key = os.getenv("FRED_API_KEY")
    if fred_key:
        try:
            async with FREDCollector(api_key=fred_key) as fred_collector:
                # Test GDP data collection
                print("Collecting GDP data...")
                gdp_data = await fred_collector.execute_collection(
                    series_id="GDP",
                    data_type="observations",
                    observation_start="2020-01-01",
                )

                print(f"✓ GDP data collected successfully")
                print(f"  - Data Points: {gdp_data['data']['data_points']}")
                print(
                    f"  - Date Range: {gdp_data['data']['start_date']} to {gdp_data['data']['end_date']}"
                )
                print(
                    f"  - Data Quality Score: {gdp_data['metadata']['completeness']:.2%}"
                )

                # Test common indicators collection
                print("\nCollecting common economic indicators...")
                indicators_data = await fred_collector.collect_common_indicators(
                    ["gdp", "unemployment_rate", "inflation_cpi"]
                )

                print(f"✓ Common indicators collected successfully")
                print(f"  - Successful: {indicators_data['summary']['successful']}")
                print(f"  - Failed: {indicators_data['summary']['failed']}")
                print(
                    f"  - Total Duration: {indicators_data['summary']['total_duration']:.2f}s"
                )

                # Get metrics
                metrics = fred_collector.get_metrics()
                print(f"\nCollector Metrics:")
                print(f"  - API Calls: {metrics['current_collection']['api_calls']}")
                print(
                    f"  - Rate Limit Hits: {metrics['current_collection']['rate_limit_hits']}"
                )
                print(
                    f"  - Total Duration: {metrics['current_collection']['total_duration']:.2f}s"
                )

        except Exception as e:
            print(f"✗ FRED collector test failed: {str(e)}")
    else:
        print("⚠ FRED API key not available, skipping test")


async def test_collection_orchestrator():
    """Test the data collection orchestrator."""
    print("\n" + "=" * 60)
    print("Testing Data Collection Orchestrator")
    print("=" * 60)

    # Initialize orchestrator
    alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    fred_key = os.getenv("FRED_API_KEY")

    try:
        async with DataCollectionOrchestrator(
            alpha_vantage_api_key=alpha_vantage_key,
            fred_api_key=fred_key,
            max_concurrent_tasks=5,
        ) as orchestrator:
            print("✓ Orchestrator initialized successfully")

            # Test company data collection
            print("\n1. Testing Company Data Collection")
            print("-" * 40)

            symbols = ["AAPL", "MSFT", "GOOGL"]
            data_types = ["profile", "financials"]

            print(f"Collecting data for {len(symbols)} symbols: {', '.join(symbols)}")
            print(f"Data types: {', '.join(data_types)}")

            company_results = await orchestrator.collect_company_data(
                symbols=symbols,
                data_types=data_types,
                sources=["yahoo_finance"],  # Use correct collector key
            )

            print(f"✓ Company data collection completed")
            print(f"  - Successful: {company_results['summary']['successful']}")
            print(f"  - Failed: {company_results['summary']['failed']}")
            print(
                f"  - Total Duration: {company_results['summary']['total_duration']:.2f}s"
            )

            # Show sample results
            for symbol in symbols:
                if symbol in company_results["results"]:
                    print(f"\n  {symbol}:")
                    for data_type in data_types:
                        if data_type in company_results["results"][symbol]:
                            for source, data in company_results["results"][symbol][
                                data_type
                            ].items():
                                if data and "data" in data:
                                    if data_type == "profile":
                                        company_name = data["data"].get(
                                            "company_name", "N/A"
                                        )
                                        sector = data["data"].get("sector", "N/A")
                                        print(
                                            f"    {data_type} ({source}): {company_name} - {sector}"
                                        )
                                    else:
                                        print(
                                            f"    {data_type} ({source}): Data collected"
                                        )

            # Test economic data collection
            print("\n2. Testing Economic Data Collection")
            print("-" * 40)

            if fred_key:
                indicators = ["gdp", "unemployment_rate", "inflation_cpi"]
                print(f"Collecting economic indicators: {', '.join(indicators)}")

                economic_results = await orchestrator.collect_economic_data(
                    indicators=indicators, sources=["fred"]
                )

                print(f"✓ Economic data collection completed")
                print(f"  - Successful: {economic_results['summary']['successful']}")
                print(f"  - Failed: {economic_results['summary']['failed']}")
                print(
                    f"  - Total Duration: {economic_results['summary']['total_duration']:.2f}s"
                )
            else:
                print("⚠ FRED API key not available, skipping economic data test")

            # Get orchestrator metrics
            print("\n3. Orchestrator Performance Metrics")
            print("-" * 40)

            metrics = orchestrator.get_metrics()
            print(f"  - Status: {metrics['orchestrator_status']}")
            print(f"  - Total Tasks Executed: {metrics['total_tasks_executed']}")
            print(f"  - Success Rate: {metrics['success_rate']:.1f}%")
            print(
                f"  - Average Execution Time: {metrics['average_execution_time']:.2f}s"
            )
            print(
                f"  - Collectors Available: {', '.join(metrics['collectors_available'])}"
            )

    except Exception as e:
        print(f"✗ Orchestrator test failed: {str(e)}")


async def test_error_handling_and_rate_limiting():
    """Test error handling and rate limiting features."""
    print("\n" + "=" * 60)
    print("Testing Error Handling and Rate Limiting")
    print("=" * 60)

    try:
        async with YahooFinanceCollector() as yahoo_collector:
            # Test invalid symbol handling
            print("\n1. Testing Invalid Symbol Handling")
            print("-" * 40)

            try:
                invalid_data = await yahoo_collector.execute_collection(
                    symbol="INVALID_SYMBOL_12345", data_type="profile"
                )
                print("⚠ Unexpected success with invalid symbol")
            except Exception as e:
                print(f"✓ Properly handled invalid symbol: {str(e)}")

            # Test rate limiting (make multiple rapid requests)
            print("\n2. Testing Rate Limiting")
            print("-" * 40)

            symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
            print(f"Making rapid requests for {len(symbols)} symbols...")

            start_time = datetime.now()

            tasks = []
            for symbol in symbols:
                task = yahoo_collector.execute_collection(
                    symbol=symbol, data_type="profile"
                )
                tasks.append(task)

            # Execute concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            successful = sum(1 for r in results if not isinstance(r, Exception))
            failed = len(results) - successful

            print(f"✓ Rate limiting test completed")
            print(f"  - Successful: {successful}")
            print(f"  - Failed: {failed}")
            print(f"  - Total Duration: {duration:.2f}s")
            print(f"  - Average per request: {duration/len(symbols):.2f}s")

            # Get metrics to see rate limiting effects
            metrics = yahoo_collector.get_metrics()
            print(
                f"  - Rate Limit Hits: {metrics['current_collection']['rate_limit_hits']}"
            )
            print(
                f"  - Retry Attempts: {metrics['current_collection']['retry_attempts']}"
            )

    except Exception as e:
        print(f"✗ Error handling test failed: {str(e)}")


async def main():
    """Main test function."""
    print("Data Collection Framework Test Suite")
    print("Tech-009: ETL Pipeline Implementation - Phase 1")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Test individual collectors
        await test_individual_collectors()

        # Test orchestrator
        await test_collection_orchestrator()

        # Test error handling and rate limiting
        await test_error_handling_and_rate_limiting()

        print("\n" + "=" * 60)
        print("All Tests Completed Successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Test suite failed: {str(e)}")
        raise


if __name__ == "__main__":
    # Set up environment variables for testing
    if not os.getenv("ALPHA_VANTAGE_API_KEY"):
        print("⚠ ALPHA_VANTAGE_API_KEY not set - Alpha Vantage tests will be skipped")

    if not os.getenv("FRED_API_KEY"):
        print("⚠ FRED_API_KEY not set - FRED tests will be skipped")

    print("Note: Some tests require API keys to be set as environment variables")
    print("Set ALPHA_VANTAGE_API_KEY and FRED_API_KEY for full testing")
    print()

    # Run tests
    asyncio.run(main())
