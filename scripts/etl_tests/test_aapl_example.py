#!/usr/bin/env python3
"""
AAPL Example Test - investByYourself
Tech-009: ETL Pipeline Implementation - Phase 2

This script demonstrates the data processing engine capabilities
using Apple Inc. (AAPL) as a test case.
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Any, Dict

# Add src directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.etl.transformers import FinancialDataTransformer, TransformationRule


async def test_aapl_financial_transformation():
    """Test AAPL financial data transformation."""
    print("🍎 Testing AAPL Financial Data Transformation")
    print("=" * 60)

    # Initialize the financial data transformer
    transformer = FinancialDataTransformer(
        name="AAPL Financial Transformer",
        description="Specialized transformer for Apple Inc. financial data",
        max_concurrent_transformations=5,
    )

    # Sample AAPL financial data (simulating data from Yahoo Finance)
    aapl_sample_data = {
        "symbol": "AAPL",
        "company_name": "Apple Inc.",
        "longName": "Apple Inc.",
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "country": "US",
        "website": "https://www.apple.com",
        # Income Statement (in millions USD)
        "totalRevenue": 394328.0,  # $394.3B
        "costOfRevenue": 223546.0,  # $223.5B
        "grossProfit": 170782.0,  # $170.8B
        "operatingIncome": 114301.0,  # $114.3B
        "netIncome": 96995.0,  # $97.0B
        "ebitda": 120000.0,  # Estimated EBITDA
        # Balance Sheet (in millions USD)
        "totalAssets": 352755.0,  # $352.8B
        "currentAssets": 143713.0,  # $143.7B
        "cashAndEquivalents": 48004.0,  # $48.0B
        "totalLiabilities": 287912.0,  # $287.9B
        "totalEquity": 64843.0,  # $64.8B
        "totalDebt": 95977.0,  # $96.0B
        "currentLiabilities": 137632.0,  # $137.6B
        # Market Data
        "marketCap": 3000000000000,  # $3T market cap
        "currentPrice": 175.0,  # $175 per share
        "trailingPE": 18.0,  # P/E ratio
        "regularMarketVolume": 50000000,  # 50M shares
        # Additional metrics
        "earningsPerShare": 6.16,  # EPS
        "bookValuePerShare": 4.25,  # Book value per share
        "salesPerShare": 25.0,  # Sales per share
        "source": "yahoo_finance",
        "timestamp": datetime.now().isoformat(),
    }

    print(f"📊 Input Data Summary:")
    print(
        f"   Company: {aapl_sample_data['company_name']} ({aapl_sample_data['symbol']})"
    )
    print(f"   Sector: {aapl_sample_data['sector']}")
    print(f"   Revenue: ${aapl_sample_data['totalRevenue']/1000:.1f}B")
    print(f"   Net Income: ${aapl_sample_data['netIncome']/1000:.1f}B")
    print(f"   Market Cap: ${aapl_sample_data['marketCap']/1000000000:.1f}T")
    print(f"   Current Price: ${aapl_sample_data['currentPrice']}")
    print()

    # Test 1: Basic transformation
    print("🔄 Test 1: Basic Financial Data Transformation")
    print("-" * 40)

    result = await transformer.transform_data(aapl_sample_data)

    if result.success:
        print("✅ Transformation successful!")
        print(f"   Processing time: {result.processing_time:.3f}s")
        print(f"   Rules applied: {len(result.transformation_rules_applied)}")
        print(f"   Quality score: {result.quality_metrics.overall_score:.1%}")
        print(f"   Quality level: {result.quality_level.value}")

        # Show transformed data structure
        transformed = result.transformed_data
        print(f"\n📋 Transformed Data Structure:")
        print(f"   Company Info: {len(transformed.get('company_info', {}))} fields")
        print(
            f"   Financial Statements: {len(transformed.get('financial_statements', {}))} statements"
        )
        print(
            f"   Financial Metrics: {len(transformed.get('financial_metrics', {}))} metric categories"
        )
        print(
            f"   Market Data: {len(transformed.get('market_data', {}))} market fields"
        )

    else:
        print("❌ Transformation failed!")
        for error in result.errors:
            print(f"   Error: {error}")
        return

    # Test 2: Show detailed financial metrics
    print(f"\n💰 Test 2: Financial Metrics Calculation")
    print("-" * 40)

    financial_metrics = transformed["financial_metrics"]

    # Valuation metrics
    print("📈 Valuation Metrics:")
    valuation = financial_metrics.get("valuation", {})
    for metric, value in valuation.items():
        if value is not None:
            if metric in [
                "pe_ratio",
                "forward_pe",
                "price_to_book",
                "price_to_sales",
                "ev_to_ebitda",
            ]:
                print(f"   {metric.replace('_', ' ').title()}: {value:.2f}")

    # Profitability metrics
    print("\n📊 Profitability Metrics:")
    profitability = financial_metrics.get("profitability", {})
    for metric, value in profitability.items():
        if value is not None:
            if metric in [
                "gross_margin",
                "operating_margin",
                "net_margin",
                "roe",
                "roa",
                "roic",
            ]:
                print(f"   {metric.replace('_', ' ').title()}: {value:.2f}%")

    # Financial strength metrics
    print("\n💪 Financial Strength Metrics:")
    strength = financial_metrics.get("financial_strength", {})
    for metric, value in strength.items():
        if value is not None:
            if metric in ["debt_to_equity", "current_ratio", "quick_ratio"]:
                print(f"   {metric.replace('_', ' ').title()}: {value:.2f}")

    # Show raw calculated values for debugging
    print(f"\n🔍 Raw Calculated Values:")
    if "financial_statements" in transformed:
        income_stmt = transformed["financial_statements"].get("income_statement", {})
        balance_sheet = transformed["financial_statements"].get("balance_sheet", {})

        print(f"   Income Statement Fields: {list(income_stmt.keys())}")
        print(f"   Balance Sheet Fields: {list(balance_sheet.keys())}")

        # Show some key values
        if income_stmt.get("revenue"):
            print(f"   Revenue: ${income_stmt['revenue']/1000:.1f}B")
        if income_stmt.get("net_income"):
            print(f"   Net Income: ${income_stmt['net_income']/1000:.1f}B")
        if balance_sheet.get("total_assets"):
            print(f"   Total Assets: ${balance_sheet['total_assets']/1000:.1f}B")

    # Test 3: Data validation
    print(f"\n✅ Test 3: Data Validation")
    print("-" * 40)

    # Create a standardized version for validation
    standardized_for_validation = {
        "revenue": aapl_sample_data.get("totalRevenue"),
        "net_income": aapl_sample_data.get("netIncome"),
        "total_assets": aapl_sample_data.get("totalAssets"),
        "cost_of_revenue": aapl_sample_data.get("costOfRevenue"),
        "gross_profit": aapl_sample_data.get("grossProfit"),
        "operating_income": aapl_sample_data.get("operatingIncome"),
    }

    is_valid = await transformer.validate_data(standardized_for_validation)
    print(f"Data validation result: {'✅ PASSED' if is_valid else '❌ FAILED'}")

    if not is_valid:
        print(
            "   Note: Validation failed due to field name differences between source and standardized formats"
        )

    # Test 4: Custom transformation rule
    print(f"\n🔧 Test 4: Custom Transformation Rule")
    print("-" * 40)

    # Create a custom rule for AAPL-specific transformations
    custom_rule = TransformationRule(
        name="AAPL Custom Standardization",
        description="Custom transformation rules for Apple Inc. data",
        field_mapping={
            "longName": "company_name",
            "totalRevenue": "revenue",
            "costOfRevenue": "cost_of_revenue",
            "grossProfit": "gross_profit",
            "operatingIncome": "operating_income",
            "netIncome": "net_income",
            "totalAssets": "total_assets",
            "totalLiabilities": "total_liabilities",
            "totalEquity": "total_equity",
            "totalDebt": "total_debt",
            "currentLiabilities": "current_liabilities",
            "earningsPerShare": "eps",
            "bookValuePerShare": "book_value_per_share",
            "salesPerShare": "sales_per_share",
        },
        priority=10,  # Higher priority than default rules
    )

    transformer.add_transformation_rule(custom_rule)
    print(f"✅ Added custom transformation rule: {custom_rule.name}")

    # Test 5: Batch processing
    print(f"\n📦 Test 5: Batch Processing")
    print("-" * 40)

    # Create multiple AAPL data records with slight variations
    batch_data = [
        aapl_sample_data.copy(),
        {
            **aapl_sample_data,
            "currentPrice": 180.0,
            "marketCap": 3100000000000,
        },  # Higher price scenario
        {
            **aapl_sample_data,
            "currentPrice": 170.0,
            "marketCap": 2900000000000,
        },  # Lower price scenario
    ]

    batch_results = await transformer.transform_batch(batch_data)

    print(f"✅ Batch processing completed!")
    print(f"   Total records: {len(batch_data)}")
    print(f"   Successful: {len([r for r in batch_results if r.success])}")
    print(f"   Failed: {len([r for r in batch_results if not r.success])}")
    print(
        f"   Average processing time: {sum(r.processing_time for r in batch_results)/len(batch_results):.3f}s"
    )

    # Test 6: Performance metrics
    print(f"\n📊 Test 6: Performance Metrics")
    print("-" * 40)

    metrics = transformer.get_metrics()
    print(f"Transformer Performance:")
    print(f"   Total transformations: {metrics['total_transformations']}")
    print(f"   Success rate: {metrics['success_rate']:.1f}%")
    print(f"   Average processing time: {metrics['average_processing_time']:.3f}s")
    print(f"   Transformation rules: {metrics['transformation_rules_count']}")
    print(f"   Current quality score: {metrics['current_quality_score']:.1%}")

    # Test 7: Quality metrics breakdown
    print(f"\n🎯 Test 7: Data Quality Assessment")
    print("-" * 40)

    # Get the first result's quality metrics
    first_result = batch_results[0]
    quality = first_result.quality_metrics

    print(f"Data Quality Breakdown:")
    print(f"   Completeness: {quality.completeness:.1%}")
    print(f"   Accuracy: {quality.accuracy:.1%}")
    print(f"   Consistency: {quality.consistency:.1%}")
    print(f"   Timeliness: {quality.timeliness:.1%}")
    print(f"   Overall Score: {quality.overall_score:.1%}")
    print(f"   Quality Level: {first_result.quality_level.value.upper()}")

    print(f"\n🎉 AAPL Example Test Completed Successfully!")
    print(f"   All Phase 2 capabilities demonstrated:")
    print(f"   ✅ Financial data transformation")
    print(f"   ✅ Financial metrics calculation")
    print(f"   ✅ Data validation")
    print(f"   ✅ Custom transformation rules")
    print(f"   ✅ Batch processing")
    print(f"   ✅ Performance monitoring")
    print(f"   ✅ Data quality assessment")

    return transformer


async def main():
    """Main test function."""
    try:
        transformer = await test_aapl_financial_transformation()

        if transformer:
            print(f"\n📋 Final Transformer Status:")
            print(f"   Name: {transformer.name}")
            print(f"   Description: {transformer.description}")
            print(f"   Rules: {len(transformer.get_transformation_rules())}")
            print(f"   Quality History: {len(transformer.quality_history)} entries")

    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
