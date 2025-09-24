#!/usr/bin/env python3
"""
Minimal API reproduction test to isolate the serialization error
"""

import asyncio
import os
import sys

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.database.connection import get_db_session, init_database
from src.models.workflow import WorkflowListResponse
from src.services.workflow_database_service import WorkflowDatabaseService

# Create minimal FastAPI app
app = FastAPI()


@app.get("/test-minimal")
async def test_minimal_endpoint():
    """Minimal test endpoint without response model."""
    try:
        # Initialize database
        await init_database()

        # Get database session
        db_session_factory = await get_db_session()
        async with db_session_factory() as db_session:
            db_service = WorkflowDatabaseService(db_session)
            workflows = await db_service.list_workflow_definitions(active_only=True)

            # Return raw data
            return {
                "workflows": [workflow.model_dump() for workflow in workflows],
                "total": len(workflows),
            }
    except Exception as e:
        import traceback

        traceback.print_exc()
        return {"error": str(e)}


@app.get("/test-with-model", response_model=WorkflowListResponse)
async def test_with_model_endpoint():
    """Test endpoint with response model."""
    try:
        # Initialize database
        await init_database()

        # Get database session
        db_session_factory = await get_db_session()
        async with db_session_factory() as db_session:
            db_service = WorkflowDatabaseService(db_session)
            workflows = await db_service.list_workflow_definitions(active_only=True)

            # Return with Pydantic model
            return WorkflowListResponse(workflows=workflows, total=len(workflows))
    except Exception as e:
        import traceback

        traceback.print_exc()
        return {"error": str(e)}


def test_minimal_reproduction():
    """Test minimal reproduction."""
    print("Testing minimal API reproduction...")

    # Create test client
    client = TestClient(app)

    print("\n1. Testing minimal endpoint (no response model)...")
    try:
        response = client.get("/test-minimal")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
            print("   ✅ Minimal endpoint works")
        else:
            print(f"   ❌ Minimal endpoint failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Minimal endpoint error: {e}")

    print("\n2. Testing with model endpoint (with response model)...")
    try:
        response = client.get("/test-with-model")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data}")
            print("   ✅ Model endpoint works")
        else:
            print(f"   ❌ Model endpoint failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Model endpoint error: {e}")


if __name__ == "__main__":
    test_minimal_reproduction()
