#!/usr/bin/env python3
"""
Test runner for the Strategy Framework
This script tests the core functionality of our investment strategy framework
"""

import os
import sys
import unittest
from pathlib import Path

# Add the testing directory to the path
sys.path.insert(0, os.path.dirname(__file__))


def test_strategy_framework_imports():
    """Test that all strategy framework modules can be imported."""
    print("🔧 Testing Strategy Framework Imports...")
    print("-" * 50)

    try:
        # Test base framework import
        from strategy_framework import BaseStrategy

        print("✅ BaseStrategy imported successfully")

        # Test momentum strategy (only one with a class)
        from momentum_strategy import MomentumStrategy

        print("✅ MomentumStrategy imported successfully")

        # Test script imports (these are just scripts, not classes)
        import sector_rotation_strategy

        print("✅ sector_rotation_strategy imported successfully")

        import hedge_strategy_backtest

        print("✅ hedge_strategy_backtest imported successfully")

        return True

    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during import test: {e}")
        return False


def test_strategy_framework_instantiation():
    """Test that strategy classes can be instantiated."""
    print("\n🔧 Testing Strategy Framework Instantiation...")
    print("-" * 50)

    try:
        from momentum_strategy import MomentumStrategy
        from strategy_framework import BaseStrategy

        # Test base strategy (should fail since it's abstract)
        try:
            base_strategy = BaseStrategy(["SPY"], "SPY", "2020-01-01", "2024-12-31")
            print("❌ BaseStrategy should not be instantiable (abstract class)")
            return False
        except TypeError:
            print("✅ BaseStrategy correctly prevents instantiation (abstract class)")

        # Test concrete strategy implementation
        momentum_strategy = MomentumStrategy()
        print("✅ MomentumStrategy instantiated successfully")

        return True

    except Exception as e:
        print(f"❌ Instantiation test failed: {e}")
        return False


def test_strategy_methods():
    """Test that strategy classes have required methods."""
    print("\n🔧 Testing Strategy Framework Methods...")
    print("-" * 50)

    try:
        from momentum_strategy import MomentumStrategy

        # Test MomentumStrategy
        momentum_strategy = MomentumStrategy()
        assert hasattr(
            momentum_strategy, "get_strategy_name"
        ), "Missing get_strategy_name method"
        assert hasattr(
            momentum_strategy, "get_strategy_description"
        ), "Missing get_strategy_description method"
        assert hasattr(
            momentum_strategy, "calculate_weights"
        ), "Missing calculate_weights method"
        print("✅ MomentumStrategy has all required methods")

        return True

    except Exception as e:
        print(f"❌ Methods test failed: {e}")
        return False


def test_strategy_outputs():
    """Test that strategy methods return expected outputs."""
    print("\n🔧 Testing Strategy Framework Outputs...")
    print("-" * 50)

    try:
        from momentum_strategy import MomentumStrategy

        momentum_strategy = MomentumStrategy()

        # Test strategy name
        name = momentum_strategy.get_strategy_name()
        assert isinstance(name, str), "Strategy name should be a string"
        assert len(name) > 0, "Strategy name should not be empty"
        print(f"✅ Strategy name: {name}")

        # Test strategy description
        description = momentum_strategy.get_strategy_description()
        assert isinstance(description, str), "Strategy description should be a string"
        assert len(description) > 0, "Strategy description should not be empty"
        print(f"✅ Strategy description: {description}")

        return True

    except Exception as e:
        print(f"❌ Outputs test failed: {e}")
        return False


def test_script_functions():
    """Test that strategy scripts have required functions."""
    print("\n🔧 Testing Strategy Script Functions...")
    print("-" * 50)

    try:
        import hedge_strategy_backtest
        import sector_rotation_strategy

        # Test sector rotation strategy functions
        assert hasattr(
            sector_rotation_strategy, "download_data"
        ), "Missing download_data function"
        assert hasattr(
            sector_rotation_strategy, "calculate_portfolio_weights"
        ), "Missing calculate_portfolio_weights function"
        assert hasattr(sector_rotation_strategy, "main"), "Missing main function"
        print("✅ sector_rotation_strategy has all required functions")

        # Test hedge strategy functions
        assert hasattr(
            hedge_strategy_backtest, "download_data"
        ), "Missing download_data function"
        assert hasattr(
            hedge_strategy_backtest, "calculate_hedge_strategy_weights"
        ), "Missing calculate_hedge_strategy_weights function"
        assert hasattr(hedge_strategy_backtest, "main"), "Missing main function"
        print("✅ hedge_strategy_backtest has all required functions")

        return True

    except Exception as e:
        print(f"❌ Script functions test failed: {e}")
        return False


def test_file_structure():
    """Test that all required files exist."""
    print("\n🔧 Testing File Structure...")
    print("-" * 50)

    # Get the testing directory path
    testing_dir = os.path.dirname(os.path.abspath(__file__))

    required_files = [
        "strategy_framework.py",
        "sector_rotation_strategy.py",
        "hedge_strategy_backtest.py",
        "momentum_strategy.py",
        "requirements.txt",
    ]

    missing_files = []
    for file in required_files:
        file_path = os.path.join(testing_dir, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
        else:
            print(f"✅ {file} exists")

    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False

    print("✅ All required files exist")
    return True


def main():
    """Run all tests."""
    print("🚀 Strategy Framework Test Suite")
    print("=" * 60)

    tests = [
        test_file_structure,
        test_strategy_framework_imports,
        test_strategy_framework_instantiation,
        test_strategy_methods,
        test_strategy_outputs,
        test_script_functions,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            print(f"❌ {test.__name__} crashed: {e}")

    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Strategy framework is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
