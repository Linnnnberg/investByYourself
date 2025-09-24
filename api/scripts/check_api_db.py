#!/usr/bin/env python3
"""
Check API database status and tables.
"""

import os
import sqlite3


def check_database():
    """Check database status."""
    db_path = "/app/investbyyourself_dev.db"

    if os.path.exists(db_path):
        print(f"API database found at: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Tables: {[table[0] for table in tables]}")

        # Check companies table if it exists
        if any("companies" in table[0] for table in tables):
            cursor.execute("SELECT COUNT(*) FROM companies")
            count = cursor.fetchone()[0]
            print(f"Companies count: {count}")

            # Show some sample companies
            cursor.execute("SELECT symbol, name, country FROM companies LIMIT 10")
            companies = cursor.fetchall()
            print("Sample companies:")
            for company in companies:
                print(f"  {company[0]}: {company[1]} ({company[2]})")

        conn.close()
    else:
        print(f"API database file not found at: {db_path}")


if __name__ == "__main__":
    check_database()
