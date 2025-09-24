#!/usr/bin/env python3
"""
Test exact API endpoint logic
"""

import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.database.connection import get_db_session, init_database
from src.models.workflow import WorkflowListResponse
from src.services.workflow_database_service import WorkflowDatabaseService


async def test_api_exact():
    """Test exact API endpoint logic."""
    print("Testing exact API endpoint logic...")

    try:
        # Initialize database first
        print("1. Initializing database...")
        await init_database()
        print("✅ Database initialized")

        # Get database session
        db_session_factory = await get_db_session()
        async with db_session_factory() as db_session:
            db_service = WorkflowDatabaseService(db_session)

            print("2. Calling list_workflow_definitions...")
            workflows = await db_service.list_workflow_definitions(active_only=True)
            print(f"✅ Found {len(workflows)} workflows")

            print("3. Creating WorkflowListResponse...")
            response = WorkflowListResponse(workflows=workflows, total=len(workflows))
            print(f"✅ WorkflowListResponse created: {response}")

            print("4. Testing model_dump...")
            response_dict = response.model_dump()
            print(f"✅ model_dump successful: {response_dict}")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_api_exact())
