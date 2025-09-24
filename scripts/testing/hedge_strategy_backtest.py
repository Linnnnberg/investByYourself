#!/usr/bin/env python3
"""
Hedge Strategy Backtest Script
------------------------------
Implements a dynamic hedge strategy using:
- SPY (S&P 500) as the risk asset
- TLT (20+ Year Treasury) as the defensive asset

Strategy: Trend-following with inverse volatility weighting
- Risk-ON: SPY above 200-day SMA, inverse volatility weights
- Risk-OFF: SPY below 200-day SMA, 100% TLT
- Daily rebalancing with 1-day lag to avoid look-ahead bias

Period: 2020-01-01 to 2024-12-31
Initial Investment: $10,000

Usage:
  python hedge_strategy_backtest.py
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
RISK_ASSET = "SPY"  # S&P 500 ETF
DEFENSIVE_ASSET = "TLT"  # 20+ Year Treasury ETF
START_DATE = "2020-01-01"
END_DATE = "2024-12-31"
INITIAL_INVESTMENT = 10000  # $10,000 initial investment
SMA_PERIOD = 200  # 200-day Simple Moving Average
VOL_PERIOD = 60  # 60-day rolling volatility


def download_data(risk_asset, defensive_asset, start_date, end_date):
    """Download historical data for risk and defensive assets."""
    print(f"Downloading data for {risk_asset} and {defensive_asset}...")
    print(f"Period: {start_date} to {end_date}")

    # Download both assets
    tickers = [risk_asset, defensive_asset]
    data = yf.download(
        tickers, start=start_date, end=end_date, progress=False, auto_adjust=False
    )

    if data.empty:
        raise ValueError("No data downloaded. Please check ticker symbols and dates.")

    print(f"Data columns: {data.columns.tolist()}")
    print(f"Data shape: {data.shape}")

    # Extract adjusted close prices
    if len(tickers) == 1:
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
    print(f"Adjusted Close columns: {adj_close.columns.tolist()}")
    return adj_close, volume


def calculate_returns(prices):
    """Calculate daily returns from prices."""
    return prices.pct_change().fillna(0)


def calculate_sma(prices, period):
    """Calculate Simple Moving Average."""
    return prices.rolling(period).mean()


def calculate_rolling_volatility(returns, period):
    """Calculate rolling volatility."""
    return returns.rolling(period).std()


def inverse_volatility_weights(vol_risk, vol_defensive):
    """Calculate inverse volatility weights."""
    if vol_risk == 0 or vol_defensive == 0:
        return 0.5, 0.5

    # Inverse volatility weighting
    inv_vol_risk = 1 / vol_risk
    inv_vol_defensive = 1 / vol_defensive
    total_inv_vol = inv_vol_risk + inv_vol_defensive

    weight_risk = inv_vol_risk / total_inv_vol
    weight_defensive = inv_vol_defensive / total_inv_vol

    return weight_risk, weight_defensive


def calculate_hedge_strategy_weights(
    prices, risk_asset, defensive_asset, sma_period, vol_period
):
    """Calculate hedge strategy weights based on trend and volatility."""
    # Calculate returns
    returns = calculate_returns(prices)

    # Calculate 200-day SMA for trend detection
    sma_200 = calculate_sma(prices[risk_asset], sma_period)

    # Calculate rolling volatility
    vol_risk = calculate_rolling_volatility(returns[risk_asset], vol_period)
    vol_defensive = calculate_rolling_volatility(returns[defensive_asset], vol_period)

    # Initialize weight DataFrames
    weights_df = pd.DataFrame(
        index=prices.index, columns=[risk_asset, defensive_asset], dtype=float
    )

    # Calculate weights for each day
    for i, date in enumerate(prices.index):
        if (
            pd.isna(sma_200.loc[date])
            or pd.isna(vol_risk.loc[date])
            or pd.isna(vol_defensive.loc[date])
        ):
            # Warm-up period - equal weights
            weights_df.loc[date, risk_asset] = 0.5
            weights_df.loc[date, defensive_asset] = 0.5
        else:
            # Check if we're in risk-ON or risk-OFF mode
            risk_on = prices.loc[date, risk_asset] >= sma_200.loc[date]

            if risk_on:
                # Risk-ON: Use inverse volatility weighting
                w_risk, w_defensive = inverse_volatility_weights(
                    vol_risk.loc[date], vol_defensive.loc[date]
                )
            else:
                # Risk-OFF: 100% defensive
                w_risk, w_defensive = 0.0, 1.0

            weights_df.loc[date, risk_asset] = w_risk
            weights_df.loc[date, defensive_asset] = w_defensive

    # Lag weights by 1 day to avoid look-ahead bias
    weights_df_lagged = weights_df.shift(1).fillna(0.5)

    return weights_df, weights_df_lagged, sma_200, vol_risk, vol_defensive


def calculate_portfolio_performance(prices, weights_df, risk_asset, defensive_asset):
    """Calculate portfolio performance over time."""
    # Calculate returns
    returns = calculate_returns(prices)

    # Calculate strategy returns
    strategy_returns = (
        weights_df[risk_asset] * returns[risk_asset]
        + weights_df[defensive_asset] * returns[defensive_asset]
    )

    # Calculate equity curves
    strategy_equity = (1 + strategy_returns).cumprod() * INITIAL_INVESTMENT
    risk_equity = (1 + returns[risk_asset]).cumprod() * INITIAL_INVESTMENT
    defensive_equity = (1 + returns[defensive_asset]).cumprod() * INITIAL_INVESTMENT

    return strategy_returns, strategy_equity, risk_equity, defensive_equity


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


def create_visualizations(
    strategy_equity,
    risk_equity,
    defensive_equity,
    weights_df,
    sma_200,
    vol_risk,
    vol_defensive,
    output_dir,
):
    """Create and save performance visualizations."""
    os.makedirs(output_dir, exist_ok=True)

    # 1. Equity Curve Comparison
    plt.figure(figsize=(12, 6))
    plt.plot(
        strategy_equity.index,
        strategy_equity / strategy_equity.iloc[0] * 100,
        label="Hedge Strategy",
        linewidth=2,
        color="blue",
    )
    plt.plot(
        risk_equity.index,
        risk_equity / risk_equity.iloc[0] * 100,
        label=f"{RISK_ASSET} (Risk Asset)",
        linewidth=2,
        color="red",
    )
    plt.plot(
        defensive_equity.index,
        defensive_equity / defensive_equity.iloc[0] * 100,
        label=f"{DEFENSIVE_ASSET} (Defensive Asset)",
        linewidth=2,
        color="green",
    )
    plt.title(
        "Hedge Strategy vs Assets\nTrend-Following with Inverse Volatility Weighting",
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
    plt.plot(
        weights_df.index,
        weights_df[RISK_ASSET] * 100,
        label=f"{RISK_ASSET} Weight",
        linewidth=2,
        color="red",
    )
    plt.plot(
        weights_df.index,
        weights_df[DEFENSIVE_ASSET] * 100,
        label=f"{DEFENSIVE_ASSET} Weight",
        linewidth=2,
        color="green",
    )
    plt.title(
        "Portfolio Weights Over Time\nDynamic Allocation Based on Trend and Volatility",
        fontsize=14,
        fontweight="bold",
    )
    plt.xlabel("Date")
    plt.ylabel("Weight (%)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.axhline(
        y=50, color="black", linestyle="--", alpha=0.5, label="Equal Weight (50%)"
    )
    plt.tight_layout()
    plt.savefig(
        os.path.join(output_dir, "portfolio_weights.png"), dpi=300, bbox_inches="tight"
    )
    plt.close()

    # 3. Trend Signal (SPY vs 200-day SMA)
    plt.figure(figsize=(12, 6))
    plt.plot(
        risk_equity.index,
        risk_equity / risk_equity.iloc[0] * 100,
        label=f"{RISK_ASSET} Price (Normalized)",
        linewidth=2,
        color="red",
    )
    plt.plot(
        sma_200.index,
        sma_200 / sma_200.iloc[0] * 100,
        label="200-Day SMA (Normalized)",
        linewidth=2,
        color="blue",
        linestyle="--",
    )
    plt.title(
        "Trend Signal: SPY vs 200-Day Moving Average\nAbove SMA = Risk-ON, Below SMA = Risk-OFF",
        fontsize=14,
        fontweight="bold",
    )
    plt.xlabel("Date")
    plt.ylabel("Normalized Value")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        os.path.join(output_dir, "trend_signal.png"), dpi=300, bbox_inches="tight"
    )
    plt.close()

    # 4. Rolling Volatility Comparison
    plt.figure(figsize=(12, 6))
    plt.plot(
        vol_risk.index,
        vol_risk * np.sqrt(252) * 100,
        label=f"{RISK_ASSET} Volatility (Annualized)",
        linewidth=2,
        color="red",
    )
    plt.plot(
        vol_defensive.index,
        vol_defensive * np.sqrt(252) * 100,
        label=f"{DEFENSIVE_ASSET} Volatility (Annualized)",
        linewidth=2,
        color="green",
    )
    plt.title(
        "Rolling 60-Day Volatility Comparison\nUsed for Inverse Volatility Weighting",
        fontsize=14,
        fontweight="bold",
    )
    plt.xlabel("Date")
    plt.ylabel("Annualized Volatility (%)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        os.path.join(output_dir, "rolling_volatility.png"), dpi=300, bbox_inches="tight"
    )
    plt.close()

    # 5. Drawdown Comparison
    def calculate_drawdown(equity_curve):
        cumulative_max = equity_curve.cummax()
        return (equity_curve - cumulative_max) / cumulative_max * 100

    strategy_dd = calculate_drawdown(strategy_equity)
    risk_dd = calculate_drawdown(risk_equity)
    defensive_dd = calculate_drawdown(defensive_equity)

    plt.figure(figsize=(12, 6))
    plt.plot(
        strategy_dd.index,
        strategy_dd,
        label="Hedge Strategy",
        linewidth=2,
        color="blue",
    )
    plt.plot(risk_dd.index, risk_dd, label=f"{RISK_ASSET}", linewidth=2, color="red")
    plt.plot(
        defensive_dd.index,
        defensive_dd,
        label=f"{DEFENSIVE_ASSET}",
        linewidth=2,
        color="green",
    )
    plt.title(
        "Drawdown Comparison\nHedge Strategy vs Individual Assets",
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
    strategy_equity,
    risk_equity,
    defensive_equity,
    weights_df,
    strategy_returns,
    metrics,
    output_dir,
):
    """Save all results to CSV files."""
    os.makedirs(output_dir, exist_ok=True)

    # Portfolio values
    portfolio_df = pd.DataFrame(
        {
            "Hedge_Strategy": strategy_equity,
            f"{RISK_ASSET}_Asset": risk_equity,
            f"{DEFENSIVE_ASSET}_Asset": defensive_equity,
        }
    )
    portfolio_df.to_csv(os.path.join(output_dir, "portfolio_values.csv"))

    # Portfolio weights
    weights_df.to_csv(os.path.join(output_dir, "portfolio_weights.csv"))

    # Strategy returns
    returns_df = pd.DataFrame(
        {
            "Strategy_Returns": strategy_returns,
            f"{RISK_ASSET}_Returns": strategy_equity.pct_change(),
            f"{DEFENSIVE_ASSET}_Returns": defensive_equity.pct_change(),
        }
    )
    returns_df.to_csv(os.path.join(output_dir, "strategy_returns.csv"))

    # Performance metrics
    metrics_df = pd.DataFrame(list(metrics.items()), columns=["Metric", "Value"])
    metrics_df.to_csv(os.path.join(output_dir, "performance_metrics.csv"), index=False)

    # Summary report
    summary = f"""Hedge Strategy Backtest Report
===============================================

Strategy: Dynamic Hedge with Trend-Following and Inverse Volatility
Risk Asset: {RISK_ASSET} (S&P 500 ETF)
Defensive Asset: {DEFENSIVE_ASSET} (20+ Year Treasury ETF)
Period: {START_DATE} to {END_DATE}
Initial Investment: ${INITIAL_INVESTMENT:,.2f}
SMA Period: {SMA_PERIOD} days
Volatility Period: {VOL_PERIOD} days

Strategy Rules:
- Risk-ON: When {RISK_ASSET} > 200-day SMA, use inverse volatility weighting
- Risk-OFF: When {RISK_ASSET} < 200-day SMA, 100% {DEFENSIVE_ASSET}
- Rebalancing: Daily with 1-day lag to avoid look-ahead bias

Key Results:
- Total Return: {metrics['Total Return']:.2%}
- Annualized Return: {metrics['Annualized Return']:.2%}
- Annualized Volatility: {metrics['Annualized Volatility']:.2%}
- Sharpe Ratio: {metrics['Sharpe Ratio']:.2f}
- Maximum Drawdown: {metrics['Max Drawdown']:.2%}
- Calmar Ratio: {metrics['Calmar Ratio']:.2f}

Files Generated:
- portfolio_values.csv: Daily portfolio and asset values
- portfolio_weights.csv: Daily portfolio weights
- strategy_returns.csv: Daily strategy and asset returns
- performance_metrics.csv: Key performance metrics
- equity_curve_comparison.png: Portfolio vs assets performance
- portfolio_weights.png: Weight evolution over time
- trend_signal.png: Trend signal visualization
- rolling_volatility.png: Volatility comparison
- drawdown_comparison.png: Drawdown analysis

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    with open(os.path.join(output_dir, "summary_report.txt"), "w") as f:
        f.write(summary)

    print(f"✅ Results saved to: {output_dir}")


def main():
    """Main execution function."""
    print("🚀 Hedge Strategy Backtest")
    print("=" * 50)

    try:
        # Download data
        adj_close, volume = download_data(
            RISK_ASSET, DEFENSIVE_ASSET, START_DATE, END_DATE
        )

        # Debug: Print data structure information
        print(f"\n🔍 DATA STRUCTURE DEBUG:")
        print(f"Adj Close type: {type(adj_close)}")
        print(f"Adj Close shape: {adj_close.shape}")
        print(f"Adj Close columns: {adj_close.columns.tolist()}")

        # Calculate hedge strategy weights
        print("\n📊 Calculating hedge strategy weights...")
        (
            weights_df,
            weights_df_lagged,
            sma_200,
            vol_risk,
            vol_defensive,
        ) = calculate_hedge_strategy_weights(
            adj_close, RISK_ASSET, DEFENSIVE_ASSET, SMA_PERIOD, VOL_PERIOD
        )

        # Calculate portfolio performance
        print("📈 Calculating portfolio performance...")
        (
            strategy_returns,
            strategy_equity,
            risk_equity,
            defensive_equity,
        ) = calculate_portfolio_performance(
            adj_close, weights_df_lagged, RISK_ASSET, DEFENSIVE_ASSET
        )

        # Calculate performance metrics
        print("📊 Calculating performance metrics...")
        strategy_metrics = calculate_metrics(strategy_equity)
        risk_metrics = calculate_metrics(risk_equity)
        defensive_metrics = calculate_metrics(defensive_equity)

        if (
            strategy_metrics is None
            or risk_metrics is None
            or defensive_metrics is None
        ):
            print("❌ Error: Could not calculate performance metrics")
            return

        # Display results
        print("\n📊 PERFORMANCE RESULTS")
        print("=" * 50)
        print(f"Strategy: Dynamic Hedge ({RISK_ASSET} + {DEFENSIVE_ASSET})")
        print(f"Period: {START_DATE} to {END_DATE}")
        print(f"Initial Investment: ${INITIAL_INVESTMENT:,.2f}")
        print()

        print("📈 HEDGE STRATEGY METRICS:")
        for metric, value in strategy_metrics.items():
            if "Return" in metric or "Drawdown" in metric:
                print(f"  {metric}: {value:.2%}")
            else:
                print(f"  {metric}: {value:.2f}")

        print(f"\n📊 {RISK_ASSET} METRICS:")
        for metric, value in risk_metrics.items():
            if "Return" in metric or "Drawdown" in metric:
                print(f"  {metric}: {value:.2%}")
            else:
                print(f"  {metric}: {value:.2f}")

        print(f"\n📊 {DEFENSIVE_ASSET} METRICS:")
        for metric, value in defensive_metrics.items():
            if "Return" in metric or "Drawdown" in metric:
                print(f"  {metric}: {value:.2%}")
            else:
                print(f"  {metric}: {value:.2f}")

        # Calculate relative performance
        excess_return_vs_risk = (
            strategy_metrics["Total Return"] - risk_metrics["Total Return"]
        )
        excess_return_vs_defensive = (
            strategy_metrics["Total Return"] - defensive_metrics["Total Return"]
        )

        print(f"\n🎯 RELATIVE PERFORMANCE:")
        print(f"  vs {RISK_ASSET}: {excess_return_vs_risk:.2%}")
        print(f"  vs {DEFENSIVE_ASSET}: {excess_return_vs_defensive:.2%}")

        # Create visualizations and save results
        output_dir = "hedge_strategy_results"
        print(f"\n📊 Creating visualizations...")
        create_visualizations(
            strategy_equity,
            risk_equity,
            defensive_equity,
            weights_df_lagged,
            sma_200,
            vol_risk,
            vol_defensive,
            output_dir,
        )

        print(f"💾 Saving results...")
        save_results(
            strategy_equity,
            risk_equity,
            defensive_equity,
            weights_df_lagged,
            strategy_returns,
            strategy_metrics,
            output_dir,
        )

        print(f"\n🎉 Hedge strategy backtest completed successfully!")
        print(f"📁 Check the '{output_dir}' folder for detailed results and charts")

    except Exception as e:
        print(f"❌ Error during backtest: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
