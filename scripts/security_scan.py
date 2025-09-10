#!/usr/bin/env python3
"""
Security Scanner for investByYourself Codebase
Scans for hardcoded credentials, secrets, and other security issues.
"""

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Set


class SecurityScanner:
    """Scans codebase for security vulnerabilities."""

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.issues = []

        # Patterns to detect secrets and credentials
        self.secret_patterns = {
            "password": r"password\s*[=:]\s*['\"][^'\"]+['\"]",
            "secret": r"secret\s*[=:]\s*['\"][^'\"]+['\"]",
            "api_key": r"api_key\s*[=:]\s*['\"][^'\"]+['\"]",
            "token": r"token\s*[=:]\s*['\"][^'\"]+['\"]",
            "credential": r"credential\s*[=:]\s*['\"][^'\"]+['\"]",
            "private_key": r"private_key\s*[=:]\s*['\"][^'\"]+['\"]",
            "access_key": r"access_key\s*[=:]\s*['\"][^'\"]+['\"]",
            "secret_key": r"secret_key\s*[=:]\s*['\"][^'\"]+['\"]",
            "auth": r"auth\s*[=:]\s*['\"][^'\"]+['\"]",
            "login": r"login\s*[=:]\s*['\"][^'\"]+['\"]",
        }

        # File extensions to scan
        self.scannable_extensions = {
            ".py",
            ".js",
            ".ts",
            ".jsx",
            ".tsx",
            ".java",
            ".cpp",
            ".c",
            ".h",
            ".yml",
            ".yaml",
            ".json",
            ".xml",
            ".html",
            ".css",
            ".sh",
            ".bash",
            ".env",
            ".conf",
            ".config",
            ".ini",
            ".toml",
        }

        # Directories to exclude
        self.exclude_dirs = {
            "__pycache__",
            ".git",
            ".venv",
            "venv",
            "env",
            "node_modules",
            ".pytest_cache",
            ".mypy_cache",
            "build",
            "dist",
            "target",
        }

        # Files to exclude
        self.exclude_files = {
            ".gitignore",
            ".env.example",
            "docker.env.example",
            "env.template",
            "docker.env.example",
            "test.env",
            "test_env_config.env",
        }

    def scan_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Scan a single file for security issues."""
        issues = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                lines = content.split("\n")

                for line_num, line in enumerate(lines, 1):
                    for pattern_name, pattern in self.secret_patterns.items():
                        matches = re.finditer(pattern, line, re.IGNORECASE)
                        for match in matches:
                            # Check if it's a false positive (environment variable usage)
                            if self._is_environment_variable_usage(line):
                                continue

                            issues.append(
                                {
                                    "file": str(file_path),
                                    "line": line_num,
                                    "pattern": pattern_name,
                                    "content": line.strip(),
                                    "match": match.group(),
                                    "severity": "HIGH",
                                }
                            )

                # Check for hardcoded URLs with credentials
                url_pattern = r"https?://[^:\s]+:[^@\s]+@[^\s]+"
                url_matches = re.finditer(url_pattern, content)
                for match in url_matches:
                    issues.append(
                        {
                            "file": str(file_path),
                            "line": 0,  # Couldn't determine line number easily
                            "pattern": "hardcoded_url_with_credentials",
                            "content": match.group(),
                            "match": match.group(),
                            "severity": "CRITICAL",
                        }
                    )

        except Exception as e:
            issues.append(
                {
                    "file": str(file_path),
                    "line": 0,
                    "pattern": "file_read_error",
                    "content": f"Error reading file: {str(e)}",
                    "match": "",
                    "severity": "LOW",
                }
            )

        return issues

    def _is_environment_variable_usage(self, line: str) -> bool:
        """Check if the line uses environment variables instead of hardcoded values."""
        env_patterns = [
            r"os\.getenv\(",
            r"os\.environ\[",
            r"os\.environ\.get\(",
            r"load_dotenv\(",
            r"\$\{.*\}",
            r"process\.env\.",
            r"System\.getenv\(",
            r"getenv\(",
        ]

        return any(re.search(pattern, line) for pattern in env_patterns)

    def scan_directory(self) -> Dict[str, Any]:
        """Scan the entire directory for security issues."""
        print(f"🔍 Scanning directory: {self.root_dir}")
        print("=" * 60)

        total_files = 0
        scanned_files = 0

        for file_path in self.root_dir.rglob("*"):
            if file_path.is_file():
                total_files += 1

                # Skip excluded directories
                if any(exclude in file_path.parts for exclude in self.exclude_dirs):
                    continue

                # Skip excluded files
                if file_path.name in self.exclude_files:
                    continue

                # Check if file extension is scannable
                if file_path.suffix not in self.scannable_extensions:
                    continue

                scanned_files += 1
                file_issues = self.scan_file(file_path)
                self.issues.extend(file_issues)

                if file_issues:
                    print(f"⚠️  Found {len(file_issues)} issues in {file_path}")

        print(f"\n📊 Scan Summary:")
        print(f"  Total files: {total_files}")
        print(f"  Scanned files: {scanned_files}")
        print(f"  Issues found: {len(self.issues)}")

        return {
            "total_files": total_files,
            "scanned_files": scanned_files,
            "issues": self.issues,
        }

    def generate_report(self, output_file: str = None) -> str:
        """Generate a security scan report."""
        if not self.issues:
            report = "✅ No security issues found! Your codebase appears to be secure."
            print(report)
            return report

        # Group issues by severity
        issues_by_severity = {}
        for issue in self.issues:
            severity = issue["severity"]
            if severity not in issues_by_severity:
                issues_by_severity[severity] = []
            issues_by_severity[severity].append(issue)

        # Generate report
        report_lines = [
            "🚨 Security Scan Report",
            "=" * 60,
            f"Total Issues Found: {len(self.issues)}",
            "",
        ]

        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            if severity in issues_by_severity:
                issues = issues_by_severity[severity]
                report_lines.extend(
                    [f"🔴 {severity} Issues ({len(issues)}):", "-" * 40]
                )

                for issue in issues:
                    report_lines.extend(
                        [
                            f"File: {issue['file']}",
                            f"Line: {issue['line']}",
                            f"Pattern: {issue['pattern']}",
                            f"Content: {issue['content']}",
                            f"Match: {issue['match']}",
                            "",
                        ]
                    )

        # Recommendations
        report_lines.extend(
            [
                "💡 Recommendations:",
                "-" * 40,
                "1. Replace hardcoded credentials with environment variables",
                "2. Use configuration files that are not committed to version control",
                "3. Implement proper secret management (e.g., AWS Secrets Manager, HashiCorp Vault)",
                "4. Use pre-commit hooks to prevent committing secrets",
                "5. Regularly rotate credentials and API keys",
                "6. Consider using GitGuardian or similar tools for continuous monitoring",
                "",
            ]
        )

        report = "\n".join(report_lines)

        # Save to file if specified
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"📄 Report saved to: {output_file}")

        print(report)
        return report

    def check_git_history(self) -> List[Dict[str, Any]]:
        """Check git history for potential secrets (basic check)."""
        print("\n🔍 Checking git history for potential secrets...")

        try:
            import subprocess

            result = subprocess.run(
                [
                    "git",
                    "log",
                    "--all",
                    "--full-history",
                    "--",
                    "*.py",
                    "*.yml",
                    "*.yaml",
                    "*.env*",
                ],
                capture_output=True,
                text=True,
                cwd=self.root_dir,
            )

            if result.returncode == 0:
                # Look for potential secrets in commit messages
                commit_patterns = [
                    r"password.*=.*['\"][^'\"]+['\"]",
                    r"secret.*=.*['\"][^'\"]+['\"]",
                    r"api_key.*=.*['\"][^'\"]+['\"]",
                ]

                git_issues = []
                for line in result.stdout.split("\n"):
                    for pattern in commit_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            git_issues.append(
                                {
                                    "type": "git_history",
                                    "content": line.strip(),
                                    "severity": "MEDIUM",
                                }
                            )

                if git_issues:
                    print(f"⚠️  Found {len(git_issues)} potential issues in git history")
                    return git_issues
                else:
                    print("✅ No obvious secrets found in git history")
                    return []
            else:
                print("⚠️  Could not check git history")
                return []

        except Exception as e:
            print(f"⚠️  Error checking git history: {e}")
            return []


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description="Security Scanner for investByYourself Codebase"
    )
    parser.add_argument(
        "--dir", default=".", help="Directory to scan (default: current directory)"
    )
    parser.add_argument("--output", help="Output file for the report")
    parser.add_argument(
        "--check-git", action="store_true", help="Check git history for secrets"
    )

    args = parser.parse_args()

    # Create scanner
    scanner = SecurityScanner(args.dir)

    # Scan directory
    scan_results = scanner.scan_directory()

    # Check git history if requested
    if args.check_git:
        git_issues = scanner.check_git_history()
        if git_issues:
            scanner.issues.extend(git_issues)

    # Generate report
    scanner.generate_report(args.output)

    # Exit with error code if issues found
    if scanner.issues:
        print(f"\n❌ Security scan completed with {len(scanner.issues)} issues found!")
        exit(1)
    else:
        print(f"\n✅ Security scan completed successfully!")
        exit(0)


if __name__ == "__main__":
    main()
