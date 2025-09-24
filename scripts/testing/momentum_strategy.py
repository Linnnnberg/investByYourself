#!/usr/bin/env python3
"""
Momentum Strategy Implementation
===============================
Implements a cross-sectional momentum strategy using the generalized framework.

Strategy: 12-1 momentum (12-month return excluding most recent month)
- Each month, pick the asset with higher trailing 12-month return
- Allocate 100% to the stronger momentum asset
- Rebalance monthly on last business day
- Compare performance to SPY buy & hold

Assets: NVDA (stock) and QQQ (NASDAQ-100 ETF proxy)
Benchmark: SPY (S&P 500)
Period: 2020-01-01 to 2024-12-31

Usage:
    python momentum_strategy.py
"""

import os
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from strategy_framework import BaseStrategy


class MomentumStrategy(BaseStrategy):
    """Cross-sectional momentum strategy implementation."""

    def __init__(
        self,
        tickers: list = None,
        benchmark: str = "SPY",
        start_date: str = "2020-01-01",
        end_date: str = "2024-12-31",
        initial_investment: float = 10000,
        momentum_period: int = 12,
        skip_period: int = 1,
        rebalance_frequency: str = "M",
    ):
        """
        Initialize momentum strategy.

        Args:
            tickers: List of ticker symbols (default: ['NVDA', 'QQQ'])
            benchmark: Benchmark ticker for comparison
            start_date: Start date for backtest
            end_date: End date for backtest
            initial_investment: Initial portfolio value
            momentum_period: Period for momentum calculation (months)
            skip_period: Periods to skip for momentum calculation
            rebalance_frequency: Rebalancing frequency ('M' for monthly)
        """
        if tickers is None:
            tickers = ["NVDA", "QQQ"]

        super().__init__(
            tickers,
            benchmark,
            start_date,
            end_date,
            initial_investment,
            momentum_period=momentum_period,
            skip_period=skip_period,
            rebalance_frequency=rebalance_frequency,
        )

    def get_strategy_name(self) -> str:
        """Return strategy name."""
        return "Cross-Sectional Momentum"

    def get_strategy_description(self) -> str:
        """Return strategy description."""
        return (
            f"12-1 momentum strategy: monthly rebalancing to strongest momentum asset"
        )

    def calculate_momentum(
        self, prices: pd.DataFrame, period: int = 12, skip: int = 1
    ) -> pd.DataFrame:
        """
        Calculate momentum for each asset.

        Args:
            prices: DataFrame with price data
            period: Momentum calculation period in months
            skip: Number of months to skip (to avoid look-ahead bias)

        Returns:
            DataFrame with momentum values over time
        """
        # Convert to monthly data for momentum calculation
        monthly_prices = prices.resample("M").last()

        # Calculate momentum: (P_t / P_{t-period-skip}) - 1
        momentum = pd.DataFrame(index=monthly_prices.index, columns=self.tickers)

        for i in range(period + skip, len(monthly_prices)):
            current_date = monthly_prices.index[i]
            lookback_date = monthly_prices.index[i - period - skip]

            for ticker in self.tickers:
                if pd.notna(monthly_prices.loc[lookback_date, ticker]) and pd.notna(
                    monthly_prices.loc[current_date, ticker]
                ):
                    momentum.loc[current_date, ticker] = (
                        monthly_prices.loc[current_date, ticker]
                        / monthly_prices.loc[lookback_date, ticker]
                    ) - 1
                else:
                    momentum.loc[current_date, ticker] = np.nan

        return momentum

    def calculate_weights(self, prices: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """
        Calculate portfolio weights based on momentum strategy.

        Args:
            prices: DataFrame with price data
            **kwargs: Strategy parameters

        Returns:
            DataFrame with weights over time
        """
        momentum_period = kwargs.get("momentum_period", 12)
        skip_period = kwargs.get("skip_period", 1)
        rebalance_freq = kwargs.get("rebalance_frequency", "M")

        print(f"📊 Calculating {momentum_period}-{skip_period} momentum...")

        # Calculate momentum
        momentum = self.calculate_momentum(prices, momentum_period, skip_period)

        # Initialize weights DataFrame
        weights = pd.DataFrame(index=prices.index, columns=self.tickers, dtype=float)
        weights.fillna(0, inplace=True)

        # Set initial weights (equal weight)
        initial_weight = 1.0 / len(self.tickers)
        weights.iloc[0] = [initial_weight] * len(self.tickers)

        # Calculate weights for each month
        monthly_dates = prices.resample("M").last().index

        for i, month_date in enumerate(monthly_dates):
            if (
                month_date in momentum.index
                and not momentum.loc[month_date].isna().all()
            ):
                # Find the asset with highest momentum
                month_momentum = momentum.loc[month_date]
                best_asset = month_momentum.idxmax()

                # Set weights: 100% to best momentum asset
                for ticker in self.tickers:
                    if ticker == best_asset:
                        weights.loc[month_date:, ticker] = 1.0
                    else:
                        weights.loc[month_date:, ticker] = 0.0

        # Forward fill weights to daily frequency
        weights = weights.fillna(method="ffill")

        # Ensure weights sum to 1
        weights = weights.div(weights.sum(axis=1), axis=0)

        print(f"✅ Momentum weights calculated for {len(monthly_dates)} months")
        return weights

    def create_visualizations(
        self, strategy_equity, benchmark_equity, weights, output_dir
    ):
        """Create momentum-specific visualizations."""
        super().create_visualizations(
            strategy_equity, benchmark_equity, weights, output_dir
        )

        # Additional momentum-specific chart: Momentum values over time
        if hasattr(self, "prices"):
            momentum = self.calculate_momentum(
                self.prices,
                self.kwargs.get("momentum_period", 12),
                self.kwargs.get("skip_period", 1),
            )

            plt.figure(figsize=(12, 6))
            for ticker in self.tickers:
                plt.plot(
                    momentum.index,
                    momentum[ticker] * 100,
                    label=f"{ticker} Momentum",
                    linewidth=2,
                )
            plt.title(
                f"{self.get_strategy_name()}\n12-1 Momentum Values Over Time",
                fontsize=14,
                fontweight="bold",
            )
            plt.xlabel("Date")
            plt.ylabel("Momentum (%)")
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.axhline(y=0, color="black", linestyle="-", alpha=0.3)
            plt.tight_layout()
            plt.savefig(
                os.path.join(output_dir, "momentum_values.png"),
                dpi=300,
                bbox_inches="tight",
            )
            plt.close()

            print(f"📊 Created momentum-specific visualization: momentum_values.png")


def main():
    """Main execution function."""
    print("🚀 Momentum Strategy Backtest")
    print("=" * 50)

    # Create and run momentum strategy
    strategy = MomentumStrategy(
        tickers=["NVDA", "QQQ"],
        benchmark="SPY",
        start_date="2020-01-01",
        end_date="2024-12-31",
        initial_investment=10000,
        momentum_period=12,
        skip_period=1,
        rebalance_frequency="M",
    )

    # Run backtest
    results = strategy.run_backtest()

    if results:
        print(f"\n🎉 Momentum strategy backtest completed!")
        print(f"📁 Results saved to: {results['output_dir']}")
    else:
        print("❌ Backtest failed")


if __name__ == "__main__":
    main()
