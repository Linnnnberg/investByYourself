#!/usr/bin/env python3
"""
InvestByYourself API Workflow Management Endpoints
Tech-028: API Implementation

Workflow management endpoints with database integration.
"""

import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from src.database.sync_connection import get_db
from src.models.workflow import (
    StepExecutionRequest,
    WorkflowCancelRequest,
    WorkflowDefinition,
    WorkflowExecutionRequest,
    WorkflowExecutionResponse,
    WorkflowListResponse,
    WorkflowPauseRequest,
    WorkflowResumeRequest,
    WorkflowStatus,
    WorkflowStatusResponse,
)
from src.models.workflow_execution import WorkflowDefinition as DBWorkflowDefinition
from src.models.workflow_execution import WorkflowExecution, WorkflowStepExecution
from src.services.workflow_database_service import WorkflowDatabaseService

# Create router
router = APIRouter()


# Initialize workflow engine (dummy for now)
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


# Initialize workflow engine
workflow_engine = MinimalWorkflowEngine()


@router.post("/definitions", response_model=Dict[str, Any])
async def create_workflow_definition(
    workflow_def: Dict[str, Any],
    db: Session = Depends(get_db),
):
    """Create a new workflow definition."""
    try:
        # Create workflow definition in database
        db_workflow_def = DBWorkflowDefinition(
            id=workflow_def.get("id", str(uuid4())),
            name=workflow_def.get("name", "Unnamed Workflow"),
            description=workflow_def.get("description", ""),
            version=workflow_def.get("version", "1.0"),
            category=workflow_def.get("category", "general"),
            definition=workflow_def.get("definition", {}),
            is_active=workflow_def.get("is_active", True),
            created_by=workflow_def.get("created_by", "system"),
        )

        db.add(db_workflow_def)
        db.commit()
        db.refresh(db_workflow_def)

        return {
            "id": db_workflow_def.id,
            "name": db_workflow_def.name,
            "description": db_workflow_def.description,
            "version": db_workflow_def.version,
            "category": db_workflow_def.category,
            "is_active": db_workflow_def.is_active,
            "created_at": db_workflow_def.created_at.isoformat()
            if db_workflow_def.created_at
            else None,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create workflow definition: {str(e)}",
        )


@router.get("/definitions", response_model=List[Dict[str, Any]])
async def list_workflow_definitions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """List workflow definitions."""
    try:
        query = db.query(DBWorkflowDefinition).filter(
            DBWorkflowDefinition.is_active == True
        )

        if category:
            query = query.filter(DBWorkflowDefinition.category == category)

        definitions = query.offset(skip).limit(limit).all()

        return [
            {
                "id": defn.id,
                "name": defn.name,
                "description": defn.description,
                "version": defn.version,
                "category": defn.category,
                "is_active": defn.is_active,
                "created_at": defn.created_at.isoformat() if defn.created_at else None,
            }
            for defn in definitions
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list workflow definitions: {str(e)}",
        )


@router.get("/definitions/{workflow_id}", response_model=Dict[str, Any])
async def get_workflow_definition(
    workflow_id: str = Path(..., description="Workflow definition ID"),
    db: Session = Depends(get_db),
):
    """Get a specific workflow definition."""
    try:
        definition = (
            db.query(DBWorkflowDefinition)
            .filter(
                DBWorkflowDefinition.id == workflow_id,
                DBWorkflowDefinition.is_active == True,
            )
            .first()
        )

        if not definition:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow definition '{workflow_id}' not found",
            )

        return {
            "id": definition.id,
            "name": definition.name,
            "description": definition.description,
            "version": definition.version,
            "category": definition.category,
            "definition": definition.definition,
            "is_active": definition.is_active,
            "created_at": definition.created_at.isoformat()
            if definition.created_at
            else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow definition: {str(e)}",
        )


@router.get("/health", response_model=Dict[str, str])
async def health_check():
    """Health check endpoint for workflow service."""
    return {"status": "healthy", "service": "workflow-engine"}


@router.get("/", response_model=WorkflowListResponse)
async def list_workflows(db: Session = Depends(get_db)):
    """List all available workflow templates."""
    try:
        # Get workflow definitions from database
        db_service = WorkflowDatabaseService(db)
        workflow_defs = db_service.get_workflow_definitions()

        # Convert to API response format
        workflows = []
        for workflow_def in workflow_defs:
            workflows.append(
                WorkflowDefinition(
                    id=workflow_def.id,
                    name=workflow_def.name,
                    description=workflow_def.description,
                    steps=workflow_def.get_workflow_steps(),
                    entry_points=workflow_def.get_entry_points(),
                    exit_points=workflow_def.get_exit_points(),
                    created_at=workflow_def.created_at,
                )
            )

        return WorkflowListResponse(workflows=workflows, total=len(workflows))

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list workflows: {str(e)}",
        )


@router.get("/{workflow_id}", response_model=WorkflowDefinition)
async def get_workflow(
    workflow_id: str = Path(..., description="Workflow ID"),
    db: Session = Depends(get_db),
):
    """Get a specific workflow definition."""
    try:
        db_service = WorkflowDatabaseService(db)
        workflow_def = db_service.get_workflow_definition(workflow_id)

        if not workflow_def:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow '{workflow_id}' not found",
            )

        return WorkflowDefinition(
            id=workflow_def.id,
            name=workflow_def.name,
            description=workflow_def.description,
            steps=workflow_def.get_workflow_steps(),
            entry_points=workflow_def.get_entry_points(),
            exit_points=workflow_def.get_exit_points(),
            created_at=workflow_def.created_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow: {str(e)}",
        )


@router.post("/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(
    request: WorkflowExecutionRequest, db: Session = Depends(get_db)
):
    """Execute a workflow."""
    try:
        # Get workflow definition from database
        db_service = WorkflowDatabaseService(db)
        workflow_def = db_service.get_workflow_definition(request.workflow_id)

        if not workflow_def:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow '{request.workflow_id}' not found",
            )

        # Create workflow execution in database
        execution = db_service.create_execution(
            workflow_id=request.workflow_id,
            user_id=request.context.user_id,
            session_id=request.context.session_id,
            context_data=request.context.data,
        )

        # Update status to running
        db_service.update_execution_status(
            execution.id,
            WorkflowStatus.RUNNING,
            current_step_id=workflow_def.definition.get("entry_points", [None])[0]
            if workflow_def.definition.get("entry_points")
            else None,
        )

        # Execute workflow (dummy implementation for now)
        context = create_workflow_context(
            request.context.user_id, request.context.session_id
        )
        if request.context.data:
            for key, value in request.context.data.items():
                context.update_data(key, value)

        results = workflow_engine.execute_workflow(workflow_def.definition, context)

        # Update execution with results
        db_service.update_execution_results(execution.id, results)
        db_service.update_execution_status(execution.id, WorkflowStatus.COMPLETED)

        # Get updated execution
        execution = db_service.get_execution(execution.id)

        return WorkflowExecutionResponse(
            execution_id=execution.id,
            workflow_id=execution.workflow_id,
            status=WorkflowStatus(execution.status),
            progress=float(execution.progress) if execution.progress else 0.0,
            results=execution.results,
            error_message=execution.error_message,
            started_at=execution.started_at,
            completed_at=execution.completed_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow execution failed: {str(e)}",
        )


@router.post("/execute-step", response_model=Dict[str, Any])
async def execute_step(request: StepExecutionRequest, db: Session = Depends(get_db)):
    """Execute a single workflow step."""
    try:
        # Get execution from database
        db_service = WorkflowDatabaseService(db)
        execution = db_service.get_execution(request.execution_id)

        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow execution '{request.execution_id}' not found",
            )

        # Get workflow definition
        workflow_def = db_service.get_workflow_definition(execution.workflow_id)
        if not workflow_def:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow definition not found",
            )

        # Create step execution
        step_execution = db_service.create_step_execution(
            execution_id=execution.id,
            step_id=request.step_id,
            step_name=f"Step {request.step_id}",
            step_type="data_collection",  # Default type
            input_data=request.step_input,
        )

        # Execute step (dummy implementation)
        context = create_workflow_context(
            request.context.user_id, request.context.session_id
        )
        if request.context.data:
            for key, value in request.context.data.items():
                context.update_data(key, value)

        step_results = workflow_engine.execute_step(
            workflow_def.definition, request.step_id, context, execution.results
        )

        # Update step execution
        db_service.update_step_execution(
            execution.id, request.step_id, "completed", output_data=step_results
        )

        return {
            "execution_id": request.execution_id,
            "workflow_id": execution.workflow_id,
            "step_id": request.step_id,
            "status": "completed",
            "result": step_results,
            "executed_at": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Step execution failed: {str(e)}",
        )


@router.get("/executions", response_model=List[WorkflowExecutionResponse])
async def list_workflow_executions(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    workflow_id: Optional[str] = Query(None, description="Filter by workflow ID"),
    status: Optional[WorkflowStatus] = Query(None, description="Filter by status"),
    limit: int = Query(10, description="Number of executions to return"),
    offset: int = Query(0, description="Number of executions to skip"),
    db: Session = Depends(get_db),
):
    """List workflow executions with optional filtering."""
    try:
        db_service = WorkflowDatabaseService(db)
        executions = db_service.get_executions(
            user_id=user_id,
            workflow_id=workflow_id,
            status=status,
            limit=limit,
            offset=offset,
        )

        return [
            WorkflowExecutionResponse(
                execution_id=execution.id,
                workflow_id=execution.workflow_id,
                status=WorkflowStatus(execution.status),
                progress=float(execution.progress) if execution.progress else 0.0,
                results=execution.results,
                error_message=execution.error_message,
                started_at=execution.started_at,
                completed_at=execution.completed_at,
            )
            for execution in executions
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list workflow executions: {str(e)}",
        )


@router.get("/executions/{execution_id}", response_model=WorkflowStatusResponse)
async def get_workflow_status(
    execution_id: str = Path(..., description="Execution ID"),
    db: Session = Depends(get_db),
):
    """Get workflow execution status."""
    try:
        db_service = WorkflowDatabaseService(db)
        execution = db_service.get_execution(execution_id)

        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow execution '{execution_id}' not found",
            )

        # Get step executions
        step_executions = db_service.get_step_executions(execution.id)
        step_results = {step.step_id: step.to_dict() for step in step_executions}

        return WorkflowStatusResponse(
            execution_id=execution.id,
            workflow_id=execution.workflow_id,
            status=WorkflowStatus(execution.status),
            current_step=execution.current_step_id,
            progress=float(execution.progress) if execution.progress else 0.0,
            step_results=step_results,
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
async def pause_workflow(request: WorkflowPauseRequest, db: Session = Depends(get_db)):
    """Pause a running workflow."""
    try:
        db_service = WorkflowDatabaseService(db)
        execution = db_service.get_execution(request.execution_id)

        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow execution '{request.execution_id}' not found",
            )

        if not execution.can_be_paused():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Workflow execution '{request.execution_id}' cannot be paused from status {execution.status}",
            )

        db_service.update_execution_status(execution.id, WorkflowStatus.PAUSED)
        return {"message": "Workflow paused successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to pause workflow: {str(e)}",
        )


@router.post("/resume", response_model=Dict[str, str])
async def resume_workflow(
    request: WorkflowResumeRequest, db: Session = Depends(get_db)
):
    """Resume a paused workflow."""
    try:
        db_service = WorkflowDatabaseService(db)
        execution = db_service.get_execution(request.execution_id)

        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow execution '{request.execution_id}' not found",
            )

        if not execution.can_be_resumed():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Workflow execution '{request.execution_id}' cannot be resumed from status {execution.status}",
            )

        db_service.update_execution_status(execution.id, WorkflowStatus.RUNNING)
        return {"message": "Workflow resumed successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resume workflow: {str(e)}",
        )


@router.post("/cancel", response_model=Dict[str, str])
async def cancel_workflow(
    request: WorkflowCancelRequest, db: Session = Depends(get_db)
):
    """Cancel a running or paused workflow."""
    try:
        db_service = WorkflowDatabaseService(db)
        execution = db_service.get_execution(request.execution_id)

        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow execution '{request.execution_id}' not found",
            )

        if not execution.can_be_cancelled():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Workflow execution '{request.execution_id}' cannot be cancelled from status {execution.status}",
            )

        db_service.update_execution_status(execution.id, WorkflowStatus.CANCELLED)
        return {"message": "Workflow cancelled successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel workflow: {str(e)}",
        )
