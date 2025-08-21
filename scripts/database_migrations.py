#!/usr/bin/env python3
"""
Database Migration Script
Tech-008: Database Infrastructure Setup

This script manages database schema migrations and updates for the ETL pipeline.
It provides version control for database schema changes and rollback capabilities.
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

import logging

from config.database import get_db_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DatabaseMigration:
    """Database migration management class."""

    def __init__(self):
        self.db_manager = get_db_manager()
        self.migrations_table = "schema_migrations"

    def ensure_migrations_table(self):
        """Ensure the migrations tracking table exists."""
        try:
            with self.db_manager.get_db_session() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS schema_migrations (
                            id SERIAL PRIMARY KEY,
                            version VARCHAR(50) UNIQUE NOT NULL,
                            name VARCHAR(255) NOT NULL,
                            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            checksum VARCHAR(64),
                            execution_time_ms INTEGER,
                            status VARCHAR(20) DEFAULT 'success'
                        );
                    """
                    )
                    conn.commit()
                    logger.info("✅ Migrations table ensured")
                    return True
        except Exception as e:
            logger.error(f"❌ Failed to create migrations table: {e}")
            return False

    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions."""
        try:
            with self.db_manager.get_db_session() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT version FROM schema_migrations ORDER BY applied_at"
                    )
                    versions = [row[0] for row in cur.fetchall()]
                    return versions
        except Exception as e:
            logger.error(f"❌ Failed to get applied migrations: {e}")
            return []

    def record_migration(
        self,
        version: str,
        name: str,
        checksum: str,
        execution_time_ms: int,
        status: str = "success",
    ):
        """Record a migration in the tracking table."""
        try:
            with self.db_manager.get_db_session() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO schema_migrations (version, name, checksum, execution_time_ms, status)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (version) DO UPDATE SET
                            applied_at = CURRENT_TIMESTAMP,
                            checksum = EXCLUDED.checksum,
                            execution_time_ms = EXCLUDED.execution_time_ms,
                            status = EXCLUDED.status
                    """,
                        (version, name, checksum, execution_time_ms, status),
                    )
                    conn.commit()
                    logger.info(f"✅ Recorded migration: {version} - {name}")
                    return True
        except Exception as e:
            logger.error(f"❌ Failed to record migration {version}: {e}")
            return False

    def apply_migration(self, version: str, name: str, sql_script: str) -> bool:
        """Apply a single migration."""
        logger.info(f"🔄 Applying migration: {version} - {name}")

        start_time = time.time()
        checksum = self._calculate_checksum(sql_script)

        try:
            with self.db_manager.get_db_session() as conn:
                with conn.cursor() as cur:
                    # Execute the migration SQL
                    cur.execute(sql_script)
                    conn.commit()

                    execution_time_ms = int((time.time() - start_time) * 1000)

                    # Record successful migration
                    self.record_migration(
                        version, name, checksum, execution_time_ms, "success"
                    )

                    logger.info(
                        f"✅ Migration {version} applied successfully in {execution_time_ms}ms"
                    )
                    return True

        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            self.record_migration(version, name, checksum, execution_time_ms, "failed")
            logger.error(f"❌ Migration {version} failed: {e}")
            return False

    def _calculate_checksum(self, content: str) -> str:
        """Calculate SHA256 checksum of migration content."""
        import hashlib

        return hashlib.sha256(content.encode()).hexdigest()

    def rollback_migration(self, version: str) -> bool:
        """Rollback a specific migration."""
        logger.info(f"🔄 Rolling back migration: {version}")

        # Get migration details
        try:
            with self.db_manager.get_db_session() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT name, checksum FROM schema_migrations
                        WHERE version = %s
                    """,
                        (version,),
                    )
                    result = cur.fetchone()

                    if not result:
                        logger.error(f"❌ Migration {version} not found")
                        return False

                    name, checksum = result

                    # For now, we'll just mark it as rolled back
                    # In a real implementation, you'd have rollback SQL scripts
                    cur.execute(
                        """
                        UPDATE schema_migrations
                        SET status = 'rolled_back'
                        WHERE version = %s
                    """,
                        (version,),
                    )
                    conn.commit()

                    logger.info(f"✅ Migration {version} marked as rolled back")
                    return True

        except Exception as e:
            logger.error(f"❌ Failed to rollback migration {version}: {e}")
            return False

    def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status."""
        try:
            with self.db_manager.get_db_session() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT
                            COUNT(*) as total_migrations,
                            COUNT(CASE WHEN status = 'success' THEN 1 END) as successful,
                            COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
                            COUNT(CASE WHEN status = 'rolled_back' THEN 1 END) as rolled_back,
                            MAX(applied_at) as last_migration
                        FROM schema_migrations
                    """
                    )
                    result = cur.fetchone()

                    return {
                        "total_migrations": result[0],
                        "successful": result[1],
                        "failed": result[2],
                        "rolled_back": result[3],
                        "last_migration": result[4],
                    }

        except Exception as e:
            logger.error(f"❌ Failed to get migration status: {e}")
            return {}


def create_sample_migration():
    """Create a sample migration for testing."""
    return {
        "version": "001",
        "name": "add_company_metadata_table",
        "sql_script": """
            CREATE TABLE IF NOT EXISTS company_metadata (
                id SERIAL PRIMARY KEY,
                company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
                metadata_key VARCHAR(100) NOT NULL,
                metadata_value TEXT,
                data_source VARCHAR(50),
                confidence_score DECIMAL(3,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                UNIQUE(company_id, metadata_key)
            );

            CREATE INDEX IF NOT EXISTS idx_company_metadata_company_id
            ON company_metadata(company_id);

            CREATE INDEX IF NOT EXISTS idx_company_metadata_key
            ON company_metadata(metadata_key);
        """,
    }


def main():
    """Main migration function."""
    logger.info("🚀 Starting Database Migration System (Tech-008)")
    logger.info("=" * 60)

    migration_manager = DatabaseMigration()

    # Ensure migrations table exists
    if not migration_manager.ensure_migrations_table():
        logger.error("❌ Failed to ensure migrations table")
        return False

    # Get current migration status
    status = migration_manager.get_migration_status()
    logger.info("📊 Current Migration Status:")
    logger.info(f"  📈 Total migrations: {status.get('total_migrations', 0)}")
    logger.info(f"  ✅ Successful: {status.get('successful', 0)}")
    logger.info(f"  ❌ Failed: {status.get('failed', 0)}")
    logger.info(f"  🔄 Rolled back: {status.get('rolled_back', 0)}")

    # Get applied migrations
    applied = migration_manager.get_applied_migrations()
    logger.info(f"📋 Applied migrations: {', '.join(applied) if applied else 'None'}")

    # Create and apply sample migration if none exist
    if not applied:
        logger.info("🆕 No migrations applied yet. Creating sample migration...")
        sample_migration = create_sample_migration()

        if migration_manager.apply_migration(
            sample_migration["version"],
            sample_migration["name"],
            sample_migration["sql_script"],
        ):
            logger.info("✅ Sample migration applied successfully!")
        else:
            logger.error("❌ Sample migration failed!")
            return False

    logger.info("=" * 60)
    logger.info("🎉 Database Migration System Ready!")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
