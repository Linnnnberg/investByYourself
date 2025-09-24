#!/usr/bin/env python3
"""
Test workflow database operations
"""

import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.database.connection import get_db_session, init_database
from src.services.workflow_database_service import WorkflowDatabaseService
from src.workflows.allocation_framework_steps import AllocationFrameworkSteps


async def test_workflow_db():
    """Test workflow database operations."""
    print("Testing workflow database operations...")

    try:
        # Initialize database first
        print("0. Initializing database...")
        await init_database()
        print("✅ Database initialized")

        # Get database session
        db_session_factory = await get_db_session()
        async with db_session_factory() as db_session:
            db_service = WorkflowDatabaseService(db_session)

            # Test creating a workflow
            print("1. Creating workflow...")
            workflow = AllocationFrameworkSteps.get_portfolio_creation_workflow()
            workflow_id = await db_service.create_workflow_definition(workflow)
            print(f"✅ Created workflow: {workflow_id}")

            # Test listing workflows
            print("2. Listing workflows...")
            workflows = await db_service.list_workflow_definitions(active_only=True)
            print(f"✅ Found {len(workflows)} workflows")

            for i, wf in enumerate(workflows):
                print(f"   {i+1}. {wf.name} ({wf.id})")
                print(f"      Steps: {len(wf.steps)}")
                print(f"      Entry points: {wf.entry_points}")
                print(f"      Exit points: {wf.exit_points}")

            print("✅ Database test completed successfully")

    except Exception as e:
        print(f"❌ Database test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_workflow_db())
