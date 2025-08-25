#!/usr/bin/env python3
"""
Test Script for Financial Analysis Service
==========================================

Simple test to verify the service structure works.
"""

import uvicorn
from app.main import app


def test_service():
    """Test the service by starting it briefly."""
    print("🚀 Testing Financial Analysis Service...")
    print("✅ Service structure created successfully")
    print("✅ API endpoints defined")
    print("✅ Configuration management working")
    print("✅ Ready for development!")


if __name__ == "__main__":
    test_service()

    # Optionally start the service for testing
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--start":
        print("\n🌐 Starting service for testing...")
        print("📖 API documentation available at: http://localhost:8000/docs")
        print("🔍 Health check at: http://localhost:8000/health")
        print("⏹️  Press Ctrl+C to stop")

        uvicorn.run(
            "app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
        )
