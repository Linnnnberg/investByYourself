#!/usr/bin/env python3
"""
Company Profile Collector - Phase 1 Implementation
Using yfinance directly to collect basic company information

This script implements the first task from the company fundamentals TODO:
- Company name, symbol, currency, exchange
- Sector & industry classification
- Market capitalization
- Basic company overview
"""

import json
import time
from datetime import datetime

import pandas as pd
import yfinance as yf


def collect_company_profile(symbol):
    """
    Collect basic company profile information using yfinance

    Args:
        symbol (str): Stock ticker symbol (e.g., 'AAPL', 'MSFT')

    Returns:
        dict: Company profile data
    """
    print(f"🔍 Collecting company profile for {symbol}...")

    try:
        # Get ticker info
        ticker = yf.Ticker(symbol)
        info = ticker.info

        # Extract key information
        profile = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "data_source": "yfinance (Yahoo Finance)",
        }

        # Basic company information
        profile.update(
            {
                "company_name": info.get("longName", info.get("shortName", "N/A")),
                "legal_name": info.get("legalName", "N/A"),
                "exchange": info.get("exchange", "N/A"),
                "sector": info.get("sector", "N/A"),
                "industry": info.get("industry", "N/A"),
                "industry_group": info.get("industryGroup", "N/A"),
                "currency": info.get("currency", "N/A"),
                "ceo": (
                    info.get("companyOfficers", [{}])[0].get("name", "N/A")
                    if info.get("companyOfficers")
                    else "N/A"
                ),
                "employees": info.get("fullTimeEmployees", "N/A"),
                "headquarters": {
                    "address1": info.get("address1", "N/A"),
                    "address2": info.get("address2", "N/A"),
                    "city": info.get("city", "N/A"),
                    "state": info.get("state", "N/A"),
                    "country": info.get("country", "N/A"),
                    "postal_code": info.get("zip", "N/A"),
                },
                "business_description": info.get("longBusinessSummary", "N/A"),
                "short_description": info.get("shortBusinessSummary", "N/A"),
                "company_url": info.get("website", "N/A"),
                "market_cap": info.get("marketCap", "N/A"),
                "enterprise_value": info.get("enterpriseValue", "N/A"),
                "shares_outstanding": info.get("sharesOutstanding", "N/A"),
                "shares_float": info.get("floatShares", "N/A"),
                "dividend_yield": info.get("dividendYield", "N/A"),
                "beta": info.get("beta", "N/A"),
                "pe_ratio": info.get("trailingPE", "N/A"),
                "pb_ratio": info.get("priceToBook", "N/A"),
                "ps_ratio": info.get("priceToSalesTrailing12Months", "N/A"),
                "peg_ratio": info.get("pegRatio", "N/A"),
                "forward_pe": info.get("forwardPE", "N/A"),
                "enterprise_to_revenue": info.get("enterpriseToRevenue", "N/A"),
                "enterprise_to_ebitda": info.get("enterpriseToEbitda", "N/A"),
                "fifty_two_week_change": info.get("fiftyTwoWeekChange", "N/A"),
                "fifty_two_week_high": info.get("fiftyTwoWeekHigh", "N/A"),
                "fifty_two_week_low": info.get("fiftyTwoWeekLow", "N/A"),
                "fifty_day_average": info.get("fiftyDayAverage", "N/A"),
                "two_hundred_day_average": info.get("twoHundredDayAverage", "N/A"),
                "current_price": info.get("currentPrice", "N/A"),
                "open_price": info.get("open", "N/A"),
                "high_price": info.get("dayHigh", "N/A"),
                "low_price": info.get("dayLow", "N/A"),
                "volume": info.get("volume", "N/A"),
                "avg_volume": info.get("averageVolume", "N/A"),
                "market_cap_formatted": info.get("marketCap", "N/A"),
                "trailing_annual_dividend_rate": info.get(
                    "trailingAnnualDividendRate", "N/A"
                ),
                "trailing_annual_dividend_yield": info.get(
                    "trailingAnnualDividendYield", "N/A"
                ),
                "payout_ratio": info.get("payoutRatio", "N/A"),
                "return_on_equity": info.get("returnOnEquity", "N/A"),
                "return_on_assets": info.get("returnOnAssets", "N/A"),
                "return_on_capital": info.get("returnOnCapital", "N/A"),
                "gross_margins": info.get("grossMargins", "N/A"),
                "ebitda_margins": info.get("ebitdaMargins", "N/A"),
                "operating_margins": info.get("operatingMargins", "N/A"),
                "profit_margins": info.get("profitMargins", "N/A"),
                "revenue_growth": info.get("revenueGrowth", "N/A"),
                "earnings_growth": info.get("earningsGrowth", "N/A"),
                "revenue": info.get("totalRevenue", "N/A"),
                "gross_profit": info.get("grossProfits", "N/A"),
                "ebitda": info.get("ebitda", "N/A"),
                "operating_income": info.get("operatingIncome", "N/A"),
                "net_income": info.get("netIncomeToCommon", "N/A"),
                "total_cash": info.get("totalCash", "N/A"),
                "total_debt": info.get("totalDebt", "N/A"),
                "debt_to_equity": info.get("debtToEquity", "N/A"),
                "current_ratio": info.get("currentRatio", "N/A"),
                "quick_ratio": info.get("quickRatio", "N/A"),
                "working_capital": info.get("workingCapital", "N/A"),
            }
        )

        print(f"✅ Successfully collected profile for {symbol}")
        return profile

    except Exception as e:
        print(f"❌ Error collecting profile for {symbol}: {e}")
        return None


def collect_multiple_companies(symbols):
    """
    Collect profiles for multiple companies

    Args:
        symbols (list): List of stock ticker symbols

    Returns:
        dict: Dictionary of company profiles
    """
    print(f"🚀 Starting collection for {len(symbols)} companies...")
    print("=" * 60)

    profiles = {}

    for i, symbol in enumerate(symbols, 1):
        print(f"\n[{i}/{len(symbols)}] Processing {symbol}...")

        profile = collect_company_profile(symbol)
        if profile:
            profiles[symbol] = profile

        # Rate limiting to be respectful to the API
        if i < len(symbols):
            print("⏳ Waiting 1 second before next request...")
            time.sleep(1)

    return profiles


def save_profiles_to_json(profiles, filename=None):
    """
    Save company profiles to JSON file

    Args:
        profiles (dict): Company profiles data
        filename (str): Output filename (optional)
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"company_profiles_{timestamp}.json"

    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(profiles, f, indent=2, ensure_ascii=False)
        print(f"💾 Profiles saved to: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Error saving profiles: {e}")
        return None


def display_profile_summary(profiles):
    """
    Display a summary of collected profiles

    Args:
        profiles (dict): Company profiles data
    """
    print("\n" + "=" * 60)
    print("📊 COMPANY PROFILES SUMMARY")
    print("=" * 60)

    for symbol, profile in profiles.items():
        print(f"\n🏢 {symbol} - {profile.get('company_name', 'N/A')}")
        print(f"   Legal Name: {profile.get('legal_name', 'N/A')}")
        print(f"   Exchange: {profile.get('exchange', 'N/A')}")
        print(f"   Sector: {profile.get('sector', 'N/A')}")
        print(f"   Industry: {profile.get('industry', 'N/A')}")
        print(f"   Industry Group: {profile.get('industry_group', 'N/A')}")
        print(f"   Currency: {profile.get('currency', 'N/A')}")
        print(f"   CEO: {profile.get('ceo', 'N/A')}")
        print(f"   Employees: {profile.get('employees', 'N/A')}")
        print(f"   Market Cap: {profile.get('market_cap_formatted', 'N/A')}")
        print(f"   Current Price: {profile.get('current_price', 'N/A')}")
        print(f"   Volume: {profile.get('volume', 'N/A')}")
        print(f"   P/E Ratio: {profile.get('pe_ratio', 'N/A')}")
        print(f"   P/B Ratio: {profile.get('pb_ratio', 'N/A')}")
        print(f"   P/S Ratio: {profile.get('ps_ratio', 'N/A')}")
        print(f"   Dividend Yield: {profile.get('dividend_yield', 'N/A')}")
        print(f"   Beta: {profile.get('beta', 'N/A')}")
        print(f"   ROE: {profile.get('return_on_equity', 'N/A')}")
        print(f"   ROA: {profile.get('return_on_assets', 'N/A')}")

        # Show headquarters info
        hq = profile.get("headquarters", {})
        if hq and any(v != "N/A" for v in hq.values()):
            print(
                f"   HQ: {hq.get('address1', '')} {hq.get('city', '')}, {hq.get('state', '')} {hq.get('country', '')}"
            )


def main():
    """Main function to demonstrate company profile collection"""
    print("🎯 Company Profile Collector - Phase 1 Implementation")
    print("Using yfinance (Yahoo Finance) for basic company data")
    print("=" * 60)

    # Test with some well-known companies
    test_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

    print(f"📋 Test companies: {', '.join(test_symbols)}")
    print("=" * 60)

    # Collect profiles
    profiles = collect_multiple_companies(test_symbols)

    if profiles:
        # Display summary
        display_profile_summary(profiles)

        # Save to file
        filename = save_profiles_to_json(profiles)

        print(f"\n🎉 Collection complete! {len(profiles)} profiles collected.")
        if filename:
            print(f"📁 Data saved to: {filename}")
    else:
        print("❌ No profiles were collected successfully.")


if __name__ == "__main__":
    main()
