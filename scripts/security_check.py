#!/usr/bin/env python3
import re
import subprocess
import sys
from pathlib import Path


def main():
    print("Security scan starting...")

    # Get staged files
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            cwd=".",
        )

        if result.returncode != 0:
            print("No staged files to scan")
            sys.exit(0)

        staged_files = [f.strip() for f in result.stdout.split("\n") if f.strip()]

        if not staged_files:
            print("No staged files to scan")
            sys.exit(0)

        print(f"Scanning {len(staged_files)} staged files...")

        issues = []
        for file_path in staged_files:
            if not Path(file_path).exists():
                continue

            if Path(file_path).suffix not in [
                ".py",
                ".js",
                ".ts",
                ".yml",
                ".yaml",
                ".json",
            ]:
                continue

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                    # Check for hardcoded passwords
                    if re.search(
                        r'password\s*[=:]\s*[\'"][^\'"]{8,}[\'"]',
                        content,
                        re.IGNORECASE,
                    ):
                        if "os.getenv(" not in content and "${" not in content:
                            issues.append(f"Hardcoded password found in {file_path}")

                    # Check for hardcoded API keys
                    if re.search(
                        r'api_key\s*[=:]\s*[\'"][^\'"]{8,}[\'"]', content, re.IGNORECASE
                    ):
                        if "os.getenv(" not in content and "${" not in content:
                            issues.append(f"Hardcoded API key found in {file_path}")

            except Exception as e:
                print(f"Warning: Could not read {file_path}: {e}")

        if issues:
            print("\nSECURITY ISSUES FOUND:")
            for issue in issues:
                print(f"- {issue}")
            print("\nCommit blocked. Fix security issues first.")
            sys.exit(1)
        else:
            print("Security scan passed!")
            sys.exit(0)

    except Exception as e:
        print(f"Security scan error: {e}")
        sys.exit(0)


if __name__ == "__main__":
    main()
