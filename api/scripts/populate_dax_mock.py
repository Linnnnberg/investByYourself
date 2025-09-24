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

logger = None


def setup_logging():
    """Setup logging."""
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    return logging.getLogger(__name__)


def create_mock_company_data(symbol):
    """Create mock company data for a symbol."""
    mock_data = {
        "SAP.DE": {
            "name": "SAP SE",
            "sector": "Technology",
            "industry": "Software",
            "country": "Germany",
        },
        "SIE.DE": {
            "name": "Siemens AG",
            "sector": "Industrial",
            "industry": "Industrial Conglomerates",
            "country": "Germany",
        },
        "ALV.DE": {
            "name": "Allianz SE",
            "sector": "Financial Services",
            "industry": "Insurance",
            "country": "Germany",
        },
        "BAS.DE": {
            "name": "BASF SE",
            "sector": "Materials",
            "industry": "Chemicals",
            "country": "Germany",
        },
        "BAYN.DE": {
            "name": "Bayer AG",
            "sector": "Healthcare",
            "industry": "Pharmaceuticals",
            "country": "Germany",
        },
        "BMW.DE": {
            "name": "BMW AG",
            "sector": "Consumer Discretionary",
            "industry": "Automotive",
            "country": "Germany",
        },
        "CON.DE": {
            "name": "Continental AG",
            "sector": "Consumer Discretionary",
            "industry": "Automotive Parts",
            "country": "Germany",
        },
        "DAI.DE": {
            "name": "Daimler Truck Holding AG",
            "sector": "Consumer Discretionary",
            "industry": "Commercial Vehicles",
            "country": "Germany",
        },
        "DBK.DE": {
            "name": "Deutsche Bank AG",
            "sector": "Financial Services",
            "industry": "Banks",
            "country": "Germany",
        },
        "DB1.DE": {
            "name": "Deutsche Börse AG",
            "sector": "Financial Services",
            "industry": "Financial Exchanges",
            "country": "Germany",
        },
    }

    base_data = mock_data.get(
        symbol,
        {
            "name": f"Company {symbol}",
            "sector": "Unknown",
            "industry": "Unknown",
            "country": "Germany",
        },
    )

    return {
        "symbol": symbol,
        "name": base_data["name"],
        "sector": base_data["sector"],
        "industry": base_data["industry"],
        "exchange": "XETRA",
        "currency": "EUR",
        "country": base_data["country"],
        "website": f"https://www.{symbol.lower().replace('.de', '')}.com",
        "description": f"{base_data['name']} is a leading company in the {base_data['industry']} industry.",
        "employee_count": 50000,
        "market_cap": 50000000000,
        "enterprise_value": 45000000000,
        "ceo": "CEO Name",
        "headquarters": "Germany",
        "founded_year": 1900,
        "is_active": True,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }


def create_mock_historical_data(symbol, days=30):
    """Create mock historical data for a symbol."""
    import random
    from datetime import timedelta

    historical_data = []
    base_price = 100.0

    for i in range(days):
        date = datetime.now() - timedelta(days=days - i)

        # Simple price movement simulation
        price_change = (random.random() - 0.5) * 2  # Random walk
        price = base_price + price_change
        base_price = price

        data_point = {
            "symbol": symbol,
            "date": date.strftime("%Y-%m-%d"),
            "open": price * 0.99,
            "high": price * 1.02,
            "low": price * 0.98,
            "close": price,
            "volume": 1000000 + random.randint(0, 100000),
            "adjusted_close": price,
            "source": "mock",
            "created_at": datetime.now().isoformat(),
        }
        historical_data.append(data_point)

    return historical_data


def populate_dax_mock_data():
    """Populate database with mock DAX 40 data."""
    global logger
    logger = setup_logging()

    logger.info("Starting DAX 40 mock data population...")

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
        # Use existing companies table (don't create new one)

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

                # Create mock company profile
                profile = create_mock_company_data(symbol)

                # Insert company profile (using existing schema)
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO companies
                    (id, symbol, name, sector, industry, exchange, currency, country,
                     website, description, employee_count, market_cap, enterprise_value,
                     ceo, headquarters, founded_year, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        f"company_{i}",  # Generate a simple ID
                        profile["symbol"],
                        profile["name"],
                        profile["sector"],
                        profile["industry"],
                        profile["exchange"],
                        profile["currency"],
                        profile["country"],
                        profile["website"],
                        profile["description"],
                        profile["employee_count"],
                        profile["market_cap"],
                        profile["enterprise_value"],
                        profile["ceo"],
                        profile["headquarters"],
                        profile["founded_year"],
                        profile["is_active"],
                        profile["created_at"],
                        profile["updated_at"],
                    ),
                )

                # Create mock historical data
                historical_data = create_mock_historical_data(symbol, 30)

                # Insert historical data
                for data_point in historical_data:
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
                    f"✅ {symbol}: {profile['name']} - {len(historical_data)} historical records"
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
    populate_dax_mock_data()
