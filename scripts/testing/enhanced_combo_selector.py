#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced K-of-N Asset Combination Selector
==========================================

This enhanced version provides multiple usage levels for portfolio analysis:

Level 1: Basic Asset Selection
- Simple momentum-based selection
- Equal weighting
- Basic performance metrics

Level 2: Advanced Optimization
- Multiple weighting schemes
- Walk-forward training
- Transaction cost modeling
- Comprehensive risk metrics

Level 3: Portfolio Integration
- Integration with our portfolio optimization framework
- Risk parity and HRP methods
- Portfolio-level constraints
- Multi-objective optimization

Level 4: Production Portfolio Management
- Real-time portfolio monitoring
- Dynamic rebalancing
- Risk management alerts
- Performance attribution analysis

Usage Examples:
--------------
# Level 1: Basic selection
python enhanced_combo_selector.py --level 1 --tickers "SPY,TLT,GLD,EFA,IEF" --k 3

# Level 2: Advanced optimization
python enhanced_combo_selector.py --level 2 --tickers "SPY,TLT,GLD,EFA,IEF" --k 3 --weighting mvo --train_win 36

# Level 3: Portfolio integration
python enhanced_combo_selector.py --level 3 --tickers "SPY,TLT,GLD,EFA,IEF" --k 3 --method risk_parity --constraints

# Level 4: Production management
python enhanced_combo_selector.py --level 4 --tickers "SPY,TLT,GLD,EFA,IEF" --k 3 --monitor --alerts
"""

import argparse
import itertools
import math
import sys
import warnings
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

try:
    import yfinance as yf
except ImportError:
    raise SystemExit("Please install yfinance: pip install yfinance")

try:
    from tabulate import tabulate
except ImportError:
    tabulate = None

# Import our portfolio optimization framework
try:
    from portfolio_optimization_framework import PortfolioOptimizer

    OPTIMIZER_AVAILABLE = True
except ImportError:
    OPTIMIZER_AVAILABLE = False
    print(
        "Warning: Portfolio optimization framework not available. Level 3+ features disabled."
    )

# Import our core modules
try:
    from src.core.portfolio import Asset, Portfolio, PortfolioManager
    from src.core.strategy import (MomentumStrategy, StrategyManager,
                                   StrategyParameters, StrategyType)

    CORE_AVAILABLE = True
except ImportError:
    CORE_AVAILABLE = False
    print("Warning: Core modules not available. Level 4 features disabled.")


# ==================== UTILITY FUNCTIONS ====================


def _to_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
    """Convert index to datetime if needed"""
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    return df.sort_index()


def download_adj_close(
    tickers: List[str],
    start: Optional[str] = None,
    end: Optional[str] = None,
    interval: str = "1d",
) -> pd.DataFrame:
    """Download adjusted close prices via yfinance"""
    if not tickers:
        raise ValueError("No tickers provided.")

    data = yf.download(
        tickers=list(set(tickers)),
        start=start,
        end=end,
        auto_adjust=False,
        interval=interval,
        progress=False,
        threads=True,
        group_by="ticker",
    )

    # Build Adj Close wide table
    if isinstance(data.columns, pd.MultiIndex):
        out = {}
        for t in tickers:
            col = (t, "Adj Close")
            if col in data.columns:
                s = data[col].copy()
            else:
                # try lowercase for some locales
                s = data[(t, "Adj Close".lower())]
            s.name = t
            out[t] = s
        adj = pd.concat(out.values(), axis=1)
    else:
        # Single-index columns case: direct 'Adj Close'
        if "Adj Close" in data.columns:
            adj = data["Adj Close"].copy()
            # Ensure all requested tickers present
            missing = [t for t in tickers if t not in adj.columns]
            if missing:
                print("Warning: Missing tickers in download:", missing)
        else:
            raise RuntimeError(
                "Unexpected yfinance response format. No 'Adj Close' found."
            )

    adj = _to_datetime_index(adj)
    return adj


def to_period_prices(adj: pd.DataFrame, freq: str = "M") -> pd.DataFrame:
    """Resample to period-end prices"""
    return adj.resample(freq).last()


# ==================== PERFORMANCE METRICS ====================


def calculate_metrics(
    returns: pd.Series,
    weights: pd.DataFrame,
    asset_daily: Optional[pd.DataFrame] = None,
    tcost_bps: float = 5.0,
) -> Dict[str, float]:
    """Calculate comprehensive performance metrics"""
    if returns.empty:
        return {
            k: np.nan
            for k in [
                "CAGR",
                "AnnVol",
                "Sharpe",
                "Sortino",
                "MaxDD",
                "Calmar",
                "Ulcer",
                "VaR95",
                "CVaR95",
                "AvgPairCorr",
                "TurnoverAvg",
                "CostDrag",
                "InformationRatio",
            ]
        }

    # Basic metrics
    equity = (1.0 + returns).cumprod()
    periods_per_year = 12  # Monthly data

    # Return metrics
    cagr = ((equity.iloc[-1] / equity.iloc[0]) ** (periods_per_year / len(returns))) - 1
    vol = returns.std() * np.sqrt(periods_per_year)

    # Risk-adjusted metrics
    sharpe = (returns.mean() * periods_per_year) / vol if vol > 0 else np.nan
    sortino = (
        (returns.mean() * periods_per_year)
        / (returns[returns < 0].std() * np.sqrt(periods_per_year))
        if len(returns[returns < 0]) > 0
        else np.nan
    )

    # Drawdown metrics
    running_max = equity.expanding().max()
    drawdown = (equity - running_max) / running_max
    max_dd = drawdown.min()
    calmar = cagr / abs(max_dd) if max_dd < 0 else np.nan

    # Ulcer Index
    ulcer = np.sqrt(np.mean(np.square(drawdown * 100)))

    # Risk metrics
    var95 = returns.quantile(0.05)
    cvar95 = returns[returns <= var95].mean()

    # Correlation metrics
    if asset_daily is not None and not weights.empty:
        daily_combo = asset_daily[weights.columns].dropna(how="any")
        if daily_combo.shape[1] > 1:
            corr_matrix = daily_combo.pct_change().dropna().corr()
            # Get upper triangle of correlation matrix
            upper_tri = corr_matrix.where(
                np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
            )
            avg_corr = upper_tri.stack().mean()
        else:
            avg_corr = np.nan
    else:
        avg_corr = np.nan

    # Turnover and costs
    turnover = weights.diff().abs().sum(axis=1).mean() if not weights.empty else np.nan
    cost_drag = (tcost_bps / 10000) * turnover if not np.isnan(turnover) else np.nan

    # Information ratio (assuming 0% benchmark)
    information_ratio = returns.mean() / returns.std() if returns.std() > 0 else np.nan

    return {
        "CAGR": cagr,
        "AnnVol": vol,
        "Sharpe": sharpe,
        "Sortino": sortino,
        "MaxDD": max_dd,
        "Calmar": calmar,
        "Ulcer": ulcer,
        "VaR95": var95,
        "CVaR95": cvar95,
        "AvgPairCorr": avg_corr,
        "TurnoverAvg": turnover,
        "CostDrag": cost_drag,
        "InformationRatio": information_ratio,
    }


# ==================== WEIGHTING SCHEMES ====================


def equal_weights(assets: List[str]) -> pd.Series:
    """Equal weight allocation"""
    n = len(assets)
    if n == 0:
        return pd.Series(dtype=float)
    return pd.Series(1.0 / n, index=assets, dtype=float)


def inv_vol_weights(train_returns: pd.DataFrame, epsilon: float = 1e-8) -> pd.Series:
    """Inverse volatility weighting"""
    vols = train_returns.std(ddof=0).replace(0.0, np.nan)
    inv = 1.0 / vols
    inv = inv.replace([np.inf, -np.inf], np.nan).fillna(0.0)

    if inv.sum() == 0.0:
        return equal_weights(train_returns.columns)

    w = inv / inv.sum()
    return w


def mvo_weights(
    train_returns: pd.DataFrame,
    ridge: float = 1e-4,
    allow_negative: bool = False,
    wmax: float = 1.0,
) -> pd.Series:
    """Mean-variance optimization weights"""
    mu = train_returns.mean()
    Sigma = train_returns.cov()

    # Ridge for stability
    if ridge > 0:
        Sigma = Sigma + ridge * np.eye(Sigma.shape[0])

    try:
        invSigma = pd.DataFrame(
            np.linalg.inv(Sigma.values), index=Sigma.index, columns=Sigma.columns
        )
    except np.linalg.LinAlgError:
        # Fallback: use diagonal k*I
        invSigma = pd.DataFrame(
            np.eye(Sigma.shape[0]) / (Sigma.values.diagonal() + 1e-8),
            index=Sigma.index,
            columns=Sigma.columns,
        )

    raw = invSigma.dot(mu)
    if raw.abs().sum() == 0.0:
        w = equal_weights(train_returns.columns)
    else:
        w = raw / raw.abs().sum()  # Scale by L1 to control extremes

    if not allow_negative:
        w = w.clip(lower=0.0)

    # Cap and renormalize
    if wmax < 1.0:
        w = w.clip(upper=wmax)
    if w.sum() == 0.0:
        w = equal_weights(train_returns.columns)
    else:
        w = w / w.sum()

    return w


def risk_parity_weights(train_returns: pd.DataFrame) -> pd.Series:
    """Risk parity weighting using our framework if available"""
    if not OPTIMIZER_AVAILABLE:
        print(
            "Warning: Portfolio optimization framework not available. Using inverse volatility."
        )
        return inv_vol_weights(train_returns)

    try:
        optimizer = PortfolioOptimizer(risk_free_rate=0.02)
        optimizer.prepare_data(train_returns)
        weights, _ = optimizer.optimize_risk_parity()

        if weights is not None:
            return pd.Series(weights, index=train_returns.columns)
        else:
            return inv_vol_weights(train_returns)
    except Exception as e:
        print(f"Risk parity optimization failed: {e}. Using inverse volatility.")
        return inv_vol_weights(train_returns)


def hrp_weights(train_returns: pd.DataFrame) -> pd.Series:
    """Hierarchical Risk Parity weighting using our framework if available"""
    if not OPTIMIZER_AVAILABLE:
        print(
            "Warning: Portfolio optimization framework not available. Using inverse volatility."
        )
        return inv_vol_weights(train_returns)

    try:
        optimizer = PortfolioOptimizer(risk_free_rate=0.02)
        optimizer.prepare_data(train_returns)
        weights, _ = optimizer.optimize_hrp()

        if weights is not None:
            return pd.Series(weights, index=train_returns.columns)
        else:
            return inv_vol_weights(train_returns)
    except Exception as e:
        print(f"HRP optimization failed: {e}. Using inverse volatility.")
        return inv_vol_weights(train_returns)


# ==================== BACKTEST ENGINE ====================


@dataclass
class BacktestConfig:
    """Configuration for backtesting"""

    k: int
    weighting: str = "equal"  # "equal", "inv_vol", "mvo", "risk_parity", "hrp"
    rebalance: str = "M"  # "M" (monthly) or "Q" (quarterly)
    train_win: int = 36  # months of training window
    start: Optional[str] = None
    end: Optional[str] = None
    tcost_bps: float = 5.0
    objective: str = "sharpe"  # "sharpe", "calmar", "sortino", "composite"
    alpha_sharpe: float = 1.0  # composite weights
    beta_calmar: float = 0.5
    gamma_maxdd: float = 0.5  # penalty
    delta_corr: float = 0.5  # penalty
    periods_per_year: int = 12
    level: int = 2  # Usage level (1-4)
    constraints: bool = False  # Apply portfolio constraints
    monitor: bool = False  # Real-time monitoring
    alerts: bool = False  # Risk alerts


def compute_weights(
    method: str, assets: List[str], train_rets: pd.DataFrame, config: BacktestConfig
) -> pd.Series:
    """Compute weights based on method"""
    if method == "equal":
        return equal_weights(assets)
    elif method == "inv_vol":
        return inv_vol_weights(train_rets[assets])
    elif method == "mvo":
        return mvo_weights(
            train_rets[assets], ridge=1e-3, allow_negative=False, wmax=0.5
        )
    elif method == "risk_parity":
        return risk_parity_weights(train_rets[assets])
    elif method == "hrp":
        return hrp_weights(train_rets[assets])
    else:
        raise ValueError(f"Unknown weighting method: {method}")


def backtest_combo(
    prices_m: pd.DataFrame, combo: List[str], config: BacktestConfig
) -> Tuple[pd.Series, pd.DataFrame]:
    """Walk-forward backtest for a given combination"""
    # Use prices for combo; drop incomplete months
    pr = prices_m[list(combo)].dropna(how="any")

    if pr.shape[0] < config.train_win + 12:  # need at least train + 1 year
        return pd.Series(dtype=float), pd.DataFrame()

    rets = pr.pct_change().dropna(how="any")

    # Rebalance dates: use all months after we have at least train_win months
    dates = rets.index
    weights = pd.DataFrame(index=rets.index, columns=combo, data=0.0)

    prev_w = pd.Series(0.0, index=combo)
    first_idx = config.train_win  # first rebalance after initial training window

    for i in range(first_idx, len(dates)):
        dt = dates[i]

        # Determine last rebalance depending on cadence
        if config.rebalance == "Q":
            # rebalance on quarter ends (every 3 months)
            is_reb = dt.month in (3, 6, 9, 12)
        else:
            # monthly
            is_reb = True

        if is_reb:
            train_start = dates[i - config.train_win]
            train_end = dates[i - 1]
            train_slice = rets.loc[train_start:train_end]
            w = compute_weights(config.weighting, combo, train_slice, config)

            # Apply constraints if enabled
            if config.constraints and config.level >= 3:
                w = apply_portfolio_constraints(w, config)
        else:
            w = prev_w.copy()

        weights.loc[dt] = w.values
        prev_w = w

    # Shift weights to apply next-period returns (avoid look-ahead)
    weights = weights.shift(1).fillna(0.0)

    # Portfolio returns before costs
    port_rets_gross = (weights * rets).sum(axis=1)

    # Transaction costs via turnover each period
    weight_changes = weights.diff().abs().sum(axis=1).fillna(0.0)
    costs = (config.tcost_bps / 10000) * weight_changes
    port_rets_net = port_rets_gross - costs

    return port_rets_net, weights


def apply_portfolio_constraints(
    weights: pd.Series, config: BacktestConfig
) -> pd.Series:
    """Apply portfolio-level constraints"""
    if not config.constraints:
        return weights

    # Maximum position size
    max_position = 0.4  # 40% max per asset

    # Minimum position size
    min_position = 0.05  # 5% min per asset

    # Apply constraints
    constrained_weights = weights.clip(lower=min_position, upper=max_position)

    # Renormalize
    total_weight = constrained_weights.sum()
    if total_weight > 0:
        constrained_weights = constrained_weights / total_weight

    return constrained_weights


# ==================== LEVEL-SPECIFIC FEATURES ====================


class Level1Analyzer:
    """Basic asset selection and analysis"""

    def __init__(self, config: BacktestConfig):
        self.config = config

    def analyze(self, prices: pd.DataFrame, combo: List[str]) -> Dict[str, Any]:
        """Basic analysis for Level 1"""
        # Simple momentum-based selection
        lookback = 12  # 12-month momentum
        momentum_scores = {}

        for asset in combo:
            if len(prices[asset]) >= lookback:
                current_price = prices[asset].iloc[-1]
                lookback_price = prices[asset].iloc[-lookback]
                momentum = (current_price - lookback_price) / lookback_price
                momentum_scores[asset] = momentum

        # Select top assets by momentum
        sorted_assets = sorted(
            momentum_scores.items(), key=lambda x: x[1], reverse=True
        )
        selected = [asset for asset, _ in sorted_assets[: self.config.k]]

        # Equal weights
        weights = equal_weights(selected)

        return {
            "selected_assets": selected,
            "weights": weights,
            "momentum_scores": momentum_scores,
            "analysis_level": "Basic momentum selection with equal weighting",
        }


class Level2Analyzer:
    """Advanced optimization and backtesting"""

    def __init__(self, config: BacktestConfig):
        self.config = config

    def analyze(self, prices: pd.DataFrame, combo: List[str]) -> Dict[str, Any]:
        """Advanced analysis for Level 2"""
        # Run full backtest
        returns, weights = backtest_combo(prices, combo, self.config)

        if returns.empty:
            return {"error": "Insufficient data for backtest"}

        # Calculate comprehensive metrics
        metrics = calculate_metrics(returns, weights, prices, self.config.tcost_bps)

        # Calculate additional statistics
        equity_curve = (1 + returns).cumprod()
        rolling_sharpe = calculate_rolling_sharpe(returns, window=12)

        return {
            "returns": returns,
            "weights": weights,
            "equity_curve": equity_curve,
            "metrics": metrics,
            "rolling_sharpe": rolling_sharpe,
            "analysis_level": "Advanced optimization with walk-forward training",
        }


class Level3Analyzer:
    """Portfolio integration and advanced optimization"""

    def __init__(self, config: BacktestConfig):
        self.config = config
        if not OPTIMIZER_AVAILABLE:
            raise ValueError("Portfolio optimization framework required for Level 3")

    def analyze(self, prices: pd.DataFrame, combo: List[str]) -> Dict[str, Any]:
        """Portfolio integration analysis for Level 3"""
        # Create portfolio optimizer
        optimizer = PortfolioOptimizer(risk_free_rate=0.02)
        optimizer.prepare_data(prices[combo])

        # Run multiple optimization methods
        results = {}

        # MVO optimization
        try:
            mvo_weights, mvo_perf = optimizer.optimize_mvo(max_sharpe=True)
            if mvo_weights is not None:
                results["mvo"] = {"weights": mvo_weights, "performance": mvo_perf}
        except Exception as e:
            print(f"MVO optimization failed: {e}")

        # HRP optimization
        try:
            hrp_weights, hrp_perf = optimizer.optimize_hrp()
            if hrp_weights is not None:
                results["hrp"] = {"weights": hrp_weights, "performance": hrp_perf}
        except Exception as e:
            print(f"HRP optimization failed: {e}")

        # Risk parity (if available)
        try:
            # Use inverse volatility as approximation for risk parity
            rp_weights = inv_vol_weights(prices[combo])
            if rp_weights is not None:
                results["risk_parity"] = {
                    "weights": rp_weights,
                    "performance": "Inverse volatility approximation",
                }
        except Exception as e:
            print(f"Risk parity optimization failed: {e}")

        # Compare methods
        comparison = compare_optimization_methods(results, prices[combo])

        return {
            "optimization_results": results,
            "comparison": comparison,
            "analysis_level": "Portfolio integration with multiple optimization methods",
        }


class Level4Analyzer:
    """Production portfolio management"""

    def __init__(self, config: BacktestConfig):
        self.config = config
        if not CORE_AVAILABLE:
            raise ValueError("Core modules required for Level 4")

    def analyze(self, prices: pd.DataFrame, combo: List[str]) -> Dict[str, Any]:
        """Production analysis for Level 4"""
        # Create portfolio
        portfolio_manager = PortfolioManager()
        portfolio = portfolio_manager.create_portfolio(
            name="KofN_Portfolio",
            description=f"K-of-N portfolio with {len(combo)} assets",
        )

        # Create assets
        assets = {}
        for symbol in combo:
            asset = Asset(
                symbol=symbol, name=symbol, asset_type="etf", sector="diversified"
            )
            assets[symbol] = asset

        # Run backtest with portfolio tracking
        returns, weights = backtest_combo(prices, combo, self.config)

        if returns.empty:
            return {"error": "Insufficient data for backtest"}

        # Simulate portfolio positions
        portfolio_history = simulate_portfolio_positions(
            portfolio, assets, weights, prices
        )

        # Calculate advanced metrics
        metrics = calculate_metrics(returns, weights, prices, self.config.tcost_bps)

        # Risk monitoring
        risk_alerts = generate_risk_alerts(returns, weights, metrics)

        # Performance attribution
        attribution = calculate_performance_attribution(returns, weights, prices[combo])

        return {
            "portfolio": portfolio,
            "portfolio_history": portfolio_history,
            "metrics": metrics,
            "risk_alerts": risk_alerts,
            "attribution": attribution,
            "analysis_level": "Production portfolio management with real-time monitoring",
        }


# ==================== HELPER FUNCTIONS ====================


def calculate_rolling_sharpe(returns: pd.Series, window: int = 12) -> pd.Series:
    """Calculate rolling Sharpe ratio"""
    if len(returns) < window:
        return pd.Series(dtype=float)

    rolling_mean = returns.rolling(window=window).mean() * 12
    rolling_std = returns.rolling(window=window).std() * np.sqrt(12)
    rolling_sharpe = rolling_mean / rolling_std

    return rolling_sharpe


def compare_optimization_methods(
    results: Dict[str, Any], prices: pd.DataFrame
) -> pd.DataFrame:
    """Compare different optimization methods"""
    comparison_data = []

    for method, result in results.items():
        if "weights" in result and "performance" in result:
            weights = result["weights"]
            perf = result["performance"]

            # Calculate portfolio metrics
            if isinstance(weights, dict):
                weight_series = pd.Series(weights)
            else:
                weight_series = pd.Series(weights, index=prices.columns)

            # Simulate returns
            returns = (prices * weight_series).sum(axis=1).pct_change().dropna()

            # Calculate metrics
            metrics = calculate_metrics(returns, pd.DataFrame(weight_series).T)

            comparison_data.append(
                {
                    "Method": method,
                    "Sharpe": metrics.get("Sharpe", np.nan),
                    "Sortino": metrics.get("Sortino", np.nan),
                    "MaxDD": metrics.get("MaxDD", np.nan),
                    "Calmar": metrics.get("Calmar", np.nan),
                    "Volatility": metrics.get("AnnVol", np.nan),
                    "CAGR": metrics.get("CAGR", np.nan),
                }
            )

    return pd.DataFrame(comparison_data)


def simulate_portfolio_positions(
    portfolio, assets: Dict[str, Any], weights: pd.DataFrame, prices: pd.DataFrame
) -> List[Dict]:
    """Simulate portfolio positions over time"""
    portfolio_history = []

    for date in weights.index:
        # Update portfolio with current weights
        total_value = 100000  # Starting value

        for symbol, weight in weights.loc[date].items():
            if weight > 0 and symbol in assets:
                asset = assets[symbol]
                price = prices.loc[date, symbol]
                quantity = (weight * total_value) / price

                # Add position to portfolio
                portfolio.add_position(asset, quantity, price)

        # Update prices
        current_prices = {
            symbol: prices.loc[date, symbol] for symbol in weights.columns
        }
        portfolio.update_prices(current_prices)

        # Record portfolio state
        portfolio_history.append(
            {
                "date": date,
                "total_value": portfolio.total_market_value,
                "positions": len(portfolio.positions),
                "weights": portfolio.get_weights(),
                "unrealized_pnl": portfolio.total_unrealized_pnl,
            }
        )

    return portfolio_history


def generate_risk_alerts(
    returns: pd.Series, weights: pd.DataFrame, metrics: Dict[str, float]
) -> List[Dict]:
    """Generate risk alerts based on portfolio metrics"""
    alerts = []

    # Volatility alert
    if metrics.get("AnnVol", 0) > 0.20:  # 20% annual volatility
        alerts.append(
            {
                "type": "HIGH_VOLATILITY",
                "severity": "WARNING",
                "message": f"Portfolio volatility ({metrics['AnnVol']:.1%}) exceeds 20% threshold",
            }
        )

    # Drawdown alert
    if metrics.get("MaxDD", 0) < -0.15:  # -15% max drawdown
        alerts.append(
            {
                "type": "HIGH_DRAWDOWN",
                "severity": "CRITICAL",
                "message": f"Maximum drawdown ({metrics['MaxDD']:.1%}) exceeds -15% threshold",
            }
        )

    # Sharpe ratio alert
    if metrics.get("Sharpe", 0) < 0.5:  # Sharpe ratio below 0.5
        alerts.append(
            {
                "type": "LOW_SHARPE",
                "severity": "WARNING",
                "message": f"Sharpe ratio ({metrics['Sharpe']:.2f}) below 0.5 threshold",
            }
        )

    return alerts


def calculate_performance_attribution(
    returns: pd.Series, weights: pd.DataFrame, asset_prices: pd.DataFrame
) -> Dict[str, Any]:
    """Calculate performance attribution analysis"""
    if returns.empty or weights.empty:
        return {}

    # Calculate asset contributions
    asset_contributions = {}
    for asset in weights.columns:
        asset_returns = asset_prices[asset].pct_change().dropna()
        asset_weights = weights[asset].dropna()

        # Align indices
        common_idx = asset_returns.index.intersection(asset_weights.index)
        if len(common_idx) > 0:
            contribution = (
                asset_returns.loc[common_idx] * asset_weights.loc[common_idx]
            ).sum()
            asset_contributions[asset] = contribution

    # Calculate sector allocation (if available)
    sector_allocation = {}
    # This would require sector information for assets

    return {
        "asset_contributions": asset_contributions,
        "sector_allocation": sector_allocation,
        "total_return": returns.sum(),
        "excess_return": returns.sum()
        - (0.02 / 12 * len(returns)),  # Assuming 2% risk-free rate
    }


# ==================== MAIN RUNNER ====================


def run_analysis(config: BacktestConfig, tickers: List[str]) -> None:
    """Run the analysis based on the specified level"""
    print(f"Running Level {config.level} Analysis")
    print("=" * 50)
    print(f"Tickers (N={len(tickers)}): {', '.join(tickers)}")
    print(f"Target combination size (K): {config.k}")
    print(f"Weighting method: {config.weighting}")
    print(f"Rebalancing: {config.rebalance}")

    if config.k < 1 or config.k > len(tickers):
        raise SystemExit(f"--k must be between 1 and N={len(tickers)}")

    # Download data
    print("\nDownloading data...")
    daily = download_adj_close(
        tickers, start=config.start, end=config.end, interval="1d"
    )

    # Drop tickers with too little data
    min_daily = 252 * 3  # ~3 years minimum
    keep = [
        t for t in tickers if t in daily.columns and daily[t].notna().sum() >= min_daily
    ]

    if len(keep) < config.k:
        raise SystemExit(
            "Not enough tickers with sufficient history for the requested K."
        )

    if len(keep) < len(tickers):
        dropped = [t for t in tickers if t not in keep]
        print(f"Dropping due to insufficient history: {dropped}")

    daily = daily[keep]
    prices_m = to_period_prices(daily, "M").dropna(how="any")

    # Evaluate combinations based on level
    if config.level == 1:
        analyzer = Level1Analyzer(config)
        results = analyzer.analyze(prices_m, keep)
        print_level1_results(results)

    elif config.level == 2:
        analyzer = Level2Analyzer(config)
        results = analyzer.analyze(prices_m, keep)
        print_level2_results(results)

    elif config.level == 3:
        if not OPTIMIZER_AVAILABLE:
            print(
                "Warning: Portfolio optimization framework not available. Falling back to Level 2."
            )
            config.level = 2
            analyzer = Level2Analyzer(config)
            results = analyzer.analyze(prices_m, keep)
            print_level2_results(results)
        else:
            analyzer = Level3Analyzer(config)
            results = analyzer.analyze(prices_m, keep)
            print_level3_results(results)

    elif config.level == 4:
        if not CORE_AVAILABLE:
            print("Warning: Core modules not available. Falling back to Level 3.")
            config.level = 3
            analyzer = Level3Analyzer(config)
            results = analyzer.analyze(prices_m, keep)
            print_level3_results(results)
        else:
            analyzer = Level4Analyzer(config)
            results = analyzer.analyze(prices_m, keep)
            print_level4_results(results)

    else:
        raise ValueError(f"Invalid level: {config.level}. Must be 1-4.")


def print_level1_results(results: Dict[str, Any]):
    """Print Level 1 results"""
    print("\n=== LEVEL 1 RESULTS ===")
    print(f"Selected Assets: {', '.join(results['selected_assets'])}")
    print(f"Analysis: {results['analysis_level']}")

    print("\nWeights:")
    for asset, weight in results["weights"].items():
        print(f"  {asset}: {weight:.1%}")

    if "momentum_scores" in results:
        print("\nMomentum Scores:")
        for asset, score in results["momentum_scores"].items():
            print(f"  {asset}: {score:.2%}")


def print_level2_results(results: Dict[str, Any]):
    """Print Level 2 results"""
    print("\n=== LEVEL 2 RESULTS ===")
    print(f"Analysis: {results['analysis_level']}")

    if "error" in results:
        print(f"Error: {results['error']}")
        return

    metrics = results["metrics"]
    print(f"\nPerformance Metrics:")
    print(f"  CAGR: {metrics.get('CAGR', 'N/A'):.2%}")
    print(f"  Annual Volatility: {metrics.get('AnnVol', 'N/A'):.2%}")
    print(f"  Sharpe Ratio: {metrics.get('Sharpe', 'N/A'):.2f}")
    print(f"  Sortino Ratio: {metrics.get('Sortino', 'N/A'):.2f}")
    print(f"  Max Drawdown: {metrics.get('MaxDD', 'N/A'):.2%}")
    print(f"  Calmar Ratio: {metrics.get('Calmar', 'N/A'):.2f}")
    print(f"  Ulcer Index: {metrics.get('Ulcer', 'N/A'):.2f}")
    print(f"  VaR (95%): {metrics.get('VaR95', 'N/A'):.2%}")
    print(f"  CVaR (95%): {metrics.get('CVaR95', 'N/A'):.2%}")
    print(f"  Avg Pairwise Correlation: {metrics.get('AvgPairCorr', 'N/A'):.2f}")
    print(f"  Average Turnover: {metrics.get('TurnoverAvg', 'N/A'):.2%}")
    print(f"  Cost Drag: {metrics.get('CostDrag', 'N/A'):.2%}")


def print_level3_results(results: Dict[str, Any]):
    """Print Level 3 results"""
    print("\n=== LEVEL 3 RESULTS ===")
    print(f"Analysis: {results['analysis_level']}")

    if "comparison" in results and not results["comparison"].empty:
        print("\nOptimization Method Comparison:")
        if tabulate:
            print(
                tabulate(
                    results["comparison"],
                    headers="keys",
                    tablefmt="github",
                    floatfmt=".4f",
                )
            )
        else:
            print(
                results["comparison"].to_string(
                    index=False, float_format=lambda x: f"{x:.4f}"
                )
            )


def print_level4_results(results: Dict[str, Any]):
    """Print Level 4 results"""
    print("\n=== LEVEL 4 RESULTS ===")
    print(f"Analysis: {results['analysis_level']}")

    if "portfolio" in results:
        portfolio = results["portfolio"]
        print(f"\nPortfolio: {portfolio.name}")
        print(f"Total Value: ${portfolio.total_market_value:,.2f}")
        print(f"Positions: {len(portfolio.positions)}")

    if "risk_alerts" in results and results["risk_alerts"]:
        print("\nRisk Alerts:")
        for alert in results["risk_alerts"]:
            severity_icon = "🚨" if alert["severity"] == "CRITICAL" else "⚠️"
            print(f"  {severity_icon} {alert['type']}: {alert['message']}")

    if "attribution" in results:
        attribution = results["attribution"]
        if "asset_contributions" in attribution:
            print("\nPerformance Attribution:")
            for asset, contribution in attribution["asset_contributions"].items():
                print(f"  {asset}: {contribution:.2%}")


def parse_args() -> Tuple[BacktestConfig, List[str]]:
    """Parse command line arguments"""
    ap = argparse.ArgumentParser(
        description="Enhanced K-of-N Asset Combination Selector"
    )

    # Level selection
    ap.add_argument(
        "--level",
        type=int,
        choices=[1, 2, 3, 4],
        default=2,
        help="Analysis level (1=Basic, 2=Advanced, 3=Portfolio, 4=Production)",
    )

    # Universe
    g = ap.add_argument_group("Universe")
    g.add_argument(
        "--tickers",
        type=str,
        default=None,
        help="Comma-separated list of tickers (e.g., 'SPY,TLT,GLD,EFA,IEF')",
    )
    g.add_argument(
        "--tickers_file",
        type=str,
        default=None,
        help="Path to a file with one ticker per line",
    )

    # Backtest
    h = ap.add_argument_group("Backtest")
    h.add_argument(
        "--k", type=int, required=True, help="Number of assets per combination"
    )
    h.add_argument("--start", type=str, default=None, help="Start date (YYYY-MM-DD)")
    h.add_argument("--end", type=str, default=None, help="End date (YYYY-MM-DD)")
    h.add_argument(
        "--rebalance",
        type=str,
        choices=["M", "Q"],
        default="M",
        help="Rebalance cadence: M or Q",
    )
    h.add_argument(
        "--tcost_bps",
        type=float,
        default=5.0,
        help="Transaction cost per side in basis points",
    )

    # Weighting & Training
    w = ap.add_argument_group("Weighting & Training")
    w.add_argument(
        "--weighting",
        type=str,
        choices=["equal", "inv_vol", "mvo", "risk_parity", "hrp"],
        default="equal",
        help="Weighting scheme",
    )
    w.add_argument(
        "--train_win",
        type=int,
        default=36,
        help="Training window in months for optimization methods",
    )

    # Objective
    o = ap.add_argument_group("Objective")
    o.add_argument(
        "--objective",
        type=str,
        choices=["sharpe", "calmar", "sortino", "composite"],
        default="sharpe",
        help="Selection objective",
    )
    o.add_argument(
        "--alpha_sharpe", type=float, default=1.0, help="Composite: weight on Sharpe"
    )
    o.add_argument(
        "--beta_calmar", type=float, default=0.5, help="Composite: weight on Calmar"
    )
    o.add_argument(
        "--gamma_maxdd", type=float, default=0.5, help="Composite: penalty on |MaxDD|"
    )
    o.add_argument(
        "--delta_corr",
        type=float,
        default=0.5,
        help="Composite: penalty on AvgPairCorr",
    )

    # Advanced features
    a = ap.add_argument_group("Advanced Features")
    a.add_argument(
        "--constraints",
        action="store_true",
        help="Apply portfolio constraints (Level 3+)",
    )
    a.add_argument(
        "--monitor", action="store_true", help="Enable real-time monitoring (Level 4)"
    )
    a.add_argument("--alerts", action="store_true", help="Enable risk alerts (Level 4)")

    args = ap.parse_args()

    # Collect tickers
    tickers: List[str] = []
    if args.tickers:
        tickers += [t.strip() for t in args.tickers.split(",") if t.strip()]
    if args.tickers_file:
        with open(args.tickers_file, "r", encoding="utf-8") as f:
            tickers += [line.strip() for line in f if line.strip()]

    tickers = list(dict.fromkeys(tickers))  # de-duplicate preserving order
    if not tickers:
        raise SystemExit("Provide --tickers or --tickers_file.")

    # Create config
    config = BacktestConfig(
        k=args.k,
        weighting=args.weighting,
        rebalance=args.rebalance,
        train_win=args.train_win,
        start=args.start,
        end=args.end,
        tcost_bps=args.tcost_bps,
        objective=args.objective,
        alpha_sharpe=args.alpha_sharpe,
        beta_calmar=args.beta_calmar,
        gamma_maxdd=args.gamma_maxdd,
        delta_corr=args.delta_corr,
        level=args.level,
        constraints=args.constraints,
        monitor=args.monitor,
        alerts=args.alerts,
    )

    return config, tickers


if __name__ == "__main__":
    config, tickers = parse_args()
    run_analysis(config, tickers)
