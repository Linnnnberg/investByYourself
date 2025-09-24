#!/usr/bin/env python3
"""
Test WorkflowListResponse creation
"""

import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.database.connection import get_db_session, init_database
from src.models.workflow import WorkflowListResponse
from src.services.workflow_database_service import WorkflowDatabaseService


async def test_workflow_response():
    """Test WorkflowListResponse creation."""
    print("Testing WorkflowListResponse creation...")

    try:
        # Initialize database first
        print("1. Initializing database...")
        await init_database()
        print("✅ Database initialized")

        # Get database session
        db_session_factory = await get_db_session()
        async with db_session_factory() as db_session:
            db_service = WorkflowDatabaseService(db_session)

            print("2. Getting workflows from database...")
            workflows = await db_service.list_workflow_definitions(active_only=True)
            print(f"✅ Found {len(workflows)} workflows")

            print("3. Checking workflow types...")
            for i, workflow in enumerate(workflows):
                print(f"   Workflow {i+1}: {type(workflow)}")
                print(f"   Steps: {len(workflow.steps)}")
                if workflow.steps:
                    print(f"   First step type: {type(workflow.steps[0])}")
                    print(f"   First step: {workflow.steps[0]}")

            print("4. Creating WorkflowListResponse...")
            response = WorkflowListResponse(workflows=workflows, total=len(workflows))
            print(f"✅ WorkflowListResponse created successfully: {response}")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_workflow_response())
