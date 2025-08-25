#!/usr/bin/env python3
"""
Generalized Investment Strategy Framework
========================================
This framework provides a standardized structure for implementing and backtesting
any investment strategy. It handles the common components while allowing
customization of the core strategy logic.

Framework Components:
1. Data Management (download, validation, preprocessing)
2. Strategy Logic (weight calculation, rebalancing rules)
3. Performance Calculation (returns, metrics, attribution)
4. Visualization (standardized charts and analysis)
5. Results Export (CSV, reports, charts)

Usage:
    Inherit from BaseStrategy and implement:
    - calculate_weights(): Core strategy logic
    - get_strategy_name(): Strategy identifier
    - get_strategy_description(): Strategy description
"""

import os
import warnings
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore")


class BaseStrategy(ABC):
    """Base class for all investment strategies."""

    def __init__(
        self,
        tickers: List[str],
        benchmark: str,
        start_date: str,
        end_date: str,
        initial_investment: float = 10000,
        **kwargs,
    ):
        """
        Initialize strategy parameters.

        Args:
            tickers: List of ticker symbols for strategy assets
            benchmark: Benchmark ticker for comparison
            start_date: Start date for backtest (YYYY-MM-DD)
            end_date: End date for backtest (YYYY-MM-DD)
            initial_investment: Initial portfolio value
            **kwargs: Additional strategy-specific parameters
        """
        self.tickers = tickers
        self.benchmark = benchmark
        self.start_date = start_date
        self.end_date = end_date
        self.initial_investment = initial_investment
        self.kwargs = kwargs

        # Data storage
        self.prices = None
        self.returns = None
        self.weights = None
        self.portfolio_values = None
        self.benchmark_values = None

        # Results storage
        self.strategy_metrics = None
        self.benchmark_metrics = None

    @abstractmethod
    def get_strategy_name(self) -> str:
        """Return strategy name for identification."""
        pass

    @abstractmethod
    def get_strategy_description(self) -> str:
        """Return strategy description for documentation."""
        pass

    @abstractmethod
    def calculate_weights(self, prices: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """
        Calculate portfolio weights based on strategy logic.

        Args:
            prices: DataFrame with price data (tickers as columns)
            **kwargs: Additional parameters for weight calculation

        Returns:
            DataFrame with weights over time (tickers as columns)
        """
        pass

    def download_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Download historical data for all tickers and benchmark."""
        print(
            f"📥 Downloading data for {', '.join(self.tickers)} and {self.benchmark}..."
        )
        print(f"📅 Period: {self.start_date} to {self.end_date}")

        # Download all tickers including benchmark
        all_tickers = self.tickers + [self.benchmark]
        data = yf.download(
            all_tickers,
            start=self.start_date,
            end=self.end_date,
            progress=False,
            auto_adjust=False,
        )

        if data.empty:
            raise ValueError(
                "No data downloaded. Please check ticker symbols and dates."
            )

        print(f"📊 Data shape: {data.shape}")

        # Extract adjusted close prices
        if len(all_tickers) == 1:
            adj_close = data["Adj Close"]
            volume = data["Volume"]
        else:
            if isinstance(data.columns, pd.MultiIndex):
                adj_close = data["Adj Close"]
                volume = data["Volume"]
            else:
                adj_close = data["Adj Close"]
                volume = data["Volume"]

        print(f"✅ Downloaded {len(adj_close)} trading days of data")
        print(f"📈 Assets: {adj_close.columns.tolist()}")

        return adj_close, volume

    def calculate_returns(self, prices: pd.DataFrame) -> pd.DataFrame:
        """Calculate daily returns from prices."""
        return prices.pct_change().fillna(0)

    def calculate_portfolio_performance(
        self, prices: pd.DataFrame, weights: pd.DataFrame
    ) -> Tuple[pd.Series, pd.Series]:
        """Calculate portfolio and benchmark performance."""
        # Calculate returns
        returns = self.calculate_returns(prices)

        # Strategy returns (excluding benchmark)
        strategy_returns = (
            returns[self.tickers].multiply(weights[self.tickers]).sum(axis=1)
        )

        # Benchmark returns
        benchmark_returns = returns[self.benchmark]

        # Calculate equity curves
        strategy_equity = (1 + strategy_returns).cumprod() * self.initial_investment
        benchmark_equity = (1 + benchmark_returns).cumprod() * self.initial_investment

        return strategy_equity, benchmark_equity

    def calculate_metrics(self, equity_curve: pd.Series) -> Dict[str, float]:
        """Calculate key performance metrics."""
        equity_curve = equity_curve.dropna()

        if len(equity_curve) < 2:
            return None

        returns = equity_curve.pct_change().dropna()

        # Total return
        total_return = (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1

        # Annualized return
        years = len(equity_curve) / 252
        annualized_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0

        # Annualized volatility
        annualized_volatility = returns.std() * np.sqrt(252)

        # Sharpe ratio (assuming risk-free rate = 0)
        sharpe_ratio = (
            annualized_return / annualized_volatility
            if annualized_volatility > 0
            else 0
        )

        # Maximum drawdown
        cumulative_max = equity_curve.cummax()
        drawdown = (equity_curve - cumulative_max) / cumulative_max
        max_drawdown = drawdown.min()

        # Calmar ratio
        calmar_ratio = annualized_return / abs(max_drawdown) if max_drawdown != 0 else 0

        return {
            "Total Return": total_return,
            "Annualized Return": annualized_return,
            "Annualized Volatility": annualized_volatility,
            "Sharpe Ratio": sharpe_ratio,
            "Max Drawdown": max_drawdown,
            "Calmar Ratio": calmar_ratio,
        }

    def create_visualizations(
        self,
        strategy_equity: pd.Series,
        benchmark_equity: pd.Series,
        weights: pd.DataFrame,
        output_dir: str,
    ) -> None:
        """Create standardized visualizations for all strategies."""
        os.makedirs(output_dir, exist_ok=True)

        # 1. Equity Curve Comparison
        plt.figure(figsize=(12, 6))
        plt.plot(
            strategy_equity.index,
            strategy_equity / strategy_equity.iloc[0] * 100,
            label=f"{self.get_strategy_name()} Strategy",
            linewidth=2,
            color="blue",
        )
        plt.plot(
            benchmark_equity.index,
            benchmark_equity / benchmark_equity.iloc[0] * 100,
            label=f"{self.benchmark} Benchmark",
            linewidth=2,
            color="red",
        )
        plt.title(
            f"{self.get_strategy_name()} vs {self.benchmark}\n{self.get_strategy_description()}",
            fontsize=14,
            fontweight="bold",
        )
        plt.xlabel("Date")
        plt.ylabel("Portfolio Value (Normalized to 100)")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(
            os.path.join(output_dir, "equity_curve_comparison.png"),
            dpi=300,
            bbox_inches="tight",
        )
        plt.close()

        # 2. Portfolio Weights Over Time
        plt.figure(figsize=(12, 6))
        for ticker in self.tickers:
            plt.plot(
                weights.index,
                weights[ticker] * 100,
                label=f"{ticker} Weight",
                linewidth=2,
            )
        plt.title(
            f"{self.get_strategy_name()} Portfolio Weights\nAsset Allocation Over Time",
            fontsize=14,
            fontweight="bold",
        )
        plt.xlabel("Date")
        plt.ylabel("Weight (%)")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.axhline(
            y=100 / len(self.tickers),
            color="black",
            linestyle="--",
            alpha=0.5,
            label=f"Equal Weight ({100/len(self.tickers):.1f}%)",
        )
        plt.tight_layout()
        plt.savefig(
            os.path.join(output_dir, "portfolio_weights.png"),
            dpi=300,
            bbox_inches="tight",
        )
        plt.close()

        # 3. Drawdown Comparison
        def calculate_drawdown(equity_curve):
            cumulative_max = equity_curve.cummax()
            return (equity_curve - cumulative_max) / cumulative_max * 100

        strategy_dd = calculate_drawdown(strategy_equity)
        benchmark_dd = calculate_drawdown(benchmark_equity)

        plt.figure(figsize=(12, 6))
        plt.plot(
            strategy_dd.index,
            strategy_dd,
            label=f"{self.get_strategy_name()}",
            linewidth=2,
            color="blue",
        )
        plt.plot(
            benchmark_dd.index,
            benchmark_dd,
            label=f"{self.benchmark}",
            linewidth=2,
            color="red",
        )
        plt.title(
            f"Drawdown Comparison\n{self.get_strategy_name()} vs {self.benchmark}",
            fontsize=14,
            fontweight="bold",
        )
        plt.xlabel("Date")
        plt.ylabel("Drawdown (%)")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.axhline(y=0, color="black", linestyle="-", alpha=0.3)
        plt.tight_layout()
        plt.savefig(
            os.path.join(output_dir, "drawdown_comparison.png"),
            dpi=300,
            bbox_inches="tight",
        )
        plt.close()

    def save_results(
        self,
        strategy_equity: pd.Series,
        benchmark_equity: pd.Series,
        weights: pd.DataFrame,
        strategy_returns: pd.Series,
        metrics: Dict[str, float],
        output_dir: str,
    ) -> None:
        """Save all results to files."""
        os.makedirs(output_dir, exist_ok=True)

        # Portfolio values
        portfolio_df = pd.DataFrame(
            {
                "Strategy": strategy_equity,
                f"{self.benchmark}_Benchmark": benchmark_equity,
            }
        )
        portfolio_df.to_csv(os.path.join(output_dir, "portfolio_values.csv"))

        # Portfolio weights
        weights.to_csv(os.path.join(output_dir, "portfolio_weights.csv"))

        # Strategy returns
        returns_df = pd.DataFrame(
            {
                "Strategy_Returns": strategy_returns,
                f"{self.benchmark}_Returns": benchmark_equity.pct_change(),
            }
        )
        returns_df.to_csv(os.path.join(output_dir, "strategy_returns.csv"))

        # Performance metrics
        metrics_df = pd.DataFrame(list(metrics.items()), columns=["Metric", "Value"])
        metrics_df.to_csv(
            os.path.join(output_dir, "performance_metrics.csv"), index=False
        )

        # Summary report
        summary = f"""{self.get_strategy_name()} Backtest Report
===============================================

Strategy: {self.get_strategy_description()}
Assets: {', '.join(self.tickers)}
Benchmark: {self.benchmark}
Period: {self.start_date} to {self.end_date}
Initial Investment: ${self.initial_investment:,.2f}

Strategy Rules:
{self.get_strategy_description()}

Key Results:
- Total Return: {metrics['Total Return']:.2%}
- Annualized Return: {metrics['Annualized Return']:.2%}
- Annualized Volatility: {metrics['Annualized Volatility']:.2%}
- Sharpe Ratio: {metrics['Sharpe Ratio']:.2f}
- Maximum Drawdown: {metrics['Max Drawdown']:.2%}
- Calmar Ratio: {metrics['Calmar Ratio']:.2f}

Files Generated:
- portfolio_values.csv: Daily portfolio and benchmark values
- portfolio_weights.csv: Daily portfolio weights
- strategy_returns.csv: Daily strategy and benchmark returns
- performance_metrics.csv: Key performance metrics
- equity_curve_comparison.png: Strategy vs benchmark performance
- portfolio_weights.png: Weight evolution over time
- drawdown_comparison.png: Drawdown analysis

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        with open(os.path.join(output_dir, "summary_report.txt"), "w") as f:
            f.write(summary)

        print(f"✅ Results saved to: {output_dir}")

    def run_backtest(self) -> Dict[str, Any]:
        """Execute the complete backtest workflow."""
        print(f"🚀 {self.get_strategy_name()} Backtest")
        print("=" * 50)

        try:
            # 1. Download data
            self.prices, volume = self.download_data()

            # 2. Calculate strategy weights
            print(f"\n📊 Calculating {self.get_strategy_name()} weights...")
            self.weights = self.calculate_weights(self.prices, **self.kwargs)

            # 3. Calculate performance
            print("📈 Calculating portfolio performance...")
            strategy_equity, benchmark_equity = self.calculate_portfolio_performance(
                self.prices, self.weights
            )

            # 4. Calculate metrics
            print("📊 Calculating performance metrics...")
            self.strategy_metrics = self.calculate_metrics(strategy_equity)
            self.benchmark_metrics = self.calculate_metrics(benchmark_equity)

            if self.strategy_metrics is None or self.benchmark_metrics is None:
                raise ValueError("Could not calculate performance metrics")

            # 5. Display results
            self._display_results(strategy_equity, benchmark_equity)

            # 6. Create visualizations and save results
            output_dir = f"{self.get_strategy_name().lower().replace(' ', '_')}_results"
            print(f"\n📊 Creating visualizations...")
            self.create_visualizations(
                strategy_equity, benchmark_equity, self.weights, output_dir
            )

            print(f"💾 Saving results...")
            strategy_returns = strategy_equity.pct_change()
            self.save_results(
                strategy_equity,
                benchmark_equity,
                self.weights,
                strategy_returns,
                self.strategy_metrics,
                output_dir,
            )

            print(f"\n🎉 {self.get_strategy_name()} backtest completed successfully!")
            print(f"📁 Check the '{output_dir}' folder for detailed results and charts")

            return {
                "strategy_equity": strategy_equity,
                "benchmark_equity": benchmark_equity,
                "weights": self.weights,
                "strategy_metrics": self.strategy_metrics,
                "benchmark_metrics": self.benchmark_metrics,
                "output_dir": output_dir,
            }

        except Exception as e:
            print(f"❌ Error during backtest: {e}")
            import traceback

            traceback.print_exc()
            return None

    def _display_results(
        self, strategy_equity: pd.Series, benchmark_equity: pd.Series
    ) -> None:
        """Display backtest results in console."""
        print("\n📊 PERFORMANCE RESULTS")
        print("=" * 50)
        print(f"Strategy: {self.get_strategy_name()}")
        print(f"Benchmark: {self.benchmark}")
        print(f"Period: {self.start_date} to {self.end_date}")
        print(f"Initial Investment: ${self.initial_investment:,.2f}")
        print()

        print(f"📈 {self.get_strategy_name()} METRICS:")
        for metric, value in self.strategy_metrics.items():
            if "Return" in metric or "Drawdown" in metric:
                print(f"  {metric}: {value:.2%}")
            else:
                print(f"  {metric}: {value:.2f}")

        print(f"\n📊 {self.benchmark} METRICS:")
        for metric, value in self.benchmark_metrics.items():
            if "Return" in metric or "Drawdown" in metric:
                print(f"  {metric}: {value:.2%}")
            else:
                print(f"  {metric}: {value:.2f}")

        # Calculate relative performance
        excess_return = (
            self.strategy_metrics["Total Return"]
            - self.benchmark_metrics["Total Return"]
        )
        print(f"\n🎯 RELATIVE PERFORMANCE:")
        print(f"  vs {self.benchmark}: {excess_return:.2%}")


# Example usage and testing
if __name__ == "__main__":
    print("🔧 Strategy Framework Test")
    print(
        "This framework provides a base structure for implementing investment strategies."
    )
    print(
        "Inherit from BaseStrategy and implement the abstract methods to create your strategy."
    )
