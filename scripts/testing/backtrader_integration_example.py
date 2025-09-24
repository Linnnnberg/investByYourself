#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backtrader Integration Example: Portfolio Optimization Framework

This script demonstrates how to integrate our portfolio optimization framework
with Backtrader for fast, professional backtesting.
"""

import warnings
from datetime import datetime, timedelta

import backtrader as bt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# Import our optimization framework
try:
    from portfolio_optimization_framework import PortfolioOptimizer

    OPTIMIZER_AVAILABLE = True
    print("✓ Portfolio optimization framework available")
except ImportError:
    OPTIMIZER_AVAILABLE = False
    print("✗ Portfolio optimization framework not available")


class BaseOptimizedStrategy(bt.Strategy):
    """
    Base strategy class that integrates portfolio optimization with Backtrader
    """

    def __init__(self, optimizer_class=PortfolioOptimizer, **kwargs):
        super().__init__()

        # Initialize optimizer
        if OPTIMIZER_AVAILABLE:
            self.optimizer = optimizer_class(**kwargs)
        else:
            self.optimizer = None

        # Track optimization history
        self.weights_history = []
        self.optimization_history = []
        self.rebalance_counter = 0

        # Strategy parameters
        self.params.rebalance_freq = getattr(
            self.params, "rebalance_freq", 21
        )  # Monthly
        self.params.lookback = getattr(self.params, "lookback", 12)
        self.params.top_k = getattr(self.params, "top_k", 2)
        self.params.risk_free_rate = getattr(self.params, "risk_free_rate", 0.02)

    def log_optimization(self, date, weights, performance, method):
        """Log optimization results for analysis"""
        self.optimization_history.append(
            {
                "date": date,
                "weights": weights.copy() if weights else {},
                "performance": performance,
                "method": method,
            }
        )

    def _get_current_prices(self):
        """Get current prices for all assets"""
        prices = {}
        for data in self.datas:
            if len(data) > 0:
                prices[data._name] = data.close[0]
        return prices

    def _get_current_weights(self):
        """Get current portfolio weights"""
        if not hasattr(self, "broker") or not hasattr(self.broker, "getvalue"):
            return {}

        total_value = self.broker.getvalue()
        if total_value <= 0:
            return {}

        weights = {}
        for data in self.datas:
            if hasattr(data, "_name"):
                position_value = self.getposition(data).size * data.close[0]
                weights[data._name] = position_value / total_value

        return weights

    def _equal_weight_fallback(self, assets):
        """Equal weight fallback strategy"""
        if not assets:
            return {}

        weight = 1.0 / len(assets)
        return {asset: weight for asset in assets}


class OptimizedMomentumStrategy(BaseOptimizedStrategy):
    """
    Momentum strategy with integrated portfolio optimization
    """

    params = (
        ("lookback", 12),
        ("top_k", 2),
        ("rebalance_freq", 21),  # Monthly rebalancing
        ("risk_free_rate", 0.02),
        ("max_position", 0.4),  # Maximum 40% per asset
        ("min_position", 0.05),  # Minimum 5% per asset
    )

    def __init__(self):
        super().__init__()

        # Initialize momentum indicators
        self.momentum = {}
        for data in self.datas:
            self.momentum[data] = bt.indicators.MomentumOscillator(
                data, period=self.params.lookback
            )

    def next(self):
        """Main strategy logic"""
        # Check if it's time to rebalance
        if self.rebalance_counter % self.params.rebalance_freq == 0:
            self._rebalance_portfolio()

        self.rebalance_counter += 1

    def _rebalance_portfolio(self):
        """Rebalance portfolio using optimization"""
        if not self.optimizer:
            print("Optimizer not available, using equal weights")
            self._apply_equal_weights()
            return

        try:
            # Get current prices and momentum scores
            current_prices = self._get_current_prices()
            momentum_scores = self._calculate_momentum_scores()

            if not momentum_scores:
                return

            # Select top K assets by momentum
            top_assets = self._select_top_assets(momentum_scores)

            if not top_assets:
                return

            # Apply portfolio optimization
            optimal_weights = self._optimize_portfolio(current_prices, top_assets)

            if optimal_weights:
                # Apply risk constraints
                constrained_weights = self._apply_risk_constraints(optimal_weights)

                # Execute rebalancing
                self._execute_rebalancing(constrained_weights)

                # Log optimization
                self.log_optimization(
                    self.data.datetime.date(),
                    constrained_weights,
                    {"method": "optimization"},
                    "MVO",
                )
            else:
                # Fallback to equal weights
                self._apply_equal_weights()

        except Exception as e:
            print(f"Portfolio optimization failed: {e}")
            self._apply_equal_weights()

    def _calculate_momentum_scores(self):
        """Calculate momentum scores for all assets"""
        momentum_scores = {}

        for data in self.datas:
            if len(data) >= self.params.lookback:
                # Get momentum value
                mom_value = self.momentum[data][0]
                if not np.isnan(mom_value):
                    momentum_scores[data._name] = mom_value

        return momentum_scores

    def _select_top_assets(self, momentum_scores):
        """Select top K assets by momentum"""
        if len(momentum_scores) < self.params.top_k:
            return list(momentum_scores.keys())

        # Sort by momentum and select top K
        sorted_assets = sorted(
            momentum_scores.items(), key=lambda x: x[1], reverse=True
        )

        return [asset for asset, _ in sorted_assets[: self.params.top_k]]

    def _optimize_portfolio(self, prices, assets):
        """Apply portfolio optimization to selected assets"""
        if not self.optimizer or not assets:
            return None

        try:
            # Create price DataFrame for selected assets
            asset_prices = {}
            for asset in assets:
                if asset in prices:
                    asset_prices[asset] = prices[asset]

            if len(asset_prices) < 2:
                return None

            # Convert to DataFrame format expected by optimizer
            prices_df = pd.DataFrame([asset_prices])

            # Prepare data for optimizer
            self.optimizer.prepare_data(prices_df)

            # Try MVO optimization first
            weights, performance = self.optimizer.optimize_mvo(max_sharpe=True)

            if weights is not None:
                return weights

            # Fallback to HRP
            weights, performance = self.optimizer.optimize_hrp()

            if weights is not None:
                return weights

            # Final fallback to equal weight
            return self._equal_weight_fallback(assets)

        except Exception as e:
            print(f"Optimization failed: {e}")
            return self._equal_weight_fallback(assets)

    def _apply_risk_constraints(self, weights):
        """Apply risk management constraints"""
        if not weights:
            return {}

        # Apply position size constraints
        constrained_weights = {}
        for asset, weight in weights.items():
            constrained_weight = np.clip(
                weight, self.params.min_position, self.params.max_position
            )
            constrained_weights[asset] = constrained_weight

        # Renormalize weights
        total_weight = sum(constrained_weights.values())
        if total_weight > 0:
            for asset in constrained_weights:
                constrained_weights[asset] /= total_weight

        return constrained_weights

    def _execute_rebalancing(self, target_weights):
        """Execute portfolio rebalancing"""
        current_weights = self._get_current_weights()

        for asset, target_weight in target_weights.items():
            current_weight = current_weights.get(asset, 0)

            # Only trade if difference is significant (>1%)
            if abs(target_weight - current_weight) > 0.01:
                # Find the data feed for this asset
                data_feed = None
                for data in self.datas:
                    if data._name == asset:
                        data_feed = data
                        break

                if data_feed:
                    if target_weight > current_weight:
                        # Buy more
                        size = (
                            (target_weight - current_weight)
                            * self.broker.getvalue()
                            / data_feed.close[0]
                        )
                        self.buy(data=data_feed, size=size)
                    else:
                        # Sell some
                        size = (
                            (current_weight - target_weight)
                            * self.broker.getvalue()
                            / data_feed.close[0]
                        )
                        self.sell(data=data_feed, size=size)

    def _apply_equal_weights(self):
        """Apply equal weights as fallback"""
        if not self.datas:
            return

        equal_weight = 1.0 / len(self.datas)
        target_weights = {data._name: equal_weight for data in self.datas}

        # Apply risk constraints
        constrained_weights = self._apply_risk_constraints(target_weights)

        # Execute rebalancing
        self._execute_rebalancing(constrained_weights)

        # Log fallback
        self.log_optimization(
            self.data.datetime.date(),
            constrained_weights,
            {"method": "fallback"},
            "Equal Weight",
        )


class PortfolioAnalyzer(bt.Analyzer):
    """
    Custom analyzer for portfolio optimization results
    """

    def __init__(self):
        super().__init__()
        self.rets = {}  # Required by Backtrader

    def create_analysis(self):
        """Create comprehensive analysis"""
        if not hasattr(self.strategy, "optimization_history"):
            return {}

        analysis = {
            "optimization_history": self.strategy.optimization_history,
            "portfolio_metrics": self._calculate_portfolio_metrics(),
            "rebalancing_analysis": self._analyze_rebalancing(),
        }

        return analysis

    def _calculate_portfolio_metrics(self):
        """Calculate portfolio performance metrics"""
        # This would integrate with Backtrader's built-in analyzers
        return {}

    def _analyze_rebalancing(self):
        """Analyze rebalancing frequency and effectiveness"""
        if not hasattr(self.strategy, "optimization_history"):
            return {}

        history = self.strategy.optimization_history

        analysis = {
            "total_rebalances": len(history),
            "optimization_success_rate": 0,
            "method_distribution": {},
        }

        if history:
            # Calculate success rate
            successful_optimizations = sum(
                1 for h in history if h.get("method") == "MVO"
            )
            analysis["optimization_success_rate"] = successful_optimizations / len(
                history
            )

            # Method distribution
            for h in history:
                method = h.get("method", "Unknown")
                analysis["method_distribution"][method] = (
                    analysis["method_distribution"].get(method, 0) + 1
                )

        return analysis

    def get_analysis(self):
        """Return analysis results - required by Backtrader"""
        return self.create_analysis()


def create_backtrader_datafeeds(prices_df):
    """Convert pandas DataFrame to Backtrader DataFeeds"""
    datafeeds = []

    for col in prices_df.columns:
        # Create OHLCV data (using close price for all OHLC)
        data = bt.feeds.PandasData(
            dataname=prices_df[[col]],
            datetime=None,  # Use index as datetime
            open=col,
            high=col,
            low=col,
            close=col,
            volume=None,
            openinterest=None,
        )
        datafeeds.append(data)

    return datafeeds


def run_optimized_backtest(
    prices_df, strategy_class=OptimizedMomentumStrategy, **kwargs
):
    """
    Run a complete backtest with portfolio optimization

    Args:
        prices_df: DataFrame with asset prices
        strategy_class: Strategy class to use
        **kwargs: Strategy parameters
    """
    print("Setting up Backtrader backtest...")

    # Create Backtrader engine
    cerebro = bt.Cerebro()

    # Add data feeds
    datafeeds = create_backtrader_datafeeds(prices_df)
    for i, data in enumerate(datafeeds):
        cerebro.adddata(data, name=prices_df.columns[i])

    print(f"✓ Added {len(datafeeds)} data feeds")

    # Add strategy
    cerebro.addstrategy(strategy_class, **kwargs)

    # Add analyzers
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe")
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
    cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")
    cerebro.addanalyzer(PortfolioAnalyzer, _name="portfolio")

    print("✓ Added strategy and analyzers")

    # Set initial cash
    cerebro.broker.setcash(100000.0)

    # Set commission
    cerebro.broker.setcommission(commission=0.001)  # 0.1%

    print("✓ Set broker parameters")

    # Run backtest
    print("\nRunning backtest...")
    results = cerebro.run()
    strategy = results[0]

    print("✓ Backtest completed")

    # Extract results
    sharpe = strategy.analyzers.sharpe.get_analysis()
    drawdown = strategy.analyzers.drawdown.get_analysis()
    returns = strategy.analyzers.returns.get_analysis()
    trades = strategy.analyzers.trades.get_analysis()
    portfolio = strategy.analyzers.portfolio.get_analysis()

    # Print results
    print("\n=== BACKTEST RESULTS ===")
    print(f"Sharpe Ratio: {sharpe.get('sharperatio', 'N/A')}")
    print(f"Max Drawdown: {drawdown.get('max', {}).get('drawdown', 'N/A')}")
    print(f"Total Return: {returns.get('rtot', 'N/A')}")
    print(f"Number of Trades: {trades.get('total', {}).get('total', 'N/A')}")

    if portfolio:
        print(f"\n=== PORTFOLIO ANALYSIS ===")
        print(
            f"Total Rebalances: {portfolio.get('rebalancing_analysis', {}).get('total_rebalances', 'N/A')}"
        )
        print(
            f"Optimization Success Rate: {portfolio.get('rebalancing_analysis', {}).get('optimization_success_rate', 'N/A'):.2%}"
        )

        method_dist = portfolio.get("rebalancing_analysis", {}).get(
            "method_distribution", {}
        )
        if method_dist:
            print("Method Distribution:")
            for method, count in method_dist.items():
                print(f"  {method}: {count}")

    # Plot results
    try:
        cerebro.plot(style="candlestick", barup="green", bardown="red")
    except Exception as e:
        print(f"Plotting failed: {e}")

    return results, strategy


def demonstrate_integration():
    """Demonstrate the complete integration"""
    print("Backtrader Integration Demonstration")
    print("=" * 50)

    if not OPTIMIZER_AVAILABLE:
        print("✗ Cannot demonstrate integration - optimizer not available")
        return

    # Create sample data
    print("\n1. Creating sample data...")
    np.random.seed(42)
    dates = pd.date_range("2020-01-01", "2024-12-31", freq="D")
    n_assets = 5

    # Generate more realistic price data
    price_data = np.random.randn(len(dates), n_assets).cumsum(axis=0)
    prices = pd.DataFrame(
        price_data, index=dates, columns=[f"Asset_{i}" for i in range(n_assets)]
    )
    prices = prices + 100  # Start at 100

    print(f"✓ Generated {n_assets} assets, {len(dates)} days")

    # Run backtest
    print("\n2. Running optimized backtest...")
    try:
        results, strategy = run_optimized_backtest(
            prices,
            strategy_class=OptimizedMomentumStrategy,
            lookback=60,  # 60-day momentum
            top_k=3,  # Top 3 assets
            rebalance_freq=21,  # Monthly rebalancing
            risk_free_rate=0.02,
        )

        print("\n✓ Integration demonstration successful!")

        # Show optimization history
        if hasattr(strategy, "optimization_history"):
            print(
                f"\n3. Optimization History ({len(strategy.optimization_history)} rebalances):"
            )
            for i, opt in enumerate(strategy.optimization_history[-5:]):  # Last 5
                print(
                    f"  {opt['date']}: {opt['method']} - {len(opt['weights'])} assets"
                )

    except Exception as e:
        print(f"✗ Integration demonstration failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    demonstrate_integration()
