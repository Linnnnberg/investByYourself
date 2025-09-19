#!/usr/bin/env python3
"""
Test Complete Workflow Flow
InvestByYourself Financial Platform

Test the complete workflow flow including database storage.
"""

import json

import requests


def test_complete_workflow_flow():
    """Test the complete workflow flow."""
    base_url = "http://localhost:8000/api/v1"

    print("=" * 80)
    print("TESTING COMPLETE WORKFLOW FLOW")
    print("=" * 80)

    # Step 1: Execute workflow
    print("\n1. Executing workflow...")
    workflow_request = {
        "workflow_id": "comprehensive_portfolio_creation",
        "context": {
            "user_id": "test_user",
            "session_id": "test_session_complete",
            "data": {
                "portfolio_name": "Complete Test Portfolio",
                "portfolio_description": "Testing complete workflow flow",
            },
        },
    }

    try:
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
            print(f"   Results type: {type(execution_data['results'])}")
            print(f"   Results empty: {not execution_data['results']}")
        else:
            print(f"❌ Workflow execution failed: {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print(f"❌ Error executing workflow: {e}")
        return

    # Step 2: Check execution status
    print("\n2. Checking execution status...")
    try:
        response = requests.get(
            f"{base_url}/workflows/executions/{execution_id}", timeout=5
        )
        if response.status_code == 200:
            status_data = response.json()
            print(f"✅ Execution status retrieved")
            print(f"   Status: {status_data['status']}")
            print(f"   Progress: {status_data['progress']}")
            print(f"   Step results: {status_data.get('step_results', {})}")
            print(f"   Step results type: {type(status_data.get('step_results', {}))}")
            print(f"   Step results empty: {not status_data.get('step_results', {})}")
        else:
            print(f"❌ Failed to get execution status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting execution status: {e}")

    # Step 3: Test portfolio creation
    print("\n3. Testing portfolio creation...")
    try:
        portfolio_request = {
            "workflow_id": "comprehensive_portfolio_creation",
            "execution_id": execution_id,
            "context": {
                "portfolio_name": "Complete Test Portfolio",
                "portfolio_description": "Testing complete workflow flow",
            },
            "user_id": "test_user",
        }

        response = requests.post(
            f"{base_url}/portfolios/create", json=portfolio_request, timeout=10
        )
        if response.status_code == 200:
            portfolio_data = response.json()
            print(f"✅ Portfolio created successfully")
            print(f"   Portfolio ID: {portfolio_data.get('portfolio', {}).get('id')}")
            print(
                f"   Portfolio Name: {portfolio_data.get('portfolio', {}).get('name')}"
            )
        else:
            print(f"❌ Portfolio creation failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error creating portfolio: {e}")


if __name__ == "__main__":
    test_complete_workflow_flow()
