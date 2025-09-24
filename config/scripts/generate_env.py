#!/usr/bin/env python3
"""
InvestByYourself - Environment Configuration Generator
Tech-026: Unified Environment Configuration Management

This script generates environment configuration files by combining
base templates with environment-specific and service-specific overrides.

Usage:
    python config/scripts/generate_env.py --environment development --service backend
    python config/scripts/generate_env.py --environment production --service frontend
    python config/scripts/generate_env.py --environment development --all-services
"""

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ConfigFile:
    """Represents a configuration file with its path and content."""

    path: Path
    content: str
    priority: int  # Higher number = higher priority (overrides lower priority)


class EnvironmentGenerator:
    """Generates environment configuration files from templates."""

    def __init__(self, config_root: Path):
        self.config_root = config_root
        self.environments_dir = config_root / "environments"
        self.services_dir = config_root / "services"
        self.output_dir = config_root.parent  # Project root

    def generate_config(
        self,
        environment: str,
        service: Optional[str] = None,
        output_file: Optional[str] = None,
    ) -> str:
        """
        Generate environment configuration by combining templates.

        Args:
            environment: Target environment (development, staging, production)
            service: Target service (backend, frontend, etl) or None for base
            output_file: Output file path (defaults to .env.{environment}.{service})

        Returns:
            Generated configuration content
        """
        config_files = self._collect_config_files(environment, service)
        merged_content = self._merge_config_files(config_files, environment)
        validated_content = self._validate_config(merged_content, environment)

        if output_file:
            output_path = Path(output_file)
        else:
            if service:
                output_path = self.output_dir / f".env.{environment}.{service}"
            else:
                output_path = self.output_dir / f".env.{environment}"

        # Create backup of existing file if it exists
        if output_path.exists():
            backup_dir = (
                self.config_root / "backups" / f"config_backup_{environment}_{service}"
            )
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_path = backup_dir / output_path.name
            backup_path.write_text(output_path.read_text())
            print(f"Created backup: {backup_path}")

        # Write the generated configuration
        output_path.write_text(validated_content)
        print(f"Generated configuration: {output_path}")

        return validated_content

    def _collect_config_files(
        self, environment: str, service: Optional[str]
    ) -> List[ConfigFile]:
        """Collect configuration files in priority order."""
        config_files = []

        # Base configuration (priority 1)
        base_file = self.environments_dir / "base.env.template"
        if base_file.exists():
            config_files.append(
                ConfigFile(path=base_file, content=base_file.read_text(), priority=1)
            )

        # Environment-specific configuration (priority 2)
        env_file = self.environments_dir / f"{environment}.env.template"
        if env_file.exists():
            config_files.append(
                ConfigFile(path=env_file, content=env_file.read_text(), priority=2)
            )

        # Service-specific configuration (priority 3)
        if service:
            service_file = self.services_dir / f"{service}.env.template"
            if service_file.exists():
                config_files.append(
                    ConfigFile(
                        path=service_file, content=service_file.read_text(), priority=3
                    )
                )

        # Sort by priority (higher priority files override lower priority)
        config_files.sort(key=lambda x: x.priority)

        return config_files

    def _resolve_variable(
        self, value: str, variables: Dict[str, str], environment: str
    ) -> str:
        """Resolve a variable value, handling inheritance and defaults."""
        # Extract comment if present
        value_parts = value.split("#", 1)
        value = value_parts[0].strip()
        comment = f" # {value_parts[1].strip()}" if len(value_parts) > 1 else ""

        # Match ${VAR:-default} pattern
        default_match = re.match(r"\${([A-Z_]+):-([^}]+)}", value)
        if default_match:
            var_name = default_match.group(1)
            default_value = default_match.group(2)
            resolved = variables.get(var_name, default_value)
            return f"{resolved}{comment}"

        # Match ${VAR} pattern
        inherit_match = re.match(r"\${([A-Z_]+)}", value)
        if inherit_match:
            var_name = inherit_match.group(1)
            if var_name in variables:
                return f"{variables[var_name]}{comment}"

            # Load from environment if available
            env_value = os.getenv(var_name)
            if env_value:
                return f"{env_value}{comment}"

            # Generate placeholder for development
            if environment == "development":
                if any(key in var_name for key in ["PASSWORD", "SECRET", "KEY"]):
                    placeholder = f"dev_{var_name.lower()}_2025"
                else:
                    placeholder = f"dev_{var_name.lower()}"
                print(f"Warning: Using development placeholder for {var_name}")
                return f"{placeholder}{comment}"

            print(f"Warning: Required variable {var_name} not found")
            return f"${{{var_name}}}{comment}"

        return f"{value}{comment}"

    def _merge_config_files(
        self, config_files: List[ConfigFile], environment: str
    ) -> str:
        """Merge configuration files, with later files overriding earlier ones."""
        merged_vars = {}
        comments = []
        section_comments = {}
        current_section = None

        for config_file in config_files:
            content = config_file.content

            # Extract comments and variables
            for line in content.split("\n"):
                line = line.strip()

                # Skip empty lines
                if not line:
                    continue

                # Collect comments
                if line.startswith("#"):
                    # Check for section header
                    if "====" in line:
                        current_section = line
                        if current_section not in section_comments:
                            section_comments[current_section] = []
                    elif current_section:
                        section_comments[current_section].append(line)
                    else:
                        comments.append(line)
                    continue

                # Parse variable assignments
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()

                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    # Resolve variable references
                    resolved_value = self._resolve_variable(
                        value, merged_vars, environment
                    )
                    merged_vars[key] = resolved_value

        # Generate merged content
        merged_content = []

        # Add header comment
        merged_content.append("# =====================================================")
        merged_content.append(
            "# InvestByYourself - Generated Environment Configuration"
        )
        merged_content.append(
            "# Tech-026: Unified Environment Configuration Management"
        )
        merged_content.append("# =====================================================")
        merged_content.append("#")
        merged_content.append(
            "# This file was automatically generated by generate_env.py"
        )
        merged_content.append("# DO NOT EDIT THIS FILE MANUALLY")
        merged_content.append(
            "# To modify configuration, edit the template files in config/"
        )
        merged_content.append("# =====================================================")
        merged_content.append("")

        # Add variables grouped by category
        categories = self._categorize_variables(merged_vars)

        for category, vars_in_category in categories.items():
            if vars_in_category:
                merged_content.append(
                    f"# ====================================================="
                )
                merged_content.append(f"# {category.upper()}")
                merged_content.append(
                    f"# ====================================================="
                )
                merged_content.append("")

                for key, value in sorted(vars_in_category.items()):
                    # Escape value if it contains spaces or special characters
                    if " " in value or any(char in value for char in ["$", "`", "\\"]):
                        value = f'"{value}"'
                    merged_content.append(f"{key}={value}")

                merged_content.append("")

        return "\n".join(merged_content)

    def _categorize_variables(
        self, variables: Dict[str, str]
    ) -> Dict[str, Dict[str, str]]:
        """Categorize variables by their prefix or purpose."""
        categories = {
            "Environment & Application": {},
            "Database Configuration": {},
            "Cache & Storage": {},
            "External APIs": {},
            "Supabase Configuration": {},
            "Security Configuration": {},
            "Performance & Monitoring": {},
            "Service Configuration": {},
            "Development Settings": {},
            "Other": {},
        }

        for key, value in variables.items():
            if any(
                prefix in key.upper()
                for prefix in ["ENVIRONMENT", "DEBUG", "LOG_LEVEL", "APP_"]
            ):
                categories["Environment & Application"][key] = value
            elif any(prefix in key.upper() for prefix in ["POSTGRES", "DB_"]):
                categories["Database Configuration"][key] = value
            elif any(prefix in key.upper() for prefix in ["REDIS", "MINIO", "CACHE_"]):
                categories["Cache & Storage"][key] = value
            elif any(
                prefix in key.upper()
                for prefix in ["FRED", "ALPHA_VANTAGE", "FMP", "YFINANCE", "API_"]
            ):
                categories["External APIs"][key] = value
            elif "SUPABASE" in key.upper():
                categories["Supabase Configuration"][key] = value
            elif any(
                prefix in key.upper()
                for prefix in ["AUTH", "JWT", "ENCRYPTION", "CORS", "SECURITY"]
            ):
                categories["Security Configuration"][key] = value
            elif any(
                prefix in key.upper()
                for prefix in ["PERFORMANCE", "MONITORING", "SENTRY", "PROMETHEUS"]
            ):
                categories["Performance & Monitoring"][key] = value
            elif any(
                prefix in key.upper()
                for prefix in ["SERVICE_", "PORT", "TIMEOUT", "RATE_LIMIT"]
            ):
                categories["Service Configuration"][key] = value
            elif any(prefix in key.upper() for prefix in ["DEV_", "TEST_", "MOCK_"]):
                categories["Development Settings"][key] = value
            else:
                categories["Other"][key] = value

        return categories

    def _validate_config(self, content: str, environment: str = "production") -> str:
        """Validate the generated configuration using enhanced validation."""
        from validate_env import EnvironmentValidator, ValidationLevel

        # Create a temporary file for validation
        temp_file = self.config_root / ".temp_config"
        try:
            temp_file.write_text(content)

            # Initialize validator with environment context
            validator = EnvironmentValidator(self.config_root)
            validator.current_environment = environment

            # Run validation
            results = validator.validate_file(temp_file)

            # Process validation results
            has_critical = False
            for result in results:
                # Skip placeholder warnings in development
                if (
                    environment == "development"
                    and result.level == ValidationLevel.WARNING
                    and "placeholder" in result.message.lower()
                ):
                    continue

                # Skip numeric validation for values with units
                if (
                    result.level == ValidationLevel.ERROR
                    and "Invalid numeric value" in result.message
                    and any(unit in result.message for unit in ["MB", "GB", "KB", "B"])
                ):
                    continue

                if result.level == ValidationLevel.CRITICAL:
                    # Skip sensitive variable warnings in development
                    if (
                        environment == "development"
                        and "Sensitive variable contains placeholder" in result.message
                    ):
                        continue
                    print(f"❌ CRITICAL: {result.message}")
                    if result.suggestion:
                        print(f"   Suggestion: {result.suggestion}")
                    has_critical = True
                elif result.level == ValidationLevel.ERROR:
                    print(f"⚠️ ERROR: {result.message}")
                    if result.suggestion:
                        print(f"   Suggestion: {result.suggestion}")
                elif result.level == ValidationLevel.WARNING:
                    print(f"⚠️ Warning: {result.message}")
                    if result.suggestion:
                        print(f"   Suggestion: {result.suggestion}")

            # If there are critical issues in production, raise an exception
            if has_critical and environment != "development":
                raise ValueError("Critical validation errors found")

            return content

        finally:
            # Clean up temporary file
            if temp_file.exists():
                temp_file.unlink()

    def generate_all_services(self, environment: str) -> Dict[str, str]:
        """Generate configuration for all services in an environment."""
        services = ["backend", "frontend", "etl"]
        results = {}

        for service in services:
            try:
                content = self.generate_config(environment, service)
                results[service] = content
            except Exception as e:
                print(f"Error generating config for {service}: {e}")
                results[service] = None

        return results


def main():
    """Main entry point for the environment generator."""
    parser = argparse.ArgumentParser(
        description="Generate environment configuration files from templates"
    )
    parser.add_argument(
        "--environment",
        required=True,
        choices=["development", "staging", "production"],
        help="Target environment",
    )
    parser.add_argument(
        "--service",
        choices=["backend", "frontend", "etl"],
        help="Target service (optional)",
    )
    parser.add_argument(
        "--all-services",
        action="store_true",
        help="Generate configuration for all services",
    )
    parser.add_argument("--output", help="Output file path (optional)")
    parser.add_argument(
        "--config-root",
        default="config",
        help="Configuration root directory (default: config)",
    )

    args = parser.parse_args()

    # Validate arguments
    if args.service and args.all_services:
        print("Error: Cannot specify both --service and --all-services")
        sys.exit(1)

    config_root = Path(args.config_root)
    if not config_root.exists():
        print(f"Error: Configuration root directory not found: {config_root}")
        sys.exit(1)

    generator = EnvironmentGenerator(config_root)

    try:
        if args.all_services:
            print(
                f"Generating configuration for all services in {args.environment} environment..."
            )
            results = generator.generate_all_services(args.environment)

            for service, content in results.items():
                if content:
                    print(f"✅ Generated configuration for {service}")
                else:
                    print(f"❌ Failed to generate configuration for {service}")
        else:
            print(
                f"Generating configuration for {args.environment} environment"
                + (f" and {args.service} service" if args.service else "")
            )

            content = generator.generate_config(
                args.environment, args.service, args.output
            )

            print("✅ Configuration generated successfully")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
