#!/usr/bin/env python3
"""
Workflow Database Service
Story-009: Workflow Engine Implementation

Database operations for workflow management.
"""

import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.workflow_engine_minimal import WorkflowStatus
from src.core.workflow_minimal import WorkflowContext as CoreWorkflowContext
from src.core.workflow_minimal import WorkflowDefinition as CoreWorkflowDefinition
from src.core.workflow_minimal import WorkflowStep as CoreWorkflowStep
from src.models.database import (
    DBStepExecution,
    DBWorkflowDefinition,
    DBWorkflowExecution,
)
from src.models.workflow import WorkflowContext, WorkflowDefinition, WorkflowStep


class WorkflowDatabaseService:
    """Service for workflow database operations."""

    def __init__(self, db_session: AsyncSession):
        """Initialize with database session."""
        self.db = db_session

    async def create_workflow_definition(self, workflow: CoreWorkflowDefinition) -> str:
        """Create a new workflow definition in the database."""
        db_workflow = DBWorkflowDefinition(
            id=workflow.id,
            name=workflow.name,
            description=workflow.description,
            steps=[
                {
                    "id": step.id,
                    "name": step.name,
                    "step_type": step.step_type,
                    "description": step.description,
                    "config": step.config,
                    "dependencies": step.dependencies,
                }
                for step in workflow.steps
            ],
            entry_points=workflow.entry_points,
            exit_points=workflow.exit_points,
            created_at=workflow.created_at or datetime.utcnow(),
        )

        self.db.add(db_workflow)
        await self.db.commit()
        return db_workflow.id

    async def get_workflow_definition(
        self, workflow_id: str
    ) -> Optional[CoreWorkflowDefinition]:
        """Get a workflow definition by ID."""
        result = await self.db.execute(
            select(DBWorkflowDefinition).where(DBWorkflowDefinition.id == workflow_id)
        )
        db_workflow = result.scalar_one_or_none()

        if not db_workflow:
            return None

        # Convert database model to CoreWorkflowDefinition
        steps = [CoreWorkflowStep(**step_data) for step_data in db_workflow.steps]

        return CoreWorkflowDefinition(
            id=db_workflow.id,
            name=db_workflow.name,
            description=db_workflow.description,
            steps=steps,
            entry_points=db_workflow.entry_points,
            exit_points=db_workflow.exit_points,
            created_at=db_workflow.created_at,
        )

    async def list_workflow_definitions(
        self, active_only: bool = True
    ) -> List[WorkflowDefinition]:
        """List all workflow definitions."""
        query = select(DBWorkflowDefinition)
        if active_only:
            query = query.where(DBWorkflowDefinition.is_active == True)

        result = await self.db.execute(query)
        db_workflows = result.scalars().all()

        workflows = []
        for db_workflow in db_workflows:
            # db_workflow.steps is a list of dictionaries from JSON column
            steps = []
            for step_data in db_workflow.steps:
                print(f"DEBUG: step_data type: {type(step_data)}")
                print(f"DEBUG: step_data: {step_data}")
                if isinstance(step_data, dict):
                    # Create Pydantic WorkflowStep object
                    steps.append(WorkflowStep(**step_data))
                else:
                    # If it's already a WorkflowStep object, convert it
                    if hasattr(step_data, "id"):
                        steps.append(
                            WorkflowStep(
                                id=step_data.id,
                                name=step_data.name,
                                step_type=step_data.step_type,
                                description=step_data.description,
                                config=step_data.config,
                                dependencies=step_data.dependencies,
                            )
                        )
                    else:
                        steps.append(step_data)

            workflows.append(
                WorkflowDefinition(
                    id=db_workflow.id,
                    name=db_workflow.name,
                    description=db_workflow.description,
                    steps=steps,
                    entry_points=db_workflow.entry_points,
                    exit_points=db_workflow.exit_points,
                    created_at=db_workflow.created_at,
                )
            )

        return workflows

    async def create_workflow_execution(
        self, workflow_id: str, context: CoreWorkflowContext
    ) -> str:
        """Create a new workflow execution."""
        execution_id = str(uuid.uuid4())

        db_execution = DBWorkflowExecution(
            id=execution_id,
            workflow_id=workflow_id,
            user_id=context.user_id,
            session_id=context.session_id,
            status=WorkflowStatus.PENDING,
            context_data=context.data,
            started_at=datetime.utcnow(),
        )

        self.db.add(db_execution)
        await self.db.commit()
        return execution_id

    async def get_workflow_execution(
        self, execution_id: str
    ) -> Optional[DBWorkflowExecution]:
        """Get a workflow execution by ID."""
        result = await self.db.execute(
            select(DBWorkflowExecution)
            .where(DBWorkflowExecution.id == execution_id)
            .options(selectinload(DBWorkflowExecution.workflow_definition))
        )
        return result.scalar_one_or_none()

    async def update_workflow_execution_status(
        self,
        execution_id: str,
        status: WorkflowStatus,
        current_step: Optional[str] = None,
        progress: float = 0.0,
        error_message: Optional[str] = None,
    ) -> bool:
        """Update workflow execution status."""
        update_data = {"status": status, "updated_at": datetime.utcnow()}

        if current_step is not None:
            update_data["current_step"] = current_step
        if progress is not None:
            update_data["progress"] = progress
        if error_message is not None:
            update_data["error_message"] = error_message
        if status in [
            WorkflowStatus.COMPLETED,
            WorkflowStatus.FAILED,
            WorkflowStatus.CANCELLED,
        ]:
            update_data["completed_at"] = datetime.utcnow()

        result = await self.db.execute(
            update(DBWorkflowExecution)
            .where(DBWorkflowExecution.id == execution_id)
            .values(**update_data)
        )

        await self.db.commit()
        return result.rowcount > 0

    async def update_workflow_context(
        self, execution_id: str, context_data: Dict[str, Any]
    ) -> bool:
        """Update workflow execution context data."""
        result = await self.db.execute(
            update(DBWorkflowExecution)
            .where(DBWorkflowExecution.id == execution_id)
            .values(context_data=context_data, updated_at=datetime.utcnow())
        )

        await self.db.commit()
        return result.rowcount > 0

    async def update_step_results(
        self, execution_id: str, step_results: Dict[str, Any]
    ) -> bool:
        """Update workflow step results."""
        result = await self.db.execute(
            update(DBWorkflowExecution)
            .where(DBWorkflowExecution.id == execution_id)
            .values(step_results=step_results, updated_at=datetime.utcnow())
        )

        await self.db.commit()
        return result.rowcount > 0

    async def create_step_execution(
        self,
        workflow_execution_id: str,
        step: WorkflowStep,
        input_data: Dict[str, Any] = None,
        status: str = "pending",
    ) -> str:
        """Create a step execution record."""
        step_execution_id = str(uuid.uuid4())

        db_step_execution = DBStepExecution(
            id=step_execution_id,
            workflow_execution_id=workflow_execution_id,
            step_id=step.id,
            step_name=step.name,
            step_type=step.step_type,
            status=status,
            input_data=input_data or {},
            started_at=datetime.utcnow() if status == "running" else None,
        )

        self.db.add(db_step_execution)
        await self.db.commit()
        return step_execution_id

    async def update_step_execution(
        self,
        step_execution_id: str,
        status: str,
        output_data: Dict[str, Any] = None,
        error_message: Optional[str] = None,
    ) -> bool:
        """Update step execution status and results."""
        update_data = {"status": status, "updated_at": datetime.utcnow()}

        if output_data is not None:
            update_data["output_data"] = output_data
        if error_message is not None:
            update_data["error_message"] = error_message
        if status in ["completed", "failed", "skipped"]:
            update_data["completed_at"] = datetime.utcnow()

        result = await self.db.execute(
            update(DBStepExecution)
            .where(DBStepExecution.id == step_execution_id)
            .values(**update_data)
        )

        await self.db.commit()
        return result.rowcount > 0

    async def get_step_executions(
        self, workflow_execution_id: str
    ) -> List[DBStepExecution]:
        """Get all step executions for a workflow execution."""
        result = await self.db.execute(
            select(DBStepExecution)
            .where(DBStepExecution.workflow_execution_id == workflow_execution_id)
            .order_by(DBStepExecution.created_at)
        )
        return result.scalars().all()

    async def list_workflow_executions(
        self,
        user_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[DBWorkflowExecution]:
        """List workflow executions with optional filters."""
        query = select(DBWorkflowExecution)

        if user_id:
            query = query.where(DBWorkflowExecution.user_id == user_id)
        if workflow_id:
            query = query.where(DBWorkflowExecution.workflow_id == workflow_id)
        if status:
            query = query.where(DBWorkflowExecution.status == status)

        query = query.order_by(DBWorkflowExecution.created_at.desc())
        query = query.offset(offset).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def delete_workflow_execution(self, execution_id: str) -> bool:
        """Delete a workflow execution and all related step executions."""
        # Delete step executions first
        await self.db.execute(
            delete(DBStepExecution).where(
                DBStepExecution.workflow_execution_id == execution_id
            )
        )

        # Delete workflow execution
        result = await self.db.execute(
            delete(DBWorkflowExecution).where(DBWorkflowExecution.id == execution_id)
        )

        await self.db.commit()
        return result.rowcount > 0
