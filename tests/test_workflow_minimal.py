#!/usr/bin/env python3
"""
Tests for Minimal Workflow Engine
InvestByYourself Financial Platform

Basic tests for the minimal workflow engine implementation.
"""

from datetime import datetime

import pytest

from core.workflow_engine_minimal import MinimalWorkflowEngine
from core.workflow_minimal import (
    WorkflowContext,
    WorkflowDefinition,
    WorkflowStatus,
    WorkflowStep,
    WorkflowStepType,
    create_workflow_context,
    validate_workflow_definition,
)
from workflows.allocation_framework_steps import AllocationFrameworkSteps


class TestWorkflowMinimal:
    """Test cases for minimal workflow engine."""

    def test_workflow_context_creation(self):
        """Test workflow context creation."""
        context = create_workflow_context("user123", "session456")

        assert context.user_id == "user123"
        assert context.session_id == "session456"
        assert isinstance(context.data, dict)
        assert isinstance(context.created_at, datetime)

    def test_workflow_context_data_operations(self):
        """Test workflow context data operations."""
        context = create_workflow_context("user123")

        # Test update_data
        context.update_data("test_key", "test_value")
        assert context.get_data("test_key") == "test_value"

        # Test get_data with default
        assert context.get_data("nonexistent_key", "default") == "default"

    def test_workflow_step_creation(self):
        """Test workflow step creation."""
        step = WorkflowStep(
            id="test_step",
            name="Test Step",
            step_type=WorkflowStepType.DATA_COLLECTION,
            description="A test step",
        )

        assert step.id == "test_step"
        assert step.name == "Test Step"
        assert step.step_type == WorkflowStepType.DATA_COLLECTION
        assert step.description == "A test step"
        assert isinstance(step.config, dict)
        assert isinstance(step.dependencies, list)

    def test_workflow_definition_creation(self):
        """Test workflow definition creation."""
        steps = [
            WorkflowStep(
                id="step1",
                name="Step 1",
                step_type=WorkflowStepType.DATA_COLLECTION,
                description="First step",
            ),
            WorkflowStep(
                id="step2",
                name="Step 2",
                step_type=WorkflowStepType.DECISION,
                description="Second step",
            ),
        ]

        workflow = WorkflowDefinition(
            id="test_workflow",
            name="Test Workflow",
            description="A test workflow",
            steps=steps,
            entry_points=["step1"],
            exit_points=["step2"],
        )

        assert workflow.id == "test_workflow"
        assert workflow.name == "Test Workflow"
        assert len(workflow.steps) == 2
        assert workflow.entry_points == ["step1"]
        assert workflow.exit_points == ["step2"]

    def test_workflow_definition_validation(self):
        """Test workflow definition validation."""
        # Valid workflow
        valid_workflow = WorkflowDefinition(
            id="valid_workflow",
            name="Valid Workflow",
            description="A valid workflow",
            steps=[
                WorkflowStep(
                    id="step1",
                    name="Step 1",
                    step_type=WorkflowStepType.DATA_COLLECTION,
                    description="First step",
                )
            ],
            entry_points=["step1"],
            exit_points=["step1"],
        )

        assert validate_workflow_definition(valid_workflow) == True

        # Invalid workflow (empty ID)
        with pytest.raises(ValueError):
            WorkflowDefinition(
                id="",
                name="Invalid Workflow",
                description="An invalid workflow",
                steps=[],
                entry_points=[],
                exit_points=[],
            )

    def test_workflow_definition_get_step(self):
        """Test getting step from workflow definition."""
        workflow = WorkflowDefinition(
            id="test_workflow",
            name="Test Workflow",
            description="A test workflow",
            steps=[
                WorkflowStep(
                    id="step1",
                    name="Step 1",
                    step_type=WorkflowStepType.DATA_COLLECTION,
                    description="First step",
                )
            ],
            entry_points=["step1"],
            exit_points=["step1"],
        )

        # Test getting existing step
        step = workflow.get_step("step1")
        assert step is not None
        assert step.id == "step1"

        # Test getting non-existing step
        step = workflow.get_step("nonexistent")
        assert step is None

    def test_workflow_definition_get_steps_by_type(self):
        """Test getting steps by type from workflow definition."""
        workflow = WorkflowDefinition(
            id="test_workflow",
            name="Test Workflow",
            description="A test workflow",
            steps=[
                WorkflowStep(
                    id="step1",
                    name="Step 1",
                    step_type=WorkflowStepType.DATA_COLLECTION,
                    description="First step",
                ),
                WorkflowStep(
                    id="step2",
                    name="Step 2",
                    step_type=WorkflowStepType.DECISION,
                    description="Second step",
                ),
                WorkflowStep(
                    id="step3",
                    name="Step 3",
                    step_type=WorkflowStepType.DATA_COLLECTION,
                    description="Third step",
                ),
            ],
            entry_points=["step1"],
            exit_points=["step3"],
        )

        # Test getting data collection steps
        data_steps = workflow.get_steps_by_type(WorkflowStepType.DATA_COLLECTION)
        assert len(data_steps) == 2
        assert all(
            step.step_type == WorkflowStepType.DATA_COLLECTION for step in data_steps
        )

        # Test getting decision steps
        decision_steps = workflow.get_steps_by_type(WorkflowStepType.DECISION)
        assert len(decision_steps) == 1
        assert decision_steps[0].id == "step2"


class TestAllocationFrameworkSteps:
    """Test cases for allocation framework workflow steps."""

    def test_portfolio_creation_workflow(self):
        """Test portfolio creation workflow definition."""
        workflow = AllocationFrameworkSteps.get_portfolio_creation_workflow()

        assert workflow.id == "portfolio_creation_basic"
        assert workflow.name == "Portfolio Creation with Allocation Framework"
        assert len(workflow.steps) > 0
        assert "profile_assessment" in workflow.entry_points
        assert "portfolio_validation" in workflow.exit_points

    def test_framework_builder_workflow(self):
        """Test framework builder workflow definition."""
        workflow = AllocationFrameworkSteps.get_framework_builder_workflow()

        assert workflow.id == "framework_builder"
        assert workflow.name == "Custom Framework Builder"
        assert len(workflow.steps) > 0
        assert "framework_type_selection" in workflow.entry_points
        assert "framework_validation" in workflow.exit_points

    def test_rebalancing_workflow(self):
        """Test rebalancing workflow definition."""
        workflow = AllocationFrameworkSteps.get_rebalancing_workflow()

        assert workflow.id == "portfolio_rebalancing"
        assert workflow.name == "Portfolio Rebalancing"
        assert len(workflow.steps) > 0
        assert "drift_analysis" in workflow.entry_points
        assert "rebalance_validation" in workflow.exit_points

    def test_workflow_templates(self):
        """Test workflow templates."""
        templates = AllocationFrameworkSteps.get_workflow_templates()

        assert "portfolio_creation" in templates
        assert "framework_builder" in templates
        assert "rebalancing" in templates

        for workflow_id, workflow in templates.items():
            # The workflow should be a WorkflowDefinition instance
            assert isinstance(workflow, WorkflowDefinition)
            # The workflow ID in the template key should match the workflow's actual ID
            assert workflow.id in [
                "portfolio_creation_basic",
                "framework_builder",
                "portfolio_rebalancing",
            ]

    def test_list_available_workflows(self):
        """Test listing available workflows."""
        workflows = AllocationFrameworkSteps.list_available_workflows()

        assert len(workflows) == 3
        assert all("id" in workflow for workflow in workflows)
        assert all("name" in workflow for workflow in workflows)
        assert all("description" in workflow for workflow in workflows)
        assert all("step_count" in workflow for workflow in workflows)


class TestMinimalWorkflowEngine:
    """Test cases for minimal workflow engine."""

    def test_workflow_engine_initialization(self):
        """Test workflow engine initialization."""
        engine = MinimalWorkflowEngine()

        assert engine is not None
        assert len(engine.step_executors) > 0
        assert WorkflowStepType.DATA_COLLECTION in engine.step_executors
        assert WorkflowStepType.DECISION in engine.step_executors
        assert WorkflowStepType.VALIDATION in engine.step_executors
        assert WorkflowStepType.USER_INTERACTION in engine.step_executors

    def test_simple_workflow_execution(self):
        """Test simple workflow execution."""
        # Create a simple workflow
        workflow = WorkflowDefinition(
            id="simple_test",
            name="Simple Test Workflow",
            description="A simple test workflow",
            steps=[
                WorkflowStep(
                    id="step1",
                    name="Data Collection",
                    step_type=WorkflowStepType.DATA_COLLECTION,
                    description="Collect data",
                    config={"required_fields": ["test_field"]},
                ),
                WorkflowStep(
                    id="step2",
                    name="Decision",
                    step_type=WorkflowStepType.DECISION,
                    description="Make decision",
                    config={"options": ["option1", "option2"], "default": "option1"},
                ),
            ],
            entry_points=["step1"],
            exit_points=["step2"],
        )

        # Create context
        context = create_workflow_context("test_user")

        # Execute workflow
        engine = MinimalWorkflowEngine()
        results = engine.execute_workflow(workflow, context)

        # Verify results
        assert "step1" in results
        assert "step2" in results
        assert results["step1"]["status"] == "completed"
        assert results["step2"]["status"] == "completed"

    def test_workflow_execution_with_user_input(self):
        """Test workflow execution with user input."""
        # Create workflow with user interaction
        workflow = WorkflowDefinition(
            id="interaction_test",
            name="Interaction Test Workflow",
            description="A workflow with user interaction",
            steps=[
                WorkflowStep(
                    id="step1",
                    name="User Interaction",
                    step_type=WorkflowStepType.USER_INTERACTION,
                    description="User interaction step",
                    config={"interaction_type": "product_selection"},
                )
            ],
            entry_points=["step1"],
            exit_points=["step1"],
        )

        # Create context with user input
        context = create_workflow_context("test_user")
        context.update_data(
            "user_input", {"selected_products": ["product1", "product2"]}
        )

        # Execute workflow
        engine = MinimalWorkflowEngine()
        results = engine.execute_workflow(workflow, context)

        # Verify results
        assert "step1" in results
        assert results["step1"]["status"] == "completed"
        assert "user_input" in results["step1"]


if __name__ == "__main__":
    pytest.main([__file__])
