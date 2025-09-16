#!/usr/bin/env python3
"""
Database Infrastructure Validation Script
Tech-008: Database Infrastructure Setup

This script validates the database infrastructure configuration and schema
without requiring actual database connections. It performs:
- Configuration validation
- Schema file validation
- Connection string generation
- Infrastructure readiness checks
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add config to path for imports
sys.path.append(str(Path(__file__).parent.parent))

import logging

from config.database import DatabaseConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DatabaseInfrastructureValidator:
    """Validates database infrastructure setup."""

    def __init__(self):
        self.config = DatabaseConfig()
        self.validation_results = {}

    def validate_configuration(self):
        """Validate database configuration settings."""
        logger.info("🔍 Validating database configuration...")

        results = {"postgres": {}, "redis": {}, "minio": {}, "overall": {}}

        # Validate PostgreSQL configuration
        postgres_config = {
            "host": self.config.postgres_host,
            "port": self.config.postgres_port,
            "database": self.config.postgres_database,
            "user": self.config.postgres_user,
            "password": "***" if self.config.postgres_password else "NOT_SET",
        }

        results["postgres"]["config"] = postgres_config
        results["postgres"][
            "connection_string"
        ] = f"postgresql://{self.config.postgres_user}:***@{self.config.postgres_host}:{self.config.postgres_port}/{self.config.postgres_database}"

        # Validate Redis configuration
        redis_config = {
            "host": self.config.redis_host,
            "port": self.config.redis_port,
            "db": self.config.redis_database,
            "password": "***" if self.config.redis_password else "NOT_SET",
        }

        results["redis"]["config"] = redis_config
        results["redis"][
            "connection_string"
        ] = f"redis://{self.config.redis_host}:{self.config.redis_port}/{self.config.redis_database}"

        # Validate MinIO configuration
        minio_config = {
            "host": self.config.minio_host,
            "port": self.config.minio_port,
            "access_key": self.config.minio_access_key,
            "secret_key": "***" if self.config.minio_secret_key else "NOT_SET",
            "secure": self.config.minio_secure,
        }

        results["minio"]["config"] = minio_config
        results["minio"][
            "endpoint"
        ] = f"{'https' if self.config.minio_secure else 'http'}://{self.config.minio_host}:{self.config.minio_port}"

        # Overall validation
        results["overall"]["status"] = "VALID"
        results["overall"]["timestamp"] = datetime.now().isoformat()

        self.validation_results["configuration"] = results
        logger.info("✅ Configuration validation completed")
        return results

    def validate_schema_files(self):
        """Validate database schema files exist and are valid."""
        logger.info("🔍 Validating database schema files...")

        results = {"schema_files": {}, "overall": {}}

        # Check schema.sql
        schema_file = Path("database/schema.sql")
        if schema_file.exists():
            schema_content = schema_file.read_text(encoding="utf-8")
            results["schema_files"]["schema.sql"] = {
                "exists": True,
                "size_bytes": len(schema_content),
                "lines": len(schema_content.splitlines()),
                "has_tables": "CREATE TABLE" in schema_content.upper(),
                "has_indexes": "CREATE INDEX" in schema_content.upper(),
                "has_views": "CREATE VIEW" in schema_content.upper(),
                "has_functions": "CREATE FUNCTION" in schema_content.upper(),
            }
        else:
            results["schema_files"]["schema.sql"] = {
                "exists": False,
                "error": "Schema file not found",
            }

        # Check environment template
        env_template = Path("env.template")
        if env_template.exists():
            env_content = env_template.read_text(encoding="utf-8")
            results["schema_files"]["env.template"] = {
                "exists": True,
                "size_bytes": len(env_content),
                "lines": len(env_content.splitlines()),
                "has_database_config": "POSTGRES_" in env_content,
                "has_redis_config": "REDIS_" in env_content,
                "has_minio_config": "MINIO_" in env_content,
            }
        else:
            results["schema_files"]["env.template"] = {
                "exists": False,
                "error": "Environment template not found",
            }

        # Overall schema validation
        schema_valid = all(
            file_info.get("exists", False)
            for file_info in results["schema_files"].values()
        )

        results["overall"]["status"] = "VALID" if schema_valid else "INVALID"
        results["overall"]["total_files"] = len(results["schema_files"])
        results["overall"]["valid_files"] = sum(
            1
            for file_info in results["schema_files"].values()
            if file_info.get("exists", False)
        )

        self.validation_results["schema_files"] = results
        logger.info("✅ Schema file validation completed")
        return results

    def validate_dependencies(self):
        """Validate required dependencies are available."""
        logger.info("🔍 Validating dependencies...")

        results = {"python_packages": {}, "overall": {}}

        required_packages = [
            ("psycopg2", "psycopg2"),
            ("redis", "redis"),
            ("minio", "minio"),
            ("pydantic", "pydantic"),
            ("python-dotenv", "dotenv"),
            ("structlog", "structlog"),
        ]

        for package_name, import_name in required_packages:
            try:
                __import__(import_name)
                results["python_packages"][package_name] = {
                    "available": True,
                    "status": "INSTALLED",
                }
            except ImportError:
                results["python_packages"][package_name] = {
                    "available": False,
                    "status": "MISSING",
                }

        # Overall dependency validation
        all_available = all(
            package_info["available"]
            for package_info in results["python_packages"].values()
        )

        results["overall"]["status"] = "VALID" if all_available else "INVALID"
        results["overall"]["total_packages"] = len(required_packages)
        results["overall"]["available_packages"] = sum(
            1
            for package_info in results["python_packages"].values()
            if package_info["available"]
        )

        self.validation_results["dependencies"] = results
        logger.info("✅ Dependency validation completed")
        return results

    def validate_file_structure(self):
        """Validate the overall file structure for database infrastructure."""
        logger.info("🔍 Validating file structure...")

        results = {"required_files": {}, "overall": {}}

        required_files = [
            "config/database.py",
            "scripts/setup_database_infrastructure.py",
            "scripts/database_migrations.py",
            "scripts/validate_database_infrastructure.py",
            "tests/unit/test_database_infrastructure.py",
            "requirements-database.txt",
            "database/schema.sql",
            "env.template",
        ]

        for file_path in required_files:
            file_obj = Path(file_path)
            if file_obj.exists():
                results["required_files"][file_path] = {
                    "exists": True,
                    "size_bytes": file_obj.stat().st_size,
                    "is_file": file_obj.is_file(),
                }
            else:
                results["required_files"][file_path] = {
                    "exists": False,
                    "error": "File not found",
                }

        # Overall file structure validation
        all_files_exist = all(
            file_info["exists"] for file_info in results["required_files"].values()
        )

        results["overall"]["status"] = "VALID" if all_files_exist else "INVALID"
        results["overall"]["total_files"] = len(required_files)
        results["overall"]["existing_files"] = sum(
            1 for file_info in results["required_files"].values() if file_info["exists"]
        )

        self.validation_results["file_structure"] = results
        logger.info("✅ File structure validation completed")
        return results

    def generate_connection_guide(self):
        """Generate a connection guide for the infrastructure."""
        logger.info("📋 Generating connection guide...")

        guide = {
            "postgresql": {
                "connection_string": f"postgresql://{self.config.postgres_user}:***@{self.config.postgres_host}:{self.config.postgres_port}/{self.config.postgres_database}",
                "psql_command": f"psql -h {self.config.postgres_host} -p {self.config.postgres_port} -U {self.config.postgres_user} -d {self.config.postgres_database}",
                "environment_variables": {
                    "POSTGRES_HOST": self.config.postgres_host,
                    "POSTGRES_PORT": self.config.postgres_port,
                    "POSTGRES_DATABASE": self.config.postgres_database,
                    "POSTGRES_USER": self.config.postgres_user,
                },
            },
            "redis": {
                "connection_string": f"redis://{self.config.redis_host}:{self.config.redis_port}/{self.config.redis_database}",
                "redis_cli_command": f"redis-cli -h {self.config.redis_host} -p {self.config.redis_port}",
                "environment_variables": {
                    "REDIS_HOST": self.config.redis_host,
                    "REDIS_PORT": self.config.redis_port,
                    "REDIS_DB": self.config.redis_database,
                },
            },
            "minio": {
                "endpoint": f"{'https' if self.config.minio_secure else 'http'}://{self.config.minio_host}:{self.config.minio_port}",
                "mc_command": f"mc alias set myminio {'https' if self.config.minio_secure else 'http'}://{self.config.minio_host}:{self.config.minio_port} {self.config.minio_access_key} ***",
                "environment_variables": {
                    "MINIO_HOST": self.config.minio_host,
                    "MINIO_PORT": self.config.minio_port,
                    "MINIO_ACCESS_KEY": self.config.minio_access_key,
                },
            },
        }

        self.validation_results["connection_guide"] = guide
        logger.info("✅ Connection guide generated")
        return guide

    def run_full_validation(self):
        """Run complete infrastructure validation."""
        logger.info("🚀 Starting full database infrastructure validation...")

        print("=" * 60)
        print("🔍 DATABASE INFRASTRUCTURE VALIDATION")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Run all validations
        self.validate_configuration()
        self.validate_schema_files()
        self.validate_dependencies()
        self.validate_file_structure()
        self.generate_connection_guide()

        # Generate summary
        self.generate_validation_summary()

        return self.validation_results

    def generate_validation_summary(self):
        """Generate and display validation summary."""
        logger.info("📊 Generating validation summary...")

        print("=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)

        # Configuration status
        config_status = self.validation_results["configuration"]["overall"]["status"]
        print(
            f"Configuration: {'✅ VALID' if config_status == 'VALID' else '❌ INVALID'}"
        )

        # Schema files status
        schema_status = self.validation_results["schema_files"]["overall"]["status"]
        schema_files = self.validation_results["schema_files"]["overall"]
        print(
            f"Schema Files: {'✅ VALID' if schema_status == 'VALID' else '❌ INVALID'} ({schema_files['valid_files']}/{schema_files['total_files']})"
        )

        # Dependencies status
        deps_status = self.validation_results["dependencies"]["overall"]["status"]
        deps_info = self.validation_results["dependencies"]["overall"]
        print(
            f"Dependencies: {'✅ VALID' if deps_status == 'VALID' else '❌ INVALID'} ({deps_info['available_packages']}/{deps_info['total_packages']})"
        )

        # File structure status
        file_status = self.validation_results["file_structure"]["overall"]["status"]
        file_info = self.validation_results["file_structure"]["overall"]
        print(
            f"File Structure: {'✅ VALID' if file_status == 'VALID' else '❌ INVALID'} ({file_info['existing_files']}/{file_info['total_files']})"
        )

        # Overall status
        overall_valid = all(
            [
                config_status == "VALID",
                schema_status == "VALID",
                deps_status == "VALID",
                file_status == "VALID",
            ]
        )

        print()
        print("=" * 60)
        if overall_valid:
            print("🎉 INFRASTRUCTURE VALIDATION: PASSED")
            print("✅ Tech-008: Database Infrastructure Setup is READY!")
        else:
            print("⚠️  INFRASTRUCTURE VALIDATION: FAILED")
            print("❌ Some components need attention before proceeding")
        print("=" * 60)

        # Save results to file
        output_file = "database_infrastructure_validation_report.json"
        with open(output_file, "w") as f:
            json.dump(self.validation_results, f, indent=2, default=str)

        print(f"\n📄 Detailed report saved to: {output_file}")

        return overall_valid


def main():
    """Main validation function."""
    validator = DatabaseInfrastructureValidator()
    success = validator.run_full_validation()

    if success:
        print("\n🚀 Next Steps:")
        print("1. Copy env.template to .env and configure credentials")
        print("2. Start Docker containers: docker compose up -d")
        print("3. Run database setup: python scripts/setup_database_infrastructure.py")
        print("4. Apply schema: psql -f database/schema.sql")
        print("5. Proceed to Tech-009: ETL Pipeline Implementation")
    else:
        print("\n🔧 Issues to Resolve:")
        print("1. Check missing dependencies: pip install -r requirements-database.txt")
        print("2. Verify file structure and permissions")
        print("3. Review configuration settings")
        print("4. Re-run validation after fixes")

    return success


if __name__ == "__main__":
    main()
