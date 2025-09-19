#!/usr/bin/env python3
"""
Basic Workflow Step Executors
InvestByYourself Financial Platform

Basic step executors for the minimal workflow engine.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

from core.workflow_engine_minimal import WorkflowStepExecutor
from core.workflow_minimal import WorkflowContext, WorkflowStep, WorkflowStepType

logger = logging.getLogger(__name__)


class DataCollectionExecutor(WorkflowStepExecutor):
    """Basic data collection step executor."""

    def execute(
        self, step: WorkflowStep, context: WorkflowContext, results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute data collection step."""
        logger.info(f"Executing data collection step: {step.id}")

        # Get required fields from step config
        required_fields = step.config.get("required_fields", [])
        collected_data = {}

        # For MVP, we'll use mock data collection
        # In the future, this will integrate with actual data collection services
        for field in required_fields:
            # Try to get data from context first
            if context.get_data(field):
                collected_data[field] = context.get_data(field)
            else:
                # Generate mock data for MVP
                collected_data[field] = self._generate_mock_data(field)

        # Store collected data in context
        for field, value in collected_data.items():
            context.update_data(field, value)

        result = {
            "status": "completed",
            "step_type": "data_collection",
            "collected_data": collected_data,
            "required_fields": required_fields,
            "executed_at": datetime.utcnow().isoformat(),
        }

        logger.info(f"Data collection completed: {step.id}")
        return result

    def validate(self, step: WorkflowStep, context: WorkflowContext) -> bool:
        """Validate data collection step."""
        required_fields = step.config.get("required_fields", [])

        # Check if all required fields are available or can be collected
        for field in required_fields:
            if not context.get_data(field) and not self._can_collect_field(field):
                logger.warning(f"Required field not available: {field}")
                return False

        return True

    def get_required_inputs(self) -> List[str]:
        """Return list of required input keys."""
        return []

    def get_outputs(self) -> List[str]:
        """Return list of output keys this step produces."""
        return ["collected_data", "status", "executed_at"]

    def _generate_mock_data(self, field: str) -> Any:
        """Generate mock data for a field."""
        mock_data = {
            "risk_tolerance": "moderate",
            "time_horizon": "10_years",
            "investment_goals": "retirement",
            "liquidity_needs": "low",
            "income_needs": "moderate",
        }
        return mock_data.get(field, f"mock_{field}")

    def _can_collect_field(self, field: str) -> bool:
        """Check if a field can be collected."""
        # For MVP, assume all fields can be collected
        return True


class DecisionExecutor(WorkflowStepExecutor):
    """Basic decision step executor."""

    def execute(
        self, step: WorkflowStep, context: WorkflowContext, results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute decision step."""
        logger.info(f"Executing decision step: {step.id}")

        # Get decision options from step config
        options = step.config.get("options", [])
        default = step.config.get("default")
        description = step.config.get("description", "")
        help_text = step.config.get("help_text", "")

        # For MVP, we'll use simple decision logic
        # In the future, this will integrate with actual decision-making services
        user_choice = context.get_data("user_choice")

        # Handle different option formats
        if isinstance(options, list) and options and isinstance(options[0], dict):
            # Complex options (dictionaries with id, name, etc.)
            option_ids = [
                opt.get("id", opt.get("name", str(i))) for i, opt in enumerate(options)
            ]
            if not user_choice:
                user_choice = default or option_ids[0] if option_ids else None
            elif user_choice not in option_ids:
                logger.warning(f"Invalid choice: {user_choice}, using default")
                user_choice = default or option_ids[0] if option_ids else None
        else:
            # Simple options (strings)
            if not user_choice:
                user_choice = default or (options[0] if options else None)
            elif user_choice not in options:
                logger.warning(f"Invalid choice: {user_choice}, using default")
                user_choice = default or (options[0] if options else None)

        # Store decision in context
        context.update_data(f"decision_{step.id}", user_choice)

        result = {
            "status": "completed",
            "step_type": "decision",
            "decision": user_choice,
            "options": options,
            "description": description,
            "help_text": help_text,
            "executed_at": datetime.utcnow().isoformat(),
        }

        logger.info(f"Decision completed: {step.id}, choice: {user_choice}")
        return result

    def validate(self, step: WorkflowStep, context: WorkflowContext) -> bool:
        """Validate decision step."""
        options = step.config.get("options", [])

        # For MVP, we'll allow decision steps without options
        # In the future, this can be more strict
        if not options:
            logger.info(
                f"No options provided for decision step {step.id}, using default behavior"
            )

        return True

    def get_required_inputs(self) -> List[str]:
        """Return list of required input keys."""
        return []

    def get_outputs(self) -> List[str]:
        """Return list of output keys this step produces."""
        return ["decision", "options", "status", "executed_at"]


class ValidationExecutor(WorkflowStepExecutor):
    """Basic validation step executor."""

    def execute(
        self, step: WorkflowStep, context: WorkflowContext, results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute validation step."""
        logger.info(f"Executing validation step: {step.id}")

        validation_rules = step.config.get("rules", {})
        validation_results = {}

        # Weight validation
        if step.config.get("weight_validation", False):
            weight_result = self._validate_weights(context)
            validation_results["weight_validation"] = weight_result

        # Constraint validation
        if step.config.get("constraint_validation", False):
            constraint_result = self._validate_constraints(context)
            validation_results["constraint_validation"] = constraint_result

        # Diversification check
        if step.config.get("diversification_check", False):
            diversification_result = self._validate_diversification(context)
            validation_results["diversification_check"] = diversification_result

        # Check if all validations passed
        all_passed = all(
            result.get("passed", False) for result in validation_results.values()
        )

        result = {
            "status": "completed" if all_passed else "failed",
            "step_type": "validation",
            "validation_results": validation_results,
            "all_passed": all_passed,
            "executed_at": datetime.utcnow().isoformat(),
        }

        if not all_passed:
            result["error_message"] = "Validation failed"
            logger.warning(f"Validation failed: {step.id}")
        else:
            logger.info(f"Validation passed: {step.id}")

        return result

    def validate(self, step: WorkflowStep, context: WorkflowContext) -> bool:
        """Validate validation step."""
        # Validation steps are always valid to execute
        return True

    def get_required_inputs(self) -> List[str]:
        """Return list of required input keys."""
        return []

    def get_outputs(self) -> List[str]:
        """Return list of output keys this step produces."""
        return ["validation_results", "all_passed", "status", "executed_at"]

    def _validate_weights(self, context: WorkflowContext) -> Dict[str, Any]:
        """Validate portfolio weights."""
        # Simplified weight validation for MVP
        total_weight = context.get_data("total_weight", 0.0)

        return {
            "passed": abs(total_weight - 1.0) < 0.001,
            "total_weight": total_weight,
            "expected": 1.0,
            "tolerance": 0.001,
        }

    def _validate_constraints(self, context: WorkflowContext) -> Dict[str, Any]:
        """Validate portfolio constraints."""
        # Simplified constraint validation for MVP
        constraints = context.get_data("constraints", {})

        return {
            "passed": True,  # Placeholder for MVP
            "constraints_checked": list(constraints.keys()),
            "violations": [],
        }

    def _validate_diversification(self, context: WorkflowContext) -> Dict[str, Any]:
        """Validate portfolio diversification."""
        # Simplified diversification check for MVP
        positions = context.get_data("positions", [])

        return {
            "passed": len(positions) >= 3,  # At least 3 positions for diversification
            "position_count": len(positions),
            "minimum_positions": 3,
        }


class UserInteractionExecutor(WorkflowStepExecutor):
    """Basic user interaction step executor."""

    def execute(
        self, step: WorkflowStep, context: WorkflowContext, results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute user interaction step."""
        logger.info(f"Executing user interaction step: {step.id}")

        # Get user input from context
        user_input = context.get_data("user_input", {})

        # Process user input based on step configuration
        processed_input = self._process_user_input(step, user_input)

        # Store processed input in context
        context.update_data(f"interaction_{step.id}", processed_input)

        result = {
            "status": "completed",
            "step_type": "user_interaction",
            "user_input": processed_input,
            "interaction_type": step.config.get("interaction_type", "general"),
            "executed_at": datetime.utcnow().isoformat(),
        }

        logger.info(f"User interaction completed: {step.id}")
        return result

    def validate(self, step: WorkflowStep, context: WorkflowContext) -> bool:
        """Validate user interaction step."""
        # User interaction steps are always valid to execute
        return True

    def get_required_inputs(self) -> List[str]:
        """Return list of required input keys."""
        return ["user_input"]

    def get_outputs(self) -> List[str]:
        """Return list of output keys this step produces."""
        return ["user_input", "interaction_type", "status", "executed_at"]

    def _process_user_input(
        self, step: WorkflowStep, user_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process user input based on step configuration."""
        # For MVP, we'll do basic processing
        # In the future, this will handle complex user interactions

        processed = {
            "raw_input": user_input,
            "processed_at": datetime.utcnow().isoformat(),
            "step_id": step.id,
        }

        # Add step-specific processing
        if step.config.get("search_enabled", False):
            processed["search_results"] = self._mock_search_results(user_input)

        if step.config.get("drag_drop_enabled", False):
            processed["drag_drop_data"] = self._process_drag_drop_data(user_input)

        return processed

    def _mock_search_results(self, user_input: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate mock search results for MVP."""
        return [
            {
                "id": "mock_product_1",
                "name": "Mock ETF 1",
                "symbol": "MOCK1",
                "asset_class": "equity",
                "sector": "technology",
            },
            {
                "id": "mock_product_2",
                "name": "Mock ETF 2",
                "symbol": "MOCK2",
                "asset_class": "bonds",
                "sector": "government",
            },
        ]

    def _process_drag_drop_data(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Process drag and drop data for MVP."""
        return {
            "buckets": user_input.get("buckets", []),
            "weights": user_input.get("weights", {}),
            "hierarchy": user_input.get("hierarchy", {}),
        }
