#!/usr/bin/env python3
"""
Check Database Schema
"""

import sqlite3


def check_schema():
    conn = sqlite3.connect("/app/db/investbyyourself_dev.db")
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Tables:", [table[0] for table in tables])

    # Check if market_data table exists
    if any(table[0] == "market_data" for table in tables):
        cursor.execute("PRAGMA table_info(market_data)")
        schema = cursor.fetchall()
        print("market_data schema:", schema)
    else:
        print("market_data table does not exist")

    conn.close()


if __name__ == "__main__":
    check_schema()
