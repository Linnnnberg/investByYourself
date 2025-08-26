#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core Strategy Management Module

This module provides the core strategy management functionality including
strategy definition, execution, and performance tracking.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd


class StrategyType(Enum):
    """Types of trading strategies"""

    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    ARBITRAGE = "arbitrage"
    FACTOR_MODEL = "factor_model"
    MACHINE_LEARNING = "machine_learning"
    CUSTOM = "custom"


class StrategyStatus(Enum):
    """Strategy execution status"""

    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class StrategyParameters:
    """Strategy parameters and configuration"""

    name: str
    description: str = ""
    strategy_type: StrategyType = StrategyType.CUSTOM
    lookback_period: int = 20
    rebalance_frequency: str = "daily"  # daily, weekly, monthly
    max_positions: int = 10
    position_size: float = 0.1  # 10% per position
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    risk_free_rate: float = 0.02
    transaction_costs: float = 0.001  # 0.1%

    def __post_init__(self):
        """Validate parameters after initialization"""
        if self.lookback_period <= 0:
            raise ValueError("Lookback period must be positive")
        if self.max_positions <= 0:
            raise ValueError("Max positions must be positive")
        if not 0 < self.position_size <= 1:
            raise ValueError("Position size must be between 0 and 1")
        if self.risk_free_rate < 0:
            raise ValueError("Risk-free rate cannot be negative")
        if self.transaction_costs < 0:
            raise ValueError("Transaction costs cannot be negative")


@dataclass
class Trade:
    """Represents a trade execution"""

    symbol: str
    side: str  # buy, sell
    quantity: float
    price: float
    timestamp: datetime
    strategy_name: str
    trade_id: Optional[str] = None
    commission: float = 0.0
    slippage: float = 0.0

    @property
    def total_cost(self) -> float:
        """Calculate total cost including commission and slippage"""
        base_cost = self.quantity * self.price
        return base_cost + self.commission + self.slippage

    @property
    def trade_value(self) -> float:
        """Calculate trade value"""
        return self.quantity * self.price


@dataclass
class StrategyPerformance:
    """Strategy performance metrics"""

    strategy_name: str
    start_date: datetime
    end_date: datetime
    total_return: float = 0.0
    annualized_return: float = 0.0
    volatility: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    average_win: float = 0.0
    average_loss: float = 0.0
    largest_win: float = 0.0
    largest_loss: float = 0.0

    def calculate_metrics(self, returns: pd.Series, trades: List[Trade]) -> None:
        """Calculate performance metrics from returns and trades"""
        if returns.empty:
            return

        # Basic return metrics
        self.total_return = (
            (returns.iloc[-1] / returns.iloc[0]) - 1 if len(returns) > 1 else 0
        )

        # Annualized return
        days = (self.end_date - self.start_date).days
        if days > 0:
            self.annualized_return = ((1 + self.total_return) ** (365 / days)) - 1

        # Volatility
        self.volatility = (
            returns.pct_change().std() * np.sqrt(252) if len(returns) > 1 else 0
        )

        # Sharpe ratio
        if self.volatility > 0:
            excess_returns = returns.pct_change() - (self.risk_free_rate / 252)
            self.sharpe_ratio = (excess_returns.mean() * 252) / self.volatility

        # Drawdown
        cumulative = (1 + returns.pct_change()).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        self.max_drawdown = drawdown.min()

        # Trade metrics
        if trades:
            self.total_trades = len(trades)
            winning_trades = [t for t in trades if t.side == "sell" and t.price > 0]
            losing_trades = [t for t in trades if t.side == "sell" and t.price < 0]

            self.winning_trades = len(winning_trades)
            self.losing_trades = len(losing_trades)

            if self.total_trades > 0:
                self.win_rate = self.winning_trades / self.total_trades

            if winning_trades:
                self.average_win = np.mean([t.price for t in winning_trades])
                self.largest_win = max([t.price for t in winning_trades])

            if losing_trades:
                self.average_loss = np.mean([t.price for t in losing_trades])
                self.largest_loss = min([t.price for t in losing_trades])

            if self.average_loss != 0:
                self.profit_factor = abs(self.average_win / self.average_loss)


class BaseStrategy(ABC):
    """Base class for all trading strategies"""

    def __init__(self, parameters: StrategyParameters):
        self.parameters = parameters
        self.status = StrategyStatus.STOPPED
        self.positions: Dict[str, float] = {}
        self.trades: List[Trade] = []
        self.performance: Optional[StrategyPerformance] = None
        self.start_date: Optional[datetime] = None
        self.last_rebalance: Optional[datetime] = None

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> Dict[str, float]:
        """Generate trading signals from market data"""
        pass

    @abstractmethod
    def calculate_position_sizes(
        self, signals: Dict[str, float], portfolio_value: float
    ) -> Dict[str, float]:
        """Calculate position sizes based on signals and portfolio value"""
        pass

    def execute_trades(
        self, target_positions: Dict[str, float], current_prices: Dict[str, float]
    ) -> List[Trade]:
        """Execute trades to achieve target positions"""
        trades = []

        for symbol, target_size in target_positions.items():
            current_size = self.positions.get(symbol, 0)
            target_quantity = target_size / current_prices.get(symbol, 1)

            if abs(target_quantity - current_size) > 0.001:  # Minimum trade threshold
                if target_quantity > current_size:
                    # Buy
                    trade = Trade(
                        symbol=symbol,
                        side="buy",
                        quantity=target_quantity - current_size,
                        price=current_prices.get(symbol, 0),
                        timestamp=datetime.now(),
                        strategy_name=self.parameters.name,
                    )
                    trades.append(trade)
                else:
                    # Sell
                    trade = Trade(
                        symbol=symbol,
                        side="sell",
                        quantity=current_size - target_quantity,
                        price=current_prices.get(symbol, 0),
                        timestamp=datetime.now(),
                        strategy_name=self.parameters.name,
                    )
                    trades.append(trade)

        return trades

    def update_positions(self, trades: List[Trade]) -> None:
        """Update current positions based on executed trades"""
        for trade in trades:
            if trade.symbol not in self.positions:
                self.positions[trade.symbol] = 0

            if trade.side == "buy":
                self.positions[trade.symbol] += trade.quantity
            else:
                self.positions[trade.symbol] -= trade.quantity

            # Remove zero positions
            if abs(self.positions[trade.symbol]) < 0.001:
                del self.positions[trade.symbol]

    def start(self, start_date: datetime) -> None:
        """Start strategy execution"""
        self.status = StrategyStatus.ACTIVE
        self.start_date = start_date
        self.last_rebalance = start_date

    def stop(self) -> None:
        """Stop strategy execution"""
        self.status = StrategyStatus.STOPPED

    def pause(self) -> None:
        """Pause strategy execution"""
        self.status = StrategyStatus.PAUSED

    def is_active(self) -> bool:
        """Check if strategy is active"""
        return self.status == StrategyStatus.ACTIVE

    def should_rebalance(self, current_date: datetime) -> bool:
        """Check if strategy should rebalance"""
        if not self.last_rebalance:
            return True

        if self.parameters.rebalance_frequency == "daily":
            return (current_date - self.last_rebalance).days >= 1
        elif self.parameters.rebalance_frequency == "weekly":
            return (current_date - self.last_rebalance).days >= 7
        elif self.parameters.rebalance_frequency == "monthly":
            return (current_date - self.last_rebalance).days >= 30

        return False

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get strategy performance summary"""
        if not self.performance:
            return {}

        return {
            "Strategy Name": self.performance.strategy_name,
            "Status": self.status.value,
            "Total Return": f"{self.performance.total_return:.2%}",
            "Annualized Return": f"{self.performance.annualized_return:.2%}",
            "Sharpe Ratio": f"{self.performance.sharpe_ratio:.2f}",
            "Max Drawdown": f"{self.performance.max_drawdown:.2%}",
            "Win Rate": f"{self.performance.win_rate:.2%}",
            "Total Trades": self.performance.total_trades,
            "Current Positions": len(self.positions),
        }


class MomentumStrategy(BaseStrategy):
    """Momentum-based trading strategy"""

    def __init__(self, parameters: StrategyParameters):
        super().__init__(parameters)
        if parameters.strategy_type != StrategyType.MOMENTUM:
            raise ValueError("MomentumStrategy requires MOMENTUM strategy type")

    def generate_signals(self, data: pd.DataFrame) -> Dict[str, float]:
        """Generate momentum signals"""
        signals = {}

        for column in data.columns:
            if len(data[column]) >= self.parameters.lookback_period:
                # Calculate momentum (price change over lookback period)
                current_price = data[column].iloc[-1]
                lookback_price = data[column].iloc[-self.parameters.lookback_period]
                momentum = (current_price - lookback_price) / lookback_price
                signals[column] = momentum

        return signals

    def calculate_position_sizes(
        self, signals: Dict[str, float], portfolio_value: float
    ) -> Dict[str, float]:
        """Calculate position sizes based on momentum signals"""
        if not signals:
            return {}

        # Sort signals by momentum (highest first)
        sorted_signals = sorted(signals.items(), key=lambda x: x[1], reverse=True)

        # Select top assets up to max_positions
        selected_assets = sorted_signals[: self.parameters.max_positions]

        # Calculate position sizes (equal weight among selected assets)
        position_size = self.parameters.position_size / len(selected_assets)

        target_positions = {}
        for symbol, _ in selected_assets:
            target_positions[symbol] = position_size * portfolio_value

        return target_positions


class MeanReversionStrategy(BaseStrategy):
    """Mean reversion trading strategy"""

    def __init__(self, parameters: StrategyParameters):
        super().__init__(parameters)
        if parameters.strategy_type != StrategyType.MEAN_REVERSION:
            raise ValueError(
                "MeanReversionStrategy requires MEAN_REVERSION strategy type"
            )

    def generate_signals(self, data: pd.DataFrame) -> Dict[str, float]:
        """Generate mean reversion signals"""
        signals = {}

        for column in data.columns:
            if len(data[column]) >= self.parameters.lookback_period:
                # Calculate z-score (deviation from mean)
                prices = data[column].iloc[-self.parameters.lookback_period :]
                mean_price = prices.mean()
                std_price = prices.std()

                if std_price > 0:
                    current_price = data[column].iloc[-1]
                    z_score = (current_price - mean_price) / std_price
                    # Negative z-score means price is below mean (buy signal)
                    signals[column] = -z_score

        return signals

    def calculate_position_sizes(
        self, signals: Dict[str, float], portfolio_value: float
    ) -> Dict[str, float]:
        """Calculate position sizes based on mean reversion signals"""
        if not signals:
            return {}

        # Sort signals by z-score (lowest first for mean reversion)
        sorted_signals = sorted(signals.items(), key=lambda x: x[1])

        # Select assets with strongest mean reversion signals
        selected_assets = sorted_signals[: self.parameters.max_positions]

        # Calculate position sizes (equal weight among selected assets)
        position_size = self.parameters.position_size / len(selected_assets)

        target_positions = {}
        for symbol, _ in selected_assets:
            target_positions[symbol] = position_size * portfolio_value

        return target_positions


class StrategyManager:
    """Manages multiple strategies"""

    def __init__(self):
        self.strategies: Dict[str, BaseStrategy] = {}

    def add_strategy(self, strategy: BaseStrategy) -> None:
        """Add a strategy to the manager"""
        if strategy.parameters.name in self.strategies:
            raise ValueError(f"Strategy {strategy.parameters.name} already exists")

        self.strategies[strategy.parameters.name] = strategy

    def get_strategy(self, name: str) -> BaseStrategy:
        """Get a strategy by name"""
        if name not in self.strategies:
            raise ValueError(f"Strategy {name} not found")
        return self.strategies[name]

    def remove_strategy(self, name: str) -> None:
        """Remove a strategy"""
        if name not in self.strategies:
            raise ValueError(f"Strategy {name} not found")
        del self.strategies[name]

    def list_strategies(self) -> List[str]:
        """List all strategy names"""
        return list(self.strategies.keys())

    def get_strategy_summary(self) -> pd.DataFrame:
        """Get summary of all strategies"""
        if not self.strategies:
            return pd.DataFrame()

        data = []
        for strategy in self.strategies.values():
            data.append(strategy.get_performance_summary())

        return pd.DataFrame(data)

    def start_all_strategies(self, start_date: datetime) -> None:
        """Start all strategies"""
        for strategy in self.strategies.values():
            strategy.start(start_date)

    def stop_all_strategies(self) -> None:
        """Stop all strategies"""
        for strategy in self.strategies.values():
            strategy.stop()

    def get_active_strategies(self) -> List[BaseStrategy]:
        """Get list of active strategies"""
        return [s for s in self.strategies.values() if s.is_active()]
