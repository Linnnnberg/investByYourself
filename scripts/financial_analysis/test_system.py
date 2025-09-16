#!/usr/bin/env python3
"""
Test Script for Financial Data Exploration System
Tech-008: Database Infrastructure Setup

This script tests the core functionality of the financial data exploration system
to ensure everything is working correctly.
"""

import logging
import os
import sys

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from scripts.financial_analysis.data_explorer import (
    CompanyProfile,
    FinancialCharts,
    FinancialDataExplorer,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_database_connection():
    """Test database connection."""
    print("🔌 Testing database connection...")
    try:
        explorer = FinancialDataExplorer()
        print("✅ Database connection successful!")
        return explorer
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None


def test_basic_queries(explorer):
    """Test basic database queries."""
    print("\n📊 Testing basic queries...")

    try:
        # Test top companies query
        print("  - Testing top companies query...")
        top_companies = explorer.get_top_companies_by_market_cap(limit=5)
        if not top_companies.empty:
            print(f"    ✅ Found {len(top_companies)} companies")
            print(
                f"    📋 Top company: {top_companies.iloc[0]['symbol']} - {top_companies.iloc[0]['name']}"
            )
        else:
            print("    ⚠️  No companies found - database may be empty")

        # Test sector performance query
        print("  - Testing sector performance query...")
        sector_perf = explorer.get_sector_performance()
        if not sector_perf.empty:
            print(f"    ✅ Found {len(sector_perf)} sectors")
            print(f"    📋 Sectors: {', '.join(sector_perf['sector'].tolist())}")
        else:
            print("    ⚠️  No sector data found")

        return True

    except Exception as e:
        print(f"    ❌ Query test failed: {e}")
        return False


def test_chart_generation(explorer):
    """Test chart generation."""
    print("\n📈 Testing chart generation...")

    try:
        charts = FinancialCharts()

        # Get sample data for charts
        top_companies = explorer.get_top_companies_by_market_cap(limit=5)
        if not top_companies.empty:
            # Test market cap chart
            print("  - Testing market cap chart...")
            fig = charts.create_market_cap_chart(top_companies)
            print("    ✅ Market cap chart created successfully")

            # Test sector performance chart
            sector_perf = explorer.get_sector_performance()
            if not sector_perf.empty:
                print("  - Testing sector performance chart...")
                fig = charts.create_sector_performance_chart(sector_perf)
                print("    ✅ Sector performance chart created successfully")

            return True
        else:
            print("    ⚠️  No data available for chart testing")
            return False

    except Exception as e:
        print(f"    ❌ Chart generation failed: {e}")
        return False


def test_company_profiles(explorer):
    """Test company profile generation."""
    print("\n🏢 Testing company profile generation...")

    try:
        profile_generator = CompanyProfile(explorer)

        # Test with a known company (should exist if sample data was populated)
        test_symbols = ["AAPL", "MSFT", "GOOGL"]

        for symbol in test_symbols:
            print(f"  - Testing profile for {symbol}...")
            profile = profile_generator.generate_company_profile(symbol)

            if "error" not in profile:
                print(f"    ✅ Profile generated for {symbol}")
                print(f"      Name: {profile['overview']['name']}")
                print(f"      Sector: {profile['overview']['sector']}")
                if profile["overview"]["market_cap"]:
                    print(
                        f"      Market Cap: ${profile['overview']['market_cap']:,.0f}"
                    )
            else:
                print(f"    ⚠️  Profile not found for {symbol}: {profile['error']}")

        return True

    except Exception as e:
        print(f"    ❌ Company profile test failed: {e}")
        return False


def test_custom_queries(explorer):
    """Test custom SQL queries."""
    print("\n🔍 Testing custom SQL queries...")

    try:
        # Test a simple custom query
        print("  - Testing custom SQL query...")
        query = "SELECT COUNT(*) as company_count FROM companies WHERE is_active = TRUE"
        result = explorer.execute_query(query)

        if not result.empty:
            count = result.iloc[0]["company_count"]
            print(f"    ✅ Custom query successful - Found {count} active companies")
            return True
        else:
            print("    ⚠️  Custom query returned no results")
            return False

    except Exception as e:
        print(f"    ❌ Custom query test failed: {e}")
        return False


def run_system_test():
    """Run the complete system test."""
    print("🚀 Starting Financial Data Exploration System Test")
    print("=" * 60)

    # Test database connection
    explorer = test_database_connection()
    if not explorer:
        print("\n❌ System test failed - Cannot connect to database")
        return False

    # Test basic functionality
    tests = [
        ("Basic Queries", lambda: test_basic_queries(explorer)),
        ("Chart Generation", lambda: test_chart_generation(explorer)),
        ("Company Profiles", lambda: test_company_profiles(explorer)),
        ("Custom Queries", lambda: test_custom_queries(explorer)),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"    ❌ {test_name} test crashed: {e}")

    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! System is working correctly.")
        print("\n✅ You can now:")
        print("   - Run the data explorer: python data_explorer.py")
        print("   - Launch the dashboard: streamlit run financial_dashboard.py")
        print("   - Use the system for financial analysis")
        return True
    else:
        print(f"⚠️  {total - passed} tests failed. Check the errors above.")
        print("\n💡 Common solutions:")
        print("   - Ensure database is running and accessible")
        print("   - Run populate_sample_data.py to create sample data")
        print("   - Check environment variables and database configuration")
        return False


def main():
    """Main function."""
    try:
        success = run_system_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
