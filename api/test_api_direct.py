#!/usr/bin/env python3
"""
Test API directly
"""

import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.api.v1.endpoints.workflows import list_workflows
from src.database.connection import get_db_session, init_database


async def test_api_direct():
    """Test API endpoint directly."""
    print("Testing API endpoint directly...")

    try:
        # Initialize database first
        print("1. Initializing database...")
        await init_database()
        print("✅ Database initialized")

        # Get database session
        db_session_factory = await get_db_session()
        async with db_session_factory() as db_session:
            print("2. Testing list_workflows endpoint...")
            result = await list_workflows(db_session)
            print(f"✅ API endpoint result: {result}")

    except Exception as e:
        print(f"❌ API test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_api_direct())
