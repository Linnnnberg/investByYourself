#!/usr/bin/env python3
"""
Minimal test for WorkflowListResponse
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.models.workflow import (
    WorkflowDefinition,
    WorkflowListResponse,
    WorkflowStep,
    WorkflowStepType,
)


def test_minimal_response():
    """Test minimal WorkflowListResponse creation."""
    print("Testing minimal WorkflowListResponse creation...")

    try:
        # Create a minimal WorkflowStep
        step = WorkflowStep(
            id="test_step",
            name="Test Step",
            step_type=WorkflowStepType.DATA_COLLECTION,
            description="Test step description",
            config={},
            dependencies=[],
        )
        print(f"✅ WorkflowStep created: {type(step)}")

        # Create a minimal WorkflowDefinition
        workflow = WorkflowDefinition(
            id="test_workflow",
            name="Test Workflow",
            description="Test workflow description",
            steps=[step],
            entry_points=["test_step"],
            exit_points=["test_step"],
            created_at=None,
        )
        print(f"✅ WorkflowDefinition created: {type(workflow)}")

        # Create WorkflowListResponse
        response = WorkflowListResponse(workflows=[workflow], total=1)
        print(f"✅ WorkflowListResponse created: {response}")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_minimal_response()
