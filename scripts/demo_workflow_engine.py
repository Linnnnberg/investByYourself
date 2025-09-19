#!/usr/bin/env python3
"""
Workflow Engine Demo Script
InvestByYourself Financial Platform

Demonstrates the minimal workflow engine functionality for allocation framework.
"""

import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.workflow_engine_minimal import MinimalWorkflowEngine
from core.workflow_minimal import create_workflow_context
from workflows.allocation_framework_steps import AllocationFrameworkSteps


def demo_portfolio_creation_workflow():
    """Demo the portfolio creation workflow."""
    print("=" * 60)
    print("PORTFOLIO CREATION WORKFLOW DEMO")
    print("=" * 60)

    # Get the portfolio creation workflow
    workflow = AllocationFrameworkSteps.get_portfolio_creation_workflow()
    print(f"Workflow: {workflow.name}")
    print(f"Description: {workflow.description}")
    print(f"Steps: {len(workflow.steps)}")
    print()

    # Create workflow context
    context = create_workflow_context("demo_user", "demo_session")

    # Add some mock user data
    context.update_data(
        "profile_data",
        {
            "risk_tolerance": "moderate",
            "time_horizon": "10_years",
            "investment_goals": "retirement",
        },
    )
    context.update_data("user_choice", "framework")  # Choose framework allocation
    context.update_data(
        "user_input",
        {
            "selected_products": ["VTI", "BND", "VXUS"],
            "weights": {"VTI": 0.6, "BND": 0.3, "VXUS": 0.1},
        },
    )
    context.update_data("total_weight", 1.0)
    context.update_data("positions", ["VTI", "BND", "VXUS"])
    context.update_data("constraints", {"max_single_position": 0.5})

    # Execute workflow
    engine = MinimalWorkflowEngine()

    print("Executing workflow...")
    print("-" * 40)

    try:
        results = engine.execute_workflow(workflow, context)

        print("Workflow completed successfully!")
        print()
        print("Results:")
        print("-" * 20)

        for step_id, result in results.items():
            print(f"Step: {step_id}")
            print(f"  Status: {result.get('status', 'unknown')}")
            print(f"  Type: {result.get('step_type', 'unknown')}")
            if "decision" in result:
                print(f"  Decision: {result['decision']}")
            if "collected_data" in result:
                print(f"  Collected: {list(result['collected_data'].keys())}")
            if "validation_results" in result:
                print(f"  Validation: {result['all_passed']}")
            print()

    except Exception as e:
        print(f"Workflow execution failed: {e}")


def demo_framework_builder_workflow():
    """Demo the framework builder workflow."""
    print("=" * 60)
    print("FRAMEWORK BUILDER WORKFLOW DEMO")
    print("=" * 60)

    # Get the framework builder workflow
    workflow = AllocationFrameworkSteps.get_framework_builder_workflow()
    print(f"Workflow: {workflow.name}")
    print(f"Description: {workflow.description}")
    print(f"Steps: {len(workflow.steps)}")
    print()

    # Create workflow context
    context = create_workflow_context("demo_user", "demo_session_2")

    # Add mock user data for framework building
    context.update_data("user_choice", "asset_class")  # Choose asset class framework
    context.update_data(
        "user_input",
        {
            "buckets": [
                {"name": "Equity", "weight": 0.6},
                {"name": "Bonds", "weight": 0.3},
                {"name": "Alternatives", "weight": 0.1},
            ],
            "constraints": {
                "min_equity": 0.4,
                "max_equity": 0.8,
                "rebalancing_band": 0.05,
            },
        },
    )
    context.update_data("total_weight", 1.0)

    # Execute workflow
    engine = MinimalWorkflowEngine()

    print("Executing framework builder workflow...")
    print("-" * 40)

    try:
        results = engine.execute_workflow(workflow, context)

        print("Framework builder workflow completed successfully!")
        print()
        print("Results:")
        print("-" * 20)

        for step_id, result in results.items():
            print(f"Step: {step_id}")
            print(f"  Status: {result.get('status', 'unknown')}")
            print(f"  Type: {result.get('step_type', 'unknown')}")
            if "decision" in result:
                print(f"  Decision: {result['decision']}")
            if "user_input" in result:
                print(f"  User Input: {list(result['user_input'].keys())}")
            if "validation_results" in result:
                print(f"  Validation: {result['all_passed']}")
            print()

    except Exception as e:
        print(f"Framework builder workflow execution failed: {e}")


def demo_workflow_templates():
    """Demo available workflow templates."""
    print("=" * 60)
    print("AVAILABLE WORKFLOW TEMPLATES")
    print("=" * 60)

    # List available workflows
    workflows = AllocationFrameworkSteps.list_available_workflows()

    for workflow in workflows:
        print(f"ID: {workflow['id']}")
        print(f"Name: {workflow['name']}")
        print(f"Description: {workflow['description']}")
        print(f"Steps: {workflow['step_count']}")
        print(f"Entry Points: {workflow['entry_points']}")
        print(f"Exit Points: {workflow['exit_points']}")
        print("-" * 40)

    print(f"Total workflows available: {len(workflows)}")


def demo_step_execution():
    """Demo individual step execution."""
    print("=" * 60)
    print("INDIVIDUAL STEP EXECUTION DEMO")
    print("=" * 60)

    # Get a workflow
    workflow = AllocationFrameworkSteps.get_portfolio_creation_workflow()

    # Create context
    context = create_workflow_context("demo_user", "demo_session_3")
    context.update_data("profile_data", {"risk_tolerance": "aggressive"})

    # Execute individual steps
    engine = MinimalWorkflowEngine()

    print("Executing individual steps...")
    print("-" * 40)

    # Execute first step (profile assessment)
    try:
        result1 = engine.execute_step(workflow, "profile_assessment", context)
        print("Step 1 (Profile Assessment):")
        print(f"  Status: {result1['status']}")
        print(f"  Collected Data: {list(result1['collected_data'].keys())}")
        print()

        # Execute second step (allocation method choice)
        context.update_data("user_choice", "manual")
        result2 = engine.execute_step(
            workflow,
            "allocation_method_choice",
            context,
            {"profile_assessment": result1},
        )
        print("Step 2 (Allocation Method Choice):")
        print(f"  Status: {result2['status']}")
        print(f"  Decision: {result2['decision']}")
        print()

    except Exception as e:
        print(f"Step execution failed: {e}")


def main():
    """Main demo function."""
    print("INVESTBYYOURSELF WORKFLOW ENGINE DEMO")
    print("=" * 60)
    print(f"Demo started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Demo 1: Portfolio Creation Workflow
    demo_portfolio_creation_workflow()
    print()

    # Demo 2: Framework Builder Workflow
    demo_framework_builder_workflow()
    print()

    # Demo 3: Available Templates
    demo_workflow_templates()
    print()

    # Demo 4: Individual Step Execution
    demo_step_execution()
    print()

    print("=" * 60)
    print("DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print("Next Steps:")
    print("1. Integrate with frontend React components")
    print("2. Add API endpoints for workflow execution")
    print("3. Connect with allocation framework system")
    print("4. Add database persistence for workflow executions")


if __name__ == "__main__":
    main()
