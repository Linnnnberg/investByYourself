#!/usr/bin/env python3
"""
InvestByYourself API Workflow Models
Tech-028: API Implementation

Pydantic models for workflow management.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class WorkflowStepType(str, Enum):
    """Workflow step types."""

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


class WorkflowStep(BaseModel):
    """Workflow step definition."""

    id: str
    name: str
    step_type: WorkflowStepType
    description: str
    config: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)


class WorkflowDefinition(BaseModel):
    """Workflow definition."""

    id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    entry_points: List[str]
    exit_points: List[str]
    created_at: Optional[datetime] = None


class WorkflowContext(BaseModel):
    """Workflow execution context."""

    user_id: str
    session_id: str
    data: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None


class WorkflowExecutionRequest(BaseModel):
    """Request to execute a workflow."""

    workflow_id: str
    context: WorkflowContext


class StepExecutionRequest(BaseModel):
    """Request to execute a single workflow step."""

    execution_id: str
    workflow_id: str
    step_id: str
    context: WorkflowContext
    step_input: Optional[Dict[str, Any]] = Field(default_factory=dict)


class WorkflowExecutionResponse(BaseModel):
    """Response from workflow execution."""

    execution_id: str
    workflow_id: str
    status: WorkflowStatus
    current_step: Optional[str] = None
    progress: float = 0.0
    results: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class StepExecutionResponse(BaseModel):
    """Response from step execution."""

    step_id: str
    status: str
    result: Dict[str, Any] = Field(default_factory=dict)
    executed_at: datetime
    error_message: Optional[str] = None


class WorkflowListResponse(BaseModel):
    """Response for listing available workflows."""

    workflows: List[WorkflowDefinition]
    total: int


class WorkflowExecutionListResponse(BaseModel):
    """Response for listing workflow executions."""

    executions: List[WorkflowExecutionResponse]
    total: int
    page: int
    page_size: int


class WorkflowStatusResponse(BaseModel):
    """Response for workflow status."""

    execution_id: str
    workflow_id: str
    status: WorkflowStatus
    current_step: Optional[str] = None
    progress: float = 0.0
    step_results: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class WorkflowPauseRequest(BaseModel):
    """Request to pause a workflow."""

    execution_id: str


class WorkflowResumeRequest(BaseModel):
    """Request to resume a workflow."""

    execution_id: str


class WorkflowCancelRequest(BaseModel):
    """Request to cancel a workflow."""

    execution_id: str


class WorkflowErrorResponse(BaseModel):
    """Error response for workflow operations."""

    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
