#!/usr/bin/env python3
"""
Update Companies One by One
Tech-028: API Implementation

This script updates company data one by one with proper delays to avoid rate limits.
It can be run multiple times to gradually improve data quality.
"""

import asyncio
import random
import sqlite3
import time
from datetime import datetime
from typing import Dict, List, Optional

import yfinance as yf


class CompanyUpdater:
    """Update company data one by one with rate limiting."""

    def __init__(self):
        self.rate_limit = 2.0  # 2 seconds between requests
        self.last_request = 0
        self.updated_count = 0
        self.skipped_count = 0
        self.error_count = 0

    async def _rate_limit(self):
        """Apply rate limiting with some randomness."""
        current_time = time.time()
        time_since_last = current_time - self.last_request

        # Add some randomness to avoid predictable patterns
        delay = self.rate_limit + random.uniform(0, 1)

        if time_since_last < delay:
            sleep_time = delay - time_since_last
            print(f"⏳ Rate limiting: sleeping for {sleep_time:.2f} seconds")
            await asyncio.sleep(sleep_time)

        self.last_request = time.time()

    async def get_yahoo_data(self, symbol: str) -> Optional[Dict]:
        """Get company data from Yahoo Finance with error handling."""
        try:
            await self._rate_limit()

            print(f"🔍 Fetching Yahoo Finance data for {symbol}...")
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Extract relevant information
            yahoo_data = {
                "name": info.get("longName", ""),
                "sector": info.get("sector", ""),
                "industry": info.get("industry", ""),
                "description": info.get("longBusinessSummary", ""),
                "employee_count": info.get("fullTimeEmployees", 0),
                "market_cap": info.get("marketCap", 0),
                "website": info.get("website", ""),
                "country": info.get("country", ""),
                "currency": info.get("currency", "EUR"),
                "exchange": info.get("exchange", ""),
                "ceo": info.get("companyOfficers", [{}])[0].get("name", "")
                if info.get("companyOfficers")
                else "",
                "headquarters": f"{info.get('city', '')}, {info.get('state', '')}, {info.get('country', '')}".strip(
                    ", "
                ),
                "founded_year": info.get("founded", 0),
            }

            # Check if we got meaningful data
            if yahoo_data["name"] and len(yahoo_data["name"]) > 3:
                print(f"✅ Got Yahoo Finance data for {symbol}: {yahoo_data['name']}")
                return yahoo_data
            else:
                print(f"⚠️  Incomplete Yahoo Finance data for {symbol}")
                return None

        except Exception as e:
            print(f"❌ Error fetching Yahoo Finance data for {symbol}: {str(e)}")
            self.error_count += 1
            return None

    async def update_single_company(self, symbol: str, current_data: Dict) -> bool:
        """Update a single company with Yahoo Finance data."""
        try:
            print(f"\n📊 Processing {symbol}...")
            print(f"   Current: {current_data['name']} | {current_data['sector']}")

            # Get Yahoo Finance data
            yahoo_data = await self.get_yahoo_data(symbol)

            if not yahoo_data:
                print(f"⚠️  Skipped {symbol} - no Yahoo Finance data available")
                self.skipped_count += 1
                return False

            # Check if we should update (only if Yahoo data is better)
            should_update = False
            updates = []
            values = []

            # Update name if Yahoo has a better one
            if (
                yahoo_data["name"]
                and yahoo_data["name"] != current_data["name"]
                and len(yahoo_data["name"]) > len(current_data["name"])
            ):
                updates.append("name = ?")
                values.append(yahoo_data["name"])
                should_update = True
                print(f"   📝 Name: {current_data['name']} → {yahoo_data['name']}")

            # Update sector if Yahoo has one and we don't
            if (
                yahoo_data["sector"]
                and yahoo_data["sector"] != current_data["sector"]
                and current_data["sector"] == "Unknown"
            ):
                updates.append("sector = ?")
                values.append(yahoo_data["sector"])
                should_update = True
                print(f"   📝 Sector: {current_data['sector']} → {yahoo_data['sector']}")

            # Update industry if Yahoo has one
            if yahoo_data["industry"]:
                updates.append("industry = ?")
                values.append(yahoo_data["industry"])
                should_update = True
                print(f"   📝 Industry: {yahoo_data['industry']}")

            # Update description if Yahoo has a better one
            if yahoo_data["description"] and len(yahoo_data["description"]) > len(
                current_data.get("description", "")
            ):
                updates.append("description = ?")
                values.append(yahoo_data["description"])
                should_update = True
                print(f"   📝 Description: Updated")

            # Update employee count if Yahoo has one
            if yahoo_data["employee_count"] and yahoo_data["employee_count"] > 0:
                updates.append("employee_count = ?")
                values.append(yahoo_data["employee_count"])
                should_update = True
                print(f"   📝 Employees: {yahoo_data['employee_count']:,}")

            # Update market cap if Yahoo has one
            if yahoo_data["market_cap"] and yahoo_data["market_cap"] > 0:
                updates.append("market_cap = ?")
                values.append(yahoo_data["market_cap"])
                should_update = True
                print(f"   📝 Market Cap: ${yahoo_data['market_cap']:,.0f}")

            # Update website if Yahoo has one
            if yahoo_data["website"]:
                updates.append("website = ?")
                values.append(yahoo_data["website"])
                should_update = True
                print(f"   📝 Website: {yahoo_data['website']}")

            # Update country if Yahoo has one
            if yahoo_data["country"]:
                updates.append("country = ?")
                values.append(yahoo_data["country"])
                should_update = True
                print(f"   📝 Country: {yahoo_data['country']}")

            # Update currency if Yahoo has one
            if yahoo_data["currency"]:
                updates.append("currency = ?")
                values.append(yahoo_data["currency"])
                should_update = True
                print(f"   📝 Currency: {yahoo_data['currency']}")

            if should_update:
                # Add timestamp
                updates.append("updated_at = ?")
                values.append(datetime.now())
                values.append(symbol)

                # Execute update
                query = f"UPDATE companies SET {', '.join(updates)} WHERE symbol = ?"

                conn = sqlite3.connect("/app/db/investbyyourself_dev.db")
                cursor = conn.cursor()
                cursor.execute(query, values)
                conn.commit()
                conn.close()

                self.updated_count += 1
                print(f"✅ Updated {symbol} with Yahoo Finance data")
                return True
            else:
                print(f"ℹ️  No updates needed for {symbol}")
                self.skipped_count += 1
                return False

        except Exception as e:
            print(f"❌ Error updating {symbol}: {str(e)}")
            self.error_count += 1
            return False

    async def update_companies_batch(self, limit: int = 5):
        """Update a batch of companies."""
        try:
            # Connect to database
            conn = sqlite3.connect("/app/db/investbyyourself_dev.db")
            cursor = conn.cursor()

            # Get companies that need updating (prioritize those with "Company" in name or "Unknown" sector)
            cursor.execute(
                """
                SELECT symbol, name, sector, description, employee_count, market_cap, website, country, currency
                FROM companies
                WHERE name LIKE 'Company %' OR sector = 'Unknown' OR description IS NULL OR description = ''
                ORDER BY
                    CASE WHEN name LIKE 'Company %' THEN 1 ELSE 2 END,
                    symbol
                LIMIT ?
            """,
                (limit,),
            )

            companies = cursor.fetchall()
            conn.close()

            if not companies:
                print("✅ No companies need updating!")
                return

            print(f"🔄 Updating {len(companies)} companies...")

            for company_data in companies:
                symbol = company_data[0]
                current_data = {
                    "name": company_data[1],
                    "sector": company_data[2],
                    "description": company_data[3] or "",
                    "employee_count": company_data[4] or 0,
                    "market_cap": company_data[5] or 0,
                    "website": company_data[6] or "",
                    "country": company_data[7] or "",
                    "currency": company_data[8] or "EUR",
                }

                await self.update_single_company(symbol, current_data)

                # Small delay between companies
                await asyncio.sleep(0.5)

            # Show summary
            print(f"\n📊 Batch Update Summary:")
            print(f"   Updated: {self.updated_count}")
            print(f"   Skipped: {self.skipped_count}")
            print(f"   Errors: {self.error_count}")

        except Exception as e:
            print(f"❌ Error in batch update: {str(e)}")
            raise

    async def show_status(self):
        """Show current database status."""
        try:
            conn = sqlite3.connect("/app/db/investbyyourself_dev.db")
            cursor = conn.cursor()

            # Get statistics
            cursor.execute("SELECT COUNT(*) FROM companies")
            total = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM companies WHERE name NOT LIKE 'Company %'"
            )
            proper_names = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM companies WHERE sector != 'Unknown'")
            proper_sectors = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM companies WHERE description IS NOT NULL AND description != ''"
            )
            with_descriptions = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM companies WHERE employee_count > 0")
            with_employees = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM companies WHERE market_cap > 0")
            with_market_cap = cursor.fetchone()[0]

            print(f"\n📊 Database Status:")
            print(f"   Total companies: {total}")
            print(
                f"   Proper names: {proper_names}/{total} ({proper_names/total*100:.1f}%)"
            )
            print(
                f"   Proper sectors: {proper_sectors}/{total} ({proper_sectors/total*100:.1f}%)"
            )
            print(
                f"   With descriptions: {with_descriptions}/{total} ({with_descriptions/total*100:.1f}%)"
            )
            print(
                f"   With employee count: {with_employees}/{total} ({with_employees/total*100:.1f}%)"
            )
            print(
                f"   With market cap: {with_market_cap}/{total} ({with_market_cap/total*100:.1f}%)"
            )

            # Show companies that still need work
            cursor.execute(
                """
                SELECT symbol, name, sector
                FROM companies
                WHERE name LIKE 'Company %' OR sector = 'Unknown'
                ORDER BY symbol
                LIMIT 10
            """
            )
            needs_work = cursor.fetchall()

            if needs_work:
                print(f"\n⚠️  Companies that need work:")
                for symbol, name, sector in needs_work:
                    print(f"   {symbol:<8} - {name:<30} | {sector}")

            conn.close()

        except Exception as e:
            print(f"❌ Error showing status: {str(e)}")


async def main():
    """Main function."""
    updater = CompanyUpdater()

    print("🚀 Company Data Updater")
    print("=" * 50)

    # Show current status
    await updater.show_status()

    # Update a small batch
    print(f"\n🔄 Updating companies (batch of 5)...")
    await updater.update_companies_batch(limit=5)

    # Show final status
    await updater.show_status()

    print(f"\n✅ Update completed!")
    print(f"💡 Run this script again to update more companies")


if __name__ == "__main__":
    asyncio.run(main())
