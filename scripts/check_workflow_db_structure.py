#!/usr/bin/env python3
"""
Check Workflow DB Structure
InvestByYourself Financial Platform

Check the actual workflow definition structure from the database.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api", "src"))

# Change to api directory for proper imports
os.chdir(os.path.join(os.path.dirname(__file__), "..", "api"))

from src.database.sync_connection import get_db
from src.services.workflow_database_service import WorkflowDatabaseService


def check_workflow_db_structure():
    """Check the actual workflow definition structure from database."""
    print("Checking workflow definition structure from database...")

    try:
        # Get database session
        db = next(get_db())
        db_service = WorkflowDatabaseService(db)

        # Get workflow definition
        workflow_def = db_service.get_workflow_definition(
            "comprehensive_portfolio_creation"
        )

        if workflow_def:
            print(f"Workflow ID: {workflow_def.id}")
            print(f"Workflow Name: {workflow_def.name}")
            print(f"Workflow Description: {workflow_def.description}")
            print(f"Definition type: {type(workflow_def.definition)}")
            print(f"Definition: {workflow_def.definition}")

            if workflow_def.definition:
                print(f"Definition keys: {list(workflow_def.definition.keys())}")
                steps = workflow_def.definition.get("steps", [])
                print(f"Steps in definition: {len(steps)}")
                if steps:
                    print(f"First step: {steps[0]}")
            else:
                print("Definition is None or empty")
        else:
            print("Workflow not found")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    check_workflow_db_structure()
