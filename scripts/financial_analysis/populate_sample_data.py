#!/usr/bin/env python3
"""
Sample Data Population Script
Tech-008: Database Infrastructure Setup

This script populates the database with sample financial data to demonstrate
the data exploration and visualization capabilities.
"""

import logging
import os
import random
import sys
from datetime import datetime, timedelta

import psycopg2
from psycopg2.extras import RealDictCursor

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.database import DatabaseConfig, DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SampleDataPopulator:
    """Populate database with sample financial data."""

    def __init__(self):
        """Initialize with database connection."""
        try:
            self.db_manager = DatabaseManager(DatabaseConfig.from_env())
            self.test_connection()
        except Exception as e:
            logger.error(f"Failed to initialize database connection: {e}")
            raise

    def test_connection(self):
        """Test database connection."""
        try:
            with self.db_manager.get_db_session() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    logger.info("Database connection successful")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise

    def populate_companies(self):
        """Populate companies table with sample data."""
        companies_data = [
            # Technology
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
            # Healthcare
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
                "PFE",
                "Pfizer Inc.",
                "Healthcare",
                "Drug Manufacturers",
                "NYSE",
                "United States",
                "https://www.pfizer.com",
                "Pfizer Inc. discovers, develops, manufactures, markets, distributes and sells biopharmaceutical products worldwide.",
                83000,
                200000000000,
                220000000000,
                "Albert Bourla",
                "New York, NY",
                1849,
            ),
            (
                "UNH",
                "UnitedHealth Group Inc.",
                "Healthcare",
                "Healthcare Plans",
                "NYSE",
                "United States",
                "https://www.unitedhealthgroup.com",
                "UnitedHealth Group Incorporated operates as a diversified health care company in the United States.",
                400000,
                500000000000,
                530000000000,
                "Andrew Witty",
                "Minnetonka, MN",
                1977,
            ),
            # Financial
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
                "BAC",
                "Bank of America Corp.",
                "Financial Services",
                "Banks",
                "NYSE",
                "United States",
                "https://www.bankofamerica.com",
                "Bank of America Corporation provides banking and financial products and services for individuals, small- and middle-market businesses.",
                213000,
                250000000000,
                280000000000,
                "Brian Moynihan",
                "Charlotte, NC",
                1904,
            ),
            (
                "WFC",
                "Wells Fargo & Co.",
                "Financial Services",
                "Banks",
                "NYSE",
                "United States",
                "https://www.wellsfargo.com",
                "Wells Fargo & Company operates as a diversified financial services company worldwide.",
                238000,
                180000000000,
                200000000000,
                "Charles Scharf",
                "San Francisco, CA",
                1852,
            ),
            # Consumer
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
                "KO",
                "Coca-Cola Co.",
                "Consumer Defensive",
                "Beverages",
                "NYSE",
                "United States",
                "https://www.coca-cola.com",
                "The Coca-Cola Company is a beverage company that manufactures and distributes various nonalcoholic beverages worldwide.",
                70000,
                250000000000,
                270000000000,
                "James Quincey",
                "Atlanta, GA",
                1886,
            ),
            (
                "WMT",
                "Walmart Inc.",
                "Consumer Defensive",
                "Discount Stores",
                "NYSE",
                "United States",
                "https://www.walmart.com",
                "Walmart Inc. engages in the operation of retail, wholesale, and other units in the United States and internationally.",
                2300000,
                400000000000,
                430000000000,
                "Doug McMillon",
                "Bentonville, AR",
                1962,
            ),
            # Energy
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
            (
                "CVX",
                "Chevron Corporation",
                "Energy",
                "Oil & Gas Integrated",
                "NYSE",
                "United States",
                "https://www.chevron.com",
                "Chevron Corporation engages in integrated energy and chemicals operations worldwide.",
                43000,
                300000000000,
                320000000000,
                "Michael Wirth",
                "San Ramon, CA",
                1879,
            ),
        ]

        try:
            with self.db_manager.get_db_session() as conn:
                with conn.cursor() as cur:
                    for company in companies_data:
                        cur.execute(
                            """
                            INSERT INTO companies (symbol, name, sector, industry, exchange, country, website, description,
                                                 employee_count, market_cap, enterprise_value, ceo, headquarters, founded_year)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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

                    logger.info(f"Inserted/updated {len(companies_data)} companies")

        except Exception as e:
            logger.error(f"Failed to populate companies: {e}")
            raise

    def populate_market_data(self):
        """Populate market data table with sample data."""
        try:
            with self.db_manager.get_db_session() as conn:
                with conn.cursor() as cur:
                    # Get all company IDs
                    cur.execute(
                        "SELECT id, symbol FROM companies WHERE is_active = TRUE"
                    )
                    companies = cur.fetchall()

                    # Generate sample market data for the last 30 days
                    end_date = datetime.now().date()
                    start_date = end_date - timedelta(days=30)

                    for company_id, symbol in companies:
                        # Generate realistic price data
                        base_price = random.uniform(
                            50, 500
                        )  # Base price between $50-$500

                        for i in range(31):
                            current_date = start_date + timedelta(days=i)

                            # Generate realistic price movements
                            daily_change = random.uniform(
                                -0.05, 0.05
                            )  # ±5% daily change
                            base_price *= 1 + daily_change

                            open_price = base_price
                            high_price = open_price * random.uniform(1.0, 1.03)
                            low_price = open_price * random.uniform(0.97, 1.0)
                            close_price = random.uniform(low_price, high_price)

                            # Generate realistic ratios
                            pe_ratio = random.uniform(10, 30)
                            pb_ratio = random.uniform(1, 5)
                            ps_ratio = random.uniform(1, 8)
                            dividend_yield = random.uniform(0, 0.06)  # 0-6%
                            beta = random.uniform(0.5, 1.5)

                            # Get market cap from companies table
                            cur.execute(
                                "SELECT market_cap FROM companies WHERE id = %s",
                                (company_id,),
                            )
                            market_cap = cur.fetchone()[0]

                            # Calculate volume (realistic based on market cap)
                            volume = int(
                                market_cap / base_price * random.uniform(0.001, 0.01)
                            )

                            cur.execute(
                                """
                                INSERT INTO market_data (company_id, data_date, open_price, high_price, low_price,
                                                       close_price, adjusted_close, volume, market_cap,
                                                       pe_ratio, pb_ratio, ps_ratio, dividend_yield, beta)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                            """,
                                (
                                    company_id,
                                    current_date,
                                    open_price,
                                    high_price,
                                    low_price,
                                    close_price,
                                    close_price,
                                    volume,
                                    market_cap,
                                    pe_ratio,
                                    pb_ratio,
                                    ps_ratio,
                                    dividend_yield,
                                    beta,
                                ),
                            )

                    logger.info(
                        f"Generated market data for {len(companies)} companies over 30 days"
                    )

        except Exception as e:
            logger.error(f"Failed to populate market data: {e}")
            raise

    def populate_financial_ratios(self):
        """Populate financial ratios table with sample data."""
        try:
            with self.db_manager.get_db_session() as conn:
                with conn.cursor() as cur:
                    # Get all company IDs
                    cur.execute("SELECT id FROM companies WHERE is_active = TRUE")
                    companies = cur.fetchall()

                    ratio_types = [
                        "pe_ratio",
                        "pb_ratio",
                        "ps_ratio",
                        "debt_to_equity",
                        "current_ratio",
                        "quick_ratio",
                    ]

                    for (company_id,) in companies:
                        for ratio_type in ratio_types:
                            # Generate sample ratio data for the last 12 months
                            for i in range(12):
                                ratio_date = datetime.now().date() - timedelta(
                                    days=i * 30
                                )

                                # Generate realistic ratio values
                                if ratio_type == "pe_ratio":
                                    ratio_value = random.uniform(8, 35)
                                elif ratio_type == "pb_ratio":
                                    ratio_value = random.uniform(0.5, 8)
                                elif ratio_type == "ps_ratio":
                                    ratio_value = random.uniform(0.5, 12)
                                elif ratio_type == "debt_to_equity":
                                    ratio_value = random.uniform(0.1, 2.0)
                                elif ratio_type == "current_ratio":
                                    ratio_value = random.uniform(0.8, 3.0)
                                elif ratio_type == "quick_ratio":
                                    ratio_value = random.uniform(0.5, 2.5)

                                confidence_score = random.uniform(0.8, 1.0)

                                cur.execute(
                                    """
                                    INSERT INTO financial_ratios (company_id, ratio_date, ratio_type, ratio_value,
                                                                ratio_unit, source, confidence_score)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                                    ON CONFLICT (company_id, ratio_date, ratio_type) DO UPDATE SET
                                        ratio_value = EXCLUDED.ratio_value,
                                        confidence_score = EXCLUDED.confidence_score
                                """,
                                    (
                                        company_id,
                                        ratio_date,
                                        ratio_type,
                                        ratio_value,
                                        "ratio",
                                        "sample_data",
                                        confidence_score,
                                    ),
                                )

                    logger.info(
                        f"Generated financial ratios for {len(companies)} companies"
                    )

        except Exception as e:
            logger.error(f"Failed to populate financial ratios: {e}")
            raise

    def populate_economic_indicators(self):
        """Populate economic indicators table with sample data."""
        indicators_data = [
            ("CPI", "Consumer Price Index", "index", "monthly"),
            ("PPI", "Producer Price Index", "index", "monthly"),
            ("GDP", "Gross Domestic Product", "trillions", "quarterly"),
            ("Unemployment", "Unemployment Rate", "percent", "monthly"),
            ("Interest_Rate", "Federal Funds Rate", "percent", "monthly"),
        ]

        try:
            with self.db_manager.get_db_session() as conn:
                with conn.cursor() as cur:
                    for indicator_type, description, unit, period in indicators_data:
                        # Generate sample data for the last 24 months
                        for i in range(24):
                            indicator_date = datetime.now().date() - timedelta(
                                days=i * 30
                            )

                            # Generate realistic indicator values
                            if indicator_type == "CPI":
                                base_value = 300  # Base CPI around 300
                                indicator_value = (
                                    base_value + random.uniform(-5, 5) + i * 0.5
                                )  # Gradual increase
                            elif indicator_type == "PPI":
                                base_value = 250  # Base PPI around 250
                                indicator_value = (
                                    base_value + random.uniform(-3, 3) + i * 0.3
                                )
                            elif indicator_type == "GDP":
                                base_value = 20  # Base GDP around $20T
                                indicator_value = (
                                    base_value + random.uniform(-0.5, 0.5) + i * 0.1
                                )
                            elif indicator_type == "Unemployment":
                                base_value = 4.0  # Base unemployment around 4%
                                indicator_value = base_value + random.uniform(-0.5, 0.5)
                            elif indicator_type == "Interest_Rate":
                                base_value = 5.0  # Base interest rate around 5%
                                indicator_value = base_value + random.uniform(
                                    -0.25, 0.25
                                )

                            cur.execute(
                                """
                                INSERT INTO economic_indicators (indicator_date, indicator_type, indicator_value,
                                                               indicator_unit, period_type, source)
                                VALUES (%s, %s, %s, %s, %s, %s)
                                ON CONFLICT (indicator_date, indicator_type) DO UPDATE SET
                                    indicator_value = EXCLUDED.indicator_value
                            """,
                                (
                                    indicator_date,
                                    indicator_type,
                                    indicator_value,
                                    unit,
                                    period,
                                    "sample_data",
                                ),
                            )

                    logger.info(
                        f"Generated economic indicators for {len(indicators_data)} indicators"
                    )

        except Exception as e:
            logger.error(f"Failed to populate economic indicators: {e}")
            raise

    def populate_all_data(self):
        """Populate all tables with sample data."""
        logger.info("Starting data population...")

        try:
            self.populate_companies()
            self.populate_market_data()
            self.populate_financial_ratios()
            self.populate_economic_indicators()

            logger.info("Data population completed successfully!")

        except Exception as e:
            logger.error(f"Data population failed: {e}")
            raise


def main():
    """Main function to populate sample data."""
    try:
        populator = SampleDataPopulator()
        populator.populate_all_data()

        print("=== Sample Data Population Complete ===")
        print("✅ Companies: 16 major US companies")
        print("✅ Market Data: 30 days of price history")
        print("✅ Financial Ratios: 12 months of ratio data")
        print("✅ Economic Indicators: 24 months of macro data")
        print("\nYou can now run the financial dashboard to explore the data!")

    except Exception as e:
        logger.error(f"Failed to populate sample data: {e}")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
