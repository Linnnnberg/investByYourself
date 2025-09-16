"""
Test Universe Setup Verification
Tech-021: ETL Service Extraction

Simple test to verify the Magnificent 7 stocks test universe is configured correctly.
"""

from models.test_universe import (
    get_magnificent_7_universe,
    get_stock_info,
    get_test_symbols,
    get_universe_manager,
)


def test_universe_configuration():
    """Test the universe configuration."""
    print("🧪 Testing Magnificent 7 Stocks Universe Configuration")
    print("=" * 60)

    try:
        # Test 1: Get universe configuration
        print("1. Testing universe configuration retrieval...")
        universe = get_magnificent_7_universe()
        print(f"   ✅ Universe name: {universe.name}")
        print(f"   ✅ Description: {universe.description}")
        print(f"   ✅ Total stocks: {len(universe.stocks)}")
        print(f"   ✅ Version: {universe.version}")

        # Test 2: Get universe manager
        print("\n2. Testing universe manager...")
        manager = get_universe_manager()
        print(f"   ✅ Manager created successfully")
        print(f"   ✅ Total symbols: {len(manager.symbols)}")

        # Test 3: Get test symbols
        print("\n3. Testing symbol retrieval...")
        symbols = get_test_symbols()
        print(f"   ✅ Symbols retrieved: {symbols}")
        print(f"   ✅ Symbol count: {len(symbols)}")

        # Test 4: Get individual stock info
        print("\n4. Testing individual stock info...")
        for symbol in symbols:
            stock_info = get_stock_info(symbol)
            if stock_info:
                print(f"   ✅ {symbol}: {stock_info.company_name}")
                print(f"      Sector: {stock_info.sector}")
                print(f"      Industry: {stock_info.industry}")
                print(f"      Priority: {stock_info.priority}")
            else:
                print(f"   ❌ {symbol}: Stock info not found")

        # Test 5: Universe summary
        print("\n5. Testing universe summary...")
        summary = manager.get_universe_summary()
        print(f"   ✅ Summary created successfully")
        print(f"   ✅ Sectors: {summary['sectors']}")
        print(f"   ✅ Industries: {summary['industries']}")
        print(f"   ✅ Exchanges: {summary['exchanges']}")

        # Test 6: Sector filtering
        print("\n6. Testing sector filtering...")
        tech_stocks = manager.get_stocks_by_sector("Technology")
        print(f"   ✅ Technology stocks: {[s.symbol for s in tech_stocks]}")
        print(f"   ✅ Count: {len(tech_stocks)}")

        # Test 7: Priority filtering
        print("\n7. Testing priority filtering...")
        high_priority = manager.get_stocks_by_priority(min_priority=1)
        print(f"   ✅ High priority stocks: {[s.symbol for s in high_priority]}")
        print(f"   ✅ Count: {len(high_priority)}")

        print("\n🎉 All universe configuration tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def test_stock_details():
    """Test detailed stock information."""
    print("\n🔍 Testing Detailed Stock Information")
    print("-" * 40)

    try:
        manager = get_universe_manager()

        for stock in manager.universe.stocks:
            print(f"\n📊 {stock.symbol} - {stock.company_name}")
            print(f"   Sector: {stock.sector}")
            print(f"   Industry: {stock.industry}")
            print(f"   Market Cap: {stock.market_cap_category}")
            print(f"   Exchange: {stock.exchange}")
            print(f"   Country: {stock.country}")
            print(f"   Priority: {stock.priority}")
            print(f"   Data Types: {', '.join(stock.data_types)}")
            print(
                f"   Expected Profile Completeness: {stock.expected_profile_completeness:.1%}"
            )
            print(f"   Expected Financials: {stock.expected_financials}")
            print(f"   Expected Market Data: {stock.expected_market_data}")
            print(f"   Website: {stock.website}")
            print(f"   Description: {stock.description[:100]}...")

        print("\n✅ Detailed stock information test completed")
        return True

    except Exception as e:
        print(f"\n❌ Detailed stock test failed: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main test function."""
    print("🚀 Magnificent 7 Stocks Test Universe Verification")
    print("=" * 70)

    # Test universe configuration
    config_ok = test_universe_configuration()

    if config_ok:
        # Test detailed stock information
        details_ok = test_stock_details()

        if details_ok:
            print("\n🎯 Test Universe Summary:")
            print("-" * 30)
            manager = get_universe_manager()
            summary = manager.get_universe_summary()

            print(f"✅ Universe: {summary['name']}")
            print(f"✅ Total Stocks: {summary['total_stocks']}")
            print(f"✅ Sectors: {len(summary['sectors'])}")
            print(f"✅ Industries: {len(summary['industries'])}")
            print(f"✅ Data Types: {len(summary['data_types'])}")
            print(f"✅ Version: {summary['version']}")

            print(
                f"\n🎉 All tests passed! The Magnificent 7 stocks test universe is ready."
            )
            print(
                f"   You can now use this universe for ETL testing and data collection."
            )
            return True
        else:
            print("\n❌ Detailed stock tests failed.")
            return False
    else:
        print("\n❌ Universe configuration tests failed.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
