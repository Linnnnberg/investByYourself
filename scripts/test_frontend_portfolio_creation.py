#!/usr/bin/env python3
"""
Test Frontend Portfolio Creation
InvestByYourself Financial Platform

Test that the frontend can create portfolios and they appear in the list.
"""

import json

import requests


def test_frontend_portfolio_creation():
    """Test frontend portfolio creation flow."""
    base_url = "http://localhost:8000/api/v1"

    print("=" * 80)
    print("TESTING FRONTEND PORTFOLIO CREATION")
    print("=" * 80)

    # Step 1: Check current portfolios
    print("\n1. Checking current portfolios...")
    try:
        response = requests.get(f"{base_url}/portfolios/", timeout=5)
        if response.status_code == 200:
            portfolios = response.json()
            print(
                f"✅ Found {len(portfolios.get('portfolios', []))} existing portfolios"
            )
            for portfolio in portfolios.get("portfolios", []):
                print(f"   - {portfolio['name']} ({portfolio['status']})")
        else:
            print(f"❌ Failed to get portfolios: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting portfolios: {e}")

    # Step 2: Execute workflow
    print("\n2. Executing portfolio creation workflow...")
    try:
        workflow_request = {
            "workflow_id": "comprehensive_portfolio_creation",
            "context": {
                "user_id": "frontend_test_user",
                "session_id": "frontend_test_session",
                "data": {
                    "portfolio_name": "Frontend Test Portfolio",
                    "portfolio_description": "Created via frontend test",
                },
            },
        }

        response = requests.post(
            f"{base_url}/workflows/execute", json=workflow_request, timeout=10
        )
        if response.status_code == 200:
            execution_data = response.json()
            execution_id = execution_data["execution_id"]
            print(f"✅ Workflow executed successfully")
            print(f"   Execution ID: {execution_id}")
            print(f"   Status: {execution_data['status']}")
            print(f"   Results: {execution_data['results']}")
        else:
            print(f"❌ Workflow execution failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error executing workflow: {e}")
        return

    # Step 3: Create portfolio
    print("\n3. Creating portfolio from workflow...")
    try:
        portfolio_request = {
            "workflow_id": "comprehensive_portfolio_creation",
            "execution_id": execution_id,
            "context": {
                "portfolio_name": "Frontend Test Portfolio",
                "portfolio_description": "Created via frontend test",
            },
            "user_id": "frontend_test_user",
        }

        response = requests.post(
            f"{base_url}/portfolios/create", json=portfolio_request, timeout=10
        )
        if response.status_code == 200:
            portfolio_data = response.json()
            portfolio = portfolio_data.get("portfolio")
            print(f"✅ Portfolio created successfully")
            print(f"   Portfolio ID: {portfolio['id']}")
            print(f"   Portfolio Name: {portfolio['name']}")
            print(f"   Portfolio Status: {portfolio['status']}")
        else:
            print(f"❌ Portfolio creation failed: {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print(f"❌ Error creating portfolio: {e}")
        return

    # Step 4: Verify portfolio appears in list
    print("\n4. Verifying portfolio appears in list...")
    try:
        response = requests.get(
            f"{base_url}/portfolios/?user_id=frontend_test_user", timeout=5
        )
        if response.status_code == 200:
            portfolios = response.json()
            test_portfolios = [
                p
                for p in portfolios.get("portfolios", [])
                if p["name"] == "Frontend Test Portfolio"
            ]
            if test_portfolios:
                print(
                    f"✅ Test portfolio found in list - {len(test_portfolios)} portfolio(s)"
                )
                for portfolio in test_portfolios:
                    print(
                        f"   - {portfolio['name']} ({portfolio['status']}) - {portfolio['id']}"
                    )
            else:
                print("❌ Test portfolio not found in list")
                print("Available portfolios:")
                for portfolio in portfolios.get("portfolios", []):
                    print(f"   - {portfolio['name']} ({portfolio['status']})")
        else:
            print(f"❌ Failed to get portfolios: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting portfolios: {e}")

    print("\n" + "=" * 80)
    print("✅ FRONTEND PORTFOLIO CREATION TEST COMPLETED!")
    print("=" * 80)


if __name__ == "__main__":
    test_frontend_portfolio_creation()
