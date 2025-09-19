#!/usr/bin/env python3
"""
Workflow Integration Test
InvestByYourself Financial Platform

Test the complete workflow integration between frontend and backend.
"""

import json
import time

import requests


def test_workflow_integration():
    """Test complete workflow integration."""
    print("=" * 60)
    print("WORKFLOW INTEGRATION TEST")
    print("=" * 60)

    base_url = "http://localhost:8000/api/v1"

    # Test 1: Health check
    print("\n1. Testing API Health...")
    try:
        response = requests.get(f"{base_url}/workflows/health", timeout=5)
        if response.status_code == 200:
            print("✅ API Health: PASSED")
        else:
            print(f"❌ API Health: FAILED - Status {response.status_code}")
            return
    except Exception as e:
        print(f"❌ API Health: FAILED - {e}")
        return

    # Test 2: List workflows
    print("\n2. Testing Workflow Listing...")
    try:
        response = requests.get(f"{base_url}/workflows", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(
                f"✅ Workflow Listing: PASSED - {len(data.get('workflows', []))} workflows"
            )
        else:
            print(f"❌ Workflow Listing: FAILED - Status {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Workflow Listing: FAILED - {e}")
        return

    # Test 3: Get specific workflow
    print("\n3. Testing Workflow Retrieval...")
    try:
        response = requests.get(f"{base_url}/workflows/portfolio_creation", timeout=5)
        if response.status_code == 200:
            workflow = response.json()
            print(f"✅ Workflow Retrieval: PASSED - {workflow.get('name', 'Unknown')}")
        else:
            print(f"❌ Workflow Retrieval: FAILED - Status {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Workflow Retrieval: FAILED - {e}")
        return

    # Test 4: Execute workflow
    print("\n4. Testing Workflow Execution...")
    try:
        execution_request = {
            "workflow_id": "portfolio_creation",
            "context": {
                "user_id": "test_user",
                "session_id": "test_session",
                "data": {
                    "profile_data": {
                        "risk_tolerance": "moderate",
                        "time_horizon": "10_years",
                        "investment_goals": "retirement",
                    }
                },
            },
        }

        response = requests.post(
            f"{base_url}/workflows/execute", json=execution_request, timeout=10
        )

        if response.status_code == 200:
            execution = response.json()
            execution_id = execution.get("execution_id")
            print(f"✅ Workflow Execution: PASSED - Execution ID: {execution_id}")

            # Test 5: Get execution status
            print("\n5. Testing Execution Status...")
            time.sleep(1)  # Wait a moment

            status_response = requests.get(
                f"{base_url}/workflows/executions/{execution_id}", timeout=5
            )
            if status_response.status_code == 200:
                status = status_response.json()
                print(
                    f"✅ Execution Status: PASSED - Status: {status.get('status', 'Unknown')}"
                )
            else:
                print(
                    f"❌ Execution Status: FAILED - Status {status_response.status_code}"
                )
        else:
            print(f"❌ Workflow Execution: FAILED - Status {response.status_code}")
            print(f"   Response: {response.text}")
            return

    except Exception as e:
        print(f"❌ Workflow Execution: FAILED - {e}")
        return

    print("\n" + "=" * 60)
    print("WORKFLOW INTEGRATION TEST COMPLETED SUCCESSFULLY!")
    print("=" * 60)

    print("\nNext Steps:")
    print("1. Open http://localhost:3000/workflows in your browser")
    print("2. Test the frontend workflow interface")
    print("3. Verify real-time status updates work")


if __name__ == "__main__":
    test_workflow_integration()
