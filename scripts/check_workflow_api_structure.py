#!/usr/bin/env python3
"""
Check Workflow API Structure
InvestByYourself Financial Platform

Check the workflow definition structure from the API response.
"""

import json

import requests


def check_workflow_api_structure():
    """Check workflow definition structure from API."""
    base_url = "http://localhost:8000/api/v1"

    print("Checking workflow definition structure from API...")

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
            print(f"\nDefinition type: {type(definition)}")
            print(f"Definition: {json.dumps(definition, indent=2)}")

            if definition:
                print(f"Definition keys: {list(definition.keys())}")
                steps = definition.get("steps", [])
                print(f"Steps in definition: {len(steps)}")
                if steps:
                    print(f"First step: {json.dumps(steps[0], indent=2)}")
            else:
                print("Definition is empty or None")

            # Check direct steps
            direct_steps = workflow_def.get("steps", [])
            print(f"\nDirect steps count: {len(direct_steps)}")
            if direct_steps:
                print(f"First direct step: {json.dumps(direct_steps[0], indent=2)}")

        else:
            print(f"Failed to get workflow: {response.status_code}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    check_workflow_api_structure()
