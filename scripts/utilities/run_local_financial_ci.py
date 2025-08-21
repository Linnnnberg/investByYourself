#!/usr/bin/env python3
"""
Local Financial CI Runner for investByYourself

This script runs the full financial CI/CD pipeline locally,
allowing developers to test their changes before pushing to GitHub.
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List


class FinancialCIRunner:
    """Local runner for financial CI/CD pipeline."""

    def __init__(
        self,
        skip_tests: bool = False,
        skip_security: bool = False,
        skip_integration: bool = False,
    ):
        self.skip_tests = skip_tests
        self.skip_security = skip_security
        self.skip_integration = skip_integration
        self.results: Dict[str, bool] = {}
        self.start_time = time.time()

        # Set CI environment
        os.environ["CI"] = "true"
        os.environ["FINANCIAL_CI"] = "true"

        # Set test environment variables
        os.environ["YAHOO_FINANCE_API_KEY"] = "test-key"
        os.environ["ALPHA_VANTAGE_API_KEY"] = "test-key"
        os.environ["FRED_API_KEY"] = "test-key"
        os.environ["DATABASE_URL"] = "sqlite:///./test_financial.db"
        os.environ["SECRET_KEY"] = "test-secret-key-for-financial-ci-12345"
        os.environ["MARKET_DATA_CACHE_DIR"] = ".cache/market_data"
        os.environ["FINANCIAL_CALCULATION_PRECISION"] = "0.01"

    def run_command(self, command: List[str], description: str) -> bool:
        """Run a command and return success status."""
        print(f"\n{'='*60}")
        print(f"Running: {description}")
        print(f"Command: {' '.join(command)}")
        print(f"{'='*60}")

        try:
            result = subprocess.run(
                command, check=True, capture_output=True, text=True, cwd=Path.cwd()
            )
            print(f"✅ {description} completed successfully")
            if result.stdout:
                print("Output:", result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ {description} failed with exit code {e.returncode}")
            if e.stdout:
                print("Stdout:", e.stdout)
            if e.stderr:
                print("Stderr:", e.stderr)
            return False

    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met."""
        print("🔍 Checking prerequisites...")

        # Check Python version
        python_version = sys.version_info
        if python_version.major < 3 or (
            python_version.major == 3 and python_version.minor < 8
        ):
            print(
                f"❌ Python 3.8+ required, found {python_version.major}.{python_version.minor}"
            )
            return False

        print(
            f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}"
        )

        # Check required files
        required_files = [
            "requirements.txt",
            ".pre-commit-config.yaml",
            "tests/test_financial_basic.py",
        ]

        for file_path in required_files:
            if not Path(file_path).exists():
                print(f"❌ Required file not found: {file_path}")
                return False
            print(f"✅ Found {file_path}")

        return True

    def install_dependencies(self) -> bool:
        """Install required dependencies."""
        print("\n📦 Installing dependencies...")

        # Install all requirements
        if not self.run_command(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            "Installing all dependencies",
        ):
            return False

        # Install pre-commit hooks
        if not self.run_command(
            [sys.executable, "-m", "pre_commit", "install"],
            "Installing pre-commit hooks",
        ):
            return False

        return True

    def run_pre_commit_checks(self) -> bool:
        """Run pre-commit checks."""
        print("\n🔍 Running pre-commit checks...")

        if not self.run_command(
            [sys.executable, "-m", "pre_commit", "run", "--all-files"],
            "Running pre-commit hooks",
        ):
            return False

        return True

    def run_financial_tests(self) -> bool:
        """Run financial tests."""
        if self.skip_tests:
            print("\n⏭️ Skipping financial tests as requested")
            return True

        print("\n🧪 Running financial tests...")

        # Run basic financial tests
        if not self.run_command(
            [sys.executable, "-m", "pytest", "tests/test_financial_basic.py", "-v"],
            "Running basic financial tests",
        ):
            return False

        # Run with coverage
        if not self.run_command(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/",
                "--cov=scripts",
                "--cov-report=term-missing",
            ],
            "Running tests with coverage",
        ):
            return False

        return True

    def run_code_quality_checks(self) -> bool:
        """Run code quality checks."""
        print("\n📏 Running code quality checks...")

        # Black formatting check
        if not self.run_command(
            [sys.executable, "-m", "black", "--check", "--diff", "scripts/", "tests/"],
            "Checking code formatting with Black",
        ):
            return False

        # Flake8 linting
        if not self.run_command(
            [
                sys.executable,
                "-m",
                "flake8",
                "scripts/",
                "tests/",
                "--max-line-length=88",
                "--extend-ignore=E203,W503",
            ],
            "Running Flake8 linting",
        ):
            return False

        # MyPy type checking
        if not self.run_command(
            [sys.executable, "-m", "mypy", "scripts/", "--ignore-missing-imports"],
            "Running MyPy type checking",
        ):
            return False

        return True

    def run_security_checks(self) -> bool:
        """Run security checks."""
        if self.skip_security:
            print("\n⏭️ Skipping security checks as requested")
            return True

        print("\n🔒 Running security checks...")

        # Bandit security scan
        if not self.run_command(
            [
                sys.executable,
                "-m",
                "bandit",
                "-r",
                "scripts/",
                "-f",
                "json",
                "-o",
                "bandit-report.json",
            ],
            "Running Bandit security scan",
        ):
            return False

        # Safety dependency check
        if not self.run_command(
            [
                sys.executable,
                "-m",
                "safety",
                "check",
                "--json",
                "--output",
                "safety-report.json",
            ],
            "Running Safety dependency check",
        ):
            return False

        return True

    def run_financial_validation(self) -> bool:
        """Run financial data validation."""
        print("\n📊 Running financial data validation...")

        # This will be implemented in Phase 2
        print("ℹ️ Financial data validation will be implemented in Phase 2")
        return True

    def run_integration_tests(self) -> bool:
        """Run integration tests."""
        if self.skip_integration:
            print("\n⏭️ Skipping integration tests as requested")
            return True

        print("\n🔗 Running integration tests...")

        # This will be implemented in Phase 2
        print("ℹ️ Integration tests will be implemented in Phase 2")
        return True

    def generate_documentation(self) -> bool:
        """Generate financial documentation."""
        print("\n📚 Generating financial documentation...")

        # This will be implemented in Phase 2
        print("ℹ️ Documentation generation will be implemented in Phase 2")
        return True

    def run_pipeline(self) -> bool:
        """Run the complete financial CI pipeline."""
        print("🚀 Starting Local Financial CI Pipeline")
        print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Python: {sys.executable}")
        print(f"Working Directory: {Path.cwd()}")

        # Pipeline steps
        pipeline_steps = [
            ("Prerequisites Check", self.check_prerequisites),
            ("Dependencies Installation", self.install_dependencies),
            ("Pre-commit Checks", self.run_pre_commit_checks),
            ("Code Quality Checks", self.run_code_quality_checks),
            ("Financial Tests", self.run_financial_tests),
            ("Security Checks", self.run_security_checks),
            ("Financial Validation", self.run_financial_validation),
            ("Integration Tests", self.run_integration_tests),
            ("Documentation Generation", self.generate_documentation),
        ]

        # Execute pipeline steps
        for step_name, step_function in pipeline_steps:
            print(f"\n{'='*80}")
            print(f"Step: {step_name}")
            print(f"{'='*80}")

            try:
                success = step_function()
                self.results[step_name] = success

                if not success:
                    print(f"\n❌ Pipeline failed at step: {step_name}")
                    return False

            except Exception as e:
                print(f"\n❌ Pipeline failed at step {step_name} with error: {e}")
                self.results[step_name] = False
                return False

        return True

    def print_summary(self):
        """Print pipeline summary."""
        end_time = time.time()
        duration = end_time - self.start_time

        print(f"\n{'='*80}")
        print("🏁 FINANCIAL CI PIPELINE SUMMARY")
        print(f"{'='*80}")

        print(f"Duration: {duration:.2f} seconds")
        print(f"Total Steps: {len(self.results)}")

        successful_steps = sum(1 for success in self.results.values() if success)
        print(f"Successful Steps: {successful_steps}")
        print(f"Failed Steps: {len(self.results) - successful_steps}")

        print(f"\nStep Results:")
        for step_name, success in self.results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {step_name}: {status}")

        if all(self.results.values()):
            print(f"\n🎉 All pipeline steps completed successfully!")
            print(f"Your code is ready for commit and push!")
        else:
            print(
                f"\n⚠️ Some pipeline steps failed. Please fix the issues before committing."
            )

        print(f"{'='*80}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Local Financial CI Runner for investByYourself"
    )
    parser.add_argument(
        "--skip-tests", action="store_true", help="Skip financial tests"
    )
    parser.add_argument(
        "--skip-security", action="store_true", help="Skip security checks"
    )
    parser.add_argument(
        "--skip-integration", action="store_true", help="Skip integration tests"
    )

    args = parser.parse_args()

    # Create and run CI runner
    runner = FinancialCIRunner(
        skip_tests=args.skip_tests,
        skip_security=args.skip_security,
        skip_integration=args.skip_integration,
    )

    try:
        success = runner.run_pipeline()
        runner.print_summary()

        if not success:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️ Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Pipeline failed with unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
