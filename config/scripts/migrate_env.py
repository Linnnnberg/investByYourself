#!/usr/bin/env python3
"""
InvestByYourself - Environment Configuration Migration Script
Tech-026: Unified Environment Configuration Management

This script helps migrate from the old environment configuration system
to the new unified configuration system.

Usage:
    python config/scripts/migrate_env.py --backup
    python config/scripts/migrate_env.py --migrate --environment development
    python config/scripts/migrate_env.py --cleanup
"""

import argparse
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set


class EnvironmentMigrator:
    """Migrates environment configuration from old to new system."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_root = project_root / "config"
        self.backup_dir = project_root / "config" / "backups"

        # Old configuration files to migrate
        self.old_config_files = [
            ".env",
            ".env.local",
            ".env.development",
            ".env.production",
            "env.template",
            "env.example",
            "frontend/.env.local",
            "frontend/.env.development",
            "frontend/.env.production",
            "frontend/env.example",
            "frontend/frontend-vite/.env",
            "frontend/frontend-vite/.env.local",
            "frontend/frontend-vite/env.example",
        ]

        # New configuration structure
        self.new_config_structure = {
            "environments": [
                "base.env.template",
                "development.env.template",
                "staging.env.template",
                "production.env.template",
            ],
            "services": [
                "backend.env.template",
                "frontend.env.template",
                "etl.env.template",
            ],
            "scripts": ["generate_env.py", "validate_env.py", "migrate_env.py"],
        }

    def backup_existing_configs(self) -> bool:
        """Backup existing configuration files."""
        print("Creating backup of existing configuration files...")

        # Create backup directory
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Create timestamped backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"config_backup_{timestamp}"
        backup_path.mkdir(exist_ok=True)

        backed_up_files = []
        failed_files = []

        for config_file in self.old_config_files:
            file_path = self.project_root / config_file

            if file_path.exists():
                try:
                    # Create directory structure in backup
                    backup_file_path = backup_path / config_file
                    backup_file_path.parent.mkdir(parents=True, exist_ok=True)

                    # Copy file
                    shutil.copy2(file_path, backup_file_path)
                    backed_up_files.append(config_file)
                    print(f"  ✅ Backed up: {config_file}")

                except Exception as e:
                    failed_files.append((config_file, str(e)))
                    print(f"  ❌ Failed to backup {config_file}: {e}")

        # Create backup manifest
        manifest_path = backup_path / "backup_manifest.txt"
        with open(manifest_path, "w") as f:
            f.write(f"Configuration Backup - {datetime.now().isoformat()}\n")
            f.write("=" * 50 + "\n\n")
            f.write("Backed up files:\n")
            for file in backed_up_files:
                f.write(f"  - {file}\n")
            f.write("\nFailed files:\n")
            for file, error in failed_files:
                f.write(f"  - {file}: {error}\n")

        print(f"\nBackup completed: {backup_path}")
        print(f"Backed up {len(backed_up_files)} files")
        if failed_files:
            print(f"Failed to backup {len(failed_files)} files")

        return len(failed_files) == 0

    def migrate_configurations(self, environment: str) -> bool:
        """Migrate configurations to new system."""
        print(f"Migrating configurations for {environment} environment...")

        # Find existing configuration files
        existing_configs = self._find_existing_configs()

        if not existing_configs:
            print("No existing configuration files found to migrate")
            return True

        # Extract variables from existing configs
        all_variables = self._extract_variables_from_configs(existing_configs)

        # Generate new configuration files
        success = self._generate_new_configs(environment, all_variables)

        if success:
            print(f"✅ Migration completed for {environment} environment")
        else:
            print(f"❌ Migration failed for {environment} environment")

        return success

    def cleanup_old_configs(self, confirm: bool = False) -> bool:
        """Clean up old configuration files."""
        if not confirm:
            print("This will remove old configuration files.")
            response = input("Are you sure? (yes/no): ")
            if response.lower() != "yes":
                print("Cleanup cancelled")
                return False

        print("Cleaning up old configuration files...")

        removed_files = []
        failed_files = []

        for config_file in self.old_config_files:
            file_path = self.project_root / config_file

            if file_path.exists():
                try:
                    file_path.unlink()
                    removed_files.append(config_file)
                    print(f"  ✅ Removed: {config_file}")
                except Exception as e:
                    failed_files.append((config_file, str(e)))
                    print(f"  ❌ Failed to remove {config_file}: {e}")

        print(f"\nCleanup completed:")
        print(f"  Removed {len(removed_files)} files")
        if failed_files:
            print(f"  Failed to remove {len(failed_files)} files")

        return len(failed_files) == 0

    def validate_migration(self) -> bool:
        """Validate that migration was successful."""
        print("Validating migration...")

        # Check that new configuration structure exists
        missing_files = []

        for category, files in self.new_config_structure.items():
            for file in files:
                file_path = self.config_root / category / file
                if not file_path.exists():
                    missing_files.append(f"{category}/{file}")

        if missing_files:
            print("❌ Missing files in new configuration structure:")
            for file in missing_files:
                print(f"  - {file}")
            return False

        # Check that scripts are executable
        script_files = [
            "scripts/generate_env.py",
            "scripts/validate_env.py",
            "scripts/migrate_env.py",
        ]

        for script in script_files:
            script_path = self.config_root / script
            if not script_path.exists():
                print(f"❌ Missing script: {script}")
                return False

        print("✅ Migration validation successful")
        return True

    def _find_existing_configs(self) -> List[Path]:
        """Find existing configuration files."""
        existing_configs = []

        for config_file in self.old_config_files:
            file_path = self.project_root / config_file
            if file_path.exists():
                existing_configs.append(file_path)

        return existing_configs

    def _extract_variables_from_configs(
        self, config_files: List[Path]
    ) -> Dict[str, Dict[str, str]]:
        """Extract variables from existing configuration files."""
        # Structure: { service: { environment: { variable: value } } }
        variables = {
            "base": {"development": {}, "staging": {}, "production": {}},
            "backend": {"development": {}, "staging": {}, "production": {}},
            "frontend": {"development": {}, "staging": {}, "production": {}},
            "etl": {"development": {}, "staging": {}, "production": {}},
        }

        # Define service and environment patterns
        service_patterns = {
            "backend": re.compile(r"backend|api|server", re.IGNORECASE),
            "frontend": re.compile(r"frontend|client|ui", re.IGNORECASE),
            "etl": re.compile(r"etl|data|pipeline", re.IGNORECASE),
        }

        env_patterns = {
            "development": re.compile(r"development|dev|local", re.IGNORECASE),
            "staging": re.compile(r"staging|test|qa", re.IGNORECASE),
            "production": re.compile(r"production|prod", re.IGNORECASE),
        }

        for config_file in config_files:
            try:
                content = config_file.read_text()
                file_vars = self._parse_env_file(content)

                # Determine service and environment from file path and name
                service = "base"
                environment = "development"

                file_str = str(config_file).lower()

                # Determine environment
                for env, pattern in env_patterns.items():
                    if pattern.search(file_str):
                        environment = env
                        break

                # Determine service
                for svc, pattern in service_patterns.items():
                    if pattern.search(file_str):
                        service = svc
                        break

                # Categorize variables
                for key, value in file_vars.items():
                    # Check if variable belongs to a specific service
                    assigned_service = service
                    for svc, pattern in service_patterns.items():
                        if pattern.search(key):
                            assigned_service = svc
                            break

                    # Store variable
                    variables[assigned_service][environment][key] = value

                    # If it's a common variable, also store in base
                    if not any(
                        pattern.search(key) for pattern in service_patterns.values()
                    ):
                        variables["base"][environment][key] = value

            except Exception as e:
                print(f"Warning: Error reading {config_file}: {e}")

        return variables

    def _parse_env_file(self, content: str) -> Dict[str, str]:
        """Parse environment file content."""
        variables = {}

        for line in content.split("\n"):
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

        return variables

    def _generate_new_configs(
        self, environment: str, variables: Dict[str, Dict[str, Dict[str, str]]]
    ) -> bool:
        """Generate new configuration files."""
        try:
            # Create environment-specific templates
            env_dir = self.config_root / "environments"
            env_dir.mkdir(parents=True, exist_ok=True)

            # Generate base template
            base_template = env_dir / "base.env.template"
            base_vars = variables["base"][environment]
            self._generate_template(base_template, base_vars, is_base=True)

            # Generate environment-specific template
            env_template = env_dir / f"{environment}.env.template"
            env_vars = {}
            for service in variables:
                env_vars.update(variables[service][environment])
            self._generate_template(env_template, env_vars, is_base=False)

            # Generate service-specific templates
            service_dir = self.config_root / "services"
            service_dir.mkdir(parents=True, exist_ok=True)

            for service in ["backend", "frontend", "etl"]:
                service_template = service_dir / f"{service}.env.template"
                service_vars = variables[service][environment]
                self._generate_template(service_template, service_vars, is_service=True)

            return True

        except Exception as e:
            print(f"Error generating new configurations: {e}")
            return False

    def _generate_template(
        self,
        template_path: Path,
        variables: Dict[str, str],
        is_base: bool = False,
        is_service: bool = False,
    ) -> None:
        """Generate a configuration template file."""
        # Sort variables by category
        categories = {
            "Core Settings": [],
            "Database Configuration": [],
            "Cache Configuration": [],
            "API Configuration": [],
            "Security Settings": [],
            "Service Settings": [],
            "Monitoring": [],
            "Other": [],
        }

        # Define category patterns
        category_patterns = {
            "Database Configuration": re.compile(
                r"(DB|DATABASE|POSTGRES|MYSQL)", re.IGNORECASE
            ),
            "Cache Configuration": re.compile(
                r"(CACHE|REDIS|MEMCACHED)", re.IGNORECASE
            ),
            "API Configuration": re.compile(
                r"(API|ENDPOINT|URL|TIMEOUT)", re.IGNORECASE
            ),
            "Security Settings": re.compile(
                r"(KEY|SECRET|TOKEN|PASSWORD|ENCRYPTION)", re.IGNORECASE
            ),
            "Service Settings": re.compile(
                r"(SERVICE|WORKER|QUEUE|JOB)", re.IGNORECASE
            ),
            "Monitoring": re.compile(r"(LOG|MONITOR|TRACE|DEBUG)", re.IGNORECASE),
            "Core Settings": re.compile(r"(ENV|ENVIRONMENT|MODE|DEBUG)", re.IGNORECASE),
        }

        # Categorize variables
        for key, value in variables.items():
            assigned = False
            for category, pattern in category_patterns.items():
                if pattern.search(key):
                    categories[category].append((key, value))
                    assigned = True
                    break
            if not assigned:
                categories["Other"].append((key, value))

        # Generate template content
        content = []
        content.append("#" + "=" * 78)
        if is_base:
            content.append("# Base Environment Configuration")
            content.append("# Common settings across all environments")
        elif is_service:
            service_name = template_path.stem.split(".")[0].capitalize()
            content.append(f"# {service_name} Service Configuration")
            content.append(
                f"# Environment-specific settings for {service_name} service"
            )
        else:
            env_name = template_path.stem.split(".")[0].capitalize()
            content.append(f"# {env_name} Environment Configuration")
            content.append(f"# Environment-specific overrides for {env_name}")
        content.append("#" + "=" * 78)
        content.append("")

        # Add variables by category
        for category, vars in categories.items():
            if vars:
                content.append("#" + "-" * 76)
                content.append(f"# {category}")
                content.append("#" + "-" * 76)
                content.append("")

                for key, value in sorted(vars):
                    # Add comment for the variable
                    comment = self._generate_variable_comment(key, value)
                    if comment:
                        content.append(comment)

                    # Generate variable line
                    if is_base:
                        # Base template uses direct values or defaults
                        if self._is_sensitive(key):
                            content.append(f"{key}=${{key}}")
                        else:
                            content.append(f"{key}={value}")
                    else:
                        # Environment and service templates use inheritance
                        content.append(f"{key}=${{key}}")

                    content.append("")

        # Write template
        template_path.write_text("\n".join(content))

    def _generate_variable_comment(self, key: str, value: str) -> Optional[str]:
        """Generate a helpful comment for a variable."""
        comments = []

        # Add description based on variable name
        if "URL" in key:
            comments.append("URL endpoint")
        elif "PORT" in key:
            comments.append("Port number")
        elif "TIMEOUT" in key:
            comments.append("Timeout in seconds")
        elif "PASSWORD" in key or "SECRET" in key or "KEY" in key:
            comments.append("Sensitive credential - use environment variable")
        elif "ENABLED" in key or key.startswith("ENABLE_"):
            comments.append("Feature flag (true/false)")
        elif "DEBUG" in key:
            comments.append("Debug mode flag (true/false)")
        elif "PATH" in key:
            comments.append("File system path")
        elif "MAX_" in key:
            comments.append("Maximum limit")
        elif "MIN_" in key:
            comments.append("Minimum limit")

        # Add type information
        if value.lower() in ["true", "false", "yes", "no", "0", "1"]:
            comments.append("Boolean value")
        elif value.isdigit():
            comments.append("Numeric value")
        elif "://" in value:
            comments.append("URL value")

        if comments:
            return "# " + " - ".join(comments)
        return None

    def _is_sensitive(self, key: str) -> bool:
        """Check if a variable is sensitive."""
        sensitive_patterns = [
            "password",
            "secret",
            "key",
            "token",
            "credential",
            "auth",
            "private",
        ]
        key_lower = key.lower()
        return any(pattern in key_lower for pattern in sensitive_patterns)

    def show_migration_guide(self):
        """Show migration guide to user."""
        guide = """
# InvestByYourself Environment Configuration Migration Guide

## Overview
This migration moves from scattered environment files to a unified configuration system.

## Migration Steps

### 1. Backup Existing Configurations
```bash
python config/scripts/migrate_env.py --backup
```

### 2. Migrate Configurations
```bash
# Migrate development environment
python config/scripts/migrate_env.py --migrate --environment development

# Migrate production environment
python config/scripts/migrate_env.py --migrate --environment production
```

### 3. Generate New Configuration Files
```bash
# Generate all service configurations for development
python config/scripts/generate_env.py --environment development --all-services

# Generate specific service configuration
python config/scripts/generate_env.py --environment production --service backend
```

### 4. Validate New Configurations
```bash
# Validate all configurations
python config/scripts/validate_env.py --all

# Validate specific environment
python config/scripts/validate_env.py --environment development
```

### 5. Clean Up Old Files (Optional)
```bash
python config/scripts/migrate_env.py --cleanup
```

## New Configuration Structure

```
config/
├── environments/
│   ├── base.env.template          # Base configuration
│   ├── development.env.template   # Development overrides
│   ├── staging.env.template       # Staging overrides
│   └── production.env.template    # Production overrides
├── services/
│   ├── backend.env.template       # Backend service config
│   ├── frontend.env.template      # Frontend service config
│   └── etl.env.template          # ETL service config
└── scripts/
    ├── generate_env.py           # Configuration generator
    ├── validate_env.py           # Configuration validator
    └── migrate_env.py            # Migration script
```

## Key Improvements

1. **Centralized Management**: All configurations in one place
2. **Security**: No hardcoded secrets in templates
3. **Consistency**: Unified naming conventions
4. **Validation**: Automated configuration validation
5. **Automation**: Scripts for generation and management

## After Migration

1. Update your deployment scripts to use new configuration files
2. Update documentation to reference new configuration system
3. Train team members on new configuration management
4. Set up CI/CD to use new validation scripts

## Support

If you encounter issues during migration:
1. Check the backup files in `config/backups/`
2. Run validation scripts to identify problems
3. Review the migration guide and documentation
"""

        print(guide)


def main():
    """Main entry point for the migration script."""
    parser = argparse.ArgumentParser(
        description="Migrate environment configuration to unified system"
    )
    parser.add_argument(
        "--backup", action="store_true", help="Backup existing configuration files"
    )
    parser.add_argument(
        "--migrate", action="store_true", help="Migrate configurations to new system"
    )
    parser.add_argument(
        "--environment",
        choices=["development", "staging", "production"],
        help="Target environment for migration",
    )
    parser.add_argument(
        "--cleanup", action="store_true", help="Clean up old configuration files"
    )
    parser.add_argument("--validate", action="store_true", help="Validate migration")
    parser.add_argument("--guide", action="store_true", help="Show migration guide")
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root directory (default: current directory)",
    )

    args = parser.parse_args()

    # Validate arguments
    if not any([args.backup, args.migrate, args.cleanup, args.validate, args.guide]):
        print(
            "Error: Must specify an action (--backup, --migrate, --cleanup, --validate, or --guide)"
        )
        sys.exit(1)

    if args.migrate and not args.environment:
        print("Error: --migrate requires --environment")
        sys.exit(1)

    project_root = Path(args.project_root).resolve()
    if not project_root.exists():
        print(f"Error: Project root directory not found: {project_root}")
        sys.exit(1)

    migrator = EnvironmentMigrator(project_root)

    try:
        if args.guide:
            migrator.show_migration_guide()
        elif args.backup:
            success = migrator.backup_existing_configs()
            sys.exit(0 if success else 1)
        elif args.migrate:
            success = migrator.migrate_configurations(args.environment)
            sys.exit(0 if success else 1)
        elif args.cleanup:
            success = migrator.cleanup_old_configs()
            sys.exit(0 if success else 1)
        elif args.validate:
            success = migrator.validate_migration()
            sys.exit(0 if success else 1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
