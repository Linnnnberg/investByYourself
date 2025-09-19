"""
Workflow database service.
InvestByYourself Financial Platform

Service layer for workflow execution database operations.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, asc, desc, or_
from sqlalchemy.orm import Session

from src.models.workflow import WorkflowStatus
from src.models.workflow_execution import (
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowExecutionLog,
    WorkflowStepExecution,
)


class WorkflowDatabaseService:
    """Service for workflow database operations."""

    def __init__(self, db: Session):
        self.db = db

    # Workflow Execution Operations

    def create_execution(
        self,
        workflow_id: str,
        user_id: str,
        session_id: str,
        context_data: Dict[str, Any] = None,
    ) -> WorkflowExecution:
        """Create a new workflow execution."""
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            user_id=user_id,
            session_id=session_id,
            context_data=context_data or {},
            status=WorkflowStatus.PENDING.value,
        )

        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)

        # Log creation
        self._log_execution_event(
            execution.id,
            "execution_created",
            f"Workflow execution created for workflow {workflow_id}",
            data={"workflow_id": workflow_id, "user_id": user_id},
        )

        return execution

    def get_execution(self, execution_id: UUID) -> Optional[WorkflowExecution]:
        """Get workflow execution by ID."""
        return (
            self.db.query(WorkflowExecution)
            .filter(WorkflowExecution.id == execution_id)
            .first()
        )

    def get_executions(
        self,
        user_id: str = None,
        workflow_id: str = None,
        status: WorkflowStatus = None,
        limit: int = 10,
        offset: int = 0,
    ) -> List[WorkflowExecution]:
        """Get workflow executions with filtering."""
        query = self.db.query(WorkflowExecution)

        if user_id:
            query = query.filter(WorkflowExecution.user_id == user_id)
        if workflow_id:
            query = query.filter(WorkflowExecution.workflow_id == workflow_id)
        if status:
            query = query.filter(WorkflowExecution.status == status.value)

        return (
            query.order_by(desc(WorkflowExecution.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )

    def update_execution_status(
        self,
        execution_id: UUID,
        status: WorkflowStatus,
        current_step_id: str = None,
        progress: float = None,
        error_message: str = None,
    ) -> Optional[WorkflowExecution]:
        """Update workflow execution status."""
        execution = self.get_execution(execution_id)
        if not execution:
            return None

        execution.status = status.value
        if current_step_id:
            execution.current_step_id = current_step_id
        if progress is not None:
            execution.progress = progress
        if error_message:
            execution.error_message = error_message

        if status in [
            WorkflowStatus.COMPLETED,
            WorkflowStatus.FAILED,
            WorkflowStatus.CANCELLED,
        ]:
            execution.completed_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(execution)

        # Log status change
        self._log_execution_event(
            execution_id,
            "status_changed",
            f"Execution status changed to {status.value}",
            data={"old_status": execution.status, "new_status": status.value},
        )

        return execution

    def update_execution_context(
        self, execution_id: UUID, context_data: Dict[str, Any]
    ) -> Optional[WorkflowExecution]:
        """Update workflow execution context data."""
        execution = self.get_execution(execution_id)
        if not execution:
            return None

        execution.context_data.update(context_data)
        self.db.commit()
        self.db.refresh(execution)

        return execution

    def update_execution_results(
        self, execution_id: UUID, results: Dict[str, Any]
    ) -> Optional[WorkflowExecution]:
        """Update workflow execution results."""
        execution = self.get_execution(execution_id)
        if not execution:
            return None

        execution.results.update(results)
        self.db.commit()
        self.db.refresh(execution)

        return execution

    # Workflow Step Execution Operations

    def create_step_execution(
        self,
        execution_id: UUID,
        step_id: str,
        step_name: str,
        step_type: str,
        input_data: Dict[str, Any] = None,
    ) -> WorkflowStepExecution:
        """Create a new step execution."""
        step_execution = WorkflowStepExecution(
            execution_id=execution_id,
            step_id=step_id,
            step_name=step_name,
            step_type=step_type,
            input_data=input_data or {},
            status="pending",
        )

        self.db.add(step_execution)
        self.db.commit()
        self.db.refresh(step_execution)

        return step_execution

    def get_step_execution(
        self, execution_id: UUID, step_id: str
    ) -> Optional[WorkflowStepExecution]:
        """Get step execution by execution ID and step ID."""
        return (
            self.db.query(WorkflowStepExecution)
            .filter(
                and_(
                    WorkflowStepExecution.execution_id == execution_id,
                    WorkflowStepExecution.step_id == step_id,
                )
            )
            .first()
        )

    def get_step_executions(self, execution_id: UUID) -> List[WorkflowStepExecution]:
        """Get all step executions for a workflow execution."""
        return (
            self.db.query(WorkflowStepExecution)
            .filter(WorkflowStepExecution.execution_id == execution_id)
            .order_by(asc(WorkflowStepExecution.created_at))
            .all()
        )

    def update_step_execution(
        self,
        execution_id: UUID,
        step_id: str,
        status: str,
        output_data: Dict[str, Any] = None,
        error_message: str = None,
    ) -> Optional[WorkflowStepExecution]:
        """Update step execution status and data."""
        step_execution = self.get_step_execution(execution_id, step_id)
        if not step_execution:
            return None

        step_execution.status = status
        if output_data:
            step_execution.output_data = output_data
        if error_message:
            step_execution.error_message = error_message

        if status in ["completed", "failed"]:
            step_execution.completed_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(step_execution)

        # Log step completion
        self._log_execution_event(
            execution_id,
            "step_completed",
            f"Step {step_id} completed with status {status}",
            step_id=step_id,
            data={"status": status, "output_data": output_data},
        )

        return step_execution

    # Workflow Definition Operations

    def get_workflow_definition(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """Get workflow definition by ID."""
        return (
            self.db.query(WorkflowDefinition)
            .filter(
                and_(
                    WorkflowDefinition.id == workflow_id,
                    WorkflowDefinition.is_active == True,
                )
            )
            .first()
        )

    def get_workflow_definitions(
        self, category: str = None, is_active: bool = True
    ) -> List[WorkflowDefinition]:
        """Get workflow definitions with filtering."""
        query = self.db.query(WorkflowDefinition)

        if category:
            query = query.filter(WorkflowDefinition.category == category)
        if is_active is not None:
            query = query.filter(WorkflowDefinition.is_active == is_active)

        return query.order_by(asc(WorkflowDefinition.name)).all()

    def create_workflow_definition(
        self,
        workflow_id: str,
        name: str,
        description: str,
        definition: Dict[str, Any],
        category: str = None,
        created_by: str = None,
    ) -> WorkflowDefinition:
        """Create a new workflow definition."""
        workflow_def = WorkflowDefinition(
            id=workflow_id,
            name=name,
            description=description,
            definition=definition,
            category=category,
            created_by=created_by,
            is_active=True,
        )

        self.db.add(workflow_def)
        self.db.commit()
        self.db.refresh(workflow_def)

        return workflow_def

    # Execution Logging

    def _log_execution_event(
        self,
        execution_id: UUID,
        action: str,
        message: str = None,
        step_id: str = None,
        data: Dict[str, Any] = None,
    ):
        """Log an execution event."""
        log_entry = WorkflowExecutionLog.create_log(
            execution_id=execution_id,
            action=action,
            message=message,
            step_id=step_id,
            data=data,
        )

        self.db.add(log_entry)
        self.db.commit()

    def get_execution_logs(
        self, execution_id: UUID, limit: int = 100, offset: int = 0
    ) -> List[WorkflowExecutionLog]:
        """Get execution logs for a workflow execution."""
        return (
            self.db.query(WorkflowExecutionLog)
            .filter(WorkflowExecutionLog.execution_id == execution_id)
            .order_by(desc(WorkflowExecutionLog.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )

    # Utility Methods

    def get_execution_statistics(
        self, user_id: str = None, workflow_id: str = None
    ) -> Dict[str, Any]:
        """Get execution statistics."""
        query = self.db.query(WorkflowExecution)

        if user_id:
            query = query.filter(WorkflowExecution.user_id == user_id)
        if workflow_id:
            query = query.filter(WorkflowExecution.workflow_id == workflow_id)

        total_executions = query.count()
        completed_executions = query.filter(
            WorkflowExecution.status == WorkflowStatus.COMPLETED.value
        ).count()
        failed_executions = query.filter(
            WorkflowExecution.status == WorkflowStatus.FAILED.value
        ).count()
        running_executions = query.filter(
            WorkflowExecution.status == WorkflowStatus.RUNNING.value
        ).count()

        return {
            "total_executions": total_executions,
            "completed_executions": completed_executions,
            "failed_executions": failed_executions,
            "running_executions": running_executions,
            "success_rate": (completed_executions / total_executions * 100)
            if total_executions > 0
            else 0,
        }

    def cleanup_old_executions(self, days_old: int = 30) -> int:
        """Clean up old completed executions."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)

        old_executions = (
            self.db.query(WorkflowExecution)
            .filter(
                and_(
                    WorkflowExecution.status.in_(
                        [
                            WorkflowStatus.COMPLETED.value,
                            WorkflowStatus.FAILED.value,
                            WorkflowStatus.CANCELLED.value,
                        ]
                    ),
                    WorkflowExecution.completed_at < cutoff_date,
                )
            )
            .all()
        )

        count = len(old_executions)
        for execution in old_executions:
            self.db.delete(execution)

        self.db.commit()
        return count
