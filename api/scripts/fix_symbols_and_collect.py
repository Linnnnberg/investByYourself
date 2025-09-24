#!/usr/bin/env python3
"""
Fix incorrect symbols and collect historical data for previously skipped companies.
"""

import sqlite3
import time
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf


def fix_symbols_and_collect():
    """Fix incorrect symbols and collect historical data."""

    # Symbol corrections
    symbol_corrections = {
        "DAI.DE": "DTG.DE",  # Daimler Truck Holding AG
        "DPW.DE": "DHL.DE",  # Deutsche Post AG (DHL)
        "QGEN.DE": "QGEN",  # Qiagen N.V.
    }

    # Connect to database
    conn = sqlite3.connect("/app/db/investbyyourself_dev.db")
    cursor = conn.cursor()

    print("🔧 Fixing incorrect symbols and collecting historical data...")
    print("=" * 60)

    for old_symbol, new_symbol in symbol_corrections.items():
        print(f"\n📊 Processing {old_symbol} -> {new_symbol}")

        # Update the symbol in the database
        cursor.execute(
            """
            UPDATE companies
            SET symbol = ?
            WHERE symbol = ?
        """,
            (new_symbol, old_symbol),
        )

        if cursor.rowcount > 0:
            print(f"✅ Updated symbol: {old_symbol} -> {new_symbol}")

            # Get company info
            cursor.execute(
                "SELECT id, name FROM companies WHERE symbol = ?", (new_symbol,)
            )
            company = cursor.fetchone()
            if company:
                company_id, company_name = company
                print(
                    f"📈 Collecting historical data for {company_name} ({new_symbol})..."
                )

                try:
                    # Fetch historical data
                    ticker = yf.Ticker(new_symbol)
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=365)

                    hist = ticker.history(start=start_date, end=end_date)

                    if not hist.empty:
                        print(f"✅ Got {len(hist)} days of data for {new_symbol}")

                        # Insert historical data
                        records_inserted = 0
                        for date, row in hist.iterrows():
                            try:
                                cursor.execute(
                                    """
                                    INSERT INTO market_data
                                    (company_id, data_date, open_price, high_price, low_price,
                                     close_price, adjusted_close, volume, source, created_at)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """,
                                    (
                                        company_id,
                                        date.strftime("%Y-%m-%d"),
                                        float(row["Open"])
                                        if not pd.isna(row["Open"])
                                        else None,
                                        float(row["High"])
                                        if not pd.isna(row["High"])
                                        else None,
                                        float(row["Low"])
                                        if not pd.isna(row["Low"])
                                        else None,
                                        float(row["Close"])
                                        if not pd.isna(row["Close"])
                                        else None,
                                        float(row["Close"])
                                        if not pd.isna(row["Close"])
                                        else None,  # Using Close as Adjusted Close
                                        int(row["Volume"])
                                        if not pd.isna(row["Volume"])
                                        else None,
                                        "yahoo_finance",
                                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    ),
                                )
                                records_inserted += 1
                            except Exception as e:
                                print(f"⚠️  Error inserting record for {date}: {e}")
                                continue

                        print(f"✅ Inserted {records_inserted} records for {new_symbol}")

                    else:
                        print(f"⚠️  No historical data available for {new_symbol}")

                except Exception as e:
                    print(f"❌ Error fetching data for {new_symbol}: {e}")

        else:
            print(f"❌ Company with symbol {old_symbol} not found in database")

    # Commit changes
    conn.commit()
    conn.close()

    print("\n🎉 Symbol fixes and data collection completed!")


if __name__ == "__main__":
    fix_symbols_and_collect()
