#!/usr/bin/env python3
"""
Simple Database Setup Script
Tech-008: Database Infrastructure Setup

This script sets up the database schema and inserts sample data for testing
the financial data exploration system. It works with a local PostgreSQL installation.
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


def create_database_schema():
    """Create the database schema from the schema.sql file."""
    try:
        # Read the schema file
        schema_file = Path(__file__).parent.parent / "database" / "schema.sql"

        if not schema_file.exists():
            logger.error(f"Schema file not found: {schema_file}")
            return False

        with open(schema_file, "r") as f:
            schema_sql = f.read()

        logger.info("📖 Schema file loaded successfully")
        return schema_sql

    except Exception as e:
        logger.error(f"Failed to read schema file: {e}")
        return False


def create_sample_data_script():
    """Create a script to insert sample data."""
    sample_data_sql = """
-- Sample Companies Data
INSERT INTO companies (symbol, name, sector, industry, exchange, country, website, description, employee_count, market_cap, enterprise_value, ceo, headquarters, founded_year, is_active) VALUES
('AAPL', 'Apple Inc.', 'Technology', 'Consumer Electronics', 'NASDAQ', 'United States', 'https://www.apple.com', 'Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables and accessories worldwide.', 164000, 3000000000000, 3200000000000, 'Tim Cook', 'Cupertino, CA', 1976, true),
('MSFT', 'Microsoft Corporation', 'Technology', 'Software', 'NASDAQ', 'United States', 'https://www.microsoft.com', 'Microsoft Corporation develops, licenses, and supports software, services, devices, and solutions worldwide.', 221000, 2800000000000, 3000000000000, 'Satya Nadella', 'Redmond, WA', 1975, true),
('GOOGL', 'Alphabet Inc.', 'Technology', 'Internet Content & Information', 'NASDAQ', 'United States', 'https://www.abc.xyz', 'Alphabet Inc. is an American multinational technology conglomerate holding company.', 156500, 1800000000000, 1900000000000, 'Sundar Pichai', 'Mountain View, CA', 2015, true),
('AMZN', 'Amazon.com Inc.', 'Consumer Cyclical', 'Internet Retail', 'NASDAQ', 'United States', 'https://www.amazon.com', 'Amazon.com Inc. engages in the retail sale of consumer products and subscriptions in North America and internationally.', 1608000, 1700000000000, 1800000000000, 'Andy Jassy', 'Seattle, WA', 1994, true),
('TSLA', 'Tesla Inc.', 'Consumer Cyclical', 'Auto Manufacturers', 'NASDAQ', 'United States', 'https://www.tesla.com', 'Tesla Inc. designs, develops, manufactures, leases and sells electric vehicles, and energy generation and storage systems.', 127855, 800000000000, 900000000000, 'Elon Musk', 'Austin, TX', 2003, true),
('JNJ', 'Johnson & Johnson', 'Healthcare', 'Drug Manufacturers', 'NYSE', 'United States', 'https://www.jnj.com', 'Johnson & Johnson researches, develops, manufactures and sells various products in the healthcare field worldwide.', 134000, 450000000000, 480000000000, 'Joaquin Duato', 'New Brunswick, NJ', 1886, true),
('JPM', 'JPMorgan Chase & Co.', 'Financial Services', 'Banks', 'NYSE', 'United States', 'https://www.jpmorganchase.com', 'JPMorgan Chase & Co. operates as a financial services company worldwide.', 256105, 400000000000, 450000000000, 'Jamie Dimon', 'New York, NY', 1799, true),
('PG', 'Procter & Gamble Co.', 'Consumer Defensive', 'Household & Personal Products', 'NYSE', 'United States', 'https://www.pg.com', 'The Procter & Gamble Company provides branded consumer packaged goods to consumers through mass merchandisers.', 101000, 350000000000, 380000000000, 'Jon Moeller', 'Cincinnati, OH', 1837, true),
('XOM', 'Exxon Mobil Corp.', 'Energy', 'Oil & Gas Integrated', 'NYSE', 'United States', 'https://www.exxonmobil.com', 'Exxon Mobil Corporation explores for and produces crude oil and natural gas in the United States and internationally.', 63000, 450000000000, 480000000000, 'Darren Woods', 'Irving, TX', 1999, true)
ON CONFLICT (symbol) DO UPDATE SET
    name = EXCLUDED.name,
    sector = EXCLUDED.sector,
    industry = EXCLUDED.industry,
    market_cap = EXCLUDED.market_cap,
    enterprise_value = EXCLUDED.enterprise_value,
    updated_at = CURRENT_TIMESTAMP;

-- Sample Market Data (last 30 days)
INSERT INTO market_data (company_id, data_date, open_price, high_price, low_price, close_price, adjusted_close, volume, market_cap, pe_ratio, pb_ratio, ps_ratio, dividend_yield, beta, source)
SELECT
    c.id,
    CURRENT_DATE - INTERVAL '1 day' * generate_series(0, 29),
    150.00 + (random() * 50 - 25),  -- Open price with variation
    150.00 + (random() * 50 - 25) + (random() * 10),  -- High price
    150.00 + (random() * 50 - 25) - (random() * 10),  -- Low price
    150.00 + (random() * 50 - 25),  -- Close price
    150.00 + (random() * 50 - 25),  -- Adjusted close
    1000000 + (random() * 5000000),  -- Volume
    c.market_cap,
    15.0 + (random() * 20),  -- P/E ratio
    2.0 + (random() * 3),    -- P/B ratio
    3.0 + (random() * 5),    -- P/S ratio
    0.01 + (random() * 0.04), -- Dividend yield
    0.8 + (random() * 0.8),   -- Beta
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
    beta = EXCLUDED.beta;

-- Sample Financial Ratios
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
    confidence_score = EXCLUDED.confidence_score;

-- Sample Economic Indicators
INSERT INTO economic_indicators (indicator_date, indicator_type, indicator_value, indicator_unit, period_type, source)
VALUES
(CURRENT_DATE - INTERVAL '1 month', 'CPI', 300.0 + (random() * 10), 'index', 'monthly', 'sample_data'),
(CURRENT_DATE - INTERVAL '2 months', 'CPI', 299.0 + (random() * 10), 'index', 'monthly', 'sample_data'),
(CURRENT_DATE - INTERVAL '3 months', 'CPI', 298.0 + (random() * 10), 'index', 'monthly', 'sample_data'),
(CURRENT_DATE - INTERVAL '1 month', 'GDP', 20.0 + (random() * 2), 'trillions', 'quarterly', 'sample_data'),
(CURRENT_DATE - INTERVAL '2 months', 'GDP', 19.8 + (random() * 2), 'trillions', 'quarterly', 'sample_data'),
(CURRENT_DATE - INTERVAL '3 months', 'GDP', 19.6 + (random() * 2), 'trillions', 'quarterly', 'sample_data')
ON CONFLICT (indicator_date, indicator_type) DO UPDATE SET
    indicator_value = EXCLUDED.indicator_value;
"""

    return sample_data_sql


def main():
    """Main setup function."""
    logger.info("🚀 Simple Database Setup Script")
    logger.info("=" * 50)

    # Step 1: Create schema SQL
    logger.info("📖 Creating database schema...")
    schema_sql = create_database_schema()
    if not schema_sql:
        logger.error("❌ Failed to create schema")
        return False

    # Step 2: Create sample data SQL
    logger.info("📊 Creating sample data script...")
    sample_data_sql = create_sample_data_script()

    # Step 3: Save both to files
    try:
        # Save schema
        schema_output = Path(__file__).parent / "database_schema.sql"
        with open(schema_output, "w") as f:
            f.write(schema_sql)
        logger.info(f"✅ Schema saved to: {schema_output}")

        # Save sample data
        sample_data_output = Path(__file__).parent / "sample_data.sql"
        with open(sample_data_output, "w") as f:
            f.write(sample_data_sql)
        logger.info(f"✅ Sample data script saved to: {sample_data_output}")

        logger.info("\n📋 Next Steps:")
        logger.info("1. Install PostgreSQL locally if not already installed")
        logger.info("2. Create a database named 'investbyyourself'")
        logger.info("3. Run: psql -d investbyyourself -f database_schema.sql")
        logger.info("4. Run: psql -d investbyyourself -f sample_data.sql")
        logger.info("5. Test with: python scripts/financial_analysis/data_explorer.py")

        return True

    except Exception as e:
        logger.error(f"❌ Failed to save files: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
