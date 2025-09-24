#!/usr/bin/env python3
"""
Enhance Company Data with Yahoo Finance
Tech-028: API Implementation

This script enhances company data by fetching additional information from Yahoo Finance
for companies that might have incomplete data, while using our static data as the base.
"""

import asyncio
import sqlite3
import time
from datetime import datetime
from typing import Dict, Optional

import yfinance as yf


class YahooFinanceEnhancer:
    """Enhance company data with Yahoo Finance information."""

    def __init__(self):
        self.rate_limit = 1.0  # 1 request per second
        self.last_request = 0

    async def _rate_limit(self):
        """Apply rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request

        if time_since_last < self.rate_limit:
            sleep_time = self.rate_limit - time_since_last
            print(f"⏳ Rate limiting: sleeping for {sleep_time:.2f} seconds")
            await asyncio.sleep(sleep_time)

        self.last_request = time.time()

    async def get_yahoo_data(self, symbol: str) -> Optional[Dict]:
        """Get company data from Yahoo Finance."""
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
            }

            # Only return if we got meaningful data
            if yahoo_data["name"] and yahoo_data["sector"]:
                print(f"✅ Got Yahoo Finance data for {symbol}: {yahoo_data['name']}")
                return yahoo_data
            else:
                print(f"⚠️  Incomplete Yahoo Finance data for {symbol}")
                return None

        except Exception as e:
            print(f"❌ Error fetching Yahoo Finance data for {symbol}: {str(e)}")
            return None

    async def enhance_companies(self):
        """Enhance company data with Yahoo Finance information."""
        try:
            # Connect to database
            conn = sqlite3.connect("/app/db/investbyyourself_dev.db")
            cursor = conn.cursor()

            print("🔄 Enhancing company data with Yahoo Finance...")

            # Get all companies
            cursor.execute("SELECT symbol, name, sector FROM companies ORDER BY symbol")
            companies = cursor.fetchall()

            enhanced_count = 0
            skipped_count = 0

            for symbol, current_name, current_sector in companies:
                print(f"\n📊 Processing {symbol}...")

                # Get Yahoo Finance data
                yahoo_data = await self.get_yahoo_data(symbol)

                if yahoo_data:
                    # Update with Yahoo Finance data (only if it's better)
                    updates = []
                    values = []

                    if yahoo_data["name"] and yahoo_data["name"] != current_name:
                        updates.append("name = ?")
                        values.append(yahoo_data["name"])

                    if yahoo_data["sector"] and yahoo_data["sector"] != current_sector:
                        updates.append("sector = ?")
                        values.append(yahoo_data["sector"])

                    if yahoo_data["industry"]:
                        updates.append("industry = ?")
                        values.append(yahoo_data["industry"])

                    if yahoo_data["description"]:
                        updates.append("description = ?")
                        values.append(yahoo_data["description"])

                    if yahoo_data["employee_count"]:
                        updates.append("employee_count = ?")
                        values.append(yahoo_data["employee_count"])

                    if yahoo_data["market_cap"]:
                        updates.append("market_cap = ?")
                        values.append(yahoo_data["market_cap"])

                    if yahoo_data["website"]:
                        updates.append("website = ?")
                        values.append(yahoo_data["website"])

                    if yahoo_data["country"]:
                        updates.append("country = ?")
                        values.append(yahoo_data["country"])

                    if yahoo_data["currency"]:
                        updates.append("currency = ?")
                        values.append(yahoo_data["currency"])

                    if updates:
                        updates.append("updated_at = ?")
                        values.append(datetime.now())
                        values.append(symbol)

                        query = f"UPDATE companies SET {', '.join(updates)} WHERE symbol = ?"
                        cursor.execute(query, values)

                        enhanced_count += 1
                        print(f"✅ Enhanced {symbol} with Yahoo Finance data")
                    else:
                        print(f"ℹ️  No updates needed for {symbol}")
                        skipped_count += 1
                else:
                    print(f"⚠️  Skipped {symbol} - no Yahoo Finance data available")
                    skipped_count += 1

            # Commit changes
            conn.commit()

            # Show summary
            print(f"\n📊 Enhancement Summary:")
            print(f"   Total companies: {len(companies)}")
            print(f"   Enhanced: {enhanced_count}")
            print(f"   Skipped: {skipped_count}")

            # Show some examples
            cursor.execute(
                """
                SELECT symbol, name, sector, industry
                FROM companies
                WHERE updated_at > datetime('now', '-1 hour')
                ORDER BY updated_at DESC
                LIMIT 5
            """
            )
            recent_updates = cursor.fetchall()

            if recent_updates:
                print(f"\n🔄 Recent Updates:")
                for symbol, name, sector, industry in recent_updates:
                    print(f"   {symbol:<8} - {name:<30} | {sector:<20} | {industry}")

            conn.close()
            print(f"\n✅ Company data enhancement completed!")

        except Exception as e:
            print(f"❌ Error enhancing company data: {str(e)}")
            raise


async def main():
    """Main function."""
    enhancer = YahooFinanceEnhancer()
    await enhancer.enhance_companies()


if __name__ == "__main__":
    asyncio.run(main())
