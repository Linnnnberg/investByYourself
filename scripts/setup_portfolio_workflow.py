#!/usr/bin/env python3
"""
Portfolio Creation Workflow Setup
InvestByYourself Financial Platform

Sets up a complete portfolio creation workflow with allocation framework integration.
"""

import json
import time
from typing import Any, Dict, List

import requests


def create_portfolio_workflow():
    """Create a comprehensive portfolio creation workflow."""

    base_url = "http://localhost:8000/api/v1"

    # Comprehensive Portfolio Creation Workflow
    portfolio_workflow = {
        "id": "comprehensive_portfolio_creation",
        "name": "Comprehensive Portfolio Creation",
        "description": "Complete portfolio creation workflow with risk assessment, allocation strategy, and implementation",
        "version": "1.0",
        "category": "portfolio_creation",
        "definition": {
            "steps": [
                {
                    "id": "welcome",
                    "name": "Welcome & Introduction",
                    "step_type": "user_interaction",
                    "description": "Welcome to the portfolio creation process. Let's build your personalized investment portfolio.",
                    "config": {
                        "items": [
                            {
                                "id": "understand_process",
                                "name": "I understand the portfolio creation process",
                                "description": "This will take 5-10 minutes and guide you through creating a personalized portfolio",
                            }
                        ],
                        "selectionType": "single",
                        "required": True,
                        "helpText": "This workflow will help you create a diversified portfolio based on your risk tolerance and investment goals.",
                    },
                },
                {
                    "id": "personal_info",
                    "name": "Personal Information",
                    "step_type": "data_collection",
                    "description": "Let's start with some basic information about you and your financial situation.",
                    "config": {
                        "fields": [
                            {
                                "name": "age",
                                "label": "Your Age",
                                "type": "number",
                                "required": True,
                                "validation": {"min": 18, "max": 100},
                                "helpText": "Your age helps determine appropriate risk levels and time horizons",
                            },
                            {
                                "name": "annual_income",
                                "label": "Annual Income",
                                "type": "number",
                                "required": True,
                                "validation": {"min": 0},
                                "helpText": "Your income level helps determine appropriate investment amounts",
                            },
                            {
                                "name": "investment_amount",
                                "label": "Amount to Invest",
                                "type": "number",
                                "required": True,
                                "validation": {"min": 100},
                                "helpText": "How much are you looking to invest today?",
                            },
                            {
                                "name": "monthly_contribution",
                                "label": "Monthly Contribution",
                                "type": "number",
                                "required": False,
                                "validation": {"min": 0},
                                "helpText": "How much can you contribute monthly? (Optional)",
                            },
                        ],
                        "progress": 20,
                    },
                },
                {
                    "id": "risk_assessment",
                    "name": "Risk Assessment",
                    "step_type": "data_collection",
                    "description": "Understanding your risk tolerance is crucial for building the right portfolio.",
                    "config": {
                        "fields": [
                            {
                                "name": "risk_tolerance",
                                "label": "Risk Tolerance",
                                "type": "slider",
                                "min": 1,
                                "max": 10,
                                "required": True,
                                "labels": {
                                    "1": "Very Conservative",
                                    "5": "Moderate",
                                    "10": "Very Aggressive",
                                },
                                "helpText": "Rate your comfort with investment risk (1 = very conservative, 10 = very aggressive)",
                            },
                            {
                                "name": "time_horizon",
                                "label": "Investment Time Horizon",
                                "type": "select",
                                "options": [
                                    {
                                        "value": "short",
                                        "label": "1-3 years (Short-term)",
                                    },
                                    {
                                        "value": "medium",
                                        "label": "3-7 years (Medium-term)",
                                    },
                                    {
                                        "value": "long",
                                        "label": "7-15 years (Long-term)",
                                    },
                                    {
                                        "value": "retirement",
                                        "label": "15+ years (Retirement)",
                                    },
                                ],
                                "required": True,
                                "helpText": "How long do you plan to invest before needing the money?",
                            },
                            {
                                "name": "investment_goals",
                                "label": "Primary Investment Goal",
                                "type": "select",
                                "options": [
                                    {
                                        "value": "retirement",
                                        "label": "Retirement Planning",
                                    },
                                    {
                                        "value": "wealth_building",
                                        "label": "Wealth Building",
                                    },
                                    {
                                        "value": "income_generation",
                                        "label": "Income Generation",
                                    },
                                    {
                                        "value": "capital_preservation",
                                        "label": "Capital Preservation",
                                    },
                                    {
                                        "value": "education",
                                        "label": "Education Funding",
                                    },
                                    {
                                        "value": "home_purchase",
                                        "label": "Home Purchase",
                                    },
                                ],
                                "required": True,
                                "helpText": "What is your primary reason for investing?",
                            },
                            {
                                "name": "market_volatility",
                                "label": "Market Volatility Comfort",
                                "type": "select",
                                "options": [
                                    {
                                        "value": "low",
                                        "label": "I prefer stable, predictable returns",
                                    },
                                    {
                                        "value": "medium",
                                        "label": "I can handle some ups and downs",
                                    },
                                    {
                                        "value": "high",
                                        "label": "I'm comfortable with market volatility",
                                    },
                                ],
                                "required": True,
                                "helpText": "How comfortable are you with market ups and downs?",
                            },
                        ],
                        "progress": 40,
                    },
                },
                {
                    "id": "allocation_strategy",
                    "name": "Allocation Strategy Selection",
                    "step_type": "decision",
                    "description": "Based on your risk profile, choose your preferred allocation strategy.",
                    "config": {
                        "options": [
                            {
                                "value": "conservative",
                                "label": "Conservative (30% Stocks, 70% Bonds)",
                                "description": "Lower risk, stable returns. Good for short-term goals or conservative investors.",
                            },
                            {
                                "value": "moderate",
                                "label": "Moderate (60% Stocks, 40% Bonds)",
                                "description": "Balanced approach. Good for medium-term goals and moderate risk tolerance.",
                            },
                            {
                                "value": "aggressive",
                                "label": "Aggressive (80% Stocks, 20% Bonds)",
                                "description": "Higher risk, higher potential returns. Good for long-term goals and higher risk tolerance.",
                            },
                            {
                                "value": "custom",
                                "label": "Custom Allocation",
                                "description": "Create your own allocation based on your specific needs and preferences.",
                            },
                        ],
                        "inputType": "radio",
                        "required": True,
                        "helpText": "Choose the allocation strategy that best matches your risk profile and goals.",
                    },
                },
                {
                    "id": "asset_selection",
                    "name": "Asset Selection",
                    "step_type": "user_interaction",
                    "description": "Select the specific assets for your portfolio. We'll recommend based on your allocation strategy.",
                    "config": {
                        "items": [
                            # US Stocks
                            {
                                "id": "VTI",
                                "name": "Vanguard Total Stock Market ETF",
                                "category": "US Stocks",
                                "expense_ratio": "0.03%",
                                "description": "Broad US stock market exposure",
                            },
                            {
                                "id": "SPY",
                                "name": "SPDR S&P 500 ETF",
                                "category": "US Stocks",
                                "expense_ratio": "0.09%",
                                "description": "Large-cap US stocks",
                            },
                            {
                                "id": "VEA",
                                "name": "Vanguard FTSE Developed Markets ETF",
                                "category": "US Stocks",
                                "expense_ratio": "0.05%",
                                "description": "International developed markets",
                            },
                            # International Stocks
                            {
                                "id": "VXUS",
                                "name": "Vanguard Total International Stock ETF",
                                "category": "International Stocks",
                                "expense_ratio": "0.08%",
                                "description": "Broad international stock exposure",
                            },
                            {
                                "id": "VWO",
                                "name": "Vanguard FTSE Emerging Markets ETF",
                                "category": "International Stocks",
                                "expense_ratio": "0.10%",
                                "description": "Emerging markets exposure",
                            },
                            # Bonds
                            {
                                "id": "BND",
                                "name": "Vanguard Total Bond Market ETF",
                                "category": "Bonds",
                                "expense_ratio": "0.03%",
                                "description": "Broad US bond market",
                            },
                            {
                                "id": "BNDX",
                                "name": "Vanguard Total International Bond ETF",
                                "category": "Bonds",
                                "expense_ratio": "0.08%",
                                "description": "International bonds",
                            },
                            {
                                "id": "TIP",
                                "name": "iShares TIPS Bond ETF",
                                "category": "Bonds",
                                "expense_ratio": "0.19%",
                                "description": "Inflation-protected bonds",
                            },
                            # REITs
                            {
                                "id": "VNQ",
                                "name": "Vanguard Real Estate ETF",
                                "category": "REITs",
                                "expense_ratio": "0.12%",
                                "description": "US real estate investment trusts",
                            },
                            # Commodities
                            {
                                "id": "GLD",
                                "name": "SPDR Gold Trust",
                                "category": "Commodities",
                                "expense_ratio": "0.40%",
                                "description": "Gold exposure",
                            },
                            {
                                "id": "DJP",
                                "name": "iPath Bloomberg Commodity Index ETN",
                                "category": "Commodities",
                                "expense_ratio": "0.75%",
                                "description": "Broad commodity exposure",
                            },
                        ],
                        "selectionType": "multiple",
                        "maxSelections": 8,
                        "minSelections": 3,
                        "searchEnabled": True,
                        "filters": [
                            {
                                "name": "category",
                                "label": "Category",
                                "type": "select",
                                "options": [
                                    "US Stocks",
                                    "International Stocks",
                                    "Bonds",
                                    "REITs",
                                    "Commodities",
                                ],
                            },
                            {
                                "name": "expense_ratio",
                                "label": "Max Expense Ratio",
                                "type": "range",
                                "min": 0,
                                "max": 1.0,
                                "step": 0.01,
                            },
                        ],
                        "helpText": "Select 3-8 assets for your portfolio. We recommend diversifying across different asset classes.",
                    },
                },
                {
                    "id": "allocation_weights",
                    "name": "Allocation Weights",
                    "step_type": "data_collection",
                    "description": "Set the allocation weights for your selected assets. Total must equal 100%.",
                    "config": {
                        "fields": [
                            {
                                "name": "allocation_weights",
                                "label": "Asset Allocation Weights",
                                "type": "allocation_sliders",
                                "required": True,
                                "helpText": "Adjust the allocation weights for each selected asset. Total must equal 100%.",
                                "validation": {
                                    "total_must_equal": 100,
                                    "min_weight": 1,
                                    "max_weight": 80,
                                },
                            }
                        ],
                        "progress": 80,
                    },
                },
                {
                    "id": "portfolio_validation",
                    "name": "Portfolio Validation & Analysis",
                    "step_type": "validation",
                    "description": "Let's validate your portfolio allocation and provide analysis.",
                    "config": {
                        "results": [
                            {
                                "name": "Diversification Analysis",
                                "status": "passed",
                                "message": "Portfolio shows good diversification across asset classes",
                                "details": "Your portfolio includes stocks, bonds, and alternative investments",
                            },
                            {
                                "name": "Risk Assessment",
                                "status": "passed",
                                "message": "Portfolio risk level matches your risk tolerance",
                                "details": "Based on your risk profile, this allocation is appropriate",
                            },
                            {
                                "name": "Expense Ratio Analysis",
                                "status": "info",
                                "message": "Average expense ratio: 0.12%",
                                "details": "Your portfolio has low-cost, efficient ETFs",
                            },
                            {
                                "name": "Rebalancing Recommendation",
                                "status": "info",
                                "message": "Consider rebalancing quarterly or annually",
                                "details": "Regular rebalancing helps maintain your target allocation",
                            },
                        ],
                        "overallStatus": "passed",
                        "summary": "Your portfolio is well-diversified and ready for implementation",
                        "allowRetry": True,
                        "showDetails": True,
                    },
                },
                {
                    "id": "implementation_plan",
                    "name": "Implementation Plan",
                    "step_type": "user_interaction",
                    "description": "Review your portfolio implementation plan and next steps.",
                    "config": {
                        "items": [
                            {
                                "id": "immediate_implementation",
                                "name": "Implement Portfolio Immediately",
                                "description": "Start investing with your selected allocation right away",
                            },
                            {
                                "id": "dollar_cost_averaging",
                                "name": "Dollar-Cost Averaging",
                                "description": "Invest gradually over 3-6 months to reduce market timing risk",
                            },
                            {
                                "id": "review_later",
                                "name": "Review and Implement Later",
                                "description": "Save this portfolio for later implementation",
                            },
                        ],
                        "selectionType": "single",
                        "required": True,
                        "helpText": "Choose how you'd like to implement your portfolio.",
                    },
                },
            ],
            "entry_points": ["welcome"],
            "exit_points": ["implementation_plan"],
        },
        "is_active": True,
        "created_by": "portfolio_creation_system",
    }

    return portfolio_workflow


def create_advanced_allocation_workflow():
    """Create an advanced allocation framework workflow."""

    advanced_workflow = {
        "id": "advanced_allocation_framework",
        "name": "Advanced Allocation Framework",
        "description": "Sophisticated allocation framework with factor-based investing and risk parity",
        "version": "1.0",
        "category": "allocation_framework",
        "definition": {
            "steps": [
                {
                    "id": "risk_parity_assessment",
                    "name": "Risk Parity Assessment",
                    "step_type": "data_collection",
                    "description": "Advanced risk assessment using risk parity principles",
                    "config": {
                        "fields": [
                            {
                                "name": "volatility_target",
                                "label": "Target Portfolio Volatility",
                                "type": "slider",
                                "min": 5,
                                "max": 25,
                                "required": True,
                                "labels": {
                                    "5": "5% (Conservative)",
                                    "15": "15% (Moderate)",
                                    "25": "25% (Aggressive)",
                                },
                            },
                            {
                                "name": "correlation_preference",
                                "label": "Asset Correlation Preference",
                                "type": "select",
                                "options": [
                                    {
                                        "value": "low",
                                        "label": "Low Correlation (Diversified)",
                                    },
                                    {
                                        "value": "moderate",
                                        "label": "Moderate Correlation (Balanced)",
                                    },
                                    {
                                        "value": "high",
                                        "label": "High Correlation (Concentrated)",
                                    },
                                ],
                                "required": True,
                            },
                        ]
                    },
                },
                {
                    "id": "factor_selection",
                    "name": "Factor Selection",
                    "step_type": "user_interaction",
                    "description": "Select investment factors for your portfolio",
                    "config": {
                        "items": [
                            {
                                "id": "value",
                                "name": "Value Factor",
                                "description": "Invest in undervalued stocks",
                            },
                            {
                                "id": "momentum",
                                "name": "Momentum Factor",
                                "description": "Invest in trending stocks",
                            },
                            {
                                "id": "quality",
                                "name": "Quality Factor",
                                "description": "Invest in high-quality companies",
                            },
                            {
                                "id": "size",
                                "name": "Size Factor",
                                "description": "Invest in small-cap stocks",
                            },
                            {
                                "id": "low_volatility",
                                "name": "Low Volatility Factor",
                                "description": "Invest in stable, low-volatility stocks",
                            },
                        ],
                        "selectionType": "multiple",
                        "maxSelections": 5,
                        "minSelections": 2,
                    },
                },
                {
                    "id": "optimization_validation",
                    "name": "Portfolio Optimization",
                    "step_type": "validation",
                    "description": "Advanced portfolio optimization and validation",
                    "config": {
                        "results": [
                            {
                                "name": "Sharpe Ratio",
                                "status": "passed",
                                "message": "Optimized risk-adjusted returns",
                            },
                            {
                                "name": "Maximum Drawdown",
                                "status": "passed",
                                "message": "Acceptable downside risk",
                            },
                            {
                                "name": "Factor Exposure",
                                "status": "passed",
                                "message": "Balanced factor exposure",
                            },
                            {
                                "name": "Correlation Analysis",
                                "status": "info",
                                "message": "Low correlation between assets",
                            },
                        ],
                        "overallStatus": "passed",
                        "summary": "Advanced portfolio optimization complete",
                    },
                },
            ],
            "entry_points": ["risk_parity_assessment"],
            "exit_points": ["optimization_validation"],
        },
        "is_active": True,
        "created_by": "advanced_allocation_system",
    }

    return advanced_workflow


def setup_workflows():
    """Set up all portfolio creation workflows."""
    base_url = "http://localhost:8000/api/v1"

    print("=" * 80)
    print("SETTING UP PORTFOLIO CREATION WORKFLOWS")
    print("=" * 80)

    workflows = [create_portfolio_workflow(), create_advanced_allocation_workflow()]

    for workflow in workflows:
        print(f"\nCreating workflow: {workflow['name']}")
        try:
            response = requests.post(
                f"{base_url}/workflows/definitions", json=workflow, timeout=10
            )
            if response.status_code in [200, 201]:
                print(f"✅ {workflow['name']}: Created successfully")
            else:
                print(
                    f"⚠️ {workflow['name']}: Status {response.status_code} - May already exist"
                )
        except Exception as e:
            print(f"❌ {workflow['name']}: Failed - {e}")

    # List all workflows
    print(f"\n{'='*80}")
    print("AVAILABLE WORKFLOWS")
    print(f"{'='*80}")

    try:
        response = requests.get(f"{base_url}/workflows", timeout=5)
        if response.status_code == 200:
            data = response.json()
            workflows = data.get("workflows", [])
            print(f"Total workflows available: {len(workflows)}")
            for workflow in workflows:
                print(f"\n📋 {workflow['name']}")
                print(f"   ID: {workflow['id']}")
                print(f"   Category: {workflow['category']}")
                print(f"   Description: {workflow['description']}")
        else:
            print(f"❌ Failed to list workflows: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to list workflows: {e}")

    print(f"\n{'='*80}")
    print("NEXT STEPS")
    print(f"{'='*80}")
    print("1. Visit http://localhost:3000/workflows to test the frontend")
    print("2. Visit http://localhost:8000/docs to explore the API")
    print("3. Start creating portfolios with the comprehensive workflow!")
    print("4. Test the advanced allocation framework for sophisticated strategies")


if __name__ == "__main__":
    setup_workflows()
