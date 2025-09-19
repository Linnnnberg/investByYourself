#!/usr/bin/env python3
"""
Test Get Workflow Steps
InvestByYourself Financial Platform

Test the get_workflow_steps method to see what it returns.
"""

import json

import requests


def test_get_workflow_steps():
    """Test what get_workflow_steps returns."""
    base_url = "http://localhost:8000/api/v1"

    print("Testing get_workflow_steps method...")

    # Get workflow definition from API
    try:
        response = requests.get(
            f"{base_url}/workflows/comprehensive_portfolio_creation", timeout=5
        )
        if response.status_code == 200:
            workflow_def = response.json()

            print(f"API Response structure:")
            print(f"  - ID: {workflow_def.get('id')}")
            print(f"  - Name: {workflow_def.get('name')}")
            print(f"  - Steps count: {len(workflow_def.get('steps', []))}")
            print(f"  - Definition: {workflow_def.get('definition')}")

            steps = workflow_def.get("steps", [])
            if steps:
                print(f"\nFirst step structure:")
                print(json.dumps(steps[0], indent=2))

                print(f"\nStep keys: {list(steps[0].keys())}")
                print(f"Step ID: {steps[0].get('id')}")
                print(f"Step name: {steps[0].get('name')}")
                print(f"Step type: {steps[0].get('step_type')}")

            # Test the workflow engine with this exact structure
            class MinimalWorkflowEngine:
                def execute_workflow(self, workflow, context):
                    results = {}
                    steps = workflow.get("steps", [])
                    print(f"Workflow engine received {len(steps)} steps")
                    for step in steps:
                        step_id = step["id"]
                        results[step_id] = {
                            "status": "completed",
                            "result": f"Step {step_id}",
                        }
                    return results

            context = type(
                "Context",
                (),
                {
                    "data": {},
                    "update_data": lambda self, k, v: setattr(self.data, k, v),
                },
            )()
            engine = MinimalWorkflowEngine()
            results = engine.execute_workflow(workflow_def, context)

            print(f"\nWorkflow engine results: {len(results)} results")
            print(f"Result keys: {list(results.keys())}")

        else:
            print(f"❌ Failed to get workflow: {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_get_workflow_steps()
