#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Portfolio Optimization Framework: General Concepts and Implementation

This script demonstrates the core concepts of portfolio optimization using PyPortfolioOpt
and shows how different approaches can be applied to various investment strategies.

Key Concepts:
1. Mean-Variance Optimization (MVO)
2. Risk Parity
3. Hierarchical Risk Parity (HRP)
4. Black-Litterman Model
5. Efficient Frontier Analysis
6. Risk Metrics (VaR, CVaR, Drawdown)

Requirements:
pip install PyPortfolioOpt yfinance pandas numpy matplotlib seaborn
"""

import warnings
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

warnings.filterwarnings("ignore")

try:
    from pypfopt import (EfficientFrontier, expected_returns,
                         objective_functions, risk_models)
    from pypfopt.hierarchical_portfolio import HRPOpt
    from pypfopt.risk_models import CovarianceShrinkage

    PYPFOPT_AVAILABLE = True
    print("✓ PyPortfolioOpt successfully imported")
except ImportError as e:
    print(f"✗ PyPortfolioOpt not available: {e}")
    PYPFOPT_AVAILABLE = False


class PortfolioOptimizer:
    """
    General portfolio optimization framework that can be applied to any asset universe
    """

    def __init__(self, risk_free_rate=0.02):
        self.risk_free_rate = risk_free_rate
        self.returns = None
        self.expected_returns = None
        self.covariance_matrix = None

    def prepare_data(self, prices_df, frequency=252):
        """
        Prepare data for optimization

        Args:
            prices_df: DataFrame with asset prices
            frequency: Trading frequency (252 for daily, 12 for monthly)
        """
        self.returns = prices_df.pct_change().dropna()
        self.expected_returns = expected_returns.mean_historical_return(
            self.returns, frequency=frequency
        )

        # Use covariance shrinkage for better stability
        if PYPFOPT_AVAILABLE:
            try:
                self.covariance_matrix = CovarianceShrinkage(self.returns).ledoit_wolf()
            except:
                self.covariance_matrix = risk_models.sample_cov(
                    self.returns, frequency=frequency
                )
        else:
            self.covariance_matrix = self.returns.cov()

    def optimize_mvo(self, target_return=None, target_volatility=None, max_sharpe=True):
        """
        Mean-Variance Optimization

        Args:
            target_return: Target portfolio return
            target_volatility: Target portfolio volatility
            max_sharpe: Whether to maximize Sharpe ratio
        """
        if not PYPFOPT_AVAILABLE:
            return None, "PyPortfolioOpt not available"

        try:
            ef = EfficientFrontier(self.expected_returns, self.covariance_matrix)

            if target_return is not None:
                ef.efficient_return(target_return)
            elif target_volatility is not None:
                ef.efficient_volatility(target_volatility)
            elif max_sharpe:
                ef.max_sharpe(risk_free_rate=self.risk_free_rate)
            else:
                ef.min_volatility()

            weights = ef.clean_weights()
            portfolio_perf = ef.portfolio_performance(
                risk_free_rate=self.risk_free_rate
            )

            return weights, portfolio_perf

        except Exception as e:
            return None, f"Optimization failed: {e}"

    def optimize_hrp(self):
        """
        Hierarchical Risk Parity - non-parametric approach
        """
        if not PYPFOPT_AVAILABLE:
            return None, "PyPortfolioOpt not available"

        try:
            hrp = HRPOpt(self.returns)
            weights = hrp.optimize()

            # Calculate portfolio performance
            portfolio_return = np.sum(weights * self.expected_returns)
            portfolio_vol = np.sqrt(
                np.dot(weights.T, np.dot(self.covariance_matrix, weights))
            )
            sharpe = (portfolio_return - self.risk_free_rate) / portfolio_vol

            return weights, (portfolio_return, portfolio_vol, sharpe)

        except Exception as e:
            return None, f"HRP optimization failed: {e}"

    def efficient_frontier_analysis(self, num_portfolios=100):
        """
        Generate efficient frontier for analysis
        """
        if not PYPFOPT_AVAILABLE:
            return None, "PyPortfolioOpt not available"

        try:
            ef = EfficientFrontier(self.expected_returns, self.covariance_matrix)

            # Generate efficient frontier
            ef.efficient_frontier()
            ret_range = np.linspace(
                ef.ef_return.min(), ef.ef_return.max(), num_portfolios
            )
            vol_range = []

            for ret in ret_range:
                try:
                    ef.efficient_return(ret)
                    vol_range.append(ef.portfolio_volatility())
                except:
                    vol_range.append(np.nan)

            return ret_range, vol_range

        except Exception as e:
            return None, f"Efficient frontier failed: {e}"

    def calculate_risk_metrics(self, weights):
        """
        Calculate comprehensive risk metrics for a portfolio
        """
        if weights is None:
            return {}

        try:
            # Portfolio statistics
            portfolio_return = np.sum(weights * self.expected_returns)
            portfolio_vol = np.sqrt(
                np.dot(weights.T, np.dot(self.covariance_matrix, weights))
            )

            # Sharpe ratio
            sharpe = (
                (portfolio_return - self.risk_free_rate) / portfolio_vol
                if portfolio_vol > 0
                else 0
            )

            # Portfolio returns series
            portfolio_returns = (
                self.returns * pd.Series(weights, index=self.returns.columns)
            ).sum(axis=1)

            # Drawdown
            cum_returns = (1 + portfolio_returns).cumprod()
            rolling_max = cum_returns.expanding().max()
            drawdown = (cum_returns - rolling_max) / rolling_max
            max_drawdown = drawdown.min()

            # VaR and CVaR (95% confidence)
            var_95 = np.percentile(portfolio_returns, 5)
            cvar_95 = portfolio_returns[portfolio_returns <= var_95].mean()

            # Sortino ratio
            downside_returns = portfolio_returns[portfolio_returns < 0]
            downside_dev = downside_returns.std() if len(downside_returns) > 0 else 0
            sortino = (
                (portfolio_return - self.risk_free_rate) / downside_dev
                if downside_dev > 0
                else 0
            )

            return {
                "Return": portfolio_return,
                "Volatility": portfolio_vol,
                "Sharpe": sharpe,
                "Sortino": sortino,
                "MaxDrawdown": max_drawdown,
                "VaR_95": var_95,
                "CVaR_95": cvar_95,
            }

        except Exception as e:
            return {"Error": str(e)}


class StrategyFramework:
    """
    Framework for implementing different investment strategies with optimization
    """

    def __init__(self, optimizer):
        self.optimizer = optimizer

    def momentum_strategy(self, prices_df, lookback=12, top_k=2, rebalance_freq="M"):
        """
        Generic momentum strategy that can be applied to any asset universe

        Args:
            prices_df: Asset prices
            lookback: Momentum lookback period
            top_k: Number of top assets to select
            rebalance_freq: Rebalancing frequency
        """
        # Resample to rebalancing frequency
        if rebalance_freq == "M":
            prices = prices_df.resample("ME").last()
        elif rebalance_freq == "Q":
            prices = prices_df.resample("Q").last()
        else:
            prices = prices_df

        returns = prices.pct_change().dropna()

        # Calculate momentum
        momentum = prices.shift(1) / prices.shift(lookback) - 1

        weights = pd.DataFrame(index=returns.index, columns=prices.columns, data=0.0)

        for i, date in enumerate(returns.index):
            if i == 0:
                continue

            # Get momentum signal from previous period
            signal_date = (
                momentum.index[momentum.index < date][-1]
                if (momentum.index < date).any()
                else None
            )

            if signal_date is not None:
                # Select top K assets by momentum
                mom_scores = momentum.loc[signal_date].dropna()
                if len(mom_scores) >= top_k:
                    top_assets = mom_scores.nlargest(top_k).index

                    # Apply optimization to top assets
                    top_prices = prices_df[top_assets]
                    self.optimizer.prepare_data(top_prices)

                    # Try MVO optimization first, fall back to equal weight
                    opt_weights, _ = self.optimizer.optimize_mvo(max_sharpe=True)

                    if opt_weights is not None:
                        # Apply optimized weights
                        for asset, weight in opt_weights.items():
                            weights.loc[date, asset] = weight
                    else:
                        # Fallback to equal weighting
                        for asset in top_assets:
                            weights.loc[date, asset] = 1.0 / len(top_assets)

        # Calculate portfolio returns
        portfolio_returns = (weights.shift(1) * returns).sum(axis=1)
        return portfolio_returns, weights

    def sector_rotation_strategy(self, prices_df, sector_info, lookback=12, top_k=2):
        """
        Generic sector rotation strategy

        Args:
            prices_df: Asset prices
            sector_info: Dictionary mapping assets to sectors
            lookback: Momentum lookback period
            top_k: Number of top sectors to select
        """
        # Group assets by sector and calculate sector momentum
        sector_momentum = {}
        for sector in set(sector_info.values()):
            sector_assets = [asset for asset, s in sector_info.items() if s == sector]
            if len(sector_assets) > 0:
                sector_prices = prices_df[sector_assets].mean(
                    axis=1
                )  # Equal weight within sector
                momentum = sector_prices.shift(1) / sector_prices.shift(lookback) - 1
                sector_momentum[sector] = momentum

        # Select top sectors and apply optimization
        # Implementation similar to momentum strategy but with sector-level selection
        pass


def demonstrate_concepts():
    """
    Demonstrate the key concepts with a simple example
    """
    print("Portfolio Optimization Framework - Concept Demonstration")
    print("=" * 60)

    # Create sample data (you can replace this with real data)
    np.random.seed(42)
    dates = pd.date_range("2020-01-01", "2024-12-31", freq="D")
    n_assets = 5

    # Generate synthetic price data
    price_data = np.random.randn(len(dates), n_assets).cumsum(axis=0)
    prices = pd.DataFrame(
        price_data, index=dates, columns=[f"Asset_{i}" for i in range(n_assets)]
    )
    prices = prices + 100  # Start at 100

    print(f"Generated sample data: {n_assets} assets, {len(dates)} days")

    # Initialize optimizer
    optimizer = PortfolioOptimizer(risk_free_rate=0.02)
    optimizer.prepare_data(prices)

    print("\n1. Mean-Variance Optimization (MVO)")
    print("-" * 40)

    # MVO - Max Sharpe
    weights_mvo, perf_mvo = optimizer.optimize_mvo(max_sharpe=True)
    if weights_mvo is not None:
        print("✓ MVO Max Sharpe successful")
        print(f"  Expected Return: {perf_mvo[0]:.4f}")
        print(f"  Volatility: {perf_mvo[1]:.4f}")
        print(f"  Sharpe Ratio: {perf_mvo[2]:.4f}")

        # Calculate risk metrics
        risk_metrics = optimizer.calculate_risk_metrics(weights_mvo)
        print(f"  Max Drawdown: {risk_metrics.get('MaxDrawdown', 'N/A'):.4f}")
        print(f"  VaR (95%): {risk_metrics.get('VaR_95', 'N/A'):.4f}")
    else:
        print(f"✗ MVO failed: {perf_mvo}")

    print("\n2. Hierarchical Risk Parity (HRP)")
    print("-" * 40)

    weights_hrp, perf_hrp = optimizer.optimize_hrp()
    if weights_hrp is not None:
        print("✓ HRP successful")
        print(f"  Expected Return: {perf_hrp[0]:.4f}")
        print(f"  Volatility: {perf_hrp[1]:.4f}")
        print(f"  Sharpe Ratio: {perf_hrp[2]:.4f}")
    else:
        print(f"✗ HRP failed: {perf_hrp}")

    print("\n3. Efficient Frontier Analysis")
    print("-" * 40)

    ret_range, vol_range = optimizer.efficient_frontier_analysis()
    if ret_range is not None:
        print("✓ Efficient frontier generated")
        print(f"  Return range: {ret_range.min():.4f} to {ret_range.max():.4f}")
        print(
            f"  Volatility range: {np.nanmin(vol_range):.4f} to {np.nanmax(vol_range):.4f}"
        )

        # Plot efficient frontier
        plt.figure(figsize=(10, 6))
        plt.plot(vol_range, ret_range, "b-", linewidth=2, label="Efficient Frontier")
        plt.xlabel("Portfolio Volatility")
        plt.ylabel("Portfolio Return")
        plt.title("Efficient Frontier Analysis")
        plt.legend()
        plt.grid(True, alpha=0.3)

        # Save plot
        import os

        os.makedirs("charts", exist_ok=True)
        plt.savefig("charts/efficient_frontier_demo.png", dpi=300, bbox_inches="tight")
        print("  Chart saved to: charts/efficient_frontier_demo.png")
        plt.show()
    else:
        print("✗ Efficient frontier failed")

    print("\n4. Strategy Framework Demo")
    print("-" * 40)

    strategy = StrategyFramework(optimizer)
    portfolio_returns, weights = strategy.momentum_strategy(
        prices, lookback=60, top_k=3
    )

    if not portfolio_returns.empty:
        print("✓ Momentum strategy implemented")

        # Calculate strategy performance
        total_return = (1 + portfolio_returns).prod() - 1
        volatility = portfolio_returns.std() * np.sqrt(252)
        sharpe = (
            (portfolio_returns.mean() * 252 - 0.02) / volatility
            if volatility > 0
            else 0
        )

        print(f"  Total Return: {total_return:.4f}")
        print(f"  Volatility: {volatility:.4f}")
        print(f"  Sharpe Ratio: {sharpe:.4f}")
    else:
        print("✗ Momentum strategy failed")

    print("\n" + "=" * 60)
    print("Concept demonstration complete!")
    print("\nKey Takeaways:")
    print("1. Portfolio optimization can be applied to any asset universe")
    print("2. Different optimization methods have different strengths")
    print("3. Risk metrics provide comprehensive portfolio analysis")
    print("4. Strategy framework allows easy implementation of various approaches")


if __name__ == "__main__":
    demonstrate_concepts()
