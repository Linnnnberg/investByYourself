"""
Workflow execution database models.
InvestByYourself Financial Platform

SQLAlchemy models for workflow execution persistence.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    DECIMAL,
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.models.database import Base


class WorkflowExecution(Base):
    """Workflow execution instance."""

    __tablename__ = "workflow_executions"

    # Primary key
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # Workflow identification
    workflow_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    session_id = Column(String(255), nullable=False)

    # Execution state
    status = Column(String(50), nullable=False, default="pending", index=True)
    current_step_id = Column(String(255))
    progress = Column(DECIMAL(5, 2), default=0.0)

    # Data storage
    context_data = Column(JSON, default=dict)
    results = Column(JSON, default=dict)
    error_message = Column(Text)

    # Timestamps
    started_at = Column(DateTime(timezone=True), default=func.current_timestamp())
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=func.current_timestamp())
    updated_at = Column(
        DateTime(timezone=True),
        default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    # Relationships
    step_executions = relationship(
        "WorkflowStepExecution",
        back_populates="execution",
        cascade="all, delete-orphan",
    )
    logs = relationship(
        "WorkflowExecutionLog", back_populates="execution", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("idx_workflow_executions_user_id", "user_id"),
        Index("idx_workflow_executions_workflow_id", "workflow_id"),
        Index("idx_workflow_executions_status", "status"),
        Index("idx_workflow_executions_created_at", "created_at"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "id": str(self.id),
            "workflow_id": self.workflow_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "status": self.status,
            "current_step_id": self.current_step_id,
            "progress": float(self.progress) if self.progress else 0.0,
            "context_data": self.context_data or {},
            "results": self.results or {},
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def update_progress(self, current_step_index: int, total_steps: int):
        """Update progress based on current step."""
        self.progress = Decimal((current_step_index / total_steps) * 100)

    def is_completed(self) -> bool:
        """Check if execution is completed."""
        return self.status in ["completed", "failed", "cancelled"]

    def can_be_paused(self) -> bool:
        """Check if execution can be paused."""
        return self.status in ["running", "pending"]

    def can_be_resumed(self) -> bool:
        """Check if execution can be resumed."""
        return self.status == "paused"

    def can_be_cancelled(self) -> bool:
        """Check if execution can be cancelled."""
        return self.status in ["running", "paused", "pending"]


class WorkflowStepExecution(Base):
    """Individual step execution within a workflow."""

    __tablename__ = "workflow_step_executions"

    # Primary key
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # Foreign key
    execution_id = Column(
        String(36),
        ForeignKey("workflow_executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Step identification
    step_id = Column(String(255), nullable=False, index=True)
    step_name = Column(String(255), nullable=False)
    step_type = Column(String(50), nullable=False)

    # Execution state
    status = Column(String(50), nullable=False, default="pending", index=True)

    # Data storage
    input_data = Column(JSON, default=dict)
    output_data = Column(JSON, default=dict)
    error_message = Column(Text)

    # Timestamps
    started_at = Column(DateTime(timezone=True), default=func.current_timestamp())
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=func.current_timestamp())
    updated_at = Column(
        DateTime(timezone=True),
        default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    # Relationships
    execution = relationship("WorkflowExecution", back_populates="step_executions")

    # Indexes
    __table_args__ = (
        Index("idx_workflow_step_executions_execution_id", "execution_id"),
        Index("idx_workflow_step_executions_step_id", "step_id"),
        Index("idx_workflow_step_executions_status", "status"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "id": str(self.id),
            "execution_id": str(self.execution_id),
            "step_id": self.step_id,
            "step_name": self.step_name,
            "step_type": self.step_type,
            "status": self.status,
            "input_data": self.input_data or {},
            "output_data": self.output_data or {},
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def is_completed(self) -> bool:
        """Check if step is completed."""
        return self.status in ["completed", "failed"]

    def mark_started(self):
        """Mark step as started."""
        self.status = "running"
        self.started_at = func.current_timestamp()

    def mark_completed(self, output_data: Dict[str, Any] = None):
        """Mark step as completed."""
        self.status = "completed"
        self.completed_at = func.current_timestamp()
        if output_data:
            self.output_data = output_data

    def mark_failed(self, error_message: str):
        """Mark step as failed."""
        self.status = "failed"
        self.completed_at = func.current_timestamp()
        self.error_message = error_message


class WorkflowDefinition(Base):
    """Workflow template definitions."""

    __tablename__ = "workflow_definitions"

    # Primary key
    id = Column(String(255), primary_key=True)

    # Definition metadata
    name = Column(String(255), nullable=False)
    description = Column(Text)
    version = Column(String(50), default="1.0")
    category = Column(String(100))

    # Workflow definition (JSON)
    definition = Column(JSON, nullable=False)

    # Status and metadata
    is_active = Column(Boolean, default=True)
    created_by = Column(String(255))

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.current_timestamp())
    updated_at = Column(
        DateTime(timezone=True),
        default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "category": self.category,
            "definition": self.definition,
            "is_active": self.is_active,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def get_workflow_steps(self) -> List[Dict[str, Any]]:
        """Get workflow steps from definition."""
        return self.definition.get("steps", [])

    def get_entry_points(self) -> List[str]:
        """Get workflow entry points."""
        return self.definition.get("entry_points", [])

    def get_exit_points(self) -> List[str]:
        """Get workflow exit points."""
        return self.definition.get("exit_points", [])


class WorkflowExecutionLog(Base):
    """Audit trail for workflow execution events."""

    __tablename__ = "workflow_execution_logs"

    # Primary key
    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # Foreign key
    execution_id = Column(
        String(36),
        ForeignKey("workflow_executions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Log details
    step_id = Column(String(255))
    action = Column(String(100), nullable=False)
    message = Column(Text)
    data = Column(JSON, default=dict)

    # Timestamp
    created_at = Column(
        DateTime(timezone=True), default=func.current_timestamp(), index=True
    )

    # Relationships
    execution = relationship("WorkflowExecution", back_populates="logs")

    # Indexes
    __table_args__ = (
        Index("idx_workflow_execution_logs_execution_id", "execution_id"),
        Index("idx_workflow_execution_logs_created_at", "created_at"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "id": str(self.id),
            "execution_id": str(self.execution_id),
            "step_id": self.step_id,
            "action": self.action,
            "message": self.message,
            "data": self.data or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def create_log(
        cls,
        execution_id: UUID,
        action: str,
        message: str = None,
        step_id: str = None,
        data: Dict[str, Any] = None,
    ):
        """Create a new log entry."""
        return cls(
            execution_id=execution_id,
            step_id=step_id,
            action=action,
            message=message,
            data=data or {},
        )
