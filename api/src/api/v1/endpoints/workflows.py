#!/usr/bin/env python3
"""
InvestByYourself API Workflow Management Endpoints
Tech-028: API Implementation

Workflow management endpoints for execution and monitoring.
"""

import os
import sys
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Path, Query, status


# For now, create dummy classes for API to work
# TODO: Fix import paths when workflow engine is properly integrated
class MinimalWorkflowEngine:
    def execute_workflow(self, workflow, context):
        """Execute a workflow with dummy implementation."""
        # Update context with provided data
        if hasattr(context, "data") and context.data:
            for key, value in context.data.items():
                context.update_data(key, value)

        # Simulate workflow execution
        results = {}
        for step in workflow.get("steps", []):
            step_id = step["id"]
            results[step_id] = {
                "status": "completed",
                "executed_at": datetime.utcnow().isoformat(),
                "result": f"Executed step: {step['name']}",
            }

        return results

    def execute_step(self, workflow, step_id, context, results):
        """Execute a single workflow step with dummy implementation."""
        # Find the step
        step = None
        for s in workflow.get("steps", []):
            if s["id"] == step_id:
                step = s
                break

        if not step:
            return {"error": f"Step '{step_id}' not found"}

        # Update context with provided data
        if hasattr(context, "data") and context.data:
            for key, value in context.data.items():
                context.update_data(key, value)

        # Simulate step execution
        return {
            "status": "completed",
            "executed_at": datetime.utcnow().isoformat(),
            "result": f"Executed step: {step['name']}",
        }


class AllocationFrameworkSteps:
    @staticmethod
    def list_available_workflows():
        return [
            {
                "id": "portfolio_creation",
                "name": "Portfolio Creation",
                "description": "Create a new portfolio",
            },
            {
                "id": "framework_builder",
                "name": "Framework Builder",
                "description": "Build custom allocation framework",
            },
            {
                "id": "rebalancing",
                "name": "Portfolio Rebalancing",
                "description": "Rebalance existing portfolio",
            },
        ]

    @staticmethod
    def get_workflow_by_id(workflow_id):
        if workflow_id == "portfolio_creation":
            return {
                "id": "portfolio_creation",
                "name": "Portfolio Creation",
                "description": "Create a new portfolio with allocation framework",
                "steps": [
                    {
                        "id": "profile_assessment",
                        "name": "Profile Assessment",
                        "step_type": "data_collection",
                        "description": "Assess user investment profile",
                        "config": {},
                        "dependencies": [],
                    },
                    {
                        "id": "framework_selection",
                        "name": "Framework Selection",
                        "step_type": "decision",
                        "description": "Select allocation framework",
                        "config": {},
                        "dependencies": ["profile_assessment"],
                    },
                    {
                        "id": "product_mapping",
                        "name": "Product Mapping",
                        "step_type": "validation",
                        "description": "Map products to framework",
                        "config": {},
                        "dependencies": ["framework_selection"],
                    },
                ],
                "entry_points": ["profile_assessment"],
                "exit_points": ["product_mapping"],
                "created_at": None,
            }
        return None


class DummyWorkflowContext:
    """Dummy workflow context for API testing."""

    def __init__(self, user_id, session_id):
        self.user_id = user_id
        self.session_id = session_id
        self.data = {}

    def update_data(self, key, value):
        """Update context data."""
        self.data[key] = value

    def get_data(self, key):
        """Get context data."""
        return self.data.get(key)


def create_workflow_context(user_id, session_id):
    return DummyWorkflowContext(user_id, session_id)


from src.models.workflow import (
    StepExecutionRequest,
    StepExecutionResponse,
    WorkflowCancelRequest,
    WorkflowDefinition,
    WorkflowErrorResponse,
    WorkflowExecutionRequest,
    WorkflowExecutionResponse,
    WorkflowListResponse,
    WorkflowPauseRequest,
    WorkflowResumeRequest,
    WorkflowStatus,
    WorkflowStatusResponse,
)

# Create router
router = APIRouter()

# Initialize workflow engine
workflow_engine = MinimalWorkflowEngine()

# In-memory storage for workflow executions (in production, use database)
workflow_executions: Dict[str, WorkflowExecutionResponse] = {}


@router.get("/", response_model=WorkflowListResponse)
async def list_workflows():
    """List all available workflow templates."""
    try:
        # Get available workflows from AllocationFrameworkSteps
        workflows_data = AllocationFrameworkSteps.list_available_workflows()

        # Convert to WorkflowDefinition objects
        workflows = []
        for workflow_data in workflows_data:
            # Get the actual workflow definition
            workflow_def = AllocationFrameworkSteps.get_workflow_by_id(
                workflow_data["id"]
            )
            if workflow_def:
                workflows.append(
                    WorkflowDefinition(
                        id=workflow_def["id"],
                        name=workflow_def["name"],
                        description=workflow_def["description"],
                        steps=[
                            {
                                "id": step["id"],
                                "name": step["name"],
                                "step_type": step["step_type"],
                                "description": step["description"],
                                "config": step["config"],
                                "dependencies": step["dependencies"],
                            }
                            for step in workflow_def["steps"]
                        ],
                        entry_points=workflow_def["entry_points"],
                        exit_points=workflow_def["exit_points"],
                        created_at=workflow_def["created_at"],
                    )
                )

        return WorkflowListResponse(workflows=workflows, total=len(workflows))

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list workflows: {str(e)}",
        )


@router.get("/health", response_model=Dict[str, str])
async def health_check():
    """Health check endpoint for workflow service."""
    return {"status": "healthy", "service": "workflow-engine"}


@router.get("/executions", response_model=List[WorkflowExecutionResponse])
async def list_workflow_executions(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    workflow_id: Optional[str] = Query(None, description="Filter by workflow ID"),
    status: Optional[WorkflowStatus] = Query(None, description="Filter by status"),
    limit: int = Query(10, description="Number of executions to return"),
    offset: int = Query(0, description="Number of executions to skip"),
):
    """List workflow executions with optional filtering."""
    try:
        executions = list(workflow_executions.values())

        # Apply filters
        if user_id:
            executions = [e for e in executions if e.workflow_id == user_id]
        if workflow_id:
            executions = [e for e in executions if e.workflow_id == workflow_id]
        if status:
            executions = [e for e in executions if e.status == status]

        # Apply pagination
        executions = executions[offset : offset + limit]

        return executions

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list workflow executions: {str(e)}",
        )


@router.get("/executions/{execution_id}", response_model=WorkflowStatusResponse)
async def get_workflow_status(
    execution_id: str = Path(..., description="Execution ID")
):
    """Get workflow execution status."""
    try:
        execution = workflow_executions.get(execution_id)
        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow execution '{execution_id}' not found",
            )

        return WorkflowStatusResponse(
            execution_id=execution.execution_id,
            workflow_id=execution.workflow_id,
            status=execution.status,
            current_step=None,  # For MVP, we don't track current step
            progress=execution.progress,
            step_results=execution.results,
            error_message=execution.error_message,
            started_at=execution.started_at,
            completed_at=execution.completed_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow status: {str(e)}",
        )


@router.get("/{workflow_id}", response_model=WorkflowDefinition)
async def get_workflow(workflow_id: str = Path(..., description="Workflow ID")):
    """Get a specific workflow definition."""
    try:
        workflow_def = AllocationFrameworkSteps.get_workflow_by_id(workflow_id)
        if not workflow_def:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow '{workflow_id}' not found",
            )

        return WorkflowDefinition(
            id=workflow_def["id"],
            name=workflow_def["name"],
            description=workflow_def["description"],
            steps=[
                {
                    "id": step["id"],
                    "name": step["name"],
                    "step_type": step["step_type"],
                    "description": step["description"],
                    "config": step["config"],
                    "dependencies": step["dependencies"],
                }
                for step in workflow_def["steps"]
            ],
            entry_points=workflow_def["entry_points"],
            exit_points=workflow_def["exit_points"],
            created_at=workflow_def["created_at"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow: {str(e)}",
        )


@router.post("/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(request: WorkflowExecutionRequest):
    """Execute a workflow."""
    try:
        # Get workflow definition
        workflow_def = AllocationFrameworkSteps.get_workflow_by_id(request.workflow_id)
        if not workflow_def:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow '{request.workflow_id}' not found",
            )

        # Create workflow context
        context = create_workflow_context(
            user_id=request.context.user_id, session_id=request.context.session_id
        )

        # Update context with provided data
        for key, value in request.context.data.items():
            context.update_data(key, value)

        # Generate execution ID
        execution_id = str(uuid4())

        # Execute workflow
        results = workflow_engine.execute_workflow(workflow_def, context)

        # Create execution response
        execution_response = WorkflowExecutionResponse(
            execution_id=execution_id,
            workflow_id=request.workflow_id,
            status=WorkflowStatus.COMPLETED,
            progress=100.0,
            results=results,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
        )

        # Store execution (in production, save to database)
        workflow_executions[execution_id] = execution_response

        return execution_response

    except HTTPException:
        raise
    except Exception as e:
        # Create error response
        execution_id = str(uuid4())
        error_response = WorkflowExecutionResponse(
            execution_id=execution_id,
            workflow_id=request.workflow_id,
            status=WorkflowStatus.FAILED,
            error_message=str(e),
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
        )

        workflow_executions[execution_id] = error_response

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow execution failed: {str(e)}",
        )


@router.post("/execute-step", response_model=StepExecutionResponse)
async def execute_step(request: StepExecutionRequest):
    """Execute a single workflow step."""
    try:
        # Get workflow definition
        workflow_def = AllocationFrameworkSteps.get_workflow_by_id(request.workflow_id)
        if not workflow_def:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow '{request.workflow_id}' not found",
            )

        # Create workflow context
        context = create_workflow_context(
            user_id=request.context.user_id, session_id=request.context.session_id
        )

        # Update context with provided data
        for key, value in request.context.data.items():
            context.update_data(key, value)

        # Execute step
        result = workflow_engine.execute_step(
            workflow_def, request.step_id, context, request.results
        )

        return StepExecutionResponse(
            step_id=request.step_id,
            status=result.get("status", "completed"),
            result=result,
            executed_at=datetime.utcnow(),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Step execution failed: {str(e)}",
        )


@router.get("/executions/{execution_id}", response_model=WorkflowStatusResponse)
async def get_workflow_status(
    execution_id: str = Path(..., description="Execution ID")
):
    """Get workflow execution status."""
    try:
        execution = workflow_executions.get(execution_id)
        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow execution '{execution_id}' not found",
            )

        return WorkflowStatusResponse(
            execution_id=execution.execution_id,
            workflow_id=execution.workflow_id,
            status=execution.status,
            current_step=None,  # For MVP, we don't track current step
            progress=execution.progress,
            step_results=execution.results,
            error_message=execution.error_message,
            started_at=execution.started_at,
            completed_at=execution.completed_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow status: {str(e)}",
        )


@router.post("/pause", response_model=Dict[str, str])
async def pause_workflow(request: WorkflowPauseRequest):
    """Pause a running workflow."""
    try:
        execution = workflow_executions.get(request.execution_id)
        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow execution '{request.execution_id}' not found",
            )

        if execution.status != WorkflowStatus.RUNNING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot pause workflow in status: {execution.status}",
            )

        # Update status
        execution.status = WorkflowStatus.PAUSED

        return {"message": "Workflow paused successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to pause workflow: {str(e)}",
        )


@router.post("/resume", response_model=Dict[str, str])
async def resume_workflow(request: WorkflowResumeRequest):
    """Resume a paused workflow."""
    try:
        execution = workflow_executions.get(request.execution_id)
        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow execution '{request.execution_id}' not found",
            )

        if execution.status != WorkflowStatus.PAUSED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot resume workflow in status: {execution.status}",
            )

        # Update status
        execution.status = WorkflowStatus.RUNNING

        return {"message": "Workflow resumed successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resume workflow: {str(e)}",
        )


@router.post("/cancel", response_model=Dict[str, str])
async def cancel_workflow(request: WorkflowCancelRequest):
    """Cancel a running or paused workflow."""
    try:
        execution = workflow_executions.get(request.execution_id)
        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow execution '{request.execution_id}' not found",
            )

        if execution.status not in [WorkflowStatus.RUNNING, WorkflowStatus.PAUSED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel workflow in status: {execution.status}",
            )

        # Update status
        execution.status = WorkflowStatus.CANCELLED
        execution.completed_at = datetime.utcnow()

        return {"message": "Workflow cancelled successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel workflow: {str(e)}",
        )
