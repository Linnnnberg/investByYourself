#!/usr/bin/env python3
"""
Test Workflow Engine with API Data
InvestByYourself Financial Platform

Test the workflow engine with the actual data structure from the API.
"""

import json

import requests


def test_workflow_engine_with_api_data():
    """Test workflow engine with actual API data structure."""
    base_url = "http://localhost:8000/api/v1"

    print("Testing workflow engine with API data structure...")

    # Get workflow definition from API
    try:
        response = requests.get(
            f"{base_url}/workflows/comprehensive_portfolio_creation", timeout=5
        )
        if response.status_code == 200:
            workflow_def = response.json()
            print(
                f"✅ Got workflow definition with {len(workflow_def.get('steps', []))} steps"
            )

            # Test the workflow engine with this data
            class MinimalWorkflowEngine:
                def execute_workflow(self, workflow, context):
                    """Execute a workflow with dummy implementation."""
                    results = {}

                    # Get steps from workflow definition - check both locations
                    steps = workflow.get("steps", [])
                    if not steps and "definition" in workflow:
                        steps = workflow["definition"].get("steps", [])

                    print(f"Workflow engine found {len(steps)} steps")
                    print(f"Steps: {[s.get('id') for s in steps]}")

                    for step in steps:
                        step_id = step["id"]
                        results[step_id] = {
                            "status": "completed",
                            "executed_at": "2025-09-19T22:24:00Z",
                            "result": f"Executed step: {step['name']}",
                        }
                        print(f"Executed step {step_id}: {step['name']}")

                    print(f"Returning {len(results)} results")
                    return results

            class DummyContext:
                def __init__(self):
                    self.data = {}

                def update_data(self, key, value):
                    self.data[key] = value

            # Test with the actual API data
            context = DummyContext()
            engine = MinimalWorkflowEngine()
            results = engine.execute_workflow(workflow_def, context)

            print(f"\nFinal results: {results}")
            print(f"Number of results: {len(results)}")

        else:
            print(f"❌ Failed to get workflow: {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_workflow_engine_with_api_data()
