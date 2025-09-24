"""
SQLite Data Loader
InvestByYourself Financial Platform

Loads transformed data into SQLite database.
"""

import asyncio
import logging
import sqlite3
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class SQLiteLoader:
    """SQLite data loader."""

    def __init__(self, database_url: str):
        """Initialize SQLite loader."""
        self.database_url = database_url
        self.db_path = self._extract_db_path(database_url)
        self.name = "SQLite Loader"

    def _extract_db_path(self, database_url: str) -> str:
        """Extract database path from URL."""
        if database_url.startswith("sqlite+aiosqlite:////"):
            return database_url.replace("sqlite+aiosqlite:////", "")
        else:
            raise ValueError(f"Unsupported database URL format: {database_url}")

    async def load_company_profile(self, data: Dict[str, Any]):
        """Load company profile data."""
        try:
            logger.info(f"Loading company profile for {data.get('symbol', 'unknown')}")

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Insert or update company profile
            cursor.execute(
                """
                INSERT OR REPLACE INTO companies (
                    id, symbol, name, sector, industry, exchange, currency, country,
                    website, description, employee_count, market_cap, enterprise_value,
                    ceo, headquarters, founded_year, is_active, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    f"company_{data['symbol']}",
                    data["symbol"],
                    data["name"],
                    data["sector"],
                    data["industry"],
                    data["exchange"],
                    data["currency"],
                    data["country"],
                    data["website"],
                    data["description"],
                    data["employee_count"],
                    data["market_cap"],
                    data["enterprise_value"],
                    data["ceo"],
                    data["headquarters"],
                    data["founded_year"],
                    data["is_active"],
                    data["created_at"],
                    data["updated_at"],
                ),
            )

            conn.commit()
            conn.close()

            logger.info(f"Company profile loaded for {data['symbol']}")

        except Exception as e:
            logger.error(
                f"Failed to load company profile for {data.get('symbol', 'unknown')}: {e}"
            )
            raise

    async def load_historical_data(self, data: List[Dict[str, Any]]):
        """Load historical market data."""
        try:
            logger.info(f"Loading {len(data)} historical data records")

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            for record in data:
                # Get company ID
                cursor.execute(
                    "SELECT id FROM companies WHERE symbol = ?", (record["symbol"],)
                )
                result = cursor.fetchone()

                if result:
                    company_id = result[0]

                    # Insert historical data
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO market_data (
                            id, company_id, data_date, open_price, high_price, low_price,
                            close_price, volume, adjusted_close, source, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            f"market_data_{record['symbol']}_{record['date']}",
                            company_id,
                            record["date"],
                            record["open"],
                            record["high"],
                            record["low"],
                            record["close"],
                            record["volume"],
                            record["adjusted_close"],
                            record["source"],
                            record["created_at"],
                        ),
                    )

            conn.commit()
            conn.close()

            logger.info(f"Historical data loaded: {len(data)} records")

        except Exception as e:
            logger.error(f"Failed to load historical data: {e}")
            raise

    async def load_economic_data(self, data: List[Dict[str, Any]]):
        """Load economic indicator data."""
        try:
            logger.info(f"Loading {len(data)} economic data records")

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            for record in data:
                # Insert economic data
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO economic_indicators (
                        id, indicator_code, indicator_name, data_date, value,
                        unit, frequency, source, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        f"economic_{record['indicator_code']}_{record['data_date']}",
                        record["indicator_code"],
                        record["indicator_name"],
                        record["data_date"],
                        record["value"],
                        record["unit"],
                        record["frequency"],
                        record["source"],
                        record["created_at"],
                    ),
                )

            conn.commit()
            conn.close()

            logger.info(f"Economic data loaded: {len(data)} records")

        except Exception as e:
            logger.error(f"Failed to load economic data: {e}")
            raise
