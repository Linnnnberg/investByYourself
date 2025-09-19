#!/usr/bin/env python3
"""
Debug Workflow Execution
InvestByYourself Financial Platform

Debug the workflow execution to see why results are empty.
"""

import json

import requests


def debug_workflow_execution():
    """Debug workflow execution step by step."""
    base_url = "http://localhost:8000/api/v1"

    print("=" * 80)
    print("DEBUGGING WORKFLOW EXECUTION")
    print("=" * 80)

    # Step 1: Get workflow definition
    print("\n1. Getting workflow definition...")
    try:
        response = requests.get(
            f"{base_url}/workflows/comprehensive_portfolio_creation", timeout=5
        )
        if response.status_code == 200:
            workflow_def = response.json()
            print(f"✅ Workflow found: {workflow_def['name']}")
            print(f"   Steps: {len(workflow_def.get('steps', []))}")
            print(f"   Entry points: {workflow_def.get('entry_points', [])}")
            print(f"   Exit points: {workflow_def.get('exit_points', [])}")

            # Show first few steps
            steps = workflow_def.get("steps", [])
            for i, step in enumerate(steps[:3]):
                print(f"   Step {i+1}: {step.get('id')} - {step.get('name')}")
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

            execution_id = execution_data["execution_id"]
        else:
            print(f"❌ Workflow execution failed: {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print(f"❌ Error executing workflow: {e}")
        return

    # Step 3: Check execution status
    print("\n3. Checking execution status...")
    try:
        response = requests.get(
            f"{base_url}/workflows/executions/{execution_id}", timeout=5
        )
        if response.status_code == 200:
            status_data = response.json()
            print(f"✅ Execution status retrieved")
            print(f"   Status: {status_data['status']}")
            print(f"   Current step: {status_data.get('current_step')}")
            print(f"   Progress: {status_data['progress']}")
            print(f"   Step results: {status_data.get('step_results', {})}")
            print(f"   Step results type: {type(status_data.get('step_results', {}))}")
            print(
                f"   Step results keys: {list(status_data.get('step_results', {}).keys())}"
            )
        else:
            print(f"❌ Failed to get execution status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting execution status: {e}")


if __name__ == "__main__":
    debug_workflow_execution()
