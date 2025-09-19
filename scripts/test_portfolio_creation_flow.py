#!/usr/bin/env python3
"""
Portfolio Creation Flow Test
InvestByYourself Financial Platform

Tests the complete portfolio creation flow from workflow execution to database storage.
"""

import json
import time

import requests


def test_portfolio_creation_flow():
    """Test the complete portfolio creation flow."""
    base_url = "http://localhost:8000/api/v1"

    print("=" * 80)
    print("TESTING PORTFOLIO CREATION FLOW")
    print("=" * 80)

    # Step 1: Check if portfolios API is working
    print("\n1. Testing portfolios API...")
    try:
        response = requests.get(f"{base_url}/portfolios/", timeout=5)
        if response.status_code == 200:
            portfolios = response.json()
            print(
                f"✅ Portfolios API working - Found {len(portfolios.get('portfolios', []))} portfolios"
            )
            for portfolio in portfolios.get("portfolios", []):
                print(f"   - {portfolio['name']} ({portfolio['status']})")
        else:
            print(f"❌ Portfolios API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Portfolios API error: {e}")
        return False

    # Step 2: Test workflow execution
    print("\n2. Testing workflow execution...")
    try:
        workflow_request = {
            "workflow_id": "comprehensive_portfolio_creation",
            "context": {
                "user_id": "test_user",
                "session_id": f"test_session_{int(time.time())}",
                "data": {
                    "portfolio_name": "Test Portfolio",
                    "portfolio_description": "Created via test script",
                    "template": {
                        "id": "conservative",
                        "name": "Conservative Growth",
                        "allocation": {"Bonds": 60, "Stocks": 30, "Cash": 10},
                        "riskLevel": "Low",
                    },
                },
            },
        }

        response = requests.post(
            f"{base_url}/workflows/execute", json=workflow_request, timeout=10
        )
        if response.status_code == 200:
            workflow_data = response.json()
            execution_id = workflow_data.get("execution_id")
            print(f"✅ Workflow executed successfully - Execution ID: {execution_id}")
        else:
            print(
                f"❌ Workflow execution failed: {response.status_code} - {response.text}"
            )
            return False
    except Exception as e:
        print(f"❌ Workflow execution error: {e}")
        return False

    # Step 3: Test portfolio creation from workflow
    print("\n3. Testing portfolio creation from workflow...")
    try:
        portfolio_request = {
            "workflow_id": "comprehensive_portfolio_creation",
            "execution_id": execution_id,
            "context": {
                "portfolio_name": "Test Portfolio",
                "portfolio_description": "Created via test script",
                "template": {
                    "id": "conservative",
                    "name": "Conservative Growth",
                    "allocation": {"Bonds": 60, "Stocks": 30, "Cash": 10},
                    "riskLevel": "Low",
                },
            },
            "user_id": "test_user",
        }

        response = requests.post(
            f"{base_url}/portfolios/create", json=portfolio_request, timeout=10
        )
        if response.status_code == 200:
            portfolio_data = response.json()
            portfolio = portfolio_data.get("portfolio")
            print(f"✅ Portfolio created successfully - ID: {portfolio['id']}")
            print(f"   - Name: {portfolio['name']}")
            print(f"   - Status: {portfolio['status']}")
            print(f"   - Risk Level: {portfolio['riskLevel']}")
            print(f"   - Allocation: {portfolio['allocation']}")
        else:
            print(
                f"❌ Portfolio creation failed: {response.status_code} - {response.text}"
            )
            return False
    except Exception as e:
        print(f"❌ Portfolio creation error: {e}")
        return False

    # Step 4: Verify portfolio appears in list
    print("\n4. Verifying portfolio appears in list...")
    try:
        response = requests.get(f"{base_url}/portfolios/?user_id=test_user", timeout=5)
        if response.status_code == 200:
            portfolios = response.json()
            test_portfolios = [
                p
                for p in portfolios.get("portfolios", [])
                if p["name"] == "Test Portfolio"
            ]
            if test_portfolios:
                print(
                    f"✅ Test portfolio found in list - {len(test_portfolios)} portfolio(s)"
                )
            else:
                print("❌ Test portfolio not found in list")
                return False
        else:
            print(f"❌ Failed to get portfolios: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Portfolio list error: {e}")
        return False

    print("\n" + "=" * 80)
    print("✅ PORTFOLIO CREATION FLOW TEST PASSED!")
    print("=" * 80)
    return True


if __name__ == "__main__":
    success = test_portfolio_creation_flow()
    exit(0 if success else 1)
