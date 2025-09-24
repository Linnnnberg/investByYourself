#!/usr/bin/env python3
"""
Insert Japanese Company Data
Tech-028: API Implementation

This script inserts Japanese company data from CSV files into the database.
"""

import asyncio
import glob
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import pandas as pd


class JapaneseDataInserter:
    """Insert Japanese company data from CSV files."""

    def __init__(self):
        self.data_dir = "scripts/financial_analysis"
        self.inserted_count = 0
        self.skipped_count = 0
        self.error_count = 0

        # Japanese company mapping (code to name)
        self.japanese_companies = {
            "2801": "Kikkoman Corporation",
            "2914": "Japan Tobacco Inc.",
            "3401": "Nippon Steel Corporation",
            "3407": "Nippon Steel & Sumitomo Metal Corporation",
            "4063": "Shin-Etsu Chemical Co., Ltd.",
            "4502": "Takeda Pharmaceutical Company Limited",
            "4503": "Astellas Pharma Inc.",
            "4519": "Chugai Pharmaceutical Co., Ltd.",
            "4568": "Daiichi Sankyo Company, Limited",
            "4901": "Fujifilm Holdings Corporation",
            "6098": "Recruit Holdings Co., Ltd.",
            "6501": "Hitachi, Ltd.",
            "6503": "Mitsubishi Electric Corporation",
            "6752": "Panasonic Corporation",
            "6861": "Keyence Corporation",
            "6954": "Fanuc Corporation",
            "6981": "Murata Manufacturing Co., Ltd.",
            "7203": "Toyota Motor Corporation",
            "7267": "Honda Motor Co., Ltd.",
            "7741": "Hoya Corporation",
            "7974": "Nintendo Co., Ltd.",
            "8001": "ITOCHU Corporation",
            "8002": "Marubeni Corporation",
            "8031": "Mitsui & Co., Ltd.",
            "8035": "Tokyo Electron Limited",
            "8058": "Mitsubishi Corporation",
            "8306": "Mitsubishi UFJ Financial Group, Inc.",
            "9432": "NTT DOCOMO, Inc.",
            "9984": "SoftBank Group Corp.",
        }

    def get_csv_files(self) -> List[str]:
        """Get all CSV files with Japanese company data."""
        pattern = os.path.join(self.data_dir, "price_timeseries_*.csv")
        return glob.glob(pattern)

    def get_company_info(self, file_path: str) -> Optional[Tuple[str, str, str]]:
        """Extract company information from file path."""
        filename = os.path.basename(file_path)
        # Extract company code from filename (e.g., price_timeseries_6501.csv -> 6501)
        if "price_timeseries_" in filename:
            code = filename.replace("price_timeseries_", "").replace(".csv", "")
            name = self.japanese_companies.get(code, f"Japanese Company {code}")
            symbol = f"{code}.T"  # Japanese stocks typically end with .T
            return code, name, symbol
        return None

    def read_csv_data(self, file_path: str) -> Optional[pd.DataFrame]:
        """Read and clean CSV data."""
        try:
            df = pd.read_csv(file_path)

            # Clean the data
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date")

            # Remove rows with missing essential data
            df = df.dropna(subset=["close"])

            print(f"✅ Read {len(df)} records from {os.path.basename(file_path)}")
            return df

        except Exception as e:
            print(f"❌ Error reading {file_path}: {str(e)}")
            return None

    async def insert_company_profile(self, code: str, name: str, symbol: str) -> bool:
        """Insert company profile into companies table."""
        try:
            conn = sqlite3.connect("/app/db/investbyyourself_dev.db")
            cursor = conn.cursor()

            # Check if company already exists
            cursor.execute("SELECT id FROM companies WHERE symbol = ?", (symbol,))
            if cursor.fetchone():
                print(f"⚠️  Company {symbol} already exists")
                conn.close()
                return True

            # Insert company profile
            cursor.execute(
                """
                INSERT INTO companies
                (id, symbol, name, sector, industry, country, currency, exchange,
                 description, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    f"japan_{code}",
                    symbol,
                    name,
                    "Technology",  # Default sector
                    "Electronics",  # Default industry
                    "Japan",
                    "JPY",
                    "TSE",
                    f"Japanese company {name}",
                    datetime.now(),
                    datetime.now(),
                ),
            )

            conn.commit()
            conn.close()

            print(f"✅ Inserted company profile for {symbol} ({name})")
            return True

        except Exception as e:
            print(f"❌ Error inserting company profile for {symbol}: {str(e)}")
            return False

    async def insert_historical_data(self, symbol: str, df: pd.DataFrame) -> bool:
        """Insert historical data into market_data table."""
        try:
            conn = sqlite3.connect("/app/db/investbyyourself_dev.db")
            cursor = conn.cursor()

            # Get company ID
            cursor.execute("SELECT id FROM companies WHERE symbol = ?", (symbol,))
            company_result = cursor.fetchone()
            if not company_result:
                print(f"❌ Company {symbol} not found in companies table")
                conn.close()
                return False

            company_id = company_result[0]

            # Check if data already exists
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

            # Insert historical data
            inserted_count = 0
            for _, row in df.iterrows():
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
                            row["date"].strftime("%Y-%m-%d"),
                            float(row["open"]) if pd.notna(row["open"]) else None,
                            float(row["high"]) if pd.notna(row["high"]) else None,
                            float(row["low"]) if pd.notna(row["low"]) else None,
                            float(row["close"]) if pd.notna(row["close"]) else None,
                            float(row["close"]) if pd.notna(row["close"]) else None,
                            int(row["volume"]) if pd.notna(row["volume"]) else None,
                            "csv_import",
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

    async def process_single_company(self, file_path: str) -> bool:
        """Process a single company's data."""
        try:
            # Get company info
            company_info = self.get_company_info(file_path)
            if not company_info:
                print(f"⚠️  Could not extract company info from {file_path}")
                return False

            code, name, symbol = company_info
            print(f"\n📊 Processing {symbol} ({name})...")

            # Read CSV data
            df = self.read_csv_data(file_path)
            if df is None or df.empty:
                print(f"⚠️  No data to process for {symbol}")
                return False

            # Insert company profile
            profile_success = await self.insert_company_profile(code, name, symbol)
            if not profile_success:
                return False

            # Insert historical data
            data_success = await self.insert_historical_data(symbol, df)
            if not data_success:
                return False

            print(f"✅ Successfully processed {symbol}")
            return True

        except Exception as e:
            print(f"❌ Error processing {file_path}: {str(e)}")
            return False

    async def process_all_companies(self, limit: Optional[int] = None):
        """Process all Japanese companies."""
        try:
            csv_files = self.get_csv_files()

            if not csv_files:
                print("❌ No CSV files found")
                return

            # Filter out already processed companies
            conn = sqlite3.connect("/app/db/investbyyourself_dev.db")
            cursor = conn.cursor()
            cursor.execute("SELECT symbol FROM companies WHERE country = 'Japan'")
            existing_symbols = set(row[0] for row in cursor.fetchall())
            conn.close()

            # Filter CSV files to only process new companies
            new_csv_files = []
            for file_path in csv_files:
                company_info = self.get_company_info(file_path)
                if company_info:
                    _, _, symbol = company_info
                    if symbol not in existing_symbols:
                        new_csv_files.append(file_path)

            if not new_csv_files:
                print("✅ All Japanese companies already processed!")
                return

            if limit:
                new_csv_files = new_csv_files[:limit]

            print(f"🔄 Processing {len(new_csv_files)} new Japanese companies...")

            for i, file_path in enumerate(new_csv_files, 1):
                print(
                    f"\n📊 [{i}/{len(new_csv_files)}] Processing {os.path.basename(file_path)}..."
                )

                success = await self.process_single_company(file_path)

                if success:
                    self.inserted_count += 1
                else:
                    self.skipped_count += 1

                # Small delay between companies
                await asyncio.sleep(0.1)

            # Show summary
            print(f"\n📊 Processing Summary:")
            print(f"   Processed: {len(new_csv_files)}")
            print(f"   Inserted: {self.inserted_count}")
            print(f"   Skipped: {self.skipped_count}")
            print(f"   Errors: {self.error_count}")

        except Exception as e:
            print(f"❌ Error in batch processing: {str(e)}")
            raise

    async def show_status(self):
        """Show current database status."""
        try:
            conn = sqlite3.connect("/app/db/investbyyourself_dev.db")
            cursor = conn.cursor()

            # Get statistics
            cursor.execute("SELECT COUNT(*) FROM companies WHERE country = 'Japan'")
            japanese_companies = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(DISTINCT c.symbol)
                FROM companies c
                JOIN market_data m ON c.id = m.company_id
                WHERE c.country = 'Japan'
            """
            )
            japanese_with_data = cursor.fetchone()[0]

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM market_data m
                JOIN companies c ON m.company_id = c.id
                WHERE c.country = 'Japan'
            """
            )
            japanese_records = cursor.fetchone()[0]

            print(f"\n📊 Japanese Data Status:")
            print(f"   Japanese companies: {japanese_companies}")
            print(f"   Companies with data: {japanese_with_data}")
            print(f"   Total records: {japanese_records:,}")

            # Show some examples
            cursor.execute(
                """
                SELECT c.symbol, c.name, COUNT(m.id) as record_count
                FROM companies c
                LEFT JOIN market_data m ON c.id = m.company_id
                WHERE c.country = 'Japan'
                GROUP BY c.symbol, c.name
                ORDER BY record_count DESC
                LIMIT 5
            """
            )
            examples = cursor.fetchall()

            if examples:
                print(f"\n📈 Top Japanese companies:")
                for symbol, name, count in examples:
                    print(f"   {symbol:<8} - {name:<30} | {count:>4} records")

            conn.close()

        except Exception as e:
            print(f"❌ Error showing status: {str(e)}")


async def main():
    """Main function."""
    inserter = JapaneseDataInserter()

    print("🚀 Japanese Data Inserter")
    print("=" * 50)

    # Show current status
    await inserter.show_status()

    # Get CSV files
    csv_files = inserter.get_csv_files()
    print(f"\n📁 Found {len(csv_files)} CSV files")

    if not csv_files:
        print("❌ No CSV files found")
        return

    # Process a small batch first
    print(f"\n🔄 Processing first 5 companies...")
    await inserter.process_all_companies(limit=5)

    # Show final status
    await inserter.show_status()

    print(f"\n✅ Processing completed!")
    print(f"💡 Run this script again to process more companies")


if __name__ == "__main__":
    asyncio.run(main())
