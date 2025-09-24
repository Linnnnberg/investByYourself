#!/usr/bin/env python3
"""
Check what's in the database
"""

import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.database.connection import get_db_session, init_database
from src.services.workflow_database_service import WorkflowDatabaseService


async def check_database():
    """Check what's in the database."""
    print("Checking database contents...")

    try:
        # Initialize database first
        await init_database()

        # Get database session
        db_session_factory = await get_db_session()
        async with db_session_factory() as db_session:
            db_service = WorkflowDatabaseService(db_session)

            # Get workflows
            workflows = await db_service.list_workflow_definitions(active_only=True)
            print(f"Found {len(workflows)} workflows:")
            for workflow in workflows:
                print(f"  - {workflow.name} ({workflow.id})")
                print(f"    Steps: {len(workflow.steps)}")
                print(f"    Created: {workflow.created_at}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(check_database())
