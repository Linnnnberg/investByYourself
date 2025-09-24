#!/usr/bin/env python3
"""
Minimal Workflow Engine for Allocation Framework
InvestByYourself Financial Platform

Basic data models and types for the minimal workflow engine.
This is a focused implementation for allocation framework support.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class WorkflowStepType(str, Enum):
    """Minimal set of step types needed for allocation framework."""

    DATA_COLLECTION = "data_collection"
    DECISION = "decision"
    VALIDATION = "validation"
    USER_INTERACTION = "user_interaction"


class WorkflowStatus(str, Enum):
    """Workflow execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


@dataclass
class WorkflowContext:
    """Simplified workflow context for minimal implementation."""

    user_id: str
    session_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def update_data(self, key: str, value: Any) -> None:
        """Update context data."""
        self.data[key] = value

    def get_data(self, key: str, default: Any = None) -> Any:
        """Get data from context."""
        return self.data.get(key, default)


@dataclass
class WorkflowStep:
    """Minimal workflow step definition."""

    id: str
    name: str
    step_type: WorkflowStepType
    description: str
    config: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate step configuration after initialization."""
        if not self.id:
            raise ValueError("Step ID cannot be empty")
        if not self.name:
            raise ValueError("Step name cannot be empty")
        if not self.step_type:
            raise ValueError("Step type cannot be empty")


@dataclass
class WorkflowDefinition:
    """Minimal workflow definition."""

    id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    entry_points: List[str]
    exit_points: List[str]
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate workflow definition after initialization."""
        if not self.id:
            raise ValueError("Workflow ID cannot be empty")
        if not self.name:
            raise ValueError("Workflow name cannot be empty")
        if not self.steps:
            raise ValueError("Workflow must have at least one step")
        if not self.entry_points:
            raise ValueError("Workflow must have at least one entry point")
        if not self.exit_points:
            raise ValueError("Workflow must have at least one exit point")

        # Validate entry points exist in steps
        step_ids = {step.id for step in self.steps}
        for entry_point in self.entry_points:
            if entry_point not in step_ids:
                raise ValueError(f"Entry point '{entry_point}' not found in steps")

        # Validate exit points exist in steps
        for exit_point in self.exit_points:
            if exit_point not in step_ids:
                raise ValueError(f"Exit point '{exit_point}' not found in steps")

    def get_step(self, step_id: str) -> Optional[WorkflowStep]:
        """Get step by ID."""
        for step in self.steps:
            if step.id == step_id:
                return step
        return None

    def get_steps_by_type(self, step_type: WorkflowStepType) -> List[WorkflowStep]:
        """Get all steps of a specific type."""
        return [step for step in self.steps if step.step_type == step_type]


@dataclass
class WorkflowExecution:
    """Minimal workflow execution tracking."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str = ""
    user_id: str = ""
    session_id: str = ""
    status: WorkflowStatus = WorkflowStatus.PENDING
    context: WorkflowContext = field(default_factory=lambda: WorkflowContext("", ""))
    results: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def start(self) -> None:
        """Mark workflow as started."""
        self.status = WorkflowStatus.RUNNING
        self.started_at = datetime.utcnow()

    def complete(self, results: Dict[str, Any]) -> None:
        """Mark workflow as completed."""
        self.status = WorkflowStatus.COMPLETED
        self.results = results
        self.completed_at = datetime.utcnow()

    def fail(self, error_message: str) -> None:
        """Mark workflow as failed."""
        self.status = WorkflowStatus.FAILED
        self.error_message = error_message
        self.completed_at = datetime.utcnow()

    def pause(self) -> None:
        """Pause workflow execution."""
        if self.status == WorkflowStatus.RUNNING:
            self.status = WorkflowStatus.PAUSED

    def resume(self) -> None:
        """Resume paused workflow."""
        if self.status == WorkflowStatus.PAUSED:
            self.status = WorkflowStatus.RUNNING


class WorkflowError(Exception):
    """Base exception for workflow-related errors."""

    pass


class WorkflowExecutionError(WorkflowError):
    """Exception raised during workflow execution."""

    pass


class WorkflowValidationError(WorkflowError):
    """Exception raised during workflow validation."""

    pass


class StepExecutionError(WorkflowError):
    """Exception raised during step execution."""

    pass


# Utility functions for workflow management
def create_workflow_context(user_id: str, session_id: str = None) -> WorkflowContext:
    """Create a new workflow context."""
    if session_id is None:
        session_id = str(uuid.uuid4())
    return WorkflowContext(user_id=user_id, session_id=session_id)


def validate_workflow_definition(workflow: WorkflowDefinition) -> bool:
    """Validate a workflow definition."""
    try:
        # This will raise an exception if validation fails
        workflow.__post_init__()
        return True
    except ValueError:
        return False


def create_workflow_execution(
    workflow: WorkflowDefinition, context: WorkflowContext
) -> WorkflowExecution:
    """Create a new workflow execution."""
    return WorkflowExecution(
        workflow_id=workflow.id,
        user_id=context.user_id,
        session_id=context.session_id,
        context=context,
    )
