#!/bin/bash

echo "🚀 Starting InvestByYourself API Server..."
echo "========================================"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

# Run the Python startup script
python3 start-api.py
