#!/usr/bin/env python3
"""
Collect Historical Data One by One
Tech-028: API Implementation

This script collects historical price data for companies one by one,
tracks progress, and can be resumed if interrupted.
"""

import asyncio
import json
import os
import random
import sqlite3
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import pandas as pd
import yfinance as yf


class HistoricalDataCollector:
    """Collect historical price data one by one with progress tracking."""

    def __init__(self):
        self.rate_limit = 3.0  # 3 seconds between requests
        self.last_request = 0
        self.progress_file = "/app/db/historical_data_progress.json"
        self.collected_count = 0
        self.skipped_count = 0
        self.error_count = 0

    async def _rate_limit(self):
        """Apply rate limiting with randomness."""
        current_time = time.time()
        time_since_last = current_time - self.last_request

        # Add randomness to avoid predictable patterns
        delay = self.rate_limit + random.uniform(0, 2)

        if time_since_last < delay:
            sleep_time = delay - time_since_last
            print(f"⏳ Rate limiting: sleeping for {sleep_time:.2f} seconds")
            await asyncio.sleep(sleep_time)

        self.last_request = time.time()

    def load_progress(self) -> Dict:
        """Load progress from file."""
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, "r") as f:
                    return json.load(f)
            return {"completed": [], "failed": [], "skipped": []}
        except Exception as e:
            print(f"⚠️  Error loading progress: {e}")
            return {"completed": [], "failed": [], "skipped": []}

    def save_progress(self, progress: Dict):
        """Save progress to file."""
        try:
            with open(self.progress_file, "w") as f:
                json.dump(progress, f, indent=2)
        except Exception as e:
            print(f"⚠️  Error saving progress: {e}")

    def get_companies_to_process(self) -> List[Tuple[str, str]]:
        """Get companies that still need historical data."""
        try:
            conn = sqlite3.connect("/app/db/investbyyourself_dev.db")
            cursor = conn.cursor()

            # Get all companies
            cursor.execute("SELECT symbol, name FROM companies ORDER BY symbol")
            all_companies = cursor.fetchall()

            # Load progress
            progress = self.load_progress()
            completed = set(progress.get("completed", []))
            failed = set(progress.get("failed", []))
            skipped = set(progress.get("skipped", []))

            # Filter out completed companies
            companies_to_process = []
            for symbol, name in all_companies:
                if (
                    symbol not in completed
                    and symbol not in failed
                    and symbol not in skipped
                ):
                    companies_to_process.append((symbol, name))

            conn.close()
            return companies_to_process

        except Exception as e:
            print(f"❌ Error getting companies to process: {e}")
            return []

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
            return None

    async def insert_historical_data(
        self, symbol: str, hist_data: pd.DataFrame
    ) -> bool:
        """Insert historical data into the database."""
        try:
            conn = sqlite3.connect("/app/db/investbyyourself_dev.db")
            cursor = conn.cursor()

            # The market_data table already exists with a different schema
            # We'll use the existing schema

            # Get company ID for the symbol
            cursor.execute("SELECT id FROM companies WHERE symbol = ?", (symbol,))
            company_result = cursor.fetchone()
            if not company_result:
                print(f"❌ Company {symbol} not found in companies table")
                conn.close()
                return False

            company_id = company_result[0]

            # Check if we already have data for this company
            cursor.execute(
                "SELECT COUNT(*) FROM market_data WHERE company_id = ?", (company_id,)
            )
            existing_count = cursor.fetchone()[0]

            if existing_count > 0:
                print(
                    f"⚠️  Historical data already exists for {symbol} ({existing_count} records)"
                )
                conn.close()
                return False

            # Insert historical data using the correct schema
            inserted_count = 0
            for _, row in hist_data.iterrows():
                try:
                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO market_data
                        (company_id, data_date, open_price, high_price, low_price, close_price,
                         adjusted_close, volume, source, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            company_id,
                            row["Date"],
                            float(row["Open"]) if pd.notna(row["Open"]) else None,
                            float(row["High"]) if pd.notna(row["High"]) else None,
                            float(row["Low"]) if pd.notna(row["Low"]) else None,
                            float(row["Close"]) if pd.notna(row["Close"]) else None,
                            float(row["Close"]) if pd.notna(row["Close"]) else None,
                            int(row["Volume"]) if pd.notna(row["Volume"]) else None,
                            "yahoo_finance",
                            datetime.now(),
                        ),
                    )
                    inserted_count += 1
                except Exception as e:
                    print(f"⚠️  Error inserting row for {symbol}: {str(e)}")
                    continue

            conn.commit()
            conn.close()

            print(f"✅ Inserted {inserted_count} records for {symbol}")
            return True

        except Exception as e:
            print(f"❌ Error inserting historical data for {symbol}: {str(e)}")
            return False

    async def process_single_company(
        self, symbol: str, name: str, days: int = 365
    ) -> str:
        """Process a single company and return status."""
        try:
            print(f"\n📊 Processing {symbol} ({name})...")

            # Get historical data
            hist_data = await self.get_historical_data(symbol, days)

            if hist_data is None:
                print(f"⚠️  Skipped {symbol} - no historical data available")
                return "skipped"

            # Insert into database
            success = await self.insert_historical_data(symbol, hist_data)

            if success:
                print(f"✅ Successfully processed {symbol}")
                return "completed"
            else:
                print(f"⚠️  Skipped {symbol} - data already exists")
                return "skipped"

        except Exception as e:
            print(f"❌ Error processing {symbol}: {str(e)}")
            return "failed"

    async def collect_historical_data_batch(self, limit: int = 5, days: int = 365):
        """Collect historical data for a batch of companies."""
        try:
            # Get companies to process
            companies_to_process = self.get_companies_to_process()

            if not companies_to_process:
                print("✅ All companies already have historical data!")
                return

            # Limit the batch
            batch = companies_to_process[:limit]

            print(f"🔄 Processing batch of {len(batch)} companies...")
            print(f"📅 Collecting {days} days of data for each company")

            # Load current progress
            progress = self.load_progress()

            for symbol, name in batch:
                print(
                    f"\n📊 [{len(progress.get('completed', [])) + len(progress.get('failed', [])) + len(progress.get('skipped', [])) + 1}/{len(companies_to_process)}] Processing {symbol}..."
                )

                # Process the company
                status = await self.process_single_company(symbol, name, days)

                # Update progress
                if status == "completed":
                    progress["completed"].append(symbol)
                    self.collected_count += 1
                elif status == "skipped":
                    progress["skipped"].append(symbol)
                    self.skipped_count += 1
                else:  # failed
                    progress["failed"].append(symbol)
                    self.error_count += 1

                # Save progress
                self.save_progress(progress)

                # Small delay between companies
                await asyncio.sleep(1)

            # Show summary
            print(f"\n📊 Batch Summary:")
            print(f"   Completed: {self.collected_count}")
            print(f"   Skipped: {self.skipped_count}")
            print(f"   Failed: {self.error_count}")

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

            cursor.execute("SELECT COUNT(DISTINCT company_id) FROM market_data")
            companies_with_data = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM market_data")
            total_records = cursor.fetchone()[0]

            # Load progress
            progress = self.load_progress()
            completed = len(progress.get("completed", []))
            failed = len(progress.get("failed", []))
            skipped = len(progress.get("skipped", []))

            print(f"\n📊 Historical Data Status:")
            print(f"   Total companies: {total_companies}")
            print(
                f"   Companies with historical data: {companies_with_data}/{total_companies} ({companies_with_data/total_companies*100:.1f}%)"
            )
            print(f"   Total price records: {total_records:,}")
            print(f"   Progress tracking:")
            print(f"     Completed: {completed}")
            print(f"     Failed: {failed}")
            print(f"     Skipped: {skipped}")
            print(f"     Remaining: {total_companies - completed - failed - skipped}")

            # Show companies with most data
            cursor.execute(
                """
                SELECT c.symbol, COUNT(*) as record_count,
                       MIN(m.data_date) as earliest_date, MAX(m.data_date) as latest_date
                FROM market_data m
                JOIN companies c ON m.company_id = c.id
                GROUP BY c.symbol
                ORDER BY record_count DESC
                LIMIT 5
            """
            )
            top_companies = cursor.fetchall()

            if top_companies:
                print(f"\n📈 Companies with most data:")
                for symbol, count, earliest, latest in top_companies:
                    print(
                        f"   {symbol:<8} - {count:>4} records ({earliest} to {latest})"
                    )

            # Show failed companies
            if progress.get("failed"):
                print(f"\n❌ Failed companies:")
                for symbol in progress["failed"]:
                    print(f"   {symbol}")

            conn.close()

        except Exception as e:
            print(f"❌ Error showing status: {str(e)}")

    async def reset_progress(self):
        """Reset progress tracking."""
        try:
            if os.path.exists(self.progress_file):
                os.remove(self.progress_file)
            print("✅ Progress tracking reset")
        except Exception as e:
            print(f"❌ Error resetting progress: {e}")


async def main():
    """Main function."""
    collector = HistoricalDataCollector()

    print("🚀 Historical Data Collector (One by One)")
    print("=" * 50)

    # Show current status
    await collector.show_historical_data_status()

    # Get companies to process
    companies_to_process = collector.get_companies_to_process()

    if not companies_to_process:
        print("✅ All companies already have historical data!")
        return

    print(f"\n🎯 Companies to process: {len(companies_to_process)}")
    print(f"   Next companies: {[symbol for symbol, _ in companies_to_process[:5]]}")

    # Process a small batch
    print(f"\n🔄 Processing batch of 3 companies...")
    await collector.collect_historical_data_batch(limit=3, days=365)

    # Show final status
    await collector.show_historical_data_status()

    print(f"\n✅ Batch completed!")
    print(f"💡 Run this script again to process more companies")
    print(f"💡 Use 'reset_progress' to start over")


if __name__ == "__main__":
    asyncio.run(main())
