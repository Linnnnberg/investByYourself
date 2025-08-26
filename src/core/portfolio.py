#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core Portfolio Management Module

This module provides the core portfolio management functionality including
portfolio creation, management, and basic operations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd


@dataclass
class Asset:
    """Represents a financial asset"""

    symbol: str
    name: str
    asset_type: str = "stock"  # stock, bond, etf, etc.
    currency: str = "USD"
    exchange: Optional[str] = None
    sector: Optional[str] = None
    country: Optional[str] = "US"

    def __post_init__(self):
        """Validate asset data after initialization"""
        if not self.symbol:
            raise ValueError("Asset symbol cannot be empty")
        if not self.name:
            raise ValueError("Asset name cannot be empty")


@dataclass
class Position:
    """Represents a position in an asset"""

    asset: Asset
    quantity: float
    cost_basis: float
    current_price: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

    @property
    def market_value(self) -> float:
        """Calculate current market value of position"""
        return self.quantity * self.current_price

    @property
    def unrealized_pnl(self) -> float:
        """Calculate unrealized profit/loss"""
        return self.market_value - (self.quantity * self.cost_basis)

    @property
    def unrealized_pnl_pct(self) -> float:
        """Calculate unrealized profit/loss percentage"""
        if self.cost_basis > 0:
            return (self.unrealized_pnl / (self.quantity * self.cost_basis)) * 100
        return 0.0


@dataclass
class Portfolio:
    """Represents a financial portfolio"""

    name: str
    description: Optional[str] = None
    currency: str = "USD"
    positions: Dict[str, Position] = field(default_factory=dict)
    cash: float = 0.0
    created_date: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

    def add_position(self, asset: Asset, quantity: float, cost_basis: float) -> None:
        """Add a new position to the portfolio"""
        if asset.symbol in self.positions:
            # Update existing position
            existing = self.positions[asset.symbol]
            total_quantity = existing.quantity + quantity
            total_cost = (existing.quantity * existing.cost_basis) + (
                quantity * cost_basis
            )
            avg_cost_basis = total_cost / total_quantity if total_quantity > 0 else 0

            self.positions[asset.symbol] = Position(
                asset=asset,
                quantity=total_quantity,
                cost_basis=avg_cost_basis,
                current_price=asset.current_price
                if hasattr(asset, "current_price")
                else 0.0,
            )
        else:
            # Create new position
            self.positions[asset.symbol] = Position(
                asset=asset, quantity=quantity, cost_basis=cost_basis
            )

        self.last_updated = datetime.now()

    def remove_position(self, symbol: str, quantity: float = None) -> None:
        """Remove or reduce a position"""
        if symbol not in self.positions:
            raise ValueError(f"Position {symbol} not found in portfolio")

        position = self.positions[symbol]

        if quantity is None or quantity >= position.quantity:
            # Remove entire position
            del self.positions[symbol]
        else:
            # Reduce position
            remaining_quantity = position.quantity - quantity
            self.positions[symbol] = Position(
                asset=position.asset,
                quantity=remaining_quantity,
                cost_basis=position.cost_basis,
                current_price=position.current_price,
            )

        self.last_updated = datetime.now()

    def update_prices(self, prices: Dict[str, float]) -> None:
        """Update current prices for positions"""
        for symbol, price in prices.items():
            if symbol in self.positions:
                self.positions[symbol].current_price = price
                self.positions[symbol].last_updated = datetime.now()

        self.last_updated = datetime.now()

    @property
    def total_market_value(self) -> float:
        """Calculate total portfolio market value"""
        positions_value = sum(pos.market_value for pos in self.positions.values())
        return positions_value + self.cash

    @property
    def total_cost_basis(self) -> float:
        """Calculate total portfolio cost basis"""
        return sum(pos.quantity * pos.cost_basis for pos in self.positions.values())

    @property
    def total_unrealized_pnl(self) -> float:
        """Calculate total unrealized profit/loss"""
        return sum(pos.unrealized_pnl for pos in self.positions.values())

    @property
    def total_unrealized_pnl_pct(self) -> float:
        """Calculate total unrealized profit/loss percentage"""
        if self.total_cost_basis > 0:
            return (self.total_unrealized_pnl / self.total_cost_basis) * 100
        return 0.0

    def get_weights(self) -> Dict[str, float]:
        """Calculate current portfolio weights"""
        total_value = self.total_market_value
        if total_value <= 0:
            return {}

        weights = {}
        for symbol, position in self.positions.items():
            weights[symbol] = position.market_value / total_value

        return weights

    def get_asset_allocation(self) -> Dict[str, float]:
        """Calculate asset allocation by asset type"""
        allocation = {}
        total_value = self.total_market_value

        if total_value <= 0:
            return {}

        for position in self.positions.values():
            asset_type = position.asset.asset_type
            if asset_type not in allocation:
                allocation[asset_type] = 0.0
            allocation[asset_type] += position.market_value / total_value

        return allocation

    def get_sector_allocation(self) -> Dict[str, float]:
        """Calculate sector allocation"""
        allocation = {}
        total_value = self.total_market_value

        if total_value <= 0:
            return {}

        for position in self.positions.values():
            sector = position.asset.sector or "Unknown"
            if sector not in allocation:
                allocation[sector] = 0.0
            allocation[sector] += position.market_value / total_value

        return allocation

    def to_dataframe(self) -> pd.DataFrame:
        """Convert portfolio to pandas DataFrame"""
        if not self.positions:
            return pd.DataFrame()

        data = []
        for symbol, position in self.positions.items():
            data.append(
                {
                    "Symbol": symbol,
                    "Name": position.asset.name,
                    "Asset Type": position.asset.asset_type,
                    "Sector": position.asset.sector,
                    "Quantity": position.quantity,
                    "Cost Basis": position.cost_basis,
                    "Current Price": position.current_price,
                    "Market Value": position.market_value,
                    "Unrealized PnL": position.unrealized_pnl,
                    "Unrealized PnL %": position.unrealized_pnl_pct,
                    "Weight": position.market_value / self.total_market_value
                    if self.total_market_value > 0
                    else 0,
                }
            )

        return pd.DataFrame(data)

    def summary(self) -> Dict[str, Union[str, float, int]]:
        """Get portfolio summary statistics"""
        return {
            "Name": self.name,
            "Total Positions": len(self.positions),
            "Total Market Value": self.total_market_value,
            "Total Cost Basis": self.total_cost_basis,
            "Total Unrealized PnL": self.total_unrealized_pnl,
            "Total Unrealized PnL %": self.total_unrealized_pnl_pct,
            "Cash": self.cash,
            "Cash %": (self.cash / self.total_market_value * 100)
            if self.total_market_value > 0
            else 0,
            "Last Updated": self.last_updated.strftime("%Y-%m-%d %H:%M:%S"),
        }


class PortfolioManager:
    """Manages multiple portfolios"""

    def __init__(self):
        self.portfolios: Dict[str, Portfolio] = {}

    def create_portfolio(
        self, name: str, description: str = None, currency: str = "USD"
    ) -> Portfolio:
        """Create a new portfolio"""
        if name in self.portfolios:
            raise ValueError(f"Portfolio {name} already exists")

        portfolio = Portfolio(name=name, description=description, currency=currency)
        self.portfolios[name] = portfolio
        return portfolio

    def get_portfolio(self, name: str) -> Portfolio:
        """Get a portfolio by name"""
        if name not in self.portfolios:
            raise ValueError(f"Portfolio {name} not found")
        return self.portfolios[name]

    def delete_portfolio(self, name: str) -> None:
        """Delete a portfolio"""
        if name not in self.portfolios:
            raise ValueError(f"Portfolio {name} not found")
        del self.portfolios[name]

    def list_portfolios(self) -> List[str]:
        """List all portfolio names"""
        return list(self.portfolios.keys())

    def get_portfolio_summary(self) -> pd.DataFrame:
        """Get summary of all portfolios"""
        if not self.portfolios:
            return pd.DataFrame()

        data = []
        for portfolio in self.portfolios.values():
            data.append(portfolio.summary())

        return pd.DataFrame(data)
