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

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

# Import the real workflow engine (copied to API directory)
from src.core.workflow_engine_minimal import MinimalWorkflowEngine
from src.core.workflow_minimal import WorkflowContext as CoreWorkflowContext
from src.core.workflow_minimal import WorkflowDefinition as CoreWorkflowDefinition
from src.core.workflow_minimal import WorkflowStep as CoreWorkflowStep
from src.database.connection import get_db_session
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
from src.services.workflow_database_service import WorkflowDatabaseService
from src.workflows.allocation_framework_steps import AllocationFrameworkSteps

# Create router
router = APIRouter()

# Initialize workflow engine
workflow_engine = MinimalWorkflowEngine()

# In-memory storage for workflow executions (in production, use database)
workflow_executions: Dict[str, WorkflowExecutionResponse] = {}


@router.get("/debug")
async def list_workflows_debug(db: AsyncSession = Depends(get_db_session)):
    """Test endpoint without response model."""
    try:
        db_service = WorkflowDatabaseService(db)
        workflows = await db_service.list_workflow_definitions(active_only=True)

        # Return raw data without WorkflowListResponse wrapper
        return {
            "workflows": [workflow.model_dump() for workflow in workflows],
            "total": len(workflows),
        }
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list workflows: {str(e)}",
        )


@router.get("/simple")
async def list_workflows_simple(db: AsyncSession = Depends(get_db_session)):
    """Simple test endpoint."""
    try:
        db_service = WorkflowDatabaseService(db)
        workflows = await db_service.list_workflow_definitions(active_only=True)

        # Return just the count
        return {"count": len(workflows)}
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list workflows: {str(e)}",
        )


@router.get("/", response_model=WorkflowListResponse)
async def list_workflows(db: AsyncSession = Depends(get_db_session)):
    """List all available workflow templates."""
    try:
        db_service = WorkflowDatabaseService(db)
        workflows = await db_service.list_workflow_definitions(active_only=True)

        # If no workflows in database, populate with default workflows
        if not workflows:
            # Create default workflows from AllocationFrameworkSteps
            default_workflows = [
                AllocationFrameworkSteps.get_portfolio_creation_workflow(),
                AllocationFrameworkSteps.get_framework_builder_workflow(),
                AllocationFrameworkSteps.get_rebalancing_workflow(),
            ]

            for workflow in default_workflows:
                await db_service.create_workflow_definition(workflow)

            # Get workflows again after creating them
            workflows = await db_service.list_workflow_definitions(active_only=True)

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


@router.post("/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(
    request: WorkflowExecutionRequest, db: AsyncSession = Depends(get_db_session)
):
    """Execute a workflow."""
    try:
        db_service = WorkflowDatabaseService(db)

        # Get workflow definition from database
        workflow_definition = await db_service.get_workflow_definition(
            request.workflow_id
        )
        if not workflow_definition:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow '{request.workflow_id}' not found",
            )

        # Create proper WorkflowContext
        context = CoreWorkflowContext(
            user_id=request.context.user_id,
            session_id=request.context.session_id,
            data=request.context.data or {},
            created_at=datetime.utcnow(),
        )

        # Create workflow execution in database
        execution_id = await db_service.create_workflow_execution(
            request.workflow_id, context
        )

        # Update status to running
        await db_service.update_workflow_execution_status(
            execution_id,
            WorkflowStatus.RUNNING,
            current_step=workflow_definition.entry_points[0]
            if workflow_definition.entry_points
            else None,
            progress=0.0,
        )

        # Execute workflow using real engine
        results = workflow_engine.execute_workflow(workflow_definition, context)

        # Update execution with results
        await db_service.update_workflow_execution_status(
            execution_id, WorkflowStatus.COMPLETED, progress=100.0
        )
        await db_service.update_step_results(execution_id, results)

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

        # Create proper WorkflowContext
        context = WorkflowContext(
            user_id=request.context.user_id,
            session_id=request.context.session_id,
            data=request.context.data or {},
            created_at=datetime.utcnow(),
        )

        # Convert database workflow definition to WorkflowDefinition object
        workflow_definition = WorkflowDefinition(
            id=workflow_def.id,
            name=workflow_def.name,
            description=workflow_def.description,
            steps=workflow_def.get_workflow_steps(),
            entry_points=workflow_def.get_entry_points(),
            exit_points=workflow_def.get_exit_points(),
            version=workflow_def.version or "1.0",
            category=workflow_def.category or "general",
            created_at=workflow_def.created_at,
        )

        # Execute step using real engine
        result = workflow_engine.execute_step(
            workflow_definition, request.step_id, context, request.results or {}
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
