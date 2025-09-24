#!/usr/bin/env python3
"""
Direct Workflow Engine Test
InvestByYourself Financial Platform

Test the workflow engine directly without going through the API.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.workflow_engine_minimal import MinimalWorkflowEngine
from core.workflow_minimal import (
    WorkflowContext,
    WorkflowDefinition,
    WorkflowStep,
    WorkflowStepType,
)
from workflows.allocation_framework_steps import AllocationFrameworkSteps


def test_workflow_engine_direct():
    """Test the workflow engine directly."""
    print("=" * 60)
    print("DIRECT WORKFLOW ENGINE TEST")
    print("=" * 60)

    # Test 1: Create workflow engine
    print("\n1. Testing Workflow Engine Creation...")
    try:
        engine = MinimalWorkflowEngine()
        print("✅ Workflow Engine: PASSED - Engine created successfully")
    except Exception as e:
        print(f"❌ Workflow Engine: FAILED - {e}")
        return

    # Test 2: Get workflow definition
    print("\n2. Testing Workflow Definition...")
    try:
        workflow_def = AllocationFrameworkSteps.get_portfolio_creation_workflow()
        print(f"✅ Workflow Definition: PASSED - Got workflow: {workflow_def.name}")
        print(f"   Steps: {len(workflow_def.steps)}")
        print(f"   Entry points: {workflow_def.entry_points}")
        print(f"   Exit points: {workflow_def.exit_points}")
    except Exception as e:
        print(f"❌ Workflow Definition: FAILED - {e}")
        return

    # Test 3: Create workflow context
    print("\n3. Testing Workflow Context...")
    try:
        context = WorkflowContext(
            user_id="test_user_123",
            session_id="test_session_456",
            data={"risk_tolerance": "medium", "investment_goals": "growth"},
            created_at=None,
        )
        print("✅ Workflow Context: PASSED - Context created successfully")
    except Exception as e:
        print(f"❌ Workflow Context: FAILED - {e}")
        return

    # Test 4: Execute workflow
    print("\n4. Testing Workflow Execution...")
    try:
        results = engine.execute_workflow(workflow_def, context)
        print("✅ Workflow Execution: PASSED - Workflow executed successfully")
        print(f"   Results: {len(results)} steps completed")
        for step_id, result in results.items():
            print(f"   - {step_id}: {result.get('status', 'unknown')}")
    except Exception as e:
        print(f"❌ Workflow Execution: FAILED - {e}")
        return

    # Test 5: Execute single step
    print("\n5. Testing Single Step Execution...")
    try:
        step_result = engine.execute_step(
            workflow_def, workflow_def.entry_points[0], context, {}
        )
        print("✅ Single Step Execution: PASSED - Step executed successfully")
        print(f"   Step result: {step_result.get('status', 'unknown')}")
    except Exception as e:
        print(f"❌ Single Step Execution: FAILED - {e}")
        return

    print("\n" + "=" * 60)
    print("DIRECT WORKFLOW ENGINE TEST COMPLETED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    test_workflow_engine_direct()
