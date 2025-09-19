#!/usr/bin/env python3
"""
Portfolio Migration Runner
InvestByYourself Financial Platform

Runs the portfolio tables migration.
"""

import os
import sqlite3
import sys


def run_migration():
    """Run the portfolio tables migration."""
    # Get the database path
    db_path = os.path.join(
        os.path.dirname(__file__), "..", "api", "investbyyourself_dev.db"
    )

    # Read the migration file
    migration_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "database",
        "migrations",
        "003_create_portfolio_tables_simple.sql",
    )

    try:
        with open(migration_path, "r") as f:
            migration_sql = f.read()

        # Connect to database and run migration
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Split by semicolon and execute each statement
        statements = migration_sql.split(";")
        for statement in statements:
            statement = statement.strip()
            if statement:
                cursor.execute(statement)

        conn.commit()
        conn.close()

        print("✅ Portfolio tables migration completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
