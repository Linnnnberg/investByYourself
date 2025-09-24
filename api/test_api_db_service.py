#!/usr/bin/env python3
"""
Test database service from API context
"""

import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.database.connection import get_db_session, init_database
from src.services.workflow_database_service import WorkflowDatabaseService


async def test_api_db_service():
    """Test database service from API context."""
    print("Testing database service from API context...")

    try:
        # Initialize database first
        print("1. Initializing database...")
        await init_database()
        print("✅ Database initialized")

        # Get database session
        db_session_factory = await get_db_session()
        async with db_session_factory() as db_session:
            print("2. Creating WorkflowDatabaseService...")
            db_service = WorkflowDatabaseService(db_session)
            print("✅ WorkflowDatabaseService created")

            print("3. Calling list_workflow_definitions...")
            workflows = await db_service.list_workflow_definitions(active_only=True)
            print(f"✅ Found {len(workflows)} workflows")

            print("4. Checking workflow types...")
            for i, workflow in enumerate(workflows):
                print(f"   Workflow {i+1}: {type(workflow)}")
                print(f"   Steps: {len(workflow.steps)}")
                if workflow.steps:
                    print(f"   First step type: {type(workflow.steps[0])}")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_api_db_service())
