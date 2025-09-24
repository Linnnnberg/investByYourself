#!/usr/bin/env python3
"""
Populate database with default workflows
"""

import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.database.connection import get_db_session, init_database
from src.services.workflow_database_service import WorkflowDatabaseService
from src.workflows.allocation_framework_steps import AllocationFrameworkSteps


async def populate_workflows():
    """Populate database with default workflows."""
    print("Populating database with default workflows...")

    try:
        # Initialize database first
        print("1. Initializing database...")
        await init_database()
        print("✅ Database initialized")

        # Get database session
        db_session_factory = await get_db_session()
        async with db_session_factory() as db_session:
            db_service = WorkflowDatabaseService(db_session)

            print("2. Creating default workflows...")
            default_workflows = [
                AllocationFrameworkSteps.get_portfolio_creation_workflow(),
                AllocationFrameworkSteps.get_framework_builder_workflow(),
                AllocationFrameworkSteps.get_rebalancing_workflow(),
            ]

            for i, workflow in enumerate(default_workflows):
                print(f"   Creating workflow {i+1}: {workflow.name}")
                await db_service.create_workflow_definition(workflow)
                print(f"   ✅ Workflow {i+1} created successfully")

            print("3. Verifying workflows...")
            workflows = await db_service.list_workflow_definitions(active_only=True)
            print(f"✅ Found {len(workflows)} workflows in database")

            for workflow in workflows:
                print(f"   - {workflow.name} ({workflow.id})")

    except Exception as e:
        print(f"❌ Population failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(populate_workflows())
