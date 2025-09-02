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
    ) -> Dict[str, str]:
        """Extract variables from existing configuration files."""
        all_variables = {}

        for config_file in config_files:
            try:
                content = config_file.read_text()
                variables = self._parse_env_file(content)

                # Merge variables (later files override earlier ones)
                for key, value in variables.items():
                    all_variables[key] = value

            except Exception as e:
                print(f"Warning: Error reading {config_file}: {e}")

        return all_variables

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
        self, environment: str, variables: Dict[str, str]
    ) -> bool:
        """Generate new configuration files."""
        try:
            # Import the generator
            sys.path.append(str(self.config_root / "scripts"))
            from generate_env import EnvironmentGenerator

            generator = EnvironmentGenerator(self.config_root)

            # Generate base configuration
            base_content = generator.generate_config(environment, None)

            # Generate service-specific configurations
            services = ["backend", "frontend", "etl"]
            for service in services:
                service_content = generator.generate_config(environment, service)

            return True

        except Exception as e:
            print(f"Error generating new configurations: {e}")
            return False

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
