#!/usr/bin/env python3
"""
Test API Import
InvestByYourself Financial Platform

Test if the API can import the workflow endpoints.
"""

import os
import sys

# Add api to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))


def test_api_imports():
    """Test API imports."""
    print("=" * 60)
    print("API IMPORT TESTS")
    print("=" * 60)

    # Test 1: Import main API
    print("\n1. Testing Main API Import...")
    try:
        from src.main import create_application

        print("✅ Main API: PASSED")
    except Exception as e:
        print(f"❌ Main API: FAILED - {e}")
        return

    # Test 2: Import API router
    print("\n2. Testing API Router Import...")
    try:
        from src.api.v1.router import api_router

        print("✅ API Router: PASSED")
        print(f"   Available routes: {len(api_router.routes)}")
        for route in api_router.routes:
            print(f"   - {route.path} - {route.methods}")
    except Exception as e:
        print(f"❌ API Router: FAILED - {e}")
        return

    # Test 3: Import workflow endpoints
    print("\n3. Testing Workflow Endpoints Import...")
    try:
        from src.api.v1.endpoints.workflows import router

        print("✅ Workflow Endpoints: PASSED")
        print(f"   Available routes: {len(router.routes)}")
        for route in router.routes:
            print(f"   - {route.path} - {route.methods}")
    except Exception as e:
        print(f"❌ Workflow Endpoints: FAILED - {e}")
        return

    # Test 4: Test workflow models
    print("\n4. Testing Workflow Models Import...")
    try:
        from src.models.workflow import WorkflowDefinition

        print("✅ Workflow Models: PASSED")
    except Exception as e:
        print(f"❌ Workflow Models: FAILED - {e}")
        return

    print("\n" + "=" * 60)
    print("ALL API IMPORTS SUCCESSFUL!")
    print("=" * 60)


if __name__ == "__main__":
    test_api_imports()
