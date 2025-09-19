#!/usr/bin/env python3
"""
Test API Workflow Flow
InvestByYourself Financial Platform

Test the complete API workflow flow to debug the issue.
"""

import json

import requests


def test_api_workflow_flow():
    """Test the complete API workflow flow."""
    base_url = "http://localhost:8000/api/v1"

    print("=" * 80)
    print("TESTING API WORKFLOW FLOW")
    print("=" * 80)

    # Step 1: Get workflow definition
    print("\n1. Getting workflow definition...")
    try:
        response = requests.get(
            f"{base_url}/workflows/comprehensive_portfolio_creation", timeout=5
        )
        if response.status_code == 200:
            workflow_def = response.json()
            print(f"✅ Workflow definition retrieved")
            print(f"   ID: {workflow_def.get('id')}")
            print(f"   Name: {workflow_def.get('name')}")
            print(f"   Steps count: {len(workflow_def.get('steps', []))}")
            print(
                f"   Definition keys: {list(workflow_def.get('definition', {}).keys())}"
            )

            # Check the structure
            steps = workflow_def.get("steps", [])
            if steps:
                print(f"   First step: {steps[0].get('id')} - {steps[0].get('name')}")

            definition = workflow_def.get("definition", {})
            def_steps = definition.get("steps", [])
            print(f"   Definition steps count: {len(def_steps)}")

        else:
            print(f"❌ Failed to get workflow: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error getting workflow: {e}")
        return

    # Step 2: Execute workflow
    print("\n2. Executing workflow...")
    workflow_request = {
        "workflow_id": "comprehensive_portfolio_creation",
        "context": {
            "user_id": "debug_user",
            "session_id": "debug_session",
            "data": {
                "portfolio_name": "Debug Portfolio",
                "portfolio_description": "Debug test",
            },
        },
    }

    try:
        response = requests.post(
            f"{base_url}/workflows/execute", json=workflow_request, timeout=10
        )
        if response.status_code == 200:
            execution_data = response.json()
            print(f"✅ Workflow executed successfully")
            print(f"   Execution ID: {execution_data['execution_id']}")
            print(f"   Status: {execution_data['status']}")
            print(f"   Progress: {execution_data['progress']}")
            print(f"   Results: {execution_data['results']}")
            print(f"   Results type: {type(execution_data['results'])}")
            print(f"   Results keys: {list(execution_data['results'].keys())}")

            # Check if results are empty
            if not execution_data["results"]:
                print("❌ RESULTS ARE EMPTY - This is the problem!")
            else:
                print("✅ Results are present")

        else:
            print(f"❌ Workflow execution failed: {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print(f"❌ Error executing workflow: {e}")
        return


if __name__ == "__main__":
    test_api_workflow_flow()
