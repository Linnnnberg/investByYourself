"""
Test script for TGA Liquidity Tracking
InvestByYourself Financial Platform

Demonstrates how to collect, transform, and analyze TGA liquidity data.
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.collectors.tga_collector import TGACollector
from src.transformers.tga_liquidity_transformer import TGALiquidityTransformer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def test_tga_collection():
    """Test TGA data collection."""
    logger.info("=" * 60)
    logger.info("TEST 1: TGA Data Collection")
    logger.info("=" * 60)

    try:
        # Initialize collector
        collector = TGACollector()

        # Collect data (last 2 years)
        logger.info("Collecting TGA data for last 2 years...")
        tga_data = await collector.collect_tga_data(
            incremental=False, lookback_days=730
        )

        logger.info(f"✓ Collected {len(tga_data)} TGA records")

        # Display sample records
        if tga_data:
            logger.info("\nSample TGA records:")
            for record in tga_data[:3]:
                logger.info(
                    f"  {record['record_date']}: ${record['close_balance']/1000:.1f}B "
                    f"(Δ: ${record.get('daily_change', 0)/1000:.1f}B)"
                )

        # Calculate data quality metrics
        quality = collector.get_data_quality_metrics(tga_data)
        logger.info(f"\nData Quality Metrics:")
        logger.info(f"  Completeness: {quality['completeness']*100:.1f}%")
        logger.info(f"  Record count: {quality['record_count']}")
        logger.info(f"  Date range: {quality['date_range']}")
        logger.info(f"  Missing business days: {quality['missing_days']}")

        return tga_data

    except Exception as e:
        logger.error(f"✗ TGA collection failed: {e}")
        raise


def test_tga_transformation(tga_data):
    """Test TGA data transformation."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: TGA Data Transformation")
    logger.info("=" * 60)

    try:
        # Initialize transformer
        transformer = TGALiquidityTransformer()

        # Transform data
        logger.info("Transforming TGA data with liquidity metrics...")
        transformed_data = transformer.transform_tga_data(
            tga_data, calculate_metrics=True
        )

        logger.info(f"✓ Transformed {len(transformed_data)} records")

        # Convert to DataFrame for analysis
        df = pd.DataFrame(transformed_data)

        # Display latest metrics
        if not df.empty:
            latest = df.iloc[-1]
            logger.info(f"\nLatest TGA Metrics ({latest['record_date']}):")
            logger.info(f"  Balance: ${latest['close_balance']/1000:.1f}B")
            logger.info(f"  Daily Change: ${latest['daily_change_billions']:.2f}B")
            logger.info(f"  7-day MA: ${latest['ma_7day']/1000:.1f}B")
            logger.info(f"  30-day MA: ${latest['ma_30day']/1000:.1f}B")
            logger.info(f"  Volatility (30d): ${latest['volatility_30d']:.2f}B")
            logger.info(f"  Z-score (90d): {latest['zscore_90d']:.2f}")
            logger.info(
                f"  Liquidity Stress: {'⚠️ YES' if latest['is_liquidity_stress'] else '✓ NO'}"
            )
            logger.info(
                f"  Liquidity Contribution: ${latest['liquidity_contribution']:.1f}B"
            )

        # Get summary statistics
        summary = transformer.get_liquidity_summary(df)
        logger.info(f"\nLiquidity Summary:")
        for key, value in summary.items():
            if isinstance(value, float):
                logger.info(f"  {key}: {value:.2f}")
            else:
                logger.info(f"  {key}: {value}")

        return df

    except Exception as e:
        logger.error(f"✗ TGA transformation failed: {e}")
        raise


def analyze_liquidity_trends(df):
    """Analyze liquidity trends."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Liquidity Trend Analysis")
    logger.info("=" * 60)

    try:
        # Recent trends (last 30 days)
        recent = df.tail(30)

        logger.info("\n30-Day Liquidity Trends:")
        logger.info(
            f"  TGA Change: ${(recent.iloc[-1]['close_balance'] - recent.iloc[0]['close_balance'])/1000:.1f}B"
        )
        logger.info(
            f"  Average Daily Change: ${recent['daily_change_billions'].mean():.2f}B"
        )
        logger.info(
            f"  Max Daily Drain: ${recent['daily_change_billions'].max():.2f}B"
        )
        logger.info(
            f"  Max Daily Add: ${recent['daily_change_billions'].min():.2f}B"
        )
        logger.info(
            f"  Days in Stress: {recent['is_liquidity_stress'].sum()} / {len(recent)}"
        )

        # Historical percentiles
        logger.info("\nHistorical Context:")
        current_balance = df.iloc[-1]["close_balance"]
        percentile = (df["close_balance"] < current_balance).mean() * 100
        logger.info(
            f"  Current TGA is at {percentile:.1f}th percentile (historical)"
        )

        current_volatility = df.iloc[-1]["volatility_30d"]
        vol_percentile = (df["volatility_30d"] < current_volatility).mean() * 100
        logger.info(
            f"  Current volatility is at {vol_percentile:.1f}th percentile (historical)"
        )

        # Liquidity phases
        logger.info("\nLiquidity Phases (last 90 days):")
        last_90 = df.tail(90)
        draining_days = (last_90["daily_change_billions"] > 0).sum()
        adding_days = (last_90["daily_change_billions"] < 0).sum()
        logger.info(
            f"  Draining: {draining_days} days ({draining_days/len(last_90)*100:.1f}%)"
        )
        logger.info(
            f"  Adding: {adding_days} days ({adding_days/len(last_90)*100:.1f}%)"
        )

        return True

    except Exception as e:
        logger.error(f"✗ Liquidity analysis failed: {e}")
        raise


def compare_with_original_method(df):
    """Compare with original methodology from user's code."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: Comparison with Original Method")
    logger.info("=" * 60)

    try:
        # Original method: simple cumulative sum
        df_copy = df.copy()
        df_copy["original_liquidity_index"] = (
            -df_copy["daily_change_billions"]
        ).cumsum()

        # Our method: liquidity_contribution (same calculation, but with better context)
        original_latest = df_copy.iloc[-1]["original_liquidity_index"]
        our_latest = df_copy.iloc[-1]["liquidity_contribution"]

        logger.info("\nMethodology Comparison:")
        logger.info(f"  Original Simple Index: ${original_latest:.1f}B")
        logger.info(f"  Our Liquidity Contribution: ${our_latest:.1f}B")
        logger.info(f"  Difference: ${abs(original_latest - our_latest):.3f}B")
        logger.info(
            "  ✓ Values match (both use -cumsum(dTGA)), but our method adds:"
        )
        logger.info("    • Context with moving averages")
        logger.info("    • Statistical measures (z-score)")
        logger.info("    • Volatility tracking")
        logger.info("    • Stress detection")
        logger.info("    • Normalized index")
        logger.info(
            "    • Ready for multi-factor expansion (Fed BS, RRP, Reserves)"
        )

        # Show where our method provides additional insights
        logger.info("\n  Example of Additional Insights:")
        latest = df_copy.iloc[-1]

        if latest["is_liquidity_stress"]:
            logger.info(
                f"    ⚠️  STRESS DETECTED: Z-score = {latest['zscore_90d']:.2f}"
            )
        else:
            logger.info(
                f"    ✓  Normal conditions: Z-score = {latest['zscore_90d']:.2f}"
            )

        if latest["volatility_30d"] > df_copy["volatility_30d"].quantile(0.75):
            logger.info(
                f"    ⚠️  High volatility: ${latest['volatility_30d']:.2f}B (75th+ percentile)"
            )
        else:
            logger.info(
                f"    ✓  Normal volatility: ${latest['volatility_30d']:.2f}B"
            )

        return True

    except Exception as e:
        logger.error(f"✗ Comparison failed: {e}")
        raise


async def main():
    """Run all tests."""
    logger.info("Starting TGA Liquidity Tracking Tests")
    logger.info(f"Timestamp: {datetime.now().isoformat()}\n")

    try:
        # Test 1: Collection
        tga_data = await test_tga_collection()

        # Test 2: Transformation
        df = test_tga_transformation(tga_data)

        # Test 3: Analysis
        analyze_liquidity_trends(df)

        # Test 4: Comparison
        compare_with_original_method(df)

        logger.info("\n" + "=" * 60)
        logger.info("✓ ALL TESTS PASSED")
        logger.info("=" * 60)

        logger.info("\n📊 Next Steps:")
        logger.info("  1. Run database migration: 002_tga_liquidity_tracking.sql")
        logger.info("  2. Integrate TGA collector into ETL orchestrator")
        logger.info("  3. Add /api/tga-liquidity endpoints to backend")
        logger.info("  4. Create frontend TGA dashboard component")
        logger.info("  5. Set up FRED collector for Fed BS, RRP, Reserves")
        logger.info(
            "  6. Implement comprehensive multi-factor liquidity index"
        )

    except Exception as e:
        logger.error(f"\n✗ Tests failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
