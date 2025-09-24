#!/usr/bin/env python3
"""
InvestByYourself API Server Startup Script
Tech-036: Authentication System Implementation

This script starts the API server from the project root directory,
ensuring proper import paths and environment setup.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Change to the API directory for proper module resolution
api_dir = project_root / "api"
os.chdir(api_dir)

# Add the API directory to Python path
sys.path.insert(0, str(api_dir))

# Import and run the server
if __name__ == "__main__":
    import uvicorn

    from src.main import app

    print("🚀 Starting InvestByYourself API Server...")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"🐍 Python path: {sys.path[:3]}...")
    print("=" * 50)

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(api_dir)],
        log_level="info",
    )
