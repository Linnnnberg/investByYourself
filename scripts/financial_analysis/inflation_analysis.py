#!/usr/bin/env python3
"""
Inflation Analysis Script for InvestByYourself

This script analyzes inflation data using FRED API and creates visualizations
for CPI, Core CPI, and PPI data over a 5-year period.
"""

from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from fredapi import Fred

# Set seaborn style for better looking charts
sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (12, 8)

print("Testing FRED API for CPI data (5-Year Analysis)...")
print("=" * 50)

# Initialize FRED API
# Note: You'll need to get a free API key from https://fred.stlouisfed.org/docs/api/api_key.html
try:
    # Try to load .env file if it exists
    try:
        from dotenv import load_dotenv

        load_dotenv()
        print("✅ .env file loaded successfully")
    except ImportError:
        print(
            "⚠️  python-dotenv not installed. Install with: pip install python-dotenv"
        )
    except FileNotFoundError:
        print("⚠️  .env file not found. Create one with your FRED_API_KEY")
    except UnicodeDecodeError:
        print("⚠️  .env file has encoding issues. Using environment variable directly.")

    # Try to get API key from environment variable
    import os

    api_key = os.getenv("FRED_API_KEY")

    if not api_key:
        print("⚠️  FRED API key not found in environment variables.")
        print("Please set your FRED API key as an environment variable 'FRED_API_KEY'")
        print(
            "Get a free API key from: https://fred.stlouisfed.org/docs/api/api_key.html"
        )
        print("\nFor testing purposes, we'll create sample data structure...")

        # Create sample data for demonstration
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1825)  # 5 years of data

        # Generate sample data (monthly)
        dates = pd.date_range(start=start_date, end=end_date, freq="ME")
        sample_cpi = [
            280 + i * 0.3 + np.random.normal(0, 0.1) for i in range(len(dates))
        ]
        sample_core_cpi = [
            280 + i * 0.25 + np.random.normal(0, 0.08) for i in range(len(dates))
        ]  # Core CPI typically more stable
        sample_ppi = [
            120 + i * 0.2 + np.random.normal(0, 0.15) for i in range(len(dates))
        ]  # PPI typically more volatile

        cpi_data = pd.DataFrame(
            {
                "date": dates,
                "CPIAUCSL": sample_cpi,  # Consumer Price Index for All Urban Consumers: All Items
                "CPILFESL": sample_core_cpi,  # Core CPI (All items less food and energy)
                "PPIACO": sample_ppi,  # Producer Price Index for All Commodities
            }
        )
        cpi_data.set_index("date", inplace=True)

        print("✅ Sample CPI, Core CPI, and PPI data created for demonstration")

    else:
        print("✅ FRED API key found, fetching real data...")
        fred = Fred(api_key=api_key)

        # Get data for 5 years
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1825)  # 5 years of data

        # Fetch multiple series
        cpi_data = fred.get_series("CPIAUCSL", start_date, end_date)  # CPI All Items
        core_cpi_data = fred.get_series(
            "CPILFESL", start_date, end_date
        )  # Core CPI (All items less food and energy)
        ppi_data = fred.get_series(
            "PPIACO", start_date, end_date
        )  # Producer Price Index

        # Combine into DataFrame
        combined_data = pd.DataFrame(
            {"CPIAUCSL": cpi_data, "CPILFESL": core_cpi_data, "PPIACO": ppi_data}
        )

        print(f"✅ Successfully fetched data:")
        print(f"   - CPI: {len(cpi_data)} data points")
        print(f"   - Core CPI: {len(core_cpi_data)} data points")
        print(f"   - PPI: {len(ppi_data)} data points")

        # Use the combined data for analysis
        cpi_data = combined_data

    # Calculate year-over-year changes
    cpi_data_yoy = cpi_data.pct_change(periods=12) * 100

    # Create visualization
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

    # Plot 1: Absolute values
    ax1.plot(cpi_data.index, cpi_data["CPIAUCSL"], label="CPI All Items", linewidth=2)
    ax1.plot(cpi_data.index, cpi_data["CPILFESL"], label="Core CPI", linewidth=2)
    ax1.plot(cpi_data.index, cpi_data["PPIACO"], label="PPI", linewidth=2)
    ax1.set_title("Inflation Indices (5-Year Trend)", fontsize=16, fontweight="bold")
    ax1.set_ylabel("Index Value", fontsize=12)
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)

    # Plot 2: Year-over-Year Changes
    ax2.plot(
        cpi_data_yoy.index, cpi_data_yoy["CPIAUCSL"], label="CPI YoY %", linewidth=2
    )
    ax2.plot(
        cpi_data_yoy.index,
        cpi_data_yoy["CPILFESL"],
        label="Core CPI YoY %",
        linewidth=2,
    )
    ax2.plot(cpi_data_yoy.index, cpi_data_yoy["PPIACO"], label="PPI YoY %", linewidth=2)
    ax2.axhline(y=0, color="black", linestyle="--", alpha=0.5)
    ax2.set_title(
        "Year-over-Year Inflation Changes (%)", fontsize=16, fontweight="bold"
    )
    ax2.set_ylabel("YoY Change (%)", fontsize=12)
    ax2.set_xlabel("Date", fontsize=12)
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

    # Print summary statistics
    print("\n" + "=" * 50)
    print("INFLATION ANALYSIS SUMMARY")
    print("=" * 50)

    # Calculate summary statistics
    if not api_key:
        # For sample data, calculate from the DataFrame
        cpi_yoy = cpi_data["CPIAUCSL"].pct_change(periods=12).dropna() * 100
        core_cpi_yoy = cpi_data["CPILFESL"].pct_change(periods=12).dropna() * 100
        ppi_yoy = cpi_data["PPIACO"].pct_change(periods=12).dropna() * 100
    else:
        # For real data, use the calculated YoY changes
        cpi_yoy = cpi_data_yoy["CPIAUCSL"].dropna()
        core_cpi_yoy = cpi_data_yoy["CPILFESL"].dropna()
        ppi_yoy = cpi_data_yoy["PPIACO"].dropna()

    print(f"CPI (All Items) - YoY Change:")
    print(f"   Current: {cpi_yoy.iloc[-1]:.2f}%")
    print(f"   Average: {cpi_yoy.mean():.2f}%")
    print(f"   Min: {cpi_yoy.min():.2f}%")
    print(f"   Max: {cpi_yoy.max():.2f}%")

    print(f"\nCore CPI (Excluding Food & Energy) - YoY Change:")
    print(f"   Current: {core_cpi_yoy.iloc[-1]:.2f}%")
    print(f"   Average: {core_cpi_yoy.mean():.2f}%")
    print(f"   Min: {core_cpi_yoy.min():.2f}%")
    print(f"   Max: {core_cpi_yoy.max():.2f}%")

    print(f"\nPPI (Producer Price Index) - YoY Change:")
    print(f"   Current: {ppi_yoy.iloc[-1]:.2f}%")
    print(f"   Average: {ppi_yoy.mean():.2f}%")
    print(f"   Min: {ppi_yoy.min():.2f}%")
    print(f"   Max: {ppi_yoy.max():.2f}%")

    # Inflation analysis insights
    print("\n" + "=" * 50)
    print("INFLATION INSIGHTS")
    print("=" * 50)

    current_cpi = cpi_yoy.iloc[-1]
    current_core = core_cpi_yoy.iloc[-1]
    current_ppi = ppi_yoy.iloc[-1]

    # Analyze current inflation levels
    if current_cpi > 3.0:
        print("🔥 HIGH INFLATION: Current CPI above 3% - inflationary pressure present")
    elif current_cpi < 1.0:
        print("❄️  LOW INFLATION: Current CPI below 1% - potential deflation risk")
    else:
        print("✅ MODERATE INFLATION: Current CPI between 1-3% - healthy range")

    # Analyze core vs headline inflation
    if abs(current_cpi - current_core) > 1.0:
        print("⚡ VOLATILE FOOD/ENERGY: Large gap between CPI and Core CPI")
        print(
            "   This suggests food and energy prices are driving inflation volatility"
        )
    else:
        print("📊 STABLE CORE: CPI and Core CPI moving together")
        print("   Inflation appears to be broad-based, not just food/energy")

    # Analyze PPI vs CPI relationship
    if current_ppi > current_cpi + 1.0:
        print("🏭 PRODUCER INFLATION: PPI higher than CPI")
        print("   Producer costs may be rising faster than consumer prices")
    elif current_ppi < current_cpi - 1.0:
        print("💰 CONSUMER INFLATION: CPI higher than PPI")
        print("   Consumer prices rising faster than producer costs")

    print("\n" + "=" * 50)
    print("RECOMMENDATIONS")
    print("=" * 50)

    if current_cpi > 4.0:
        print("🚨 HIGH INFLATION ALERT:")
        print("   - Consider inflation-protected investments")
        print("   - Review portfolio for inflation-sensitive assets")
        print("   - Monitor Federal Reserve policy changes")
    elif current_cpi < 1.5:
        print("📉 LOW INFLATION WATCH:")
        print("   - Monitor for deflation signals")
        print("   - Consider growth-oriented investments")
        print("   - Watch for Fed easing measures")

    print("\n✅ Inflation analysis complete!")

except Exception as e:
    print(f"❌ Error during inflation analysis: {e}")
    print("Please check your API key and internet connection.")
