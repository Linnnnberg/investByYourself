#!/usr/bin/env python3
"""
Minimal Workflow Engine Implementation
InvestByYourself Financial Platform

Basic workflow execution engine for allocation framework support.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Type

from .workflow_minimal import (
    StepExecutionError,
    WorkflowContext,
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowExecutionError,
    WorkflowStatus,
    WorkflowStep,
    WorkflowStepType,
)

logger = logging.getLogger(__name__)


class WorkflowStepExecutor:
    """Base class for workflow step executors."""

    def execute(
        self, step: WorkflowStep, context: WorkflowContext, results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a workflow step and return results."""
        raise NotImplementedError("Subclasses must implement execute method")

    def validate(self, step: WorkflowStep, context: WorkflowContext) -> bool:
        """Validate step configuration and context."""
        return True

    def get_required_inputs(self) -> List[str]:
        """Return list of required input keys."""
        return []

    def get_outputs(self) -> List[str]:
        """Return list of output keys this step produces."""
        return []


class MinimalWorkflowEngine:
    """Minimal workflow execution engine for allocation framework."""

    def __init__(self):
        self.step_executors: Dict[WorkflowStepType, WorkflowStepExecutor] = {}
        self.register_default_executors()
        logger.info("Minimal workflow engine initialized")

    def register_default_executors(self) -> None:
        """Register basic step executors."""
        # We'll implement these in the next step
        from workflows.executors.basic_executors import (
            DataCollectionExecutor,
            DecisionExecutor,
            UserInteractionExecutor,
            ValidationExecutor,
        )

        self.step_executors[WorkflowStepType.DATA_COLLECTION] = DataCollectionExecutor()
        self.step_executors[WorkflowStepType.DECISION] = DecisionExecutor()
        self.step_executors[WorkflowStepType.VALIDATION] = ValidationExecutor()
        self.step_executors[
            WorkflowStepType.USER_INTERACTION
        ] = UserInteractionExecutor()

        logger.info("Default step executors registered")

    def register_step_executor(
        self, step_type: WorkflowStepType, executor: WorkflowStepExecutor
    ) -> None:
        """Register a custom step executor."""
        self.step_executors[step_type] = executor
        logger.info(f"Custom executor registered for step type: {step_type}")

    def execute_workflow(
        self, workflow: WorkflowDefinition, context: WorkflowContext
    ) -> Dict[str, Any]:
        """Execute a workflow with basic error handling."""
        execution = WorkflowExecution(
            workflow_id=workflow.id,
            user_id=context.user_id,
            session_id=context.session_id,
            context=context,
        )

        try:
            execution.start()
            logger.info(f"Starting workflow execution: {workflow.id}")

            # Simple linear execution for MVP
            results = {}
            current_step = workflow.entry_points[0]

            while current_step:
                logger.info(f"Executing step: {current_step}")

                step = self._get_step(workflow, current_step)
                executor = self.step_executors.get(step.step_type)

                if not executor:
                    raise WorkflowExecutionError(
                        f"No executor for step type: {step.step_type}"
                    )

                # Validate step before execution
                if not executor.validate(step, context):
                    raise StepExecutionError(f"Step validation failed: {step.id}")

                # Execute step
                try:
                    result = executor.execute(step, context, results)
                    results[current_step] = result
                    logger.info(f"Step completed successfully: {current_step}")
                except Exception as e:
                    logger.error(f"Step execution failed: {current_step}, error: {e}")
                    raise StepExecutionError(f"Step execution failed: {e}")

                # Move to next step (simplified for MVP)
                current_step = self._get_next_step(workflow, current_step, result)

            # Workflow completed successfully
            execution.complete(results)
            logger.info(f"Workflow completed successfully: {workflow.id}")
            return results

        except Exception as e:
            execution.fail(str(e))
            logger.error(f"Workflow execution failed: {workflow.id}, error: {e}")
            raise WorkflowExecutionError(f"Workflow execution failed: {e}")

    def execute_step(
        self,
        workflow: WorkflowDefinition,
        step_id: str,
        context: WorkflowContext,
        results: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Execute a single workflow step."""
        if results is None:
            results = {}

        step = self._get_step(workflow, step_id)
        executor = self.step_executors.get(step.step_type)

        if not executor:
            raise WorkflowExecutionError(f"No executor for step type: {step.step_type}")

        # Validate step before execution
        if not executor.validate(step, context):
            raise StepExecutionError(f"Step validation failed: {step.id}")

        # Execute step
        try:
            result = executor.execute(step, context, results)
            logger.info(f"Step executed successfully: {step_id}")
            return result
        except Exception as e:
            logger.error(f"Step execution failed: {step_id}, error: {e}")
            raise StepExecutionError(f"Step execution failed: {e}")

    def pause_workflow(self, execution: WorkflowExecution) -> bool:
        """Pause a running workflow."""
        if execution.status == WorkflowStatus.RUNNING:
            execution.pause()
            logger.info(f"Workflow paused: {execution.id}")
            return True
        return False

    def resume_workflow(self, execution: WorkflowExecution) -> bool:
        """Resume a paused workflow."""
        if execution.status == WorkflowStatus.PAUSED:
            execution.resume()
            logger.info(f"Workflow resumed: {execution.id}")
            return True
        return False

    def cancel_workflow(self, execution: WorkflowExecution) -> bool:
        """Cancel a workflow."""
        if execution.status in [WorkflowStatus.RUNNING, WorkflowStatus.PAUSED]:
            execution.status = WorkflowStatus.CANCELLED
            execution.completed_at = datetime.utcnow()
            logger.info(f"Workflow cancelled: {execution.id}")
            return True
        return False

    def _get_step(self, workflow: WorkflowDefinition, step_id: str) -> WorkflowStep:
        """Get step by ID."""
        step = workflow.get_step(step_id)
        if not step:
            raise WorkflowExecutionError(f"Step not found: {step_id}")
        return step

    def _get_next_step(
        self, workflow: WorkflowDefinition, current_step: str, result: Any
    ) -> Optional[str]:
        """Get next step (simplified linear progression for MVP)."""
        # For MVP, we'll use simple linear progression
        # In the future, this can be enhanced with conditional logic
        current_index = None
        for i, step in enumerate(workflow.steps):
            if step.id == current_step:
                current_index = i
                break

        if current_index is None or current_index >= len(workflow.steps) - 1:
            return None

        next_step = workflow.steps[current_index + 1]
        return next_step.id

    def get_workflow_status(self, execution: WorkflowExecution) -> Dict[str, Any]:
        """Get current workflow execution status."""
        return {
            "id": execution.id,
            "workflow_id": execution.workflow_id,
            "status": execution.status.value,
            "current_step": self._get_current_step(execution),
            "progress": self._calculate_progress(execution),
            "started_at": execution.started_at.isoformat()
            if execution.started_at
            else None,
            "completed_at": execution.completed_at.isoformat()
            if execution.completed_at
            else None,
            "error_message": execution.error_message,
        }

    def _get_current_step(self, execution: WorkflowExecution) -> Optional[str]:
        """Get current step being executed."""
        # This is a simplified implementation for MVP
        # In a more complex system, we'd track the current step in the execution
        return None

    def _calculate_progress(self, execution: WorkflowExecution) -> float:
        """Calculate workflow progress percentage."""
        if execution.status == WorkflowStatus.COMPLETED:
            return 100.0
        elif execution.status == WorkflowStatus.FAILED:
            return 0.0
        else:
            # Simplified progress calculation for MVP
            return 50.0  # Placeholder
