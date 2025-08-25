#!/usr/bin/env python3
"""
Test runner for Financial Analysis Service.

This script runs the complete test suite with coverage reporting.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n🔍 {description}")
    print(f"Running: {command}")

    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def main():
    """Main test runner function."""
    print("🚀 Financial Analysis Service - Test Suite Runner")
    print("=" * 60)

    # Change to the service directory
    service_dir = Path(__file__).parent
    os.chdir(service_dir)

    # Check if we're in the right directory
    if not (service_dir / "app").exists():
        print(
            "❌ Error: app directory not found. Make sure you're in the service directory."
        )
        sys.exit(1)

    # Install dependencies if needed
    print("\n📦 Checking dependencies...")
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("❌ Failed to install dependencies")
        sys.exit(1)

    # Run tests with coverage
    print("\n🧪 Running test suite...")
    test_commands = [
        "pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html",
        "pytest tests/ -v --tb=short",
        "pytest tests/ --cov=app --cov-report=xml",
    ]

    all_tests_passed = True
    for cmd in test_commands:
        if not run_command(cmd, f"Running tests with: {cmd.split()[0]}"):
            all_tests_passed = False

    # Run code quality checks
    print("\n🔍 Running code quality checks...")
    quality_commands = [
        "black --check app/",
        "isort --check-only app/",
        "flake8 app/ --max-line-length=88 --extend-ignore=E203",
        "mypy app/ --ignore-missing-imports",
    ]

    for cmd in quality_commands:
        run_command(cmd, f"Code quality check: {cmd.split()[0]}")

    # Summary
    print("\n" + "=" * 60)
    if all_tests_passed:
        print("🎉 All tests passed successfully!")
        print("📊 Coverage report generated in htmlcov/")
        print("📈 XML coverage report generated for CI/CD")
    else:
        print("⚠️  Some tests failed. Please review the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
