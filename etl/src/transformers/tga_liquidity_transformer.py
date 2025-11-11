"""
TGA Liquidity Transformer
InvestByYourself Financial Platform

Transforms raw TGA data into comprehensive liquidity metrics.
Calculates multi-factor liquidity index combining TGA with Fed data.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class TGALiquidityTransformer:
    """TGA liquidity data transformer with advanced metrics."""

    def __init__(self):
        """Initialize TGA liquidity transformer."""
        self.name = "TGA Liquidity Transformer"

    def transform_tga_data(
        self, raw_data: List[Dict[str, Any]], calculate_metrics: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Transform TGA data and calculate liquidity metrics.

        Args:
            raw_data: Raw TGA records from collector
            calculate_metrics: If True, calculate derived metrics

        Returns:
            Transformed TGA records with liquidity metrics
        """
        try:
            logger.info(f"Transforming {len(raw_data)} TGA records")

            if not raw_data:
                logger.warning("No TGA data to transform")
                return []

            # Convert to DataFrame for efficient processing
            df = self._prepare_dataframe(raw_data)

            # Calculate liquidity metrics
            if calculate_metrics:
                df = self._calculate_liquidity_metrics(df)

            # Convert back to records
            transformed_records = df.to_dict("records")

            logger.info(
                f"Transformed {len(transformed_records)} TGA records with metrics"
            )
            return transformed_records

        except Exception as e:
            logger.error(f"Failed to transform TGA data: {e}")
            raise

    def _prepare_dataframe(self, raw_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Prepare and clean DataFrame from raw data."""
        df = pd.DataFrame(raw_data)

        # Parse dates
        df["record_date"] = pd.to_datetime(df["record_date"])

        # Ensure numeric columns
        numeric_cols = ["close_balance", "open_balance", "open_month_balance"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Sort by date
        df = df.sort_values("record_date").reset_index(drop=True)

        # Remove duplicates (keep latest)
        df = df.drop_duplicates(subset=["record_date"], keep="last")

        return df

    def _calculate_liquidity_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate comprehensive liquidity metrics from TGA data.

        Metrics calculated:
        1. Daily change (dTGA) - positive = liquidity drain, negative = liquidity add
        2. Weekly/Monthly moving averages - smooth out daily volatility
        3. Volatility (30-day rolling std) - measure TGA stability
        4. Liquidity contribution - cumulative impact on market liquidity
        5. Z-score - statistical measure of TGA level vs historical
        6. Rate of change - velocity of TGA changes
        """
        # 1. Daily change (billions)
        df["daily_change_billions"] = df["close_balance"].diff() / 1000

        # 2. Moving averages (smooth volatility)
        df["ma_7day"] = df["close_balance"].rolling(7, min_periods=1).mean()
        df["ma_30day"] = df["close_balance"].rolling(30, min_periods=1).mean()
        df["ma_90day"] = df["close_balance"].rolling(90, min_periods=1).mean()

        # 3. Volatility (30-day rolling standard deviation)
        df["volatility_30d"] = (
            df["close_balance"].rolling(30, min_periods=1).std() / 1000
        )  # billions

        # 4. Liquidity contribution (cumulative)
        # Negative dTGA = liquidity added to market (TGA decreases)
        # Positive dTGA = liquidity drained from market (TGA increases)
        df["liquidity_contribution"] = (-df["daily_change_billions"]).cumsum()

        # 5. Z-score (statistical measure vs rolling 90-day mean)
        rolling_mean = df["close_balance"].rolling(90, min_periods=30).mean()
        rolling_std = df["close_balance"].rolling(90, min_periods=30).std()
        df["zscore_90d"] = (df["close_balance"] - rolling_mean) / rolling_std

        # 6. Rate of change (7-day % change)
        df["pct_change_7d"] = df["close_balance"].pct_change(7) * 100

        # 7. Normalized liquidity index (relative to 90-day average)
        # Scale to 100 = average, >100 = above average, <100 = below average
        df["liquidity_index_norm"] = (
            (df["close_balance"] / rolling_mean) * 100
        ).fillna(100)

        # 8. Liquidity stress indicator (boolean)
        # Stress = TGA >2 std above mean OR volatility >90th percentile
        volatility_threshold = df["volatility_30d"].quantile(0.9)
        df["is_liquidity_stress"] = (
            (df["zscore_90d"].abs() > 2) | (df["volatility_30d"] > volatility_threshold)
        ).astype(bool)

        # Fill NaN values for early records
        df = df.fillna(
            {
                "daily_change_billions": 0,
                "liquidity_contribution": 0,
                "zscore_90d": 0,
                "pct_change_7d": 0,
                "is_liquidity_stress": False,
            }
        )

        # Add metadata
        df["calculated_at"] = datetime.now().isoformat()

        return df

    def calculate_comprehensive_liquidity_index(
        self,
        tga_data: pd.DataFrame,
        fed_balance_sheet: Optional[pd.DataFrame] = None,
        reverse_repo: Optional[pd.DataFrame] = None,
        bank_reserves: Optional[pd.DataFrame] = None,
    ) -> pd.DataFrame:
        """
        Calculate comprehensive multi-factor liquidity index.

        Formula:
        Liquidity = -ΔTGA + ΔFed_BS - ΔRRP + ΔReserves

        This provides a complete view of market liquidity by combining:
        - TGA: Treasury operations
        - Fed Balance Sheet: QE/QT
        - Reverse Repo: Money market liquidity
        - Bank Reserves: Banking system liquidity

        Args:
            tga_data: TGA DataFrame with daily_change
            fed_balance_sheet: FRED WALCL data (weekly)
            reverse_repo: FRED RRPONTSYD data (daily)
            bank_reserves: FRED TOTRESNS data (weekly)

        Returns:
            DataFrame with comprehensive liquidity index
        """
        try:
            logger.info("Calculating comprehensive liquidity index")

            # Start with TGA contribution
            df = tga_data[["record_date", "close_balance"]].copy()
            df = df.rename(columns={"close_balance": "tga_balance"})
            df["tga_change"] = df["tga_balance"].diff()

            # Merge Fed Balance Sheet (if provided)
            if fed_balance_sheet is not None:
                fed_bs = fed_balance_sheet.rename(
                    columns={"data_date": "record_date", "value": "fed_bs"}
                )
                df = df.merge(fed_bs[["record_date", "fed_bs"]], how="left", on="record_date")
                df["fed_bs"] = df["fed_bs"].fillna(method="ffill")  # Forward fill weekly data
                df["fed_bs_change"] = df["fed_bs"].diff()
            else:
                df["fed_bs_change"] = 0

            # Merge Reverse Repo (if provided)
            if reverse_repo is not None:
                rrp = reverse_repo.rename(
                    columns={"data_date": "record_date", "value": "rrp"}
                )
                df = df.merge(rrp[["record_date", "rrp"]], how="left", on="record_date")
                df["rrp"] = df["rrp"].fillna(method="ffill")
                df["rrp_change"] = df["rrp"].diff()
            else:
                df["rrp_change"] = 0

            # Merge Bank Reserves (if provided)
            if bank_reserves is not None:
                reserves = bank_reserves.rename(
                    columns={"data_date": "record_date", "value": "reserves"}
                )
                df = df.merge(
                    reserves[["record_date", "reserves"]], how="left", on="record_date"
                )
                df["reserves"] = df["reserves"].fillna(method="ffill")
                df["reserves_change"] = df["reserves"].diff()
            else:
                df["reserves_change"] = 0

            # Calculate comprehensive liquidity
            # Components: -TGA + Fed BS - RRP + Reserves
            df["liquidity_daily"] = (
                -df["tga_change"]
                + df["fed_bs_change"]
                - df["rrp_change"]
                + df["reserves_change"]
            )

            # Cumulative liquidity index
            df["liquidity_index"] = df["liquidity_daily"].cumsum()

            # Normalize to billions
            df["liquidity_index_billions"] = df["liquidity_index"] / 1000

            # Calculate 7-day and 30-day smoothed versions
            df["liquidity_index_7d_ma"] = (
                df["liquidity_index_billions"].rolling(7, min_periods=1).mean()
            )
            df["liquidity_index_30d_ma"] = (
                df["liquidity_index_billions"].rolling(30, min_periods=1).mean()
            )

            logger.info("Comprehensive liquidity index calculated successfully")
            return df

        except Exception as e:
            logger.error(f"Failed to calculate comprehensive liquidity index: {e}")
            raise

    def get_liquidity_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary statistics for liquidity data."""
        if df.empty:
            return {}

        latest = df.iloc[-1]
        prev_week = df.iloc[-7] if len(df) >= 7 else df.iloc[0]
        prev_month = df.iloc[-30] if len(df) >= 30 else df.iloc[0]

        summary = {
            "current_tga_balance": float(latest["close_balance"]) / 1000,  # billions
            "current_tga_balance_billions": float(latest["close_balance"]) / 1000,
            "daily_change_billions": float(latest.get("daily_change_billions", 0)),
            "week_change_billions": float(
                (latest["close_balance"] - prev_week["close_balance"]) / 1000
            ),
            "month_change_billions": float(
                (latest["close_balance"] - prev_month["close_balance"]) / 1000
            ),
            "ma_7day_billions": float(latest.get("ma_7day", 0)) / 1000,
            "ma_30day_billions": float(latest.get("ma_30day", 0)) / 1000,
            "volatility_30d_billions": float(latest.get("volatility_30d", 0)),
            "zscore_90d": float(latest.get("zscore_90d", 0)),
            "is_liquidity_stress": bool(latest.get("is_liquidity_stress", False)),
            "liquidity_index": float(latest.get("liquidity_contribution", 0)),
            "date": latest["record_date"].strftime("%Y-%m-%d"),
        }

        return summary
