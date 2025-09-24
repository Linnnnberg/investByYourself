#!/usr/bin/env python3
"""
Test Debt/Equity Ratio Fix - investByYourself
Quick test to verify financial strength metrics calculation
"""

import asyncio
import os
import sys
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.etl.transformers import FinancialDataTransformer


async def test_debt_equity_calculation():
    """Test the debt/equity ratio calculation."""
    print("🔍 Testing Debt/Equity Ratio Calculation")
    print("=" * 50)

    # Initialize transformer
    transformer = FinancialDataTransformer(
        name="Debt/Equity Test Transformer",
        description="Testing financial strength metrics calculation",
    )

    # Sample AAPL data with debt and equity
    aapl_data = {
        "symbol": "AAPL",
        "company_name": "Apple Inc.",
        "sector": "Technology",
        # Income Statement
        "totalRevenue": 394328.0,
        "costOfRevenue": 223546.0,
        "grossProfit": 170782.0,
        "operatingIncome": 114301.0,
        "netIncome": 96995.0,
        # Balance Sheet - Key fields for debt/equity
        "totalAssets": 352755.0,
        "currentAssets": 143713.0,
        "totalLiabilities": 287912.0,
        "totalEquity": 64843.0,
        "totalDebt": 95977.0,  # This should be extracted
        "currentLiabilities": 137632.0,
        # Market Data
        "marketCap": 3000000000000,
        "currentPrice": 175.0,
        "trailingPE": 18.0,
        "source": "yahoo_finance",
        "timestamp": datetime.now().isoformat(),
    }

    print(f"📊 Input Data:")
    print(f"   Total Debt: ${aapl_data['totalDebt']/1000:.1f}B")
    print(f"   Total Equity: ${aapl_data['totalEquity']/1000:.1f}B")
    print(
        f"   Expected Debt/Equity: {aapl_data['totalDebt']/aapl_data['totalEquity']:.2f}"
    )
    print()

    # Transform the data
    print("🔄 Transforming data...")
    result = await transformer.transform_data(aapl_data)

    if result.success:
        print("✅ Transformation successful!")

        # Show extracted balance sheet
        financial_statements = result.transformed_data["financial_statements"]
        if "balance_sheet" in financial_statements:
            balance_sheet = financial_statements["balance_sheet"]
            print(f"\n📋 Extracted Balance Sheet:")
            print(f"   Fields: {list(balance_sheet.keys())}")
            for key, value in balance_sheet.items():
                if value is not None:
                    if "debt" in key.lower():
                        print(f"   {key}: ${value/1000:.1f}B")
                    elif "equity" in key.lower():
                        print(f"   {key}: ${value/1000:.1f}B")
                    elif "assets" in key.lower():
                        print(f"   {key}: ${value/1000:.1f}B")
                    elif "liabilities" in key.lower():
                        print(f"   {key}: ${value/1000:.1f}B")

        # Show financial metrics
        financial_metrics = result.transformed_data["financial_metrics"]
        print(f"\n💰 Financial Metrics:")

        profitability = financial_metrics.get("profitability", {})
        if profitability.get("gross_margin"):
            print(f"   Gross Margin: {profitability['gross_margin']:.1f}%")
        if profitability.get("roe"):
            print(f"   ROE: {profitability['roe']:.1f}%")

        financial_strength = financial_metrics.get("financial_strength", {})
        if financial_strength.get("debt_to_equity"):
            print(f"   💪 Debt/Equity: {financial_strength['debt_to_equity']:.2f}")
        else:
            print(f"   ❌ Debt/Equity: NOT CALCULATED")

        if financial_strength.get("current_ratio"):
            print(f"   📈 Current Ratio: {financial_strength['current_ratio']:.2f}")
        else:
            print(f"   ❌ Current Ratio: NOT CALCULATED")

        # Debug: Check what's in the financial strength section
        print(f"\n🔍 Financial Strength Debug:")
        print(f"   Available fields: {list(financial_strength.keys())}")
        for key, value in financial_strength.items():
            print(f"   {key}: {value}")

    else:
        print(f"❌ Transformation failed: {result.errors}")

    return result


async def main():
    """Main test function."""
    try:
        result = await test_debt_equity_calculation()

        if result and result.success:
            print(f"\n🎯 Test Summary:")
            print(f"   Quality Score: {result.quality_metrics.overall_score:.1%}")
            print(f"   Quality Level: {result.quality_level.value.upper()}")

            # Verify the calculation
            financial_strength = result.transformed_data["financial_metrics"].get(
                "financial_strength", {}
            )
            if financial_strength.get("debt_to_equity"):
                print(f"   ✅ Debt/Equity ratio successfully calculated!")
            else:
                print(f"   ❌ Debt/Equity ratio calculation failed!")

    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
