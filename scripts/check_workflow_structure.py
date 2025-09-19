#!/usr/bin/env python3
"""
Check Workflow Structure
InvestByYourself Financial Platform

Check the structure of the workflow definition to debug execution.
"""

import json

import requests


def check_workflow_structure():
    """Check workflow definition structure."""
    base_url = "http://localhost:8000/api/v1"

    print("Checking workflow definition structure...")

    try:
        response = requests.get(
            f"{base_url}/workflows/comprehensive_portfolio_creation", timeout=5
        )
        if response.status_code == 200:
            workflow_def = response.json()

            print(f"Workflow ID: {workflow_def.get('id')}")
            print(f"Workflow Name: {workflow_def.get('name')}")
            print(f"Workflow Description: {workflow_def.get('description')}")

            # Check the definition structure
            definition = workflow_def.get("definition", {})
            print(f"\nDefinition keys: {list(definition.keys())}")

            steps = definition.get("steps", [])
            print(f"\nSteps count: {len(steps)}")

            if steps:
                print("\nFirst step structure:")
                first_step = steps[0]
                print(json.dumps(first_step, indent=2))

                print(f"\nStep keys: {list(first_step.keys())}")
                print(f"Step ID: {first_step.get('id')}")
                print(f"Step name: {first_step.get('name')}")
                print(f"Step type: {first_step.get('step_type')}")

            # Check if steps are directly in workflow_def
            direct_steps = workflow_def.get("steps", [])
            print(f"\nDirect steps count: {len(direct_steps)}")

            if direct_steps:
                print("\nFirst direct step:")
                print(json.dumps(direct_steps[0], indent=2))

        else:
            print(f"Failed to get workflow: {response.status_code}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    check_workflow_structure()
