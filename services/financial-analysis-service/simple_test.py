#!/usr/bin/env python3
"""
Simple Test Script for Financial Analysis Service
================================================

Test the service structure without starting the full server.
"""


def test_imports():
    """Test if all modules can be imported."""
    try:
        print("🔍 Testing imports...")

        # Test core imports
        from app.core.config import get_settings

        print("✅ Core config imported successfully")

        from app.core.database import test_database_connection

        print("✅ Database module imported successfully")

        from app.core.security import authenticate_user

        print("✅ Security module imported successfully")

        # Test API imports
        from app.api.strategies import router as strategies_router

        print("✅ Strategies API imported successfully")

        from app.api.backtesting import router as backtesting_router

        print("✅ Backtesting API imported successfully")

        from app.api.results import router as results_router

        print("✅ Results API imported successfully")

        # Test models
        from app.models.strategy import Strategy

        print("✅ Strategy model imported successfully")

        print("\n🎉 All imports successful! Service structure is working.")
        return True

    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def test_config():
    """Test configuration loading."""
    try:
        print("\n🔍 Testing configuration...")
        from app.core.config import get_settings

        settings = get_settings()
        print(f"✅ Service name: {settings.service_name}")
        print(f"✅ Service version: {settings.service_version}")
        print(f"✅ Debug mode: {settings.debug}")
        print(f"✅ Database URL: {settings.database_url}")

        return True

    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_api_structure():
    """Test API structure."""
    try:
        print("\n🔍 Testing API structure...")

        from app.api.backtesting import router as backtesting_router
        from app.api.results import router as results_router
        from app.api.strategies import router as strategies_router

        # Check if routers have endpoints
        strategy_routes = [route.path for route in strategies_router.routes]
        backtest_routes = [route.path for route in backtesting_router.routes]
        results_routes = [route.path for route in results_router.routes]

        print(f"✅ Strategies API: {len(strategy_routes)} endpoints")
        print(f"✅ Backtesting API: {len(backtest_routes)} endpoints")
        print(f"✅ Results API: {len(results_routes)} endpoints")

        return True

    except Exception as e:
        print(f"❌ API structure test failed: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Financial Analysis Service - Structure Test")
    print("=" * 50)

    # Run tests
    import_success = test_imports()
    config_success = test_config()
    api_success = test_api_structure()

    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Imports: {'✅ PASS' if import_success else '❌ FAIL'}")
    print(f"   Config:  {'✅ PASS' if config_success else '❌ FAIL'}")
    print(f"   API:     {'✅ PASS' if api_success else '❌ FAIL'}")

    if all([import_success, config_success, api_success]):
        print("\n🎉 All tests passed! Service is ready for development.")
        print("\n📋 Next steps:")
        print(
            "   1. Start the service: python -m uvicorn app.main:app --host 127.0.0.1 --port 9000"
        )
        print("   2. Test endpoints: http://127.0.0.1:9000/docs")
        print("   3. Health check: http://127.0.0.1:9000/health")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
