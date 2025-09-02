#!/usr/bin/env python3
"""
InvestByYourself - Environment Configuration Validator
Tech-026: Unified Environment Configuration Management

This script validates environment configuration files for:
- Required variables
- Placeholder values
- Security issues
- Consistency across environments
- Format compliance

Usage:
    python config/scripts/validate_env.py --file .env.development
    python config/scripts/validate_env.py --environment development
    python config/scripts/validate_env.py --all
"""

import argparse
import os
import re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class ValidationLevel(Enum):
    """Validation severity levels."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class ValidationResult:
    """Represents a validation result."""

    level: ValidationLevel
    message: str
    variable: Optional[str] = None
    suggestion: Optional[str] = None


class EnvironmentValidator:
    """Validates environment configuration files."""

    def __init__(self, config_root: Path):
        self.config_root = config_root
        self.project_root = config_root.parent

        # Service-specific configuration files
        self.service_configs = {
            "etl": "services/etl.env.template",
            "frontend": "services/frontend.env.template",
            "backend": "services/backend.env.template",
        }

        # Environment hierarchy
        self.env_hierarchy = ["base", "development", "staging", "production"]

        # Variable inheritance patterns
        self.inheritance_patterns = [
            r"\${([A-Z_]+)(?::-[^}]+)?}",  # ${VAR} or ${VAR:-default}
            r"\$([A-Z_]+)",  # $VAR
        ]

        # Define required variables by category
        self.required_variables = {
            "database": [
                "POSTGRES_HOST",
                "POSTGRES_PORT",
                "POSTGRES_DATABASE",
                "POSTGRES_USER",
                "POSTGRES_PASSWORD",
            ],
            "cache": ["REDIS_HOST", "REDIS_PORT", "REDIS_PASSWORD"],
            "storage": [
                "MINIO_HOST",
                "MINIO_PORT",
                "MINIO_ACCESS_KEY",
                "MINIO_SECRET_KEY",
            ],
            "apis": ["FRED_API_KEY", "ALPHA_VANTAGE_API_KEY", "FMP_API_KEY"],
            "supabase": [
                "SUPABASE_URL",
                "SUPABASE_ANON_KEY",
                "SUPABASE_SERVICE_ROLE_KEY",
            ],
            "security": ["ENCRYPTION_KEY", "JWT_SECRET"],
        }

        # Define sensitive variables that should not be hardcoded
        self.sensitive_variables = [
            "POSTGRES_PASSWORD",
            "REDIS_PASSWORD",
            "MINIO_SECRET_KEY",
            "SUPABASE_SERVICE_ROLE_KEY",
            "ENCRYPTION_KEY",
            "JWT_SECRET",
            "FRED_API_KEY",
            "ALPHA_VANTAGE_API_KEY",
            "FMP_API_KEY",
        ]

        # Define placeholder patterns
        self.placeholder_patterns = [
            r"your_.*_key",
            r"your_.*_password",
            r"your_.*_secret",
            r"your_.*_id",
            r"placeholder",
            r"changeme",
            r"default",
            r"test",
            r"dev_.*_2025",
        ]

    def validate_file(self, file_path: Path) -> List[ValidationResult]:
        """Validate a single environment file."""
        if not file_path.exists():
            return [
                ValidationResult(ValidationLevel.ERROR, f"File not found: {file_path}")
            ]

        try:
            content = file_path.read_text()
            results = []

            # Basic content validation
            results.extend(self._validate_content(content, file_path.name))

            # Variable inheritance validation
            results.extend(self._validate_inheritance(content, file_path.name))

            # Service-specific validation
            for service, config_path in self.service_configs.items():
                if str(file_path).endswith(config_path):
                    results.extend(self._validate_service_config(service, content))
                    break

            return results
        except Exception as e:
            return [
                ValidationResult(
                    ValidationLevel.ERROR, f"Error reading file {file_path}: {e}"
                )
            ]

    def validate_environment(self, environment: str) -> List[ValidationResult]:
        """Validate all configuration files for an environment."""
        results = []

        # Find all .env files for the environment
        env_files = list(self.project_root.glob(f".env.{environment}*"))

        if not env_files:
            results.append(
                ValidationResult(
                    ValidationLevel.WARNING,
                    f"No configuration files found for environment: {environment}",
                )
            )
            return results

        for env_file in env_files:
            file_results = self.validate_file(env_file)
            results.extend(file_results)

        # Cross-validate consistency
        consistency_results = self._validate_consistency(env_files)
        results.extend(consistency_results)

        return results

    def validate_all(self) -> Dict[str, List[ValidationResult]]:
        """Validate all environment configurations."""
        environments = ["development", "staging", "production"]
        results = {}

        for env in environments:
            results[env] = self.validate_environment(env)

        # Global validation
        global_results = self._validate_global_consistency()
        results["global"] = global_results

        return results

    def _validate_inheritance(
        self, content: str, filename: str
    ) -> List[ValidationResult]:
        """Validate variable inheritance and defaults."""
        results = []
        variables = self._extract_variables(content)

        # Extract all referenced variables
        referenced_vars = set()
        for value in variables.values():
            for pattern in self.inheritance_patterns:
                matches = re.finditer(pattern, value)
                for match in matches:
                    var_name = match.group(1)
                    referenced_vars.add(var_name)

        # Check if referenced variables exist in base config
        base_config_path = self.config_root / "environments/base.env.template"
        if base_config_path.exists():
            base_content = base_config_path.read_text()
            base_vars = self._extract_variables(base_content)

            for var in referenced_vars:
                if var not in base_vars and not any(
                    var.startswith(prefix)
                    for prefix in ["ETL_", "FRONTEND_", "BACKEND_"]
                ):
                    results.append(
                        ValidationResult(
                            ValidationLevel.ERROR,
                            f"Referenced variable {var} not found in base configuration",
                            variable=var,
                            suggestion="Add variable to base.env.template or check for typos",
                        )
                    )

        # Validate default values
        for key, value in variables.items():
            for pattern in self.inheritance_patterns:
                matches = re.finditer(pattern, value)
                for match in matches:
                    if ":-" in match.group(0):  # Has default value
                        default_val = match.group(0).split(":-")[1].rstrip("}")
                        if self._is_insecure_default(key, default_val):
                            results.append(
                                ValidationResult(
                                    ValidationLevel.WARNING,
                                    f"Insecure default value in {key}: {default_val}",
                                    variable=key,
                                    suggestion="Use a more secure default value",
                                )
                            )

        return results

    def _validate_service_config(
        self, service: str, content: str
    ) -> List[ValidationResult]:
        """Validate service-specific configuration."""
        results = []
        variables = self._extract_variables(content)

        # Service-specific required variables
        service_required = {
            "etl": [
                "SERVICE_NAME",
                "SERVICE_VERSION",
                "SERVICE_PORT",
                "DATA_COLLECTION_INTERVAL",
                "BATCH_SIZE",
                "ETL_DB_HOST",
                "ETL_DB_PORT",
                "ETL_REDIS_HOST",
                "ETL_REDIS_PORT",
            ],
            "frontend": [
                "NEXT_PUBLIC_API_BASE_URL",
                "NEXT_PUBLIC_SUPABASE_URL",
                "NEXT_PUBLIC_SUPABASE_ANON_KEY",
            ],
            "backend": [
                "API_VERSION",
                "API_PORT",
                "DB_POOL_SIZE",
                "REDIS_CACHE_ENABLED",
            ],
        }

        # Check required variables
        if service in service_required:
            for var in service_required[service]:
                if var not in variables:
                    results.append(
                        ValidationResult(
                            ValidationLevel.ERROR,
                            f"Required {service} variable missing: {var}",
                            variable=var,
                            suggestion=f"Add {var} to {service}.env.template",
                        )
                    )

        # Service-specific validation rules
        if service == "etl":
            # Validate ETL-specific settings
            if "DATA_COLLECTION_INTERVAL" in variables:
                try:
                    interval = int(variables["DATA_COLLECTION_INTERVAL"])
                    if interval < 60:
                        results.append(
                            ValidationResult(
                                ValidationLevel.WARNING,
                                "DATA_COLLECTION_INTERVAL is less than 60 seconds",
                                variable="DATA_COLLECTION_INTERVAL",
                                suggestion="Consider increasing interval to reduce API load",
                            )
                        )
                except ValueError:
                    pass  # Already handled by type validation

        elif service == "frontend":
            # Validate frontend-specific settings
            if "NEXT_PUBLIC_API_BASE_URL" in variables:
                url = variables["NEXT_PUBLIC_API_BASE_URL"]
                if not url.startswith("${") and "localhost" in url:
                    results.append(
                        ValidationResult(
                            ValidationLevel.WARNING,
                            "Hardcoded localhost URL in frontend config",
                            variable="NEXT_PUBLIC_API_BASE_URL",
                            suggestion="Use environment variable: ${API_BASE_URL:-http://localhost:8000}",
                        )
                    )

        return results

    def _validate_content(self, content: str, filename: str) -> List[ValidationResult]:
        """Validate the content of an environment file."""
        results = []
        variables = {}

        for line_num, line in enumerate(content.split("\n"), 1):
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue

            # Parse variable assignment
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                # Remove quotes
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]

                variables[key] = value

                # Validate individual variable
                var_results = self._validate_variable(key, value, filename, line_num)
                results.extend(var_results)

        # Validate required variables
        required_results = self._validate_required_variables(variables, filename)
        results.extend(required_results)

        # Validate sensitive variables
        sensitive_results = self._validate_sensitive_variables(variables, filename)
        results.extend(sensitive_results)

        return results

    def _validate_variable(
        self, key: str, value: str, filename: str, line_num: int
    ) -> List[ValidationResult]:
        """Validate a single environment variable."""
        results = []

        # Skip placeholder check for inherited values
        if not self._is_inherited_value(value):
            # Extract actual value for checking
            actual_value = self._extract_default_value(value)
            # Check for placeholder values
            for pattern in self.placeholder_patterns:
                if re.search(pattern, actual_value, re.IGNORECASE):
                    results.append(
                        ValidationResult(
                            ValidationLevel.WARNING,
                            f"Placeholder value detected: {key}={actual_value}",
                            variable=key,
                            suggestion="Replace with actual value",
                        )
                    )

        # Check for empty values
        if not value:
            results.append(
                ValidationResult(
                    ValidationLevel.ERROR,
                    f"Empty value for variable: {key}",
                    variable=key,
                    suggestion="Provide a value or remove the variable",
                )
            )

        # Check for weak passwords
        if key.endswith("_PASSWORD") and self._is_weak_password(value):
            results.append(
                ValidationResult(
                    ValidationLevel.CRITICAL,
                    f"Weak password detected: {key}",
                    variable=key,
                    suggestion="Use a strong password with 16+ characters, mixed case, numbers, and symbols",
                )
            )

        # Check for insecure defaults
        if self._is_insecure_default(key, value):
            results.append(
                ValidationResult(
                    ValidationLevel.CRITICAL,
                    f"Insecure default value: {key}={value}",
                    variable=key,
                    suggestion="Use a secure, unique value",
                )
            )

        # Validate specific variable types
        type_results = self._validate_variable_type(key, value)
        results.extend(type_results)

        return results

    def _validate_required_variables(
        self, variables: Dict[str, str], filename: str
    ) -> List[ValidationResult]:
        """Validate that all required variables are present."""
        results = []

        for category, required_vars in self.required_variables.items():
            for var in required_vars:
                if var not in variables:
                    results.append(
                        ValidationResult(
                            ValidationLevel.ERROR,
                            f"Required variable missing: {var}",
                            variable=var,
                            suggestion=f"Add {var} to {filename}",
                        )
                    )

        return results

    def _validate_sensitive_variables(
        self, variables: Dict[str, str], filename: str
    ) -> List[ValidationResult]:
        """Validate sensitive variables for security issues."""
        results = []

        for var in self.sensitive_variables:
            if var in variables:
                value = variables[var]

                # Check if it's a placeholder
                if any(
                    re.search(pattern, value, re.IGNORECASE)
                    for pattern in self.placeholder_patterns
                ):
                    results.append(
                        ValidationResult(
                            ValidationLevel.CRITICAL,
                            f"Sensitive variable contains placeholder: {var}",
                            variable=var,
                            suggestion="Replace with actual secure value",
                        )
                    )

                # Check for hardcoded secrets in templates
                if filename.endswith(".template") and not value.startswith("${"):
                    results.append(
                        ValidationResult(
                            ValidationLevel.WARNING,
                            f"Hardcoded value in template: {var}",
                            variable=var,
                            suggestion="Use placeholder format: ${VARIABLE_NAME}",
                        )
                    )

        return results

    def _extract_default_value(self, value: str) -> str:
        """Extract the default value from a shell-style variable substitution."""
        # Match ${VAR:-default} pattern
        match = re.match(r"\${[A-Z_]+:-([^}]+)}", value)
        if match:
            return match.group(1)
        # Match ${VAR} pattern (pure inheritance)
        match = re.match(r"\${([A-Z_]+)}", value)
        if match:
            return "INHERITED"
        return value

    def _is_inherited_value(self, value: str) -> bool:
        """Check if a value is inherited from another variable."""
        return bool(re.match(r"\${[A-Z_]+}", value))

    def _validate_variable_type(self, key: str, value: str) -> List[ValidationResult]:
        """Validate variable types and formats."""
        results = []
        actual_value = self._extract_default_value(value)
        is_inherited = self._is_inherited_value(value)

        # Validate numeric variables
        if key.endswith("_PORT") or key.endswith("_TIMEOUT") or key.endswith("_SIZE"):
            if not is_inherited:
                try:
                    # Handle float values for _DELAY suffixes
                    if key.endswith("_DELAY"):
                        float(actual_value)
                    else:
                        int(actual_value)
                except ValueError:
                    results.append(
                        ValidationResult(
                            ValidationLevel.ERROR,
                            f"Invalid numeric value: {key}={actual_value}",
                            variable=key,
                            suggestion="Use a valid numeric value",
                        )
                    )

        # Validate boolean variables
        if (
            key.startswith("ENABLE_")
            or key.startswith("DEBUG_")
            or key.startswith("AUTO_")
            or key.endswith("_ENABLED")
        ):
            if actual_value.lower() not in ["true", "false", "1", "0"]:
                results.append(
                    ValidationResult(
                        ValidationLevel.WARNING,
                        f"Invalid boolean value: {key}={actual_value}",
                        variable=key,
                        suggestion="Use 'true' or 'false'",
                    )
                )

        # Validate compression types
        if key.endswith("_COMPRESSION"):
            valid_compression = [
                "true",
                "false",
                "1",
                "0",
                "gzip",
                "lz4",
                "snappy",
                "zstd",
            ]
            if actual_value.lower() not in valid_compression:
                results.append(
                    ValidationResult(
                        ValidationLevel.WARNING,
                        f"Invalid compression type: {key}={actual_value}",
                        variable=key,
                        suggestion=f"Use one of: {', '.join(valid_compression)}",
                    )
                )

        # Validate URL variables
        if key.endswith("_URL") and not is_inherited:
            valid_protocols = ["http://", "https://"]

            if key.endswith("_DATABASE_URL"):
                valid_protocols.extend(["postgresql://", "mysql://", "redis://"])
            elif key == "SUPABASE_URL":
                # Supabase project URLs are always HTTPS
                valid_protocols = ["https://"]
                # Check Supabase project URL format
                if not re.match(r"https://[a-z0-9-]+\.supabase\.co/?$", actual_value):
                    results.append(
                        ValidationResult(
                            ValidationLevel.WARNING,
                            f"Invalid Supabase URL format: {key}={actual_value}",
                            variable=key,
                            suggestion="Use format: https://project-id.supabase.co",
                        )
                    )
                    return results

            if not any(
                actual_value.startswith(protocol) for protocol in valid_protocols
            ):
                suggestion = "Use full URL with protocol ("
                if key.endswith("_DATABASE_URL"):
                    suggestion += "postgresql://, mysql://, redis://"
                elif key == "SUPABASE_URL":
                    suggestion += "https://"
                else:
                    suggestion += "http://, https://"
                suggestion += ")"

                results.append(
                    ValidationResult(
                        ValidationLevel.WARNING,
                        f"Invalid URL format: {key}={actual_value}",
                        variable=key,
                        suggestion=suggestion,
                    )
                )

        return results

    def _validate_consistency(self, env_files: List[Path]) -> List[ValidationResult]:
        """Validate consistency across environment files."""
        results = []

        if len(env_files) < 2:
            return results

        # Compare variables across files
        file_variables = {}
        for env_file in env_files:
            try:
                content = env_file.read_text()
                variables = self._extract_variables(content)
                file_variables[env_file.name] = variables
            except Exception as e:
                results.append(
                    ValidationResult(
                        ValidationLevel.ERROR, f"Error reading {env_file.name}: {e}"
                    )
                )

        # Check for missing variables in some files
        all_variables = set()
        for variables in file_variables.values():
            all_variables.update(variables.keys())

        for var in all_variables:
            missing_in = []
            for filename, variables in file_variables.items():
                if var not in variables:
                    missing_in.append(filename)

            if missing_in:
                results.append(
                    ValidationResult(
                        ValidationLevel.WARNING,
                        f"Variable {var} missing in: {', '.join(missing_in)}",
                        variable=var,
                        suggestion="Consider adding to all environment files",
                    )
                )

        return results

    def _validate_global_consistency(self) -> List[ValidationResult]:
        """Validate global consistency across all environments."""
        results = []

        # Check for template files
        template_files = list(self.config_root.rglob("*.template"))
        if not template_files:
            results.append(
                ValidationResult(
                    ValidationLevel.WARNING,
                    "No template files found in config directory",
                )
            )

        # Check for hardcoded project IDs in templates
        for template_file in template_files:
            try:
                content = template_file.read_text()
                if "ztxlcatckspsdtkepmwy" in content:
                    results.append(
                        ValidationResult(
                            ValidationLevel.CRITICAL,
                            f"Hardcoded project ID found in template: {template_file.name}",
                            suggestion="Replace with placeholder: ${SUPABASE_PROJECT_ID}",
                        )
                    )
            except Exception as e:
                results.append(
                    ValidationResult(
                        ValidationLevel.ERROR,
                        f"Error reading template {template_file.name}: {e}",
                    )
                )

        return results

    def _extract_variables(self, content: str) -> Dict[str, str]:
        """Extract variables from environment file content."""
        variables = {}

        for line in content.split("\n"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                # Remove quotes
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]

                variables[key] = value

        return variables

    def _is_weak_password(self, password: str) -> bool:
        """Check if a password is weak."""
        if len(password) < 8:
            return True

        if password.lower() in ["password", "123456", "admin", "root"]:
            return True

        if re.match(r"^[a-z]+$", password) or re.match(r"^[A-Z]+$", password):
            return True

        return False

    def _is_insecure_default(self, key: str, value: str) -> bool:
        """Check if a value is an insecure default."""
        insecure_defaults = {
            "POSTGRES_PASSWORD": ["postgres", "password", "admin"],
            "REDIS_PASSWORD": ["redis", "password", "admin"],
            "MINIO_SECRET_KEY": ["minioadmin", "password", "admin"],
            "JWT_SECRET": ["secret", "jwt_secret", "changeme"],
            "ENCRYPTION_KEY": ["secret", "encryption_key", "changeme"],
        }

        if key in insecure_defaults:
            return value.lower() in insecure_defaults[key]

        return False


def main():
    """Main entry point for the environment validator."""
    parser = argparse.ArgumentParser(
        description="Validate environment configuration files"
    )
    parser.add_argument("--file", help="Validate a specific environment file")
    parser.add_argument(
        "--environment",
        choices=["development", "staging", "production"],
        help="Validate all files for an environment",
    )
    parser.add_argument(
        "--all", action="store_true", help="Validate all environment configurations"
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

    validator = EnvironmentValidator(config_root)

    try:
        if args.file:
            file_path = Path(args.file)
            results = validator.validate_file(file_path)
        elif args.environment:
            results = validator.validate_environment(args.environment)
        else:  # args.all
            all_results = validator.validate_all()
            results = []
            for env, env_results in all_results.items():
                results.extend(env_results)

        # Output results
        if args.output_format == "json":
            import json

            output = []
            for result in results:
                output.append(
                    {
                        "level": result.level.value,
                        "message": result.message,
                        "variable": result.variable,
                        "suggestion": result.suggestion,
                    }
                )
            print(json.dumps(output, indent=2))
        else:
            # Text output
            if not results:
                print("✅ No validation issues found")
            else:
                # Group by level
                by_level = {}
                for result in results:
                    if result.level not in by_level:
                        by_level[result.level] = []
                    by_level[result.level].append(result)

                # Output by severity
                for level in [
                    ValidationLevel.CRITICAL,
                    ValidationLevel.ERROR,
                    ValidationLevel.WARNING,
                    ValidationLevel.INFO,
                ]:
                    if level in by_level:
                        print(f"\n{level.value} ({len(by_level[level])} issues):")
                        for result in by_level[level]:
                            print(f"  • {result.message}")
                            if result.variable:
                                print(f"    Variable: {result.variable}")
                            if result.suggestion:
                                print(f"    Suggestion: {result.suggestion}")

        # Exit with error code if critical or error issues found
        critical_errors = sum(
            1
            for r in results
            if r.level in [ValidationLevel.CRITICAL, ValidationLevel.ERROR]
        )
        if critical_errors > 0:
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
