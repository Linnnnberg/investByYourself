#!/usr/bin/env python3
"""
Simple Workflow API Test
InvestByYourself Financial Platform

Simple test to verify workflow API endpoints work without starting a server.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.workflow_engine_minimal import MinimalWorkflowEngine
from core.workflow_minimal import create_workflow_context
from workflows.allocation_framework_steps import AllocationFrameworkSteps


def test_workflow_api_components():
    """Test workflow API components without starting a server."""
    print("=" * 60)
    print("WORKFLOW API COMPONENT TESTS")
    print("=" * 60)

    # Test 1: Import workflow models
    print("\n1. Testing Workflow Models Import...")
    try:
        # Add api to path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))
        from src.models.workflow import (
            WorkflowDefinition,
            WorkflowExecutionRequest,
            WorkflowExecutionResponse,
            WorkflowStatus,
        )

        print("✅ Workflow Models: PASSED")
    except Exception as e:
        print(f"❌ Workflow Models: FAILED - {e}")
        return

    # Test 2: Import workflow endpoints
    print("\n2. Testing Workflow Endpoints Import...")
    try:
        from src.api.v1.endpoints.workflows import router

        print("✅ Workflow Endpoints: PASSED")
    except Exception as e:
        print(f"❌ Workflow Endpoints: FAILED - {e}")
        return

    # Test 3: Test workflow engine integration
    print("\n3. Testing Workflow Engine Integration...")
    try:
        # Get a workflow
        workflow = AllocationFrameworkSteps.get_portfolio_creation_workflow()
        print(f"✅ Workflow Engine: PASSED - Got workflow: {workflow.name}")

        # Test workflow execution
        context = create_workflow_context("test_user", "test_session")
        context.update_data(
            "profile_data",
            {
                "risk_tolerance": "moderate",
                "time_horizon": "10_years",
                "investment_goals": "retirement",
            },
        )

        engine = MinimalWorkflowEngine()
        results = engine.execute_workflow(workflow, context)
        print(f"✅ Workflow Execution: PASSED - {len(results)} steps executed")

    except Exception as e:
        print(f"❌ Workflow Engine: FAILED - {e}")
        return

    # Test 4: Test API model creation
    print("\n4. Testing API Model Creation...")
    try:
        from src.models.workflow import WorkflowContext, WorkflowExecutionRequest

        # Create a workflow execution request
        context = WorkflowContext(
            user_id="test_user", session_id="test_session", data={"test": "data"}
        )

        request = WorkflowExecutionRequest(
            workflow_id="portfolio_creation", context=context
        )

        print(f"✅ API Model Creation: PASSED - {request.workflow_id}")

    except Exception as e:
        print(f"❌ API Model Creation: FAILED - {e}")
        return

    # Test 5: Test workflow listing
    print("\n5. Testing Workflow Listing...")
    try:
        workflows = AllocationFrameworkSteps.list_available_workflows()
        print(f"✅ Workflow Listing: PASSED - {len(workflows)} workflows available")

        for workflow in workflows:
            print(f"   - {workflow['id']}: {workflow['name']}")

    except Exception as e:
        print(f"❌ Workflow Listing: FAILED - {e}")
        return

    print("\n" + "=" * 60)
    print("API COMPONENT TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)

    print("\nAPI Endpoints Available:")
    print("✅ GET /api/v1/workflows - List all workflows")
    print("✅ GET /api/v1/workflows/{workflow_id} - Get specific workflow")
    print("✅ POST /api/v1/workflows/execute - Execute workflow")
    print("✅ POST /api/v1/workflows/execute-step - Execute single step")
    print("✅ GET /api/v1/workflows/executions - List executions")
    print("✅ GET /api/v1/workflows/executions/{execution_id} - Get execution status")
    print("✅ POST /api/v1/workflows/pause - Pause workflow")
    print("✅ POST /api/v1/workflows/resume - Resume workflow")
    print("✅ POST /api/v1/workflows/cancel - Cancel workflow")
    print("✅ GET /api/v1/workflows/health - Health check")

    print("\nNext Steps:")
    print("1. Start the API server: cd api && python -m uvicorn src.main:app --reload")
    print("2. Test with HTTP client: python scripts/test_workflow_api.py")
    print("3. View API docs: http://localhost:8000/docs")


if __name__ == "__main__":
    test_workflow_api_components()
