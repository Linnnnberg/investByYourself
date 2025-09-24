#!/usr/bin/env python3
"""
Enhance Existing Company Data
Tech-028: API Implementation

This script enhances existing company data with Yahoo Finance information,
focusing on improving data quality for companies that already have basic info.
"""

import asyncio
import random
import sqlite3
import time
from datetime import datetime
from typing import Dict, List, Optional

import yfinance as yf


class DataEnhancer:
    """Enhance existing company data with Yahoo Finance."""

    def __init__(self):
        self.rate_limit = 3.0  # 3 seconds between requests
        self.last_request = 0
        self.enhanced_count = 0
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

    async def get_yahoo_data(self, symbol: str) -> Optional[Dict]:
        """Get enhanced company data from Yahoo Finance."""
        try:
            await self._rate_limit()

            print(f"🔍 Fetching Yahoo Finance data for {symbol}...")
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Extract comprehensive information
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
                "enterprise_value": info.get("enterpriseValue", 0),
                "book_value": info.get("bookValue", 0),
                "price_to_book": info.get("priceToBook", 0),
                "dividend_yield": info.get("dividendYield", 0),
                "beta": info.get("beta", 0),
                "52_week_high": info.get("fiftyTwoWeekHigh", 0),
                "52_week_low": info.get("fiftyTwoWeekLow", 0),
                "avg_volume": info.get("averageVolume", 0),
                "market_cap_formatted": info.get("marketCap", 0),
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

    async def enhance_single_company(self, symbol: str, current_data: Dict) -> bool:
        """Enhance a single company with Yahoo Finance data."""
        try:
            print(f"\n📊 Enhancing {symbol}...")
            print(f"   Current: {current_data['name']} | {current_data['sector']}")

            # Get Yahoo Finance data
            yahoo_data = await self.get_yahoo_data(symbol)

            if not yahoo_data:
                print(f"⚠️  Skipped {symbol} - no Yahoo Finance data available")
                self.skipped_count += 1
                return False

            # Check for improvements
            improvements = []
            updates = []
            values = []

            # Enhance name if Yahoo has a more complete one
            if (
                yahoo_data["name"]
                and yahoo_data["name"] != current_data["name"]
                and len(yahoo_data["name"]) > len(current_data["name"])
            ):
                updates.append("name = ?")
                values.append(yahoo_data["name"])
                improvements.append(
                    f"Name: {current_data['name']} → {yahoo_data['name']}"
                )

            # Enhance sector if Yahoo has a more specific one
            if (
                yahoo_data["sector"]
                and yahoo_data["sector"] != current_data["sector"]
                and len(yahoo_data["sector"]) > len(current_data["sector"])
            ):
                updates.append("sector = ?")
                values.append(yahoo_data["sector"])
                improvements.append(
                    f"Sector: {current_data['sector']} → {yahoo_data['sector']}"
                )

            # Add industry if we don't have it
            if yahoo_data["industry"] and not current_data.get("industry"):
                updates.append("industry = ?")
                values.append(yahoo_data["industry"])
                improvements.append(f"Industry: {yahoo_data['industry']}")

            # Enhance description if Yahoo has a better one
            if yahoo_data["description"] and len(yahoo_data["description"]) > len(
                current_data.get("description", "")
            ):
                updates.append("description = ?")
                values.append(yahoo_data["description"])
                improvements.append("Description: Enhanced")

            # Update employee count if Yahoo has more recent data
            if (
                yahoo_data["employee_count"]
                and yahoo_data["employee_count"] > 0
                and yahoo_data["employee_count"]
                != current_data.get("employee_count", 0)
            ):
                updates.append("employee_count = ?")
                values.append(yahoo_data["employee_count"])
                improvements.append(f"Employees: {yahoo_data['employee_count']:,}")

            # Update market cap if Yahoo has more recent data
            if (
                yahoo_data["market_cap"]
                and yahoo_data["market_cap"] > 0
                and yahoo_data["market_cap"] != current_data.get("market_cap", 0)
            ):
                updates.append("market_cap = ?")
                values.append(yahoo_data["market_cap"])
                improvements.append(f"Market Cap: ${yahoo_data['market_cap']:,.0f}")

            # Add website if we don't have it
            if yahoo_data["website"] and not current_data.get("website"):
                updates.append("website = ?")
                values.append(yahoo_data["website"])
                improvements.append(f"Website: {yahoo_data['website']}")

            # Add CEO if we don't have it
            if yahoo_data["ceo"] and not current_data.get("ceo"):
                updates.append("ceo = ?")
                values.append(yahoo_data["ceo"])
                improvements.append(f"CEO: {yahoo_data['ceo']}")

            # Add headquarters if we don't have it
            if yahoo_data["headquarters"] and not current_data.get("headquarters"):
                updates.append("headquarters = ?")
                values.append(yahoo_data["headquarters"])
                improvements.append(f"Headquarters: {yahoo_data['headquarters']}")

            # Add founded year if we don't have it
            if yahoo_data["founded_year"] and not current_data.get("founded_year"):
                updates.append("founded_year = ?")
                values.append(yahoo_data["founded_year"])
                improvements.append(f"Founded: {yahoo_data['founded_year']}")

            if improvements:
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

                self.enhanced_count += 1
                print(f"✅ Enhanced {symbol}:")
                for improvement in improvements:
                    print(f"   📝 {improvement}")
                return True
            else:
                print(f"ℹ️  No enhancements needed for {symbol}")
                self.skipped_count += 1
                return False

        except Exception as e:
            print(f"❌ Error enhancing {symbol}: {str(e)}")
            self.error_count += 1
            return False

    async def enhance_companies_batch(self, limit: int = 3):
        """Enhance a batch of companies."""
        try:
            # Connect to database
            conn = sqlite3.connect("/app/db/investbyyourself_dev.db")
            cursor = conn.cursor()

            # Get companies that could benefit from enhancement
            cursor.execute(
                """
                SELECT symbol, name, sector, industry, description, employee_count, market_cap,
                       website, ceo, headquarters, founded_year
                FROM companies
                WHERE name NOT LIKE 'Company %'
                ORDER BY
                    CASE WHEN website IS NULL OR website = '' THEN 1 ELSE 2 END,
                    CASE WHEN ceo IS NULL OR ceo = '' THEN 1 ELSE 2 END,
                    symbol
                LIMIT ?
            """,
                (limit,),
            )

            companies = cursor.fetchall()
            conn.close()

            if not companies:
                print("✅ No companies need enhancement!")
                return

            print(f"🔄 Enhancing {len(companies)} companies...")

            for company_data in companies:
                symbol = company_data[0]
                current_data = {
                    "name": company_data[1],
                    "sector": company_data[2],
                    "industry": company_data[3] or "",
                    "description": company_data[4] or "",
                    "employee_count": company_data[5] or 0,
                    "market_cap": company_data[6] or 0,
                    "website": company_data[7] or "",
                    "ceo": company_data[8] or "",
                    "headquarters": company_data[9] or "",
                    "founded_year": company_data[10] or 0,
                }

                await self.enhance_single_company(symbol, current_data)

                # Small delay between companies
                await asyncio.sleep(1)

            # Show summary
            print(f"\n📊 Enhancement Summary:")
            print(f"   Enhanced: {self.enhanced_count}")
            print(f"   Skipped: {self.skipped_count}")
            print(f"   Errors: {self.error_count}")

        except Exception as e:
            print(f"❌ Error in batch enhancement: {str(e)}")
            raise

    async def show_enhancement_status(self):
        """Show current enhancement status."""
        try:
            conn = sqlite3.connect("/app/db/investbyyourself_dev.db")
            cursor = conn.cursor()

            # Get statistics
            cursor.execute("SELECT COUNT(*) FROM companies")
            total = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM companies WHERE website IS NOT NULL AND website != ''"
            )
            with_website = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM companies WHERE ceo IS NOT NULL AND ceo != ''"
            )
            with_ceo = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM companies WHERE headquarters IS NOT NULL AND headquarters != ''"
            )
            with_headquarters = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM companies WHERE founded_year > 0")
            with_founded_year = cursor.fetchone()[0]

            print(f"\n📊 Enhancement Status:")
            print(f"   Total companies: {total}")
            print(
                f"   With website: {with_website}/{total} ({with_website/total*100:.1f}%)"
            )
            print(f"   With CEO: {with_ceo}/{total} ({with_ceo/total*100:.1f}%)")
            print(
                f"   With headquarters: {with_headquarters}/{total} ({with_headquarters/total*100:.1f}%)"
            )
            print(
                f"   With founded year: {with_founded_year}/{total} ({with_founded_year/total*100:.1f}%)"
            )

            # Show companies that could benefit from enhancement
            cursor.execute(
                """
                SELECT symbol, name, sector,
                       CASE WHEN website IS NULL OR website = '' THEN 'No website' ELSE 'Has website' END as website_status,
                       CASE WHEN ceo IS NULL OR ceo = '' THEN 'No CEO' ELSE 'Has CEO' END as ceo_status
                FROM companies
                WHERE name NOT LIKE 'Company %'
                ORDER BY
                    CASE WHEN website IS NULL OR website = '' THEN 1 ELSE 2 END,
                    CASE WHEN ceo IS NULL OR ceo = '' THEN 1 ELSE 2 END,
                    symbol
                LIMIT 10
            """
            )
            candidates = cursor.fetchall()

            if candidates:
                print(f"\n🎯 Companies that could benefit from enhancement:")
                for symbol, name, sector, website_status, ceo_status in candidates:
                    print(
                        f"   {symbol:<8} - {name:<25} | {website_status:<12} | {ceo_status}"
                    )

            conn.close()

        except Exception as e:
            print(f"❌ Error showing enhancement status: {str(e)}")


async def main():
    """Main function."""
    enhancer = DataEnhancer()

    print("🚀 Company Data Enhancer")
    print("=" * 50)

    # Show current status
    await enhancer.show_enhancement_status()

    # Enhance a small batch
    print(f"\n🔄 Enhancing companies (batch of 3)...")
    await enhancer.enhance_companies_batch(limit=3)

    # Show final status
    await enhancer.show_enhancement_status()

    print(f"\n✅ Enhancement completed!")
    print(f"💡 Run this script again to enhance more companies")


if __name__ == "__main__":
    asyncio.run(main())
