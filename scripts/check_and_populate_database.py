#!/usr/bin/env python3
"""
Database Check and Population Script
Tech-008: Database Infrastructure Setup

This script checks the current database status and populates it with sample data
for testing the financial data exploration system.
"""

import logging
import os
import sys
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_database_status():
    """Check the current database status."""
    try:
        from config.database import DatabaseConfig, DatabaseManager

        # Initialize database manager
        db_manager = DatabaseManager(DatabaseConfig.from_env())

        # Test connection
        with db_manager.get_db_session() as conn:
            with conn.cursor() as cur:
                # Check if tables exist
                cur.execute(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """
                )
                tables = [row[0] for row in cur.fetchall()]

                logger.info(f"📊 Found {len(tables)} tables in database:")
                for table in tables:
                    logger.info(f"   - {table}")

                # Check data counts
                data_counts = {}
                for table in [
                    "companies",
                    "market_data",
                    "financial_ratios",
                    "economic_indicators",
                ]:
                    if table in tables:
                        cur.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cur.fetchone()[0]
                        data_counts[table] = count
                        logger.info(f"   📈 {table}: {count} records")

                return tables, data_counts

    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return [], {}


def populate_sample_data():
    """Populate the database with sample data."""
    try:
        from config.database import DatabaseConfig, DatabaseManager

        # Initialize database manager
        db_manager = DatabaseManager(DatabaseConfig.from_env())

        logger.info("🚀 Populating database with sample data...")

        with db_manager.get_db_session() as conn:
            with conn.cursor() as cur:
                # 1. Insert sample companies
                logger.info("📊 Inserting sample companies...")
                companies_data = [
                    (
                        "AAPL",
                        "Apple Inc.",
                        "Technology",
                        "Consumer Electronics",
                        "NASDAQ",
                        "United States",
                        "https://www.apple.com",
                        "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables and accessories worldwide.",
                        164000,
                        3000000000000,
                        3200000000000,
                        "Tim Cook",
                        "Cupertino, CA",
                        1976,
                    ),
                    (
                        "MSFT",
                        "Microsoft Corporation",
                        "Technology",
                        "Software",
                        "NASDAQ",
                        "United States",
                        "https://www.microsoft.com",
                        "Microsoft Corporation develops, licenses, and supports software, services, devices, and solutions worldwide.",
                        221000,
                        2800000000000,
                        3000000000000,
                        "Satya Nadella",
                        "Redmond, WA",
                        1975,
                    ),
                    (
                        "GOOGL",
                        "Alphabet Inc.",
                        "Technology",
                        "Internet Content & Information",
                        "NASDAQ",
                        "United States",
                        "https://www.abc.xyz",
                        "Alphabet Inc. is an American multinational technology conglomerate holding company.",
                        156500,
                        1800000000000,
                        1900000000000,
                        "Sundar Pichai",
                        "Mountain View, CA",
                        2015,
                    ),
                    (
                        "AMZN",
                        "Amazon.com Inc.",
                        "Consumer Cyclical",
                        "Internet Retail",
                        "NASDAQ",
                        "United States",
                        "https://www.amazon.com",
                        "Amazon.com Inc. engages in the retail sale of consumer products and subscriptions in North America and internationally.",
                        1608000,
                        1700000000000,
                        1800000000000,
                        "Andy Jassy",
                        "Seattle, WA",
                        1994,
                    ),
                    (
                        "TSLA",
                        "Tesla Inc.",
                        "Consumer Cyclical",
                        "Auto Manufacturers",
                        "NASDAQ",
                        "United States",
                        "https://www.tesla.com",
                        "Tesla Inc. designs, develops, manufactures, leases and sells electric vehicles, and energy generation and storage systems.",
                        127855,
                        800000000000,
                        900000000000,
                        "Elon Musk",
                        "Austin, TX",
                        2003,
                    ),
                    (
                        "JNJ",
                        "Johnson & Johnson",
                        "Healthcare",
                        "Drug Manufacturers",
                        "NYSE",
                        "United States",
                        "https://www.jnj.com",
                        "Johnson & Johnson researches, develops, manufactures and sells various products in the healthcare field worldwide.",
                        134000,
                        450000000000,
                        480000000000,
                        "Joaquin Duato",
                        "New Brunswick, NJ",
                        1886,
                    ),
                    (
                        "JPM",
                        "JPMorgan Chase & Co.",
                        "Financial Services",
                        "Banks",
                        "NYSE",
                        "United States",
                        "https://www.jpmorganchase.com",
                        "JPMorgan Chase & Co. operates as a financial services company worldwide.",
                        256105,
                        400000000000,
                        450000000000,
                        "Jamie Dimon",
                        "New York, NY",
                        1799,
                    ),
                    (
                        "PG",
                        "Procter & Gamble Co.",
                        "Consumer Defensive",
                        "Household & Personal Products",
                        "NYSE",
                        "United States",
                        "https://www.pg.com",
                        "The Procter & Gamble Company provides branded consumer packaged goods to consumers through mass merchandisers.",
                        101000,
                        350000000000,
                        380000000000,
                        "Jon Moeller",
                        "Cincinnati, OH",
                        1837,
                    ),
                    (
                        "XOM",
                        "Exxon Mobil Corp.",
                        "Energy",
                        "Oil & Gas Integrated",
                        "NYSE",
                        "United States",
                        "https://www.exxonmobil.com",
                        "Exxon Mobil Corporation explores for and produces crude oil and natural gas in the United States and internationally.",
                        63000,
                        450000000000,
                        480000000000,
                        "Darren Woods",
                        "Irving, TX",
                        1999,
                    ),
                ]

                for company in companies_data:
                    cur.execute(
                        """
                        INSERT INTO companies (symbol, name, sector, industry, exchange, country, website, description,
                                             employee_count, market_cap, enterprise_value, ceo, headquarters, founded_year, is_active)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (symbol) DO UPDATE SET
                            name = EXCLUDED.name,
                            sector = EXCLUDED.sector,
                            industry = EXCLUDED.industry,
                            market_cap = EXCLUDED.market_cap,
                            enterprise_value = EXCLUDED.enterprise_value,
                            updated_at = CURRENT_TIMESTAMP
                    """,
                        company,
                    )

                logger.info(f"✅ Inserted/updated {len(companies_data)} companies")

                # 2. Insert sample market data
                logger.info("📈 Inserting sample market data...")
                cur.execute(
                    """
                    INSERT INTO market_data (company_id, data_date, open_price, high_price, low_price, close_price,
                                           adjusted_close, volume, market_cap, pe_ratio, pb_ratio, ps_ratio,
                                           dividend_yield, beta, source)
                    SELECT
                        c.id,
                        CURRENT_DATE - INTERVAL '1 day' * generate_series(0, 29),
                        150.00 + (random() * 50 - 25),
                        150.00 + (random() * 50 - 25) + (random() * 10),
                        150.00 + (random() * 50 - 25) - (random() * 10),
                        150.00 + (random() * 50 - 25),
                        150.00 + (random() * 50 - 25),
                        1000000 + (random() * 5000000),
                        c.market_cap,
                        15.0 + (random() * 20),
                        2.0 + (random() * 3),
                        3.0 + (random() * 5),
                        0.01 + (random() * 0.04),
                        0.8 + (random() * 0.8),
                        'sample_data'
                    FROM companies c
                    WHERE c.symbol IN ('AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA')
                    ON CONFLICT (company_id, data_date) DO UPDATE SET
                        open_price = EXCLUDED.open_price,
                        high_price = EXCLUDED.high_price,
                        low_price = EXCLUDED.low_price,
                        close_price = EXCLUDED.close_price,
                        adjusted_close = EXCLUDED.adjusted_close,
                        volume = EXCLUDED.volume,
                        pe_ratio = EXCLUDED.pe_ratio,
                        pb_ratio = EXCLUDED.pb_ratio,
                        ps_ratio = EXCLUDED.ps_ratio,
                        dividend_yield = EXCLUDED.dividend_yield,
                        beta = EXCLUDED.beta
                """
                )

                logger.info("✅ Inserted sample market data")

                # 3. Insert sample financial ratios
                logger.info("📊 Inserting sample financial ratios...")
                cur.execute(
                    """
                    INSERT INTO financial_ratios (company_id, ratio_date, ratio_type, ratio_value, ratio_unit, source, confidence_score)
                    SELECT
                        c.id,
                        CURRENT_DATE - INTERVAL '1 month' * generate_series(0, 11),
                        'pe_ratio',
                        15.0 + (random() * 20),
                        'ratio',
                        'sample_data',
                        0.9 + (random() * 0.1)
                    FROM companies c
                    WHERE c.symbol IN ('AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA')
                    ON CONFLICT (company_id, ratio_date, ratio_type) DO UPDATE SET
                        ratio_value = EXCLUDED.ratio_value,
                        confidence_score = EXCLUDED.confidence_score
                """
                )

                logger.info("✅ Inserted sample financial ratios")

                # 4. Insert sample economic indicators
                logger.info("🌍 Inserting sample economic indicators...")
                cur.execute(
                    """
                    INSERT INTO economic_indicators (indicator_date, indicator_type, indicator_value, indicator_unit, period_type, source)
                    VALUES
                    (CURRENT_DATE - INTERVAL '1 month', 'CPI', 300.0 + (random() * 10), 'index', 'monthly', 'sample_data'),
                    (CURRENT_DATE - INTERVAL '2 months', 'CPI', 299.0 + (random() * 10), 'index', 'monthly', 'sample_data'),
                    (CURRENT_DATE - INTERVAL '3 months', 'CPI', 298.0 + (random() * 10), 'index', 'monthly', 'sample_data'),
                    (CURRENT_DATE - INTERVAL '1 month', 'GDP', 20.0 + (random() * 2), 'trillions', 'quarterly', 'sample_data'),
                    (CURRENT_DATE - INTERVAL '2 months', 'GDP', 19.8 + (random() * 2), 'trillions', 'quarterly', 'sample_data'),
                    (CURRENT_DATE - INTERVAL '3 months', 'GDP', 19.6 + (random() * 2), 'trillions', 'quarterly', 'sample_data')
                    ON CONFLICT (indicator_date, indicator_type) DO UPDATE SET
                        indicator_value = EXCLUDED.indicator_value
                """
                )

                logger.info("✅ Inserted sample economic indicators")

                conn.commit()
                logger.info("🎉 Database population completed successfully!")
                return True

    except Exception as e:
        logger.error(f"❌ Failed to populate database: {e}")
        return False


def main():
    """Main function."""
    logger.info("🚀 Database Check and Population Script")
    logger.info("=" * 50)

    # Step 1: Check current database status
    logger.info("🔍 Checking current database status...")
    tables, data_counts = check_database_status()

    if not tables:
        logger.error("❌ Cannot connect to database. Please check your connection.")
        return False

    # Step 2: Check if we need to populate data
    total_records = sum(data_counts.values())
    if total_records > 0:
        logger.info(f"📊 Database already has {total_records} records")
        logger.info("💡 You can now test the financial exploration system!")
        logger.info("\n📋 To test the system:")
        logger.info("1. Run: python scripts/financial_analysis/data_explorer.py")
        logger.info(
            "2. Or launch dashboard: streamlit run scripts/financial_analysis/financial_dashboard.py"
        )
        return True
    else:
        logger.info("📊 Database is empty, populating with sample data...")

        # Step 3: Populate with sample data
        if populate_sample_data():
            logger.info("\n🎉 Database is now ready for testing!")
            logger.info("\n📋 To test the system:")
            logger.info("1. Run: python scripts/financial_analysis/data_explorer.py")
            logger.info(
                "2. Or launch dashboard: streamlit run scripts/financial_analysis/financial_dashboard.py"
            )
            return True
        else:
            logger.error("❌ Failed to populate database")
            return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
