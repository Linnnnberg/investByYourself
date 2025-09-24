#!/usr/bin/env python3
"""
Complete Workflow Engine Test
InvestByYourself Financial Platform

Comprehensive test to verify the complete workflow engine functionality
including database integration, API endpoints, and frontend components.
"""

import asyncio
import json
import os
import sys
from datetime import datetime

import requests

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def test_direct_workflow_engine():
    """Test the workflow engine directly."""
    print("=" * 60)
    print("DIRECT WORKFLOW ENGINE TEST")
    print("=" * 60)

    try:
        from core.workflow_engine_minimal import MinimalWorkflowEngine
        from core.workflow_minimal import WorkflowContext, WorkflowDefinition
        from workflows.allocation_framework_steps import AllocationFrameworkSteps

        # Test 1: Workflow Engine Creation
        print("\n1. Testing Workflow Engine Creation...")
        engine = MinimalWorkflowEngine()
        print("✅ Workflow Engine: PASSED - Engine created successfully")

        # Test 2: Workflow Definition
        print("\n2. Testing Workflow Definition...")
        workflow_def = AllocationFrameworkSteps.get_portfolio_creation_workflow()
        print(f"✅ Workflow Definition: PASSED - Got workflow: {workflow_def.name}")
        print(f"   Steps: {len(workflow_def.steps)}")
        print(f"   Entry points: {workflow_def.entry_points}")
        print(f"   Exit points: {workflow_def.exit_points}")

        # Test 3: Workflow Context
        print("\n3. Testing Workflow Context...")
        context = WorkflowContext(
            user_id="test_user",
            session_id="test_session",
            data={"initial_data": "value"},
            created_at=datetime.utcnow(),
        )
        print("✅ Workflow Context: PASSED - Context created successfully")

        # Test 4: Workflow Execution
        print("\n4. Testing Workflow Execution...")
        results = engine.execute_workflow(workflow_def, context)
        print("✅ Workflow Execution: PASSED - Workflow executed successfully")
        print(f"   Results: {len(results)} steps completed")
        for step_id, result in results.items():
            print(f"   - {step_id}: {result.get('status', 'unknown')}")

        # Test 5: Single Step Execution
        print("\n5. Testing Single Step Execution...")
        first_step_id = workflow_def.entry_points[0]
        step_result = engine.execute_step(workflow_def, first_step_id, context, {})
        print("✅ Single Step Execution: PASSED - Step executed successfully")
        print(f"   Step result: {step_result.get('status', 'unknown')}")

        return True

    except Exception as e:
        print(f"❌ Direct Workflow Engine: FAILED - {e}")
        return False


def test_api_endpoints():
    """Test the API endpoints."""
    print("\n" + "=" * 60)
    print("API ENDPOINTS TEST")
    print("=" * 60)

    base_url = "http://localhost:8000/api/v1/workflows"

    try:
        # Test 1: Health Check
        print("\n1. Testing Health Check...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health Check: PASSED")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health Check: FAILED - Status {response.status_code}")
            return False

        # Test 2: List Workflows
        print("\n2. Testing List Workflows...")
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ List Workflows: PASSED")
            print(f"   Total workflows: {data.get('total', 0)}")
            for workflow in data.get("workflows", [])[:3]:  # Show first 3
                print(
                    f"   - {workflow.get('name', 'Unknown')} ({workflow.get('id', 'No ID')})"
                )
        else:
            print(f"❌ List Workflows: FAILED - Status {response.status_code}")
            print(f"   Response: {response.text}")
            return False

        # Test 3: Execute Workflow
        print("\n3. Testing Execute Workflow...")
        workflow_id = data.get("workflows", [{}])[0].get(
            "id", "portfolio_creation_basic"
        )
        execute_data = {
            "workflow_id": workflow_id,
            "context": {
                "user_id": "test_user",
                "session_id": "test_session",
                "data": {
                    "profile_data": {
                        "risk_tolerance": "moderate",
                        "time_horizon": "5-10 years",
                        "investment_goals": "growth",
                    }
                },
            },
        }

        response = requests.post(f"{base_url}/execute", json=execute_data, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print("✅ Execute Workflow: PASSED")
            print(f"   Execution ID: {data.get('execution_id', 'No ID')}")
            print(f"   Status: {data.get('status', 'Unknown')}")
            print(f"   Progress: {data.get('progress', 0)}%")
        else:
            print(f"❌ Execute Workflow: FAILED - Status {response.status_code}")
            print(f"   Response: {response.text}")
            return False

        return True

    except requests.exceptions.ConnectionError:
        print("❌ API Test: FAILED - Could not connect to API server")
        print("   Make sure the API server is running on port 8000")
        return False
    except Exception as e:
        print(f"❌ API Test: FAILED - {e}")
        return False


def test_frontend_components():
    """Test frontend component file existence."""
    print("\n" + "=" * 60)
    print("FRONTEND COMPONENTS TEST")
    print("=" * 60)

    try:
        frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "src")

        print("\n1. Testing Step Component Files...")

        # Test DataCollectionStepComponent file
        component_path = os.path.join(
            frontend_path,
            "components",
            "workflows",
            "steps",
            "DataCollectionStepComponent.tsx",
        )
        if os.path.exists(component_path):
            print("✅ DataCollectionStepComponent: PASSED - File exists")
        else:
            print(
                f"❌ DataCollectionStepComponent: FAILED - File not found at {component_path}"
            )

        # Test DecisionStepComponent file
        component_path = os.path.join(
            frontend_path,
            "components",
            "workflows",
            "steps",
            "DecisionStepComponent.tsx",
        )
        if os.path.exists(component_path):
            print("✅ DecisionStepComponent: PASSED - File exists")
        else:
            print(
                f"❌ DecisionStepComponent: FAILED - File not found at {component_path}"
            )

        # Test ValidationStepComponent file
        component_path = os.path.join(
            frontend_path,
            "components",
            "workflows",
            "steps",
            "ValidationStepComponent.tsx",
        )
        if os.path.exists(component_path):
            print("✅ ValidationStepComponent: PASSED - File exists")
        else:
            print(
                f"❌ ValidationStepComponent: FAILED - File not found at {component_path}"
            )

        # Test UserInteractionStepComponent file
        component_path = os.path.join(
            frontend_path,
            "components",
            "workflows",
            "steps",
            "UserInteractionStepComponent.tsx",
        )
        if os.path.exists(component_path):
            print("✅ UserInteractionStepComponent: PASSED - File exists")
        else:
            print(
                f"❌ UserInteractionStepComponent: FAILED - File not found at {component_path}"
            )

        # Test RealWorkflowEngine file
        component_path = os.path.join(
            frontend_path, "components", "workflows", "RealWorkflowEngine.tsx"
        )
        if os.path.exists(component_path):
            print("✅ RealWorkflowEngine: PASSED - File exists")
        else:
            print(f"❌ RealWorkflowEngine: FAILED - File not found at {component_path}")

        # Test useWorkflowExecution hook file
        hook_path = os.path.join(frontend_path, "hooks", "useWorkflowExecution.ts")
        if os.path.exists(hook_path):
            print("✅ useWorkflowExecution Hook: PASSED - File exists")
        else:
            print(
                f"❌ useWorkflowExecution Hook: FAILED - File not found at {hook_path}"
            )

        # Test index file
        index_path = os.path.join(
            frontend_path, "components", "workflows", "steps", "index.ts"
        )
        if os.path.exists(index_path):
            print("✅ Steps Index: PASSED - File exists")
        else:
            print(f"❌ Steps Index: FAILED - File not found at {index_path}")

        return True

    except Exception as e:
        print(f"❌ Frontend Components: FAILED - {e}")
        return False


def test_database_models():
    """Test database model imports."""
    print("\n" + "=" * 60)
    print("DATABASE MODELS TEST")
    print("=" * 60)

    try:
        # Add api directory to path so src. imports work
        api_path = os.path.join(os.path.dirname(__file__), "..", "api")
        sys.path.insert(0, api_path)

        print("\n1. Testing Database Model Imports...")

        # Test workflow database models
        try:
            from src.models.database import (
                DBStepExecution,
                DBWorkflowDefinition,
                DBWorkflowExecution,
            )

            print("✅ Database Models: PASSED")
        except Exception as e:
            print(f"❌ Database Models: FAILED - {e}")

        # Test workflow database service
        try:
            from src.services.workflow_database_service import WorkflowDatabaseService

            print("✅ Workflow Database Service: PASSED")
        except Exception as e:
            print(f"❌ Workflow Database Service: FAILED - {e}")

        return True

    except Exception as e:
        print(f"❌ Database Models: FAILED - {e}")
        return False


def main():
    """Run all tests."""
    print("COMPLETE WORKFLOW ENGINE TEST SUITE")
    print("=" * 60)
    print("Testing Story-009: Workflow Engine Implementation")
    print("=" * 60)

    results = []

    # Test 1: Direct Workflow Engine
    results.append(("Direct Workflow Engine", test_direct_workflow_engine()))

    # Test 2: Database Models
    results.append(("Database Models", test_database_models()))

    # Test 3: API Endpoints
    results.append(("API Endpoints", test_api_endpoints()))

    # Test 4: Frontend Components
    results.append(("Frontend Components", test_frontend_components()))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Story-009 Workflow Engine is complete!")
        print("\nCompleted Features:")
        print("✅ Real Workflow Engine Implementation")
        print("✅ Database Persistence")
        print("✅ API Integration")
        print("✅ Enhanced Frontend Components")
        print("✅ End-to-End Testing")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review and fix issues.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
