#!/usr/bin/env python3
"""
InvestByYourself - Environment Security Scanner
Tech-026: Unified Environment Configuration Management

This script scans environment configuration files for security issues using
GitGuardian and additional custom security checks.

Usage:
    python config/scripts/scan_env_security.py --file .env.development
    python config/scripts/scan_env_security.py --environment development
    python config/scripts/scan_env_security.py --all
"""

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set

from validate_env import ValidationLevel, ValidationResult


class SecurityLevel(Enum):
    """Security issue severity levels."""

    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"  # For non-security but important issues
    ERROR = "ERROR"  # For operational errors


@dataclass
class SecurityIssue:
    """Represents a security issue found in configuration."""

    level: SecurityLevel
    message: str
    file: str
    line: Optional[int] = None
    variable: Optional[str] = None
    suggestion: Optional[str] = None


class EnvironmentSecurityScanner:
    """Scans environment configuration files for security issues."""

    def __init__(self, config_root: Path):
        self.config_root = config_root
        self.project_root = config_root.parent

        # Define patterns for sensitive data
        self.sensitive_patterns = {
            "api_key": r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"]([\w\-]{16,})['\"]\s*$",
            "password": r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"]([\w\-@#$%^&*]{8,})['\"]\s*$",
            "token": r"(?i)(token|secret)\s*[:=]\s*['\"]([\w\-]{16,})['\"]\s*$",
            "private_key": r"(?i)-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----",
            "aws_key": r"(?i)(aws_access_key_id|aws_secret_access_key)\s*[:=]\s*['\"]([\w\-]{16,})['\"]\s*$",
            "supabase": r"(?i)(supabase.*key)\s*[:=]\s*['\"]([\w\-]{16,})['\"]\s*$",
        }

        # Define weak default patterns
        self.weak_defaults = {
            "password": [
                "password",
                "admin",
                "root",
                "test",
                "dev",
                "prod",
                "staging",
                "123456",
            ],
            "token": ["secret", "token", "changeme", "default"],
            "key": ["key", "apikey", "secretkey", "accesskey"],
        }

    def scan_file(self, file_path: Path) -> List[SecurityIssue]:
        """Scan a single environment file for security issues."""
        if not file_path.exists():
            return [
                SecurityIssue(
                    SecurityLevel.ERROR,
                    f"File not found: {file_path}",
                    str(file_path),
                )
            ]

        issues = []

        # Run GitGuardian scan
        gitguardian_issues = self._run_gitguardian_scan(file_path)
        issues.extend(gitguardian_issues)

        # Run custom security checks
        custom_issues = self._run_custom_checks(file_path)
        issues.extend(custom_issues)

        return issues

    def scan_environment(self, environment: str) -> List[SecurityIssue]:
        """Scan all configuration files for an environment."""
        issues = []

        # Find all .env files for the environment
        env_files = list(self.project_root.glob(f".env.{environment}*"))
        env_files.extend(list(self.project_root.glob(f".env.*.{environment}")))

        if not env_files:
            issues.append(
                SecurityIssue(
                    SecurityLevel.WARNING,
                    f"No configuration files found for environment: {environment}",
                    str(self.project_root),
                )
            )
            return issues

        for env_file in env_files:
            file_issues = self.scan_file(env_file)
            issues.extend(file_issues)

        return issues

    def scan_all(self) -> Dict[str, List[SecurityIssue]]:
        """Scan all environment configurations."""
        environments = ["development", "staging", "production"]
        results = {}

        for env in environments:
            results[env] = self.scan_environment(env)

        # Global security scan
        global_issues = self._run_global_security_scan()
        results["global"] = global_issues

        return results

    def _run_gitguardian_scan(self, file_path: Path) -> List[SecurityIssue]:
        """Run GitGuardian scan on a file."""
        issues = []

        try:
            # Run ggshield scan-file
            result = subprocess.run(
                ["ggshield", "secret", "scan", "file", str(file_path)],
                capture_output=True,
                text=True,
            )

            # Parse GitGuardian output
            if result.returncode != 0 and result.stderr:
                # Convert GitGuardian findings to SecurityIssues
                for line in result.stderr.split("\n"):
                    if "Detected" in line and "secret" in line:
                        issues.append(
                            SecurityIssue(
                                SecurityLevel.HIGH,
                                f"GitGuardian detected potential secret: {line}",
                                str(file_path),
                                suggestion="Replace with environment variable or secure secret management",
                            )
                        )

        except subprocess.CalledProcessError as e:
            issues.append(
                SecurityIssue(
                    SecurityLevel.ERROR,
                    f"Error running GitGuardian scan: {e}",
                    str(file_path),
                )
            )
        except Exception as e:
            issues.append(
                SecurityIssue(
                    SecurityLevel.ERROR,
                    f"Unexpected error during GitGuardian scan: {e}",
                    str(file_path),
                )
            )

        return issues

    def _run_custom_checks(self, file_path: Path) -> List[SecurityIssue]:
        """Run custom security checks on a file."""
        issues = []
        content = file_path.read_text()

        # Check for sensitive patterns
        for key, pattern in self.sensitive_patterns.items():
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                line_num = content.count("\n", 0, match.start()) + 1
                issues.append(
                    SecurityIssue(
                        SecurityLevel.HIGH,
                        f"Found potential {key} in plaintext",
                        str(file_path),
                        line=line_num,
                        suggestion="Use environment variable reference instead of hardcoded value",
                    )
                )

        # Check for weak defaults
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip().lower()
                value = value.strip().strip("'\"")

                # Check for weak default values
                for category, weak_values in self.weak_defaults.items():
                    if any(term in key for term in [category, f"{category}_"]):
                        if any(weak in value.lower() for weak in weak_values):
                            issues.append(
                                SecurityIssue(
                                    SecurityLevel.MEDIUM,
                                    f"Weak default value for {key}",
                                    str(file_path),
                                    line=i,
                                    variable=key,
                                    suggestion="Use a strong, unique value",
                                )
                            )

        # Check for unencrypted sensitive variables
        for line_num, line in enumerate(lines, 1):
            if any(
                term in line.lower()
                for term in ["password", "secret", "key", "token", "credential"]
            ):
                if not line.strip().startswith("#") and "=${" not in line:
                    issues.append(
                        SecurityIssue(
                            SecurityLevel.MEDIUM,
                            "Sensitive variable should use environment reference",
                            str(file_path),
                            line=line_num,
                            suggestion="Use ${VAR} syntax to reference sensitive values",
                        )
                    )

        return issues

    def _run_global_security_scan(self) -> List[SecurityIssue]:
        """Run global security checks across all configuration."""
        issues = []

        # Check for sensitive files
        sensitive_files = [".env", ".env.local", ".env.development.local"]
        for file in sensitive_files:
            file_path = self.project_root / file
            if file_path.exists():
                issues.append(
                    SecurityIssue(
                        SecurityLevel.HIGH,
                        f"Found sensitive file in version control: {file}",
                        str(file_path),
                        suggestion="Add to .gitignore and use .env.example instead",
                    )
                )

        # Check .gitignore configuration
        gitignore_path = self.project_root / ".gitignore"
        if gitignore_path.exists():
            content = gitignore_path.read_text()
            if ".env" not in content:
                issues.append(
                    SecurityIssue(
                        SecurityLevel.MEDIUM,
                        ".env files not excluded in .gitignore",
                        str(gitignore_path),
                        suggestion="Add .env* to .gitignore",
                    )
                )

        return issues


def main():
    """Main entry point for the environment security scanner."""
    parser = argparse.ArgumentParser(
        description="Scan environment configuration files for security issues"
    )
    parser.add_argument("--file", help="Scan a specific environment file")
    parser.add_argument(
        "--environment",
        choices=["development", "staging", "production"],
        help="Scan all files for an environment",
    )
    parser.add_argument(
        "--all", action="store_true", help="Scan all environment configurations"
    )
    parser.add_argument(
        "--config-root",
        default="config",
        help="Configuration root directory (default: config)",
    )
    parser.add_argument(
        "--output-format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args()

    # Validate arguments
    if not any([args.file, args.environment, args.all]):
        print("Error: Must specify --file, --environment, or --all")
        sys.exit(1)

    config_root = Path(args.config_root)
    if not config_root.exists():
        print(f"Error: Configuration root directory not found: {config_root}")
        sys.exit(1)

    scanner = EnvironmentSecurityScanner(config_root)

    try:
        if args.file:
            file_path = Path(args.file)
            results = scanner.scan_file(file_path)
        elif args.environment:
            results = scanner.scan_environment(args.environment)
        else:  # args.all
            all_results = scanner.scan_all()
            results = []
            for env, env_results in all_results.items():
                results.extend(env_results)

        # Output results
        if args.output_format == "json":
            output = []
            for result in results:
                output.append(
                    {
                        "level": result.level.value,
                        "message": result.message,
                        "file": result.file,
                        "line": result.line,
                        "variable": result.variable,
                        "suggestion": result.suggestion,
                    }
                )
            print(json.dumps(output, indent=2))
        else:
            # Text output
            if not results:
                print("✅ No security issues found")
            else:
                # Group by level
                by_level = {}
                for result in results:
                    if result.level not in by_level:
                        by_level[result.level] = []
                    by_level[result.level].append(result)

                # Output by severity
                for level in [
                    SecurityLevel.CRITICAL,
                    SecurityLevel.HIGH,
                    SecurityLevel.MEDIUM,
                    SecurityLevel.LOW,
                    SecurityLevel.INFO,
                ]:
                    if level in by_level:
                        print(f"\n{level.value} ({len(by_level[level])} issues):")
                        for result in by_level[level]:
                            print(f"  • {result.message}")
                            print(f"    File: {result.file}")
                            if result.line:
                                print(f"    Line: {result.line}")
                            if result.variable:
                                print(f"    Variable: {result.variable}")
                            if result.suggestion:
                                print(f"    Suggestion: {result.suggestion}")

        # Exit with error code if critical or high issues found
        critical_issues = sum(
            1
            for r in results
            if r.level in [SecurityLevel.CRITICAL, SecurityLevel.HIGH]
        )
        if critical_issues > 0:
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
