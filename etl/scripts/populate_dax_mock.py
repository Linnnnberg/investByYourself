#!/usr/bin/env python3
"""
Populate database with mock DAX 40 data for testing.
"""

import asyncio
import os
import sqlite3
import sys
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from collectors.mock_collector import MockCollector
from transformers.company_profile_transformer import CompanyProfileTransformer
from transformers.market_data_transformer import MarketDataTransformer

from utils.logger import setup_logging

logger = setup_logging(__name__)


async def populate_dax_mock_data():
    """Populate database with mock DAX 40 data."""
    logger.info("Starting DAX 40 mock data population...")

    # Initialize components
    mock_collector = MockCollector()
    profile_transformer = CompanyProfileTransformer()
    market_transformer = MarketDataTransformer()

    # DAX 40 symbols
    dax_symbols = [
        "SAP.DE",
        "SIE.DE",
        "ALV.DE",
        "BAS.DE",
        "BAYN.DE",
        "BMW.DE",
        "CON.DE",
        "DAI.DE",
        "DBK.DE",
        "DB1.DE",
        "DPW.DE",
        "DTE.DE",
        "EOAN.DE",
        "FRE.DE",
        "HEN3.DE",
        "IFX.DE",
        "LIN.DE",
        "MRK.DE",
        "MTX.DE",
        "MUV2.DE",
        "PUM.DE",
        "QGEN.DE",
        "RWE.DE",
        "VOW3.DE",
        "ZAL.DE",
        "ADS.DE",
        "BEI.DE",
        "CBK.DE",
        "DHER.DE",
        "ENR.DE",
        "FME.DE",
        "HNR1.DE",
        "SHL.DE",
        "SY1.DE",
        "VNA.DE",
        "WCH.DE",
        "1COV.DE",
    ]

    # Database path
    db_path = "/app/db/investbyyourself_dev.db"

    # Ensure database directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Create companies table if it doesn't exist
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                sector TEXT,
                industry TEXT,
                exchange TEXT,
                currency TEXT,
                country TEXT,
                website TEXT,
                description TEXT,
                employee_count INTEGER,
                market_cap REAL,
                enterprise_value REAL,
                ceo TEXT,
                headquarters TEXT,
                founded_year INTEGER,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create market_data table if it doesn't exist
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                date DATE NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                adjusted_close REAL,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(symbol, date)
            )
        """
        )

        logger.info(f"Processing {len(dax_symbols)} DAX 40 companies...")

        for i, symbol in enumerate(dax_symbols, 1):
            try:
                logger.info(f"Processing {symbol} ({i}/{len(dax_symbols)})...")

                # Collect mock company profile
                raw_profile = await mock_collector.collect_company_profile(symbol)
                transformed_profile = profile_transformer.transform_company_profile(
                    raw_profile
                )

                # Insert company profile
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO companies
                    (symbol, name, sector, industry, exchange, currency, country,
                     website, description, employee_count, market_cap, enterprise_value,
                     ceo, headquarters, founded_year, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        transformed_profile["symbol"],
                        transformed_profile["name"],
                        transformed_profile["sector"],
                        transformed_profile["industry"],
                        transformed_profile["exchange"],
                        transformed_profile["currency"],
                        transformed_profile["country"],
                        transformed_profile["website"],
                        transformed_profile["description"],
                        transformed_profile["employee_count"],
                        transformed_profile["market_cap"],
                        transformed_profile["enterprise_value"],
                        transformed_profile["ceo"],
                        transformed_profile["headquarters"],
                        transformed_profile["founded_year"],
                        transformed_profile["is_active"],
                        transformed_profile["created_at"],
                        transformed_profile["updated_at"],
                    ),
                )

                # Collect mock historical data
                raw_historical = await mock_collector.collect_historical_data(
                    symbol, incremental=True
                )
                transformed_historical = market_transformer.transform_historical_data(
                    raw_historical
                )

                # Insert historical data
                for data_point in transformed_historical:
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO market_data
                        (symbol, date, open, high, low, close, volume, adjusted_close, source, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            data_point["symbol"],
                            data_point["date"],
                            data_point["open"],
                            data_point["high"],
                            data_point["low"],
                            data_point["close"],
                            data_point["volume"],
                            data_point["adjusted_close"],
                            data_point["source"],
                            data_point["created_at"],
                        ),
                    )

                logger.info(
                    f"✅ {symbol}: {transformed_profile['name']} - {len(transformed_historical)} historical records"
                )

            except Exception as e:
                logger.error(f"❌ Failed to process {symbol}: {e}")

        # Commit all changes
        conn.commit()

        # Verify data
        cursor.execute("SELECT COUNT(*) FROM companies")
        company_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM market_data")
        market_data_count = cursor.fetchone()[0]

        logger.info(f"✅ Database populated successfully!")
        logger.info(f"   Companies: {company_count}")
        logger.info(f"   Market data records: {market_data_count}")

        # Show some sample data
        cursor.execute("SELECT symbol, name, country FROM companies LIMIT 10")
        samples = cursor.fetchall()
        logger.info("Sample companies:")
        for symbol, name, country in samples:
            logger.info(f"  {symbol}: {name} ({country})")

    except Exception as e:
        logger.error(f"Failed to populate database: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    asyncio.run(populate_dax_mock_data())
