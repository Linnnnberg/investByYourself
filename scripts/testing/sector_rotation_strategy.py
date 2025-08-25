#!/usr/bin/env python3
"""
Sector Rotation Strategy Backtesting Script
-------------------------------------------
Implements a sector rotation strategy using 4 sector ETFs:
- XLK (Technology)
- XLF (Financials)
- XLE (Energy)
- XLU (Utilities)

Strategy: Equal weight (25% each) with quarterly rebalancing
Comparison: SPY (S&P 500) as benchmark
Period: 2020-01-01 to 2024-12-31

Usage:
  python sector_rotation_strategy.py
"""

import os
import warnings
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore")

# Configuration
TICKERS = ["XLK", "XLF", "XLE", "XLU"]
BENCHMARK = "SPY"
START_DATE = "2020-01-01"
END_DATE = "2024-12-31"
INITIAL_INVESTMENT = 10000  # $10,000 initial investment
REBALANCE_FREQUENCY = "Q"  # Quarterly rebalancing


def download_data(tickers, benchmark, start_date, end_date):
    """Download historical data for tickers and benchmark."""
    print(f"Downloading data for {', '.join(tickers)} and {benchmark}...")
    print(f"Period: {start_date} to {end_date}")

    # Download all tickers including benchmark
    all_tickers = tickers + [benchmark]
    data = yf.download(
        all_tickers, start=start_date, end=end_date, progress=False, auto_adjust=False
    )

    if data.empty:
        raise ValueError("No data downloaded. Please check ticker symbols and dates.")

    print(f"Data columns: {data.columns.tolist()}")
    print(f"Data shape: {data.shape}")

    # Extract adjusted close prices - handle both single and multi-ticker cases
    if len(all_tickers) == 1:
        # Single ticker case
        adj_close = data["Adj Close"]
        volume = data["Volume"]
    else:
        # Multiple tickers case - yfinance returns multi-level columns
        if isinstance(data.columns, pd.MultiIndex):
            # Multi-level columns: (Ticker, DataType)
            adj_close = data["Adj Close"]
            volume = data["Volume"]
        else:
            # Single-level columns (older yfinance behavior)
            adj_close = data["Adj Close"]
            volume = data["Volume"]

    print(f"✅ Downloaded {len(adj_close)} trading days of data")
    print(f"Adjusted Close columns: {adj_close.columns.tolist()}")
    return adj_close, volume


def calculate_returns(prices):
    """Calculate daily returns from prices."""
    return prices.pct_change().fillna(0)


def calculate_portfolio_weights(prices, tickers, initial_weights):
    """Calculate portfolio weights over time with rebalancing."""
    # Initialize
    portfolio_value = INITIAL_INVESTMENT
    weights_df = pd.DataFrame(index=prices.index, columns=tickers, dtype=float)
    holdings_df = pd.DataFrame(index=prices.index, columns=tickers, dtype=float)

    # Set initial weights
    current_weights = pd.Series(initial_weights, index=tickers)
    weights_df.iloc[0] = current_weights

    # Calculate initial holdings
    initial_prices = prices.iloc[0]
    initial_holdings = (portfolio_value * current_weights) / initial_prices
    holdings_df.iloc[0] = initial_holdings

    # Track portfolio over time
    for i in range(1, len(prices)):
        current_date = prices.index[i]
        previous_date = prices.index[i - 1]

        # Update holdings based on price changes (no rebalancing yet)
        price_change = prices.loc[current_date] / prices.loc[previous_date]
        holdings_df.loc[current_date] = holdings_df.loc[previous_date] * price_change

        # Calculate current portfolio value
        current_prices = prices.loc[current_date]
        portfolio_value = (holdings_df.loc[current_date] * current_prices).sum()

        # Check if rebalancing is needed (quarterly)
        if (
            current_date.quarter != previous_date.quarter
            or current_date.year != previous_date.year
        ):
            # Rebalance to target weights
            target_holdings = (portfolio_value * current_weights) / current_prices
            holdings_df.loc[current_date] = target_holdings
            weights_df.loc[current_date] = current_weights
        else:
            # Calculate current weights without rebalancing
            current_weights_actual = (
                holdings_df.loc[current_date] * current_prices
            ) / portfolio_value
            weights_df.loc[current_date] = current_weights_actual

    return weights_df, holdings_df


def calculate_portfolio_performance(holdings, prices, tickers):
    """Calculate portfolio performance over time."""
    portfolio_values = []

    for date in prices.index:
        if date in holdings.index:
            portfolio_value = (holdings.loc[date] * prices.loc[date]).sum()
            portfolio_values.append(portfolio_value)
        else:
            portfolio_values.append(np.nan)

    portfolio_series = pd.Series(portfolio_values, index=prices.index)
    return portfolio_series


def calculate_metrics(equity_curve):
    """Calculate key performance metrics."""
    # Remove any NaN values
    equity_curve = equity_curve.dropna()

    if len(equity_curve) < 2:
        return None

    # Calculate returns
    returns = equity_curve.pct_change().dropna()

    # Total return
    total_return = (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1

    # Annualized return (assuming 252 trading days per year)
    years = len(equity_curve) / 252
    annualized_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0

    # Annualized volatility
    annualized_volatility = returns.std() * np.sqrt(252)

    # Sharpe ratio (assuming risk-free rate = 0)
    sharpe_ratio = (
        annualized_return / annualized_volatility if annualized_volatility > 0 else 0
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


def create_visualizations(portfolio_series, benchmark_series, weights_df, output_dir):
    """Create and save performance visualizations."""
    os.makedirs(output_dir, exist_ok=True)

    # 1. Equity Curve Comparison
    plt.figure(figsize=(12, 6))
    plt.plot(
        portfolio_series.index,
        portfolio_series / portfolio_series.iloc[0] * 100,
        label="Sector Rotation Portfolio",
        linewidth=2,
    )
    plt.plot(
        benchmark_series.index,
        benchmark_series / benchmark_series.iloc[0] * 100,
        label="SPY Benchmark",
        linewidth=2,
    )
    plt.title(
        "Sector Rotation Strategy vs SPY Benchmark\nEqual Weight (25% each) with Quarterly Rebalancing",
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
    for ticker in TICKERS:
        plt.plot(weights_df.index, weights_df[ticker] * 100, label=ticker, linewidth=2)
    plt.title(
        "Portfolio Weights Over Time\n(Quarterly Rebalancing to 25% each)",
        fontsize=14,
        fontweight="bold",
    )
    plt.xlabel("Date")
    plt.ylabel("Weight (%)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.axhline(
        y=25, color="black", linestyle="--", alpha=0.5, label="Target Weight (25%)"
    )
    plt.tight_layout()
    plt.savefig(
        os.path.join(output_dir, "portfolio_weights.png"), dpi=300, bbox_inches="tight"
    )
    plt.close()

    # 3. Drawdown Comparison
    def calculate_drawdown(equity_curve):
        cumulative_max = equity_curve.cummax()
        return (equity_curve - cumulative_max) / cumulative_max * 100

    portfolio_dd = calculate_drawdown(portfolio_series)
    benchmark_dd = calculate_drawdown(benchmark_series)

    plt.figure(figsize=(12, 6))
    plt.plot(
        portfolio_dd.index, portfolio_dd, label="Sector Rotation Portfolio", linewidth=2
    )
    plt.plot(benchmark_dd.index, benchmark_dd, label="SPY Benchmark", linewidth=2)
    plt.title(
        "Drawdown Comparison\nSector Rotation vs SPY", fontsize=14, fontweight="bold"
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

    # 4. Rolling 12-Month Returns
    portfolio_12m = (
        portfolio_series.pct_change(periods=252).rolling(window=252).mean() * 100
    )
    benchmark_12m = (
        benchmark_series.pct_change(periods=252).rolling(window=252).mean() * 100
    )

    plt.figure(figsize=(12, 6))
    plt.plot(
        portfolio_12m.index,
        portfolio_12m,
        label="Sector Rotation Portfolio",
        linewidth=2,
    )
    plt.plot(benchmark_12m.index, benchmark_12m, label="SPY Benchmark", linewidth=2)
    plt.title(
        "Rolling 12-Month Average Returns\nSector Rotation vs SPY",
        fontsize=14,
        fontweight="bold",
    )
    plt.xlabel("Date")
    plt.ylabel("12-Month Rolling Return (%)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.axhline(y=0, color="black", linestyle="-", alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        os.path.join(output_dir, "rolling_returns.png"), dpi=300, bbox_inches="tight"
    )
    plt.close()


def save_results(portfolio_series, benchmark_series, weights_df, metrics, output_dir):
    """Save all results to CSV files."""
    os.makedirs(output_dir, exist_ok=True)

    # Portfolio values
    portfolio_df = pd.DataFrame(
        {
            "Sector_Rotation_Portfolio": portfolio_series,
            "SPY_Benchmark": benchmark_series,
        }
    )
    portfolio_df.to_csv(os.path.join(output_dir, "portfolio_values.csv"))

    # Portfolio weights
    weights_df.to_csv(os.path.join(output_dir, "portfolio_weights.csv"))

    # Performance metrics
    metrics_df = pd.DataFrame(list(metrics.items()), columns=["Metric", "Value"])
    metrics_df.to_csv(os.path.join(output_dir, "performance_metrics.csv"), index=False)

    # Summary report
    summary = f"""Sector Rotation Strategy Backtest Report
================================================

Strategy: Equal weight (25% each) in {', '.join(TICKERS)}
Benchmark: {BENCHMARK}
Period: {START_DATE} to {END_DATE}
Initial Investment: ${INITIAL_INVESTMENT:,.2f}
Rebalancing: Quarterly

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
- performance_metrics.csv: Key performance metrics
- equity_curve_comparison.png: Portfolio vs benchmark performance
- portfolio_weights.png: Weight evolution over time
- drawdown_comparison.png: Drawdown comparison
- rolling_returns.png: Rolling 12-month returns

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    with open(os.path.join(output_dir, "summary_report.txt"), "w") as f:
        f.write(summary)

    print(f"✅ Results saved to: {output_dir}")


def main():
    """Main execution function."""
    print("🚀 Sector Rotation Strategy Backtest")
    print("=" * 50)

    try:
        # Download data
        adj_close, volume = download_data(TICKERS, BENCHMARK, START_DATE, END_DATE)

        # Debug: Print data structure information
        print(f"\n🔍 DATA STRUCTURE DEBUG:")
        print(f"Adj Close type: {type(adj_close)}")
        print(f"Adj Close shape: {adj_close.shape}")
        print(f"Adj Close columns: {adj_close.columns.tolist()}")
        print(f"Adj Close index: {type(adj_close.index)}")
        print(f"First few rows:")
        print(adj_close.head())

        # Separate ticker data and benchmark data
        ticker_prices = adj_close[TICKERS]
        benchmark_prices = adj_close[BENCHMARK]

        print(f"\n📊 Ticker prices shape: {ticker_prices.shape}")
        print(f"📊 Benchmark prices shape: {benchmark_prices.shape}")

        # Calculate returns
        ticker_returns = calculate_returns(ticker_prices)
        benchmark_returns = calculate_returns(benchmark_prices)

        # Initialize portfolio weights (25% each)
        initial_weights = [0.25] * len(TICKERS)

        # Calculate portfolio weights and holdings over time
        print("📊 Calculating portfolio performance...")
        weights_df, holdings_df = calculate_portfolio_weights(
            ticker_prices, TICKERS, initial_weights
        )

        # Calculate portfolio performance
        portfolio_series = calculate_portfolio_performance(
            holdings_df, ticker_prices, TICKERS
        )

        # Normalize benchmark to same starting value
        benchmark_series = (
            benchmark_prices / benchmark_prices.iloc[0] * INITIAL_INVESTMENT
        )

        # Calculate performance metrics
        print("📈 Calculating performance metrics...")
        portfolio_metrics = calculate_metrics(portfolio_series)
        benchmark_metrics = calculate_metrics(benchmark_series)

        if portfolio_metrics is None or benchmark_metrics is None:
            print("❌ Error: Could not calculate performance metrics")
            return

        # Display results
        print("\n📊 PERFORMANCE RESULTS")
        print("=" * 50)
        print(f"Strategy: Equal Weight Sector Rotation ({', '.join(TICKERS)})")
        print(f"Benchmark: {BENCHMARK}")
        print(f"Period: {START_DATE} to {END_DATE}")
        print(f"Initial Investment: ${INITIAL_INVESTMENT:,.2f}")
        print()

        print("📈 PORTFOLIO METRICS:")
        for metric, value in portfolio_metrics.items():
            if "Return" in metric or "Drawdown" in metric:
                print(f"  {metric}: {value:.2%}")
            else:
                print(f"  {metric}: {value:.2f}")

        print("\n📊 BENCHMARK METRICS:")
        for metric, value in benchmark_metrics.items():
            if "Return" in metric or "Drawdown" in metric:
                print(f"  {metric}: {value:.2%}")
            else:
                print(f"  {metric}: {value:.2f}")

        # Calculate relative performance
        excess_return = (
            portfolio_metrics["Total Return"] - benchmark_metrics["Total Return"]
        )
        excess_sharpe = (
            portfolio_metrics["Sharpe Ratio"] - benchmark_metrics["Sharpe Ratio"]
        )

        print(f"\n🎯 RELATIVE PERFORMANCE:")
        print(f"  Excess Return: {excess_return:.2%}")
        print(f"  Excess Sharpe: {excess_sharpe:.2f}")

        # Create visualizations and save results
        output_dir = "sector_rotation_results"
        print(f"\n📊 Creating visualizations...")
        create_visualizations(
            portfolio_series, benchmark_series, weights_df, output_dir
        )

        print(f"💾 Saving results...")
        save_results(
            portfolio_series,
            benchmark_series,
            weights_df,
            portfolio_metrics,
            output_dir,
        )

        print(f"\n🎉 Backtest completed successfully!")
        print(f"📁 Check the '{output_dir}' folder for detailed results and charts")

    except Exception as e:
        print(f"❌ Error during backtest: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
