#!/usr/bin/env python3
"""
Portfolio Database Models
InvestByYourself Financial Platform

Database models for portfolio management.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from sqlalchemy import JSON, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class AssetType(Enum):
    """Asset type enumeration."""

    STOCK = "Stock"
    ETF = "ETF"
    BOND = "Bond"
    CASH = "Cash"
    ALTERNATIVE = "Alternative"
    COMMODITY = "Commodity"
    REAL_ESTATE = "Real Estate"


class RiskLevel(Enum):
    """Risk level enumeration."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class PortfolioStatus(Enum):
    """Portfolio status enumeration."""

    DRAFT = "Draft"
    ACTIVE = "Active"
    ARCHIVED = "Archived"


class Portfolio(Base):
    """Portfolio model for storing user portfolios."""

    __tablename__ = "portfolios"

    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))

    # User identification
    user_id = Column(String, nullable=False, index=True)

    # Portfolio basic info
    name = Column(String(255), nullable=False)
    description = Column(Text)

    # Portfolio values
    value = Column(Float, default=0.0)
    change = Column(Float, default=0.0)
    change_percent = Column(Float, default=0.0)

    # Allocation data (stored as JSON)
    allocation = Column(JSON, default=dict)

    # Risk and status
    risk_level = Column(String(20), default="Medium")  # Low, Medium, High
    status = Column(String(20), default="Draft")  # Draft, Active, Archived

    # Workflow integration
    workflow_id = Column(String, nullable=True)
    execution_id = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert portfolio to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "value": self.value,
            "change": self.change,
            "changePercent": self.change_percent,
            "allocation": self.allocation or {},
            "riskLevel": self.risk_level,
            "status": self.status,
            "workflowId": self.workflow_id,
            "executionId": self.execution_id,
            "lastUpdated": self.last_updated.isoformat() + "Z"
            if self.last_updated
            else None,
            "createdAt": self.created_at.isoformat() + "Z" if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() + "Z" if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Portfolio":
        """Create portfolio from dictionary."""
        portfolio = cls()
        portfolio.id = data.get("id", str(uuid4()))
        portfolio.user_id = data.get("user_id", "current_user")
        portfolio.name = data.get("name", "Unnamed Portfolio")
        portfolio.description = data.get("description", "")
        portfolio.value = data.get("value", 0.0)
        portfolio.change = data.get("change", 0.0)
        portfolio.change_percent = data.get("changePercent", 0.0)
        portfolio.allocation = data.get("allocation", {})
        portfolio.risk_level = data.get("riskLevel", "Medium")
        portfolio.status = data.get("status", "Draft")
        portfolio.workflow_id = data.get("workflowId")
        portfolio.execution_id = data.get("executionId")

        # Handle timestamps
        if "lastUpdated" in data and data["lastUpdated"]:
            portfolio.last_updated = datetime.fromisoformat(
                data["lastUpdated"].replace("Z", "+00:00")
            )
        if "createdAt" in data and data["createdAt"]:
            portfolio.created_at = datetime.fromisoformat(
                data["createdAt"].replace("Z", "+00:00")
            )
        if "updatedAt" in data and data["updatedAt"]:
            portfolio.updated_at = datetime.fromisoformat(
                data["updatedAt"].replace("Z", "+00:00")
            )

        return portfolio


class PortfolioHolding(Base):
    """Portfolio holding model for individual positions."""

    __tablename__ = "portfolio_holdings"

    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))

    # Foreign key to portfolio
    portfolio_id = Column(String, nullable=False, index=True)

    # Holding details
    symbol = Column(String(20), nullable=False)
    name = Column(String(255))
    asset_type = Column(String(50))  # Stock, ETF, Bond, etc.

    # Position details
    quantity = Column(Float, default=0.0)
    average_price = Column(Float, default=0.0)
    current_price = Column(Float, default=0.0)
    market_value = Column(Float, default=0.0)

    # Allocation
    target_weight = Column(Float, default=0.0)
    actual_weight = Column(Float, default=0.0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert holding to dictionary."""
        return {
            "id": self.id,
            "portfolioId": self.portfolio_id,
            "symbol": self.symbol,
            "name": self.name,
            "assetType": self.asset_type,
            "quantity": self.quantity,
            "averagePrice": self.average_price,
            "currentPrice": self.current_price,
            "marketValue": self.market_value,
            "targetWeight": self.target_weight,
            "actualWeight": self.actual_weight,
            "createdAt": self.created_at.isoformat() + "Z" if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() + "Z" if self.updated_at else None,
        }


class PortfolioPerformance(Base):
    """Portfolio performance tracking model."""

    __tablename__ = "portfolio_performance"

    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))

    # Foreign key to portfolio
    portfolio_id = Column(String, nullable=False, index=True)

    # Performance metrics
    date = Column(DateTime, nullable=False, index=True)
    total_value = Column(Float, nullable=False)
    daily_return = Column(Float, default=0.0)
    cumulative_return = Column(Float, default=0.0)

    # Risk metrics
    volatility = Column(Float, default=0.0)
    sharpe_ratio = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)

    # Benchmark comparison
    benchmark_return = Column(Float, default=0.0)
    alpha = Column(Float, default=0.0)
    beta = Column(Float, default=0.0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert performance record to dictionary."""
        return {
            "id": self.id,
            "portfolioId": self.portfolio_id,
            "date": self.date.isoformat() + "Z" if self.date else None,
            "totalValue": self.total_value,
            "dailyReturn": self.daily_return,
            "cumulativeReturn": self.cumulative_return,
            "volatility": self.volatility,
            "sharpeRatio": self.sharpe_ratio,
            "maxDrawdown": self.max_drawdown,
            "benchmarkReturn": self.benchmark_return,
            "alpha": self.alpha,
            "beta": self.beta,
            "createdAt": self.created_at.isoformat() + "Z" if self.created_at else None,
        }
