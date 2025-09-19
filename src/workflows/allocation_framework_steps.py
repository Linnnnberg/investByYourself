#!/usr/bin/env python3
"""
Allocation Framework Workflow Steps
InvestByYourself Financial Platform

Pre-defined workflow steps and workflows for allocation framework functionality.
"""

from typing import Any, Dict, List

from core.workflow_minimal import WorkflowDefinition, WorkflowStep, WorkflowStepType


class AllocationFrameworkSteps:
    """Pre-defined steps for allocation framework workflows."""

    @staticmethod
    def get_portfolio_creation_workflow() -> WorkflowDefinition:
        """Get the basic portfolio creation workflow with allocation framework."""
        return WorkflowDefinition(
            id="portfolio_creation_basic",
            name="Portfolio Creation with Allocation Framework",
            description="Basic portfolio creation workflow with allocation framework support",
            steps=[
                WorkflowStep(
                    id="profile_assessment",
                    name="Investment Profile Assessment",
                    step_type=WorkflowStepType.DATA_COLLECTION,
                    description="Collect user investment profile data",
                    config={
                        "questions": "investment_profile_questions",
                        "validation": "risk_profile_validation",
                        "required_fields": [
                            "risk_tolerance",
                            "time_horizon",
                            "investment_goals",
                        ],
                    },
                ),
                WorkflowStep(
                    id="allocation_method_choice",
                    name="Allocation Method Selection",
                    step_type=WorkflowStepType.DECISION,
                    description="Choose between framework, manual, or hybrid allocation",
                    config={
                        "options": ["framework", "manual", "hybrid"],
                        "default": "framework",
                        "description": "How would you like to allocate your portfolio?",
                        "help_text": "Framework: Use pre-built allocation templates. Manual: Pick products directly. Hybrid: Start manual, add framework later.",
                    },
                    dependencies=["profile_assessment"],
                ),
                WorkflowStep(
                    id="framework_selection",
                    name="Framework Selection",
                    step_type=WorkflowStepType.DECISION,
                    description="Select allocation framework template",
                    config={
                        "condition": "allocation_method == 'framework'",
                        "templates": [
                            {
                                "id": "conservative",
                                "name": "Conservative",
                                "description": "60% Bonds, 35% Equity, 5% Alternatives",
                                "risk_level": "low",
                            },
                            {
                                "id": "balanced",
                                "name": "Balanced",
                                "description": "60% Equity, 35% Bonds, 5% Alternatives",
                                "risk_level": "medium",
                            },
                            {
                                "id": "growth",
                                "name": "Growth",
                                "description": "80% Equity, 15% Bonds, 5% Alternatives",
                                "risk_level": "high",
                            },
                            {
                                "id": "custom",
                                "name": "Custom Framework",
                                "description": "Build your own allocation framework",
                                "risk_level": "custom",
                            },
                        ],
                    },
                    dependencies=["allocation_method_choice"],
                ),
                WorkflowStep(
                    id="custom_framework_builder",
                    name="Custom Framework Builder",
                    step_type=WorkflowStepType.USER_INTERACTION,
                    description="Build custom allocation framework",
                    config={
                        "condition": "framework_selection == 'custom'",
                        "drag_drop_enabled": True,
                        "weight_validation": True,
                        "bucket_types": [
                            "asset_class",
                            "sector",
                            "geographic",
                            "market_cap",
                        ],
                    },
                    dependencies=["framework_selection"],
                ),
                WorkflowStep(
                    id="product_selection",
                    name="Product Selection",
                    step_type=WorkflowStepType.USER_INTERACTION,
                    description="Select investment products",
                    config={
                        "condition": "allocation_method in ['manual', 'hybrid']",
                        "search_enabled": True,
                        "filters": ["asset_class", "sector", "region", "market_cap"],
                        "max_products": 50,
                        "min_products": 1,
                    },
                    dependencies=["allocation_method_choice"],
                ),
                WorkflowStep(
                    id="product_mapping",
                    name="Product Mapping",
                    step_type=WorkflowStepType.USER_INTERACTION,
                    description="Map products to framework buckets",
                    config={
                        "condition": "allocation_method == 'framework'",
                        "auto_suggest": True,
                        "manual_override": True,
                        "data_health_indicators": True,
                    },
                    dependencies=["framework_selection", "product_selection"],
                ),
                WorkflowStep(
                    id="weight_adjustment",
                    name="Weight Adjustment",
                    step_type=WorkflowStepType.USER_INTERACTION,
                    description="Adjust portfolio weights",
                    config={
                        "slider_interface": True,
                        "weight_validation": True,
                        "rebalance_suggestions": True,
                    },
                    dependencies=["product_mapping", "product_selection"],
                ),
                WorkflowStep(
                    id="portfolio_validation",
                    name="Portfolio Validation",
                    step_type=WorkflowStepType.VALIDATION,
                    description="Validate final portfolio configuration",
                    config={
                        "rules": "portfolio_validation_rules",
                        "weight_validation": True,
                        "constraint_validation": True,
                        "diversification_check": True,
                    },
                    dependencies=["weight_adjustment"],
                ),
            ],
            entry_points=["profile_assessment"],
            exit_points=["portfolio_validation"],
        )

    @staticmethod
    def get_framework_builder_workflow() -> WorkflowDefinition:
        """Get workflow for building custom allocation frameworks."""
        return WorkflowDefinition(
            id="framework_builder",
            name="Custom Framework Builder",
            description="Build custom allocation frameworks",
            steps=[
                WorkflowStep(
                    id="framework_type_selection",
                    name="Framework Type Selection",
                    step_type=WorkflowStepType.DECISION,
                    description="Choose framework type (asset class, sector, geographic, etc.)",
                    config={
                        "types": [
                            {
                                "id": "asset_class",
                                "name": "Asset Class",
                                "description": "Allocate by asset classes (Equity, Bonds, Alternatives)",
                            },
                            {
                                "id": "sector",
                                "name": "Sector",
                                "description": "Allocate by economic sectors",
                            },
                            {
                                "id": "geographic",
                                "name": "Geographic",
                                "description": "Allocate by regions/countries",
                            },
                            {
                                "id": "market_cap",
                                "name": "Market Cap",
                                "description": "Allocate by company size",
                            },
                            {
                                "id": "hybrid",
                                "name": "Hybrid",
                                "description": "Combine multiple allocation methods",
                            },
                        ]
                    },
                ),
                WorkflowStep(
                    id="bucket_definition",
                    name="Bucket Definition",
                    step_type=WorkflowStepType.USER_INTERACTION,
                    description="Define allocation buckets and weights",
                    config={
                        "drag_drop_enabled": True,
                        "weight_validation": True,
                        "hierarchical_structure": True,
                        "max_depth": 3,
                    },
                    dependencies=["framework_type_selection"],
                ),
                WorkflowStep(
                    id="constraint_setup",
                    name="Constraint Setup",
                    step_type=WorkflowStepType.USER_INTERACTION,
                    description="Set up framework constraints",
                    config={
                        "constraint_types": [
                            "min_weight",
                            "max_weight",
                            "sector_caps",
                            "liquidity_requirements",
                            "rebalancing_bands",
                        ],
                        "default_constraints": True,
                    },
                    dependencies=["bucket_definition"],
                ),
                WorkflowStep(
                    id="rebalancing_setup",
                    name="Rebalancing Setup",
                    step_type=WorkflowStepType.DECISION,
                    description="Configure rebalancing rules",
                    config={
                        "rebalancing_methods": ["time_based", "drift_based", "hybrid"],
                        "default_cadence": "quarterly",
                        "default_drift_threshold": 5.0,
                    },
                    dependencies=["constraint_setup"],
                ),
                WorkflowStep(
                    id="framework_validation",
                    name="Framework Validation",
                    step_type=WorkflowStepType.VALIDATION,
                    description="Validate framework configuration",
                    config={
                        "weight_sum_validation": True,
                        "constraint_validation": True,
                        "rebalancing_validation": True,
                        "coverage_validation": True,
                    },
                    dependencies=["rebalancing_setup"],
                ),
            ],
            entry_points=["framework_type_selection"],
            exit_points=["framework_validation"],
        )

    @staticmethod
    def get_rebalancing_workflow() -> WorkflowDefinition:
        """Get workflow for portfolio rebalancing."""
        return WorkflowDefinition(
            id="portfolio_rebalancing",
            name="Portfolio Rebalancing",
            description="Rebalance existing portfolio based on framework",
            steps=[
                WorkflowStep(
                    id="drift_analysis",
                    name="Drift Analysis",
                    step_type=WorkflowStepType.DATA_COLLECTION,
                    description="Analyze current portfolio drift from target allocation",
                    config={"drift_threshold": 5.0, "analysis_period": "30d"},
                ),
                WorkflowStep(
                    id="rebalance_decision",
                    name="Rebalance Decision",
                    step_type=WorkflowStepType.DECISION,
                    description="Decide whether to rebalance",
                    config={
                        "auto_rebalance": False,
                        "drift_threshold": 5.0,
                        "user_confirmation": True,
                    },
                    dependencies=["drift_analysis"],
                ),
                WorkflowStep(
                    id="rebalance_execution",
                    name="Rebalance Execution",
                    step_type=WorkflowStepType.USER_INTERACTION,
                    description="Execute rebalancing trades",
                    config={
                        "simulation_mode": True,
                        "transaction_costs": True,
                        "tax_considerations": True,
                    },
                    dependencies=["rebalance_decision"],
                ),
                WorkflowStep(
                    id="rebalance_validation",
                    name="Rebalance Validation",
                    step_type=WorkflowStepType.VALIDATION,
                    description="Validate rebalancing results",
                    config={
                        "target_validation": True,
                        "constraint_validation": True,
                        "cost_validation": True,
                    },
                    dependencies=["rebalance_execution"],
                ),
            ],
            entry_points=["drift_analysis"],
            exit_points=["rebalance_validation"],
        )

    @staticmethod
    def get_workflow_templates() -> Dict[str, WorkflowDefinition]:
        """Get all available workflow templates."""
        return {
            "portfolio_creation": AllocationFrameworkSteps.get_portfolio_creation_workflow(),
            "framework_builder": AllocationFrameworkSteps.get_framework_builder_workflow(),
            "rebalancing": AllocationFrameworkSteps.get_rebalancing_workflow(),
        }

    @staticmethod
    def get_workflow_by_id(workflow_id: str) -> WorkflowDefinition:
        """Get workflow by ID."""
        templates = AllocationFrameworkSteps.get_workflow_templates()
        return templates.get(workflow_id)

    @staticmethod
    def list_available_workflows() -> List[Dict[str, Any]]:
        """List all available workflows with metadata."""
        templates = AllocationFrameworkSteps.get_workflow_templates()
        return [
            {
                "id": workflow_id,
                "name": workflow.name,
                "description": workflow.description,
                "step_count": len(workflow.steps),
                "entry_points": workflow.entry_points,
                "exit_points": workflow.exit_points,
            }
            for workflow_id, workflow in templates.items()
        ]
