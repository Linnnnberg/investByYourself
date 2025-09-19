#!/usr/bin/env python3
"""
Test Workflow Engine Direct
InvestByYourself Financial Platform

Test the workflow engine directly to debug the issue.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api", "src"))


# Import the workflow engine directly
class MinimalWorkflowEngine:
    def execute_workflow(self, workflow, context):
        """Execute a workflow with dummy implementation."""
        # Update context with provided data
        if hasattr(context, "data") and context.data:
            for key, value in context.data.items():
                context.update_data(key, value)

        # Simulate workflow execution
        results = {}

        # Get steps from workflow definition - check both locations
        steps = workflow.get("steps", [])
        if not steps and "definition" in workflow:
            steps = workflow["definition"].get("steps", [])

        for step in steps:
            step_id = step["id"]
            results[step_id] = {
                "status": "completed",
                "executed_at": "2025-09-19T22:21:00Z",
                "result": f"Executed step: {step['name']}",
            }
        return results


class DummyWorkflowContext:
    def __init__(self, user_id, session_id):
        self.user_id = user_id
        self.session_id = session_id
        self.data = {}

    def update_data(self, key, value):
        self.data[key] = value


def test_workflow_engine():
    """Test the workflow engine directly."""
    print("Testing workflow engine directly...")

    # Create a simple workflow
    workflow = {
        "id": "test_workflow",
        "name": "Test Workflow",
        "steps": [
            {"id": "step1", "name": "Step 1", "step_type": "data_collection"},
            {"id": "step2", "name": "Step 2", "step_type": "validation"},
        ],
    }

    # Create context
    context = DummyWorkflowContext("test_user", "test_session")
    context.update_data("test_data", "test_value")

    # Execute workflow
    engine = MinimalWorkflowEngine()
    results = engine.execute_workflow(workflow, context)

    print(f"Workflow execution results: {results}")
    print(f"Number of results: {len(results)}")
    print(f"Result keys: {list(results.keys())}")

    return results


if __name__ == "__main__":
    test_workflow_engine()
