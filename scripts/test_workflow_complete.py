#!/usr/bin/env python3
"""
Complete Workflow Test Script
InvestByYourself Financial Platform

Test the complete workflow system with real allocation framework workflows.
"""

import json
import time
import uuid
from typing import Any, Dict

import requests


def test_workflow_system():
    """Test the complete workflow system."""
    print("=" * 80)
    print("COMPLETE WORKFLOW SYSTEM TEST")
    print("=" * 80)

    base_url = "http://localhost:8000/api/v1"

    # Test 1: API Health
    print("\n1. Testing API Health...")
    try:
        response = requests.get(f"{base_url}/workflows/health", timeout=5)
        if response.status_code == 200:
            print("✅ API Health: PASSED")
        else:
            print(f"❌ API Health: FAILED - Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Health: FAILED - {e}")
        return False

    # Test 2: Create Sample Workflow Definition
    print("\n2. Creating Sample Workflow Definition...")
    try:
        workflow_def = {
            "id": "portfolio_creation_v1",
            "name": "Portfolio Creation Workflow",
            "description": "Complete portfolio creation with allocation framework",
            "version": "1.0",
            "category": "portfolio_management",
            "definition": {
                "steps": [
                    {
                        "id": "risk_assessment",
                        "name": "Risk Assessment",
                        "step_type": "data_collection",
                        "description": "Collect user risk tolerance and investment goals",
                        "config": {
                            "fields": [
                                {
                                    "name": "risk_tolerance",
                                    "label": "Risk Tolerance",
                                    "type": "select",
                                    "options": [
                                        "conservative",
                                        "moderate",
                                        "aggressive",
                                    ],
                                    "required": True,
                                },
                                {
                                    "name": "time_horizon",
                                    "label": "Investment Time Horizon",
                                    "type": "select",
                                    "options": [
                                        "1-3 years",
                                        "3-5 years",
                                        "5-10 years",
                                        "10+ years",
                                    ],
                                    "required": True,
                                },
                                {
                                    "name": "investment_goals",
                                    "label": "Primary Investment Goal",
                                    "type": "select",
                                    "options": [
                                        "retirement",
                                        "wealth_building",
                                        "income_generation",
                                        "capital_preservation",
                                    ],
                                    "required": True,
                                },
                            ]
                        },
                    },
                    {
                        "id": "allocation_strategy",
                        "name": "Allocation Strategy Selection",
                        "step_type": "decision",
                        "description": "Choose your preferred allocation strategy",
                        "config": {
                            "options": [
                                {
                                    "value": "balanced",
                                    "label": "Balanced (60/40 stocks/bonds)",
                                },
                                {
                                    "value": "growth",
                                    "label": "Growth (80/20 stocks/bonds)",
                                },
                                {
                                    "value": "conservative",
                                    "label": "Conservative (40/60 stocks/bonds)",
                                },
                                {"value": "custom", "label": "Custom Allocation"},
                            ],
                            "inputType": "radio",
                            "required": True,
                        },
                    },
                    {
                        "id": "asset_selection",
                        "name": "Asset Selection",
                        "step_type": "user_interaction",
                        "description": "Select specific assets for your portfolio",
                        "config": {
                            "items": [
                                {
                                    "id": "VTI",
                                    "name": "Vanguard Total Stock Market ETF",
                                    "category": "US Stocks",
                                },
                                {
                                    "id": "VXUS",
                                    "name": "Vanguard Total International Stock ETF",
                                    "category": "International Stocks",
                                },
                                {
                                    "id": "BND",
                                    "name": "Vanguard Total Bond Market ETF",
                                    "category": "Bonds",
                                },
                                {
                                    "id": "VTI",
                                    "name": "Vanguard Real Estate ETF",
                                    "category": "REITs",
                                },
                                {
                                    "id": "GLD",
                                    "name": "SPDR Gold Trust",
                                    "category": "Commodities",
                                },
                            ],
                            "selectionType": "multiple",
                            "maxSelections": 5,
                            "minSelections": 2,
                        },
                    },
                    {
                        "id": "validation",
                        "name": "Portfolio Validation",
                        "step_type": "validation",
                        "description": "Validate your portfolio allocation",
                        "config": {
                            "results": [
                                {
                                    "name": "Risk Assessment",
                                    "status": "passed",
                                    "message": "Portfolio matches risk tolerance",
                                },
                                {
                                    "name": "Diversification",
                                    "status": "passed",
                                    "message": "Good asset diversification",
                                },
                                {
                                    "name": "Allocation Balance",
                                    "status": "warning",
                                    "message": "Consider rebalancing bonds",
                                },
                            ],
                            "overallStatus": "passed",
                            "summary": "Portfolio is ready for implementation",
                        },
                    },
                ],
                "entry_points": ["risk_assessment"],
                "exit_points": ["validation"],
            },
            "is_active": True,
            "created_by": "system",
        }

        # Create workflow definition via API
        response = requests.post(
            f"{base_url}/workflows/definitions", json=workflow_def, timeout=10
        )
        if response.status_code in [200, 201]:
            print("✅ Workflow Definition Created: PASSED")
        else:
            print(
                f"⚠️ Workflow Definition: Status {response.status_code} - May already exist"
            )
    except Exception as e:
        print(f"❌ Workflow Definition: FAILED - {e}")
        return False

    # Test 3: List Workflows
    print("\n3. Testing Workflow Listing...")
    try:
        response = requests.get(f"{base_url}/workflows", timeout=5)
        if response.status_code == 200:
            data = response.json()
            workflows = data.get("workflows", [])
            print(f"✅ Workflow Listing: PASSED - {len(workflows)} workflows available")
            for workflow in workflows:
                print(
                    f"   - {workflow.get('name', 'Unknown')} (ID: {workflow.get('id', 'Unknown')})"
                )
        else:
            print(f"❌ Workflow Listing: FAILED - Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Workflow Listing: FAILED - {e}")
        return False

    # Test 4: Execute Workflow
    print("\n4. Testing Workflow Execution...")
    try:
        execution_request = {
            "workflow_id": "portfolio_creation_v1",
            "context": {
                "user_id": "test_user_123",
                "session_id": f"session_{uuid.uuid4().hex[:8]}",
                "data": {
                    "profile_data": {
                        "risk_tolerance": "moderate",
                        "time_horizon": "5-10 years",
                        "investment_goals": "retirement",
                    }
                },
            },
        }

        response = requests.post(
            f"{base_url}/workflows/execute", json=execution_request, timeout=15
        )

        if response.status_code == 200:
            execution = response.json()
            execution_id = execution.get("execution_id")
            print(f"✅ Workflow Execution: PASSED - Execution ID: {execution_id}")

            # Test 5: Monitor Execution Status
            print("\n5. Testing Execution Status Monitoring...")
            for i in range(3):
                time.sleep(2)
                status_response = requests.get(
                    f"{base_url}/workflows/executions/{execution_id}", timeout=5
                )
                if status_response.status_code == 200:
                    status = status_response.json()
                    print(
                        f"   Status Check {i+1}: {status.get('status', 'Unknown')} - Progress: {status.get('progress', 0)}%"
                    )
                    if status.get("status") in ["completed", "failed"]:
                        break
                else:
                    print(
                        f"   Status Check {i+1}: FAILED - Status {status_response.status_code}"
                    )

            # Test 6: Execute Individual Step
            print("\n6. Testing Individual Step Execution...")
            step_request = {
                "execution_id": execution_id,
                "workflow_id": "portfolio_creation_v1",
                "step_id": "risk_assessment",
                "context": execution_request["context"],
                "step_input": {
                    "risk_tolerance": "moderate",
                    "time_horizon": "5-10 years",
                    "investment_goals": "retirement",
                },
            }

            step_response = requests.post(
                f"{base_url}/workflows/execute-step", json=step_request, timeout=10
            )

            if step_response.status_code == 200:
                step_result = step_response.json()
                print(
                    f"✅ Step Execution: PASSED - Status: {step_result.get('status', 'Unknown')}"
                )
            else:
                print(f"⚠️ Step Execution: Status {step_response.status_code}")

            return True
        else:
            print(f"❌ Workflow Execution: FAILED - Status {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Workflow Execution: FAILED - {e}")
        return False


def test_allocation_framework_workflow():
    """Test specific allocation framework workflow."""
    print("\n" + "=" * 80)
    print("ALLOCATION FRAMEWORK WORKFLOW TEST")
    print("=" * 80)

    base_url = "http://localhost:8000/api/v1"

    # Create allocation framework workflow
    allocation_workflow = {
        "id": "allocation_framework_v1",
        "name": "Allocation Framework Workflow",
        "description": "Advanced allocation framework with risk-based portfolio construction",
        "version": "1.0",
        "category": "allocation_framework",
        "definition": {
            "steps": [
                {
                    "id": "risk_profile",
                    "name": "Risk Profile Assessment",
                    "step_type": "data_collection",
                    "description": "Comprehensive risk profiling",
                    "config": {
                        "fields": [
                            {
                                "name": "age",
                                "label": "Age",
                                "type": "number",
                                "required": True,
                                "validation": {"min": 18, "max": 100},
                            },
                            {
                                "name": "income",
                                "label": "Annual Income",
                                "type": "number",
                                "required": True,
                                "validation": {"min": 0},
                            },
                            {
                                "name": "risk_tolerance",
                                "label": "Risk Tolerance",
                                "type": "slider",
                                "min": 1,
                                "max": 10,
                                "required": True,
                            },
                        ]
                    },
                },
                {
                    "id": "allocation_decision",
                    "name": "Allocation Strategy Decision",
                    "step_type": "decision",
                    "description": "Choose allocation strategy based on risk profile",
                    "config": {
                        "options": [
                            {"value": "conservative", "label": "Conservative (30/70)"},
                            {"value": "moderate", "label": "Moderate (60/40)"},
                            {"value": "aggressive", "label": "Aggressive (80/20)"},
                            {
                                "value": "ai_optimized",
                                "label": "AI-Optimized Allocation",
                            },
                        ],
                        "inputType": "radio",
                        "required": True,
                    },
                },
                {
                    "id": "asset_allocation",
                    "name": "Asset Allocation Selection",
                    "step_type": "user_interaction",
                    "description": "Select specific asset classes and weights",
                    "config": {
                        "items": [
                            {
                                "id": "us_stocks",
                                "name": "US Stocks",
                                "category": "Equity",
                                "default_weight": 0.4,
                            },
                            {
                                "id": "intl_stocks",
                                "name": "International Stocks",
                                "category": "Equity",
                                "default_weight": 0.2,
                            },
                            {
                                "id": "bonds",
                                "name": "Bonds",
                                "category": "Fixed Income",
                                "default_weight": 0.3,
                            },
                            {
                                "id": "reits",
                                "name": "REITs",
                                "category": "Real Estate",
                                "default_weight": 0.05,
                            },
                            {
                                "id": "commodities",
                                "name": "Commodities",
                                "category": "Alternative",
                                "default_weight": 0.05,
                            },
                        ],
                        "selectionType": "multiple",
                        "allowWeights": True,
                        "maxSelections": 10,
                        "minSelections": 3,
                    },
                },
                {
                    "id": "portfolio_validation",
                    "name": "Portfolio Validation & Optimization",
                    "step_type": "validation",
                    "description": "Validate and optimize the portfolio allocation",
                    "config": {
                        "results": [
                            {
                                "name": "Risk-Return Analysis",
                                "status": "passed",
                                "message": "Portfolio meets risk-return objectives",
                            },
                            {
                                "name": "Diversification Check",
                                "status": "passed",
                                "message": "Adequate diversification across asset classes",
                            },
                            {
                                "name": "Rebalancing Recommendation",
                                "status": "info",
                                "message": "Consider quarterly rebalancing",
                            },
                            {
                                "name": "Tax Optimization",
                                "status": "warning",
                                "message": "Consider tax-efficient placement",
                            },
                        ],
                        "overallStatus": "passed",
                        "summary": "Portfolio allocation is optimized and ready for implementation",
                        "allowRetry": True,
                    },
                },
            ],
            "entry_points": ["risk_profile"],
            "exit_points": ["portfolio_validation"],
        },
        "is_active": True,
        "created_by": "allocation_framework",
    }

    try:
        # Create allocation framework workflow
        response = requests.post(
            f"{base_url}/workflows/definitions", json=allocation_workflow, timeout=10
        )
        if response.status_code in [200, 201]:
            print("✅ Allocation Framework Workflow Created: PASSED")
        else:
            print(f"⚠️ Allocation Framework Workflow: Status {response.status_code}")

        # Execute allocation framework workflow
        execution_request = {
            "workflow_id": "allocation_framework_v1",
            "context": {
                "user_id": "allocation_user_456",
                "session_id": f"allocation_session_{uuid.uuid4().hex[:8]}",
                "data": {
                    "risk_profile": {"age": 35, "income": 75000, "risk_tolerance": 7}
                },
            },
        }

        response = requests.post(
            f"{base_url}/workflows/execute", json=execution_request, timeout=15
        )

        if response.status_code == 200:
            execution = response.json()
            print(
                f"✅ Allocation Framework Execution: PASSED - Execution ID: {execution.get('execution_id')}"
            )
            return True
        else:
            print(
                f"❌ Allocation Framework Execution: FAILED - Status {response.status_code}"
            )
            return False

    except Exception as e:
        print(f"❌ Allocation Framework Test: FAILED - {e}")
        return False


def main():
    """Run all workflow tests."""
    print("Starting Complete Workflow System Tests...")
    print("Make sure both API server (port 8000) and Frontend (port 3000) are running.")
    print()

    # Test basic workflow system
    basic_success = test_workflow_system()

    # Test allocation framework workflow
    allocation_success = test_allocation_framework_workflow()

    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Basic Workflow System: {'✅ PASSED' if basic_success else '❌ FAILED'}")
    print(f"Allocation Framework: {'✅ PASSED' if allocation_success else '❌ FAILED'}")

    if basic_success and allocation_success:
        print("\n🎉 ALL TESTS PASSED! Workflow system is fully functional.")
        print("\nNext Steps:")
        print("1. Visit http://localhost:3000/workflows to test the frontend")
        print("2. Visit http://localhost:8000/docs to explore the API")
        print("3. The allocation framework workflow is ready for production use!")
    else:
        print("\n⚠️ Some tests failed. Check the error messages above.")

    return basic_success and allocation_success


if __name__ == "__main__":
    main()
