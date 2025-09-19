#!/usr/bin/env python3
"""
Test Workflow Response
InvestByYourself Financial Platform

Tests the workflow execution response to debug the null issue.
"""

import json

import requests


def test_workflow_response():
    """Test workflow execution response."""
    base_url = "http://localhost:8000/api/v1"

    print("Testing workflow execution response...")

    workflow_request = {
        "workflow_id": "comprehensive_portfolio_creation",
        "context": {
            "user_id": "test_user",
            "session_id": "test_session_debug",
            "data": {
                "portfolio_name": "Debug Test Portfolio",
                "portfolio_description": "Testing workflow response",
            },
        },
    }

    try:
        response = requests.post(
            f"{base_url}/workflows/execute", json=workflow_request, timeout=10
        )
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("Response Data:")
            print(json.dumps(data, indent=2))

            # Check if results are empty
            results = data.get("results", {})
            print(f"\nResults: {results}")
            print(f"Results type: {type(results)}")
            print(f"Results empty: {not results}")

        else:
            print(f"Error: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    test_workflow_response()
