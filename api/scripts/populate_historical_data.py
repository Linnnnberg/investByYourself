#!/usr/bin/env python3
"""
Populate Historical Price Data
Tech-028: API Implementation

This script gathers historical price time series data for all companies
and inserts it into the market_data table.
"""

import asyncio
import random
import sqlite3
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import pandas as pd
import yfinance as yf


class HistoricalDataCollector:
    """Collect historical price data for companies."""

    def __init__(self):
        self.rate_limit = 2.0  # 2 seconds between requests
        self.last_request = 0
        self.collected_count = 0
        self.skipped_count = 0
        self.error_count = 0

    async def _rate_limit(self):
        """Apply rate limiting with randomness."""
        current_time = time.time()
        time_since_last = current_time - self.last_request

        # Add randomness to avoid predictable patterns
        delay = self.rate_limit + random.uniform(0, 1)

        if time_since_last < delay:
            sleep_time = delay - time_since_last
            print(f"⏳ Rate limiting: sleeping for {sleep_time:.2f} seconds")
            await asyncio.sleep(sleep_time)

        self.last_request = time.time()

    async def get_historical_data(
        self, symbol: str, days: int = 365
    ) -> Optional[pd.DataFrame]:
        """Get historical price data from Yahoo Finance."""
        try:
            await self._rate_limit()

            print(f"📈 Fetching historical data for {symbol}...")
            ticker = yf.Ticker(symbol)

            # Get historical data for the specified period
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            hist = ticker.history(start=start_date, end=end_date)

            if hist.empty:
                print(f"⚠️  No historical data available for {symbol}")
                return None

            # Clean and format the data
            hist = hist.reset_index()
            hist["Date"] = hist["Date"].dt.strftime("%Y-%m-%d")

            print(f"✅ Got {len(hist)} days of data for {symbol}")
            return hist

        except Exception as e:
            print(f"❌ Error fetching historical data for {symbol}: {str(e)}")
            self.error_count += 1
            return None

    async def insert_historical_data(
        self, symbol: str, hist_data: pd.DataFrame
    ) -> bool:
        """Insert historical data into the database."""
        try:
            conn = sqlite3.connect("/app/db/investbyyourself_dev.db")
            cursor = conn.cursor()

            # Create market_data table if it doesn't exist
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS market_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol VARCHAR(20) NOT NULL,
                    date DATE NOT NULL,
                    open DECIMAL(10,2),
                    high DECIMAL(10,2),
                    low DECIMAL(10,2),
                    close DECIMAL(10,2),
                    volume BIGINT,
                    adjusted_close DECIMAL(10,2),
                    source VARCHAR(50) DEFAULT 'yahoo_finance',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, date)
                )
            """
            )

            # Check if we already have data for this symbol
            cursor.execute(
                "SELECT COUNT(*) FROM market_data WHERE symbol = ?", (symbol,)
            )
            existing_count = cursor.fetchone()[0]

            if existing_count > 0:
                print(
                    f"⚠️  Historical data already exists for {symbol} ({existing_count} records)"
                )
                conn.close()
                return False

            # Insert historical data
            inserted_count = 0
            for _, row in hist_data.iterrows():
                try:
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO market_data
                        (symbol, date, open, high, low, close, volume, adjusted_close, source)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            symbol,
                            row["Date"],
                            float(row["Open"]) if pd.notna(row["Open"]) else None,
                            float(row["High"]) if pd.notna(row["High"]) else None,
                            float(row["Low"]) if pd.notna(row["Low"]) else None,
                            float(row["Close"]) if pd.notna(row["Close"]) else None,
                            int(row["Volume"]) if pd.notna(row["Volume"]) else None,
                            float(row["Close"])
                            if pd.notna(row["Close"])
                            else None,  # Use close as adjusted_close for now
                            "yahoo_finance",
                        ),
                    )
                    inserted_count += 1
                except Exception as e:
                    print(f"⚠️  Error inserting row for {symbol}: {str(e)}")
                    continue

            conn.commit()
            conn.close()

            print(f"✅ Inserted {inserted_count} records for {symbol}")
            self.collected_count += 1
            return True

        except Exception as e:
            print(f"❌ Error inserting historical data for {symbol}: {str(e)}")
            self.error_count += 1
            return False

    async def collect_historical_data_batch(self, limit: int = 5, days: int = 365):
        """Collect historical data for a batch of companies."""
        try:
            # Connect to database
            conn = sqlite3.connect("/app/db/investbyyourself_dev.db")
            cursor = conn.cursor()

            # Get companies that don't have historical data yet
            cursor.execute(
                """
                SELECT c.symbol, c.name
                FROM companies c
                LEFT JOIN market_data m ON c.symbol = m.symbol
                WHERE m.symbol IS NULL
                ORDER BY c.symbol
                LIMIT ?
            """,
                (limit,),
            )

            companies = cursor.fetchall()
            conn.close()

            if not companies:
                print("✅ All companies already have historical data!")
                return

            print(f"🔄 Collecting historical data for {len(companies)} companies...")

            for symbol, name in companies:
                print(f"\n📊 Processing {symbol} ({name})...")

                # Get historical data
                hist_data = await self.get_historical_data(symbol, days)

                if hist_data is not None:
                    # Insert into database
                    await self.insert_historical_data(symbol, hist_data)
                else:
                    print(f"⚠️  Skipped {symbol} - no historical data available")
                    self.skipped_count += 1

                # Small delay between companies
                await asyncio.sleep(0.5)

            # Show summary
            print(f"\n📊 Collection Summary:")
            print(f"   Collected: {self.collected_count}")
            print(f"   Skipped: {self.skipped_count}")
            print(f"   Errors: {self.error_count}")

        except Exception as e:
            print(f"❌ Error in batch collection: {str(e)}")
            raise

    async def show_historical_data_status(self):
        """Show current historical data status."""
        try:
            conn = sqlite3.connect("/app/db/investbyyourself_dev.db")
            cursor = conn.cursor()

            # Get statistics
            cursor.execute("SELECT COUNT(*) FROM companies")
            total_companies = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM market_data")
            companies_with_data = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM market_data")
            total_records = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT symbol, COUNT(*) as record_count,
                       MIN(date) as earliest_date, MAX(date) as latest_date
                FROM market_data
                GROUP BY symbol
                ORDER BY record_count DESC
                LIMIT 5
            """
            )
            top_companies = cursor.fetchall()

            print(f"\n📊 Historical Data Status:")
            print(f"   Total companies: {total_companies}")
            print(
                f"   Companies with historical data: {companies_with_data}/{total_companies} ({companies_with_data/total_companies*100:.1f}%)"
            )
            print(f"   Total price records: {total_records:,}")

            if top_companies:
                print(f"\n📈 Companies with most data:")
                for symbol, count, earliest, latest in top_companies:
                    print(
                        f"   {symbol:<8} - {count:>4} records ({earliest} to {latest})"
                    )

            # Show companies without data
            cursor.execute(
                """
                SELECT c.symbol, c.name
                FROM companies c
                LEFT JOIN market_data m ON c.symbol = m.symbol
                WHERE m.symbol IS NULL
                ORDER BY c.symbol
                LIMIT 10
            """
            )
            missing_data = cursor.fetchall()

            if missing_data:
                print(f"\n⚠️  Companies without historical data:")
                for symbol, name in missing_data:
                    print(f"   {symbol:<8} - {name}")

            conn.close()

        except Exception as e:
            print(f"❌ Error showing status: {str(e)}")

    async def collect_all_historical_data(self, days: int = 365):
        """Collect historical data for all companies."""
        try:
            conn = sqlite3.connect("/app/db/investbyyourself_dev.db")
            cursor = conn.cursor()

            # Get all companies
            cursor.execute("SELECT symbol, name FROM companies ORDER BY symbol")
            companies = cursor.fetchall()
            conn.close()

            print(f"🔄 Collecting historical data for all {len(companies)} companies...")
            print(f"📅 Collecting {days} days of data for each company")

            for i, (symbol, name) in enumerate(companies, 1):
                print(f"\n📊 [{i}/{len(companies)}] Processing {symbol} ({name})...")

                # Get historical data
                hist_data = await self.get_historical_data(symbol, days)

                if hist_data is not None:
                    # Insert into database
                    await self.insert_historical_data(symbol, hist_data)
                else:
                    print(f"⚠️  Skipped {symbol} - no historical data available")
                    self.skipped_count += 1

                # Progress update
                if i % 5 == 0:
                    print(f"\n📊 Progress: {i}/{len(companies)} companies processed")
                    print(f"   Collected: {self.collected_count}")
                    print(f"   Skipped: {self.skipped_count}")
                    print(f"   Errors: {self.error_count}")

                # Small delay between companies
                await asyncio.sleep(0.5)

            # Final summary
            print(f"\n📊 Final Collection Summary:")
            print(f"   Total companies: {len(companies)}")
            print(f"   Collected: {self.collected_count}")
            print(f"   Skipped: {self.skipped_count}")
            print(f"   Errors: {self.error_count}")

        except Exception as e:
            print(f"❌ Error in full collection: {str(e)}")
            raise


async def main():
    """Main function."""
    collector = HistoricalDataCollector()

    print("🚀 Historical Data Collector")
    print("=" * 50)

    # Show current status
    await collector.show_historical_data_status()

    # Ask user what to do
    print(f"\n🎯 Options:")
    print(f"   1. Collect data for 5 companies (quick test)")
    print(f"   2. Collect data for all companies (full run)")
    print(f"   3. Show status only")

    # For now, let's do a quick test with 5 companies
    print(f"\n🔄 Collecting historical data for 5 companies (test run)...")
    await collector.collect_historical_data_batch(limit=5, days=365)

    # Show final status
    await collector.show_historical_data_status()

    print(f"\n✅ Collection completed!")
    print(f"💡 Run this script again to collect data for more companies")


if __name__ == "__main__":
    asyncio.run(main())
