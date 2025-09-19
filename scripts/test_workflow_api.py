#!/usr/bin/env python3
"""
Test Workflow API Endpoints
InvestByYourself Financial Platform

Tests the workflow API endpoints to ensure they work correctly.
"""

import json
from datetime import datetime

import requests

# API base URL (adjust if needed)
BASE_URL = "http://localhost:8000/api/v1"


def test_workflow_api():
    """Test workflow API endpoints."""
    print("=" * 60)
    print("WORKFLOW API ENDPOINT TESTS")
    print("=" * 60)

    # Test 1: Health Check
    print("\n1. Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/workflows/health")
        if response.status_code == 200:
            print("✅ Health Check: PASSED")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health Check: FAILED - {response.status_code}")
    except Exception as e:
        print(f"❌ Health Check: FAILED - {e}")

    # Test 2: List Workflows
    print("\n2. Testing List Workflows...")
    try:
        response = requests.get(f"{BASE_URL}/workflows")
        if response.status_code == 200:
            data = response.json()
            print("✅ List Workflows: PASSED")
            print(f"   Total workflows: {data.get('total', 0)}")
            for workflow in data.get("workflows", []):
                print(f"   - {workflow['id']}: {workflow['name']}")
        else:
            print(f"❌ List Workflows: FAILED - {response.status_code}")
    except Exception as e:
        print(f"❌ List Workflows: FAILED - {e}")

    # Test 3: Get Specific Workflow
    print("\n3. Testing Get Specific Workflow...")
    try:
        response = requests.get(f"{BASE_URL}/workflows/portfolio_creation")
        if response.status_code == 200:
            data = response.json()
            print("✅ Get Specific Workflow: PASSED")
            print(f"   Workflow: {data['name']}")
            print(f"   Steps: {len(data['steps'])}")
        else:
            print(f"❌ Get Specific Workflow: FAILED - {response.status_code}")
    except Exception as e:
        print(f"❌ Get Specific Workflow: FAILED - {e}")

    # Test 4: Execute Workflow
    print("\n4. Testing Execute Workflow...")
    try:
        workflow_request = {
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

        response = requests.post(f"{BASE_URL}/workflows/execute", json=workflow_request)

        if response.status_code == 200:
            data = response.json()
            print("✅ Execute Workflow: PASSED")
            print(f"   Execution ID: {data['execution_id']}")
            print(f"   Status: {data['status']}")
            print(f"   Progress: {data['progress']}%")
        else:
            print(f"❌ Execute Workflow: FAILED - {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Execute Workflow: FAILED - {e}")

    # Test 5: Execute Single Step
    print("\n5. Testing Execute Single Step...")
    try:
        step_request = {
            "workflow_id": "portfolio_creation",
            "step_id": "profile_assessment",
            "context": {
                "user_id": "test_user",
                "session_id": "test_session",
                "data": {"profile_data": {"risk_tolerance": "aggressive"}},
            },
            "results": {},
        }

        response = requests.post(
            f"{BASE_URL}/workflows/execute-step", json=step_request
        )

        if response.status_code == 200:
            data = response.json()
            print("✅ Execute Single Step: PASSED")
            print(f"   Step ID: {data['step_id']}")
            print(f"   Status: {data['status']}")
        else:
            print(f"❌ Execute Single Step: FAILED - {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Execute Single Step: FAILED - {e}")

    # Test 6: List Workflow Executions
    print("\n6. Testing List Workflow Executions...")
    try:
        response = requests.get(f"{BASE_URL}/workflows/executions")
        if response.status_code == 200:
            data = response.json()
            print("✅ List Workflow Executions: PASSED")
            print(f"   Total executions: {len(data)}")
        else:
            print(f"❌ List Workflow Executions: FAILED - {response.status_code}")
    except Exception as e:
        print(f"❌ List Workflow Executions: FAILED - {e}")

    print("\n" + "=" * 60)
    print("API TEST COMPLETED")
    print("=" * 60)

    print("\nNext Steps:")
    print("1. Start the API server: cd api && python -m uvicorn src.main:app --reload")
    print("2. Run this test script: python scripts/test_workflow_api.py")
    print("3. Check the API documentation at: http://localhost:8000/docs")


if __name__ == "__main__":
    test_workflow_api()
