#!/usr/bin/env python3
"""
Portfolio Database Service
InvestByYourself Financial Platform

Service for managing portfolio database operations.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session

from src.models.portfolio import Portfolio, PortfolioHolding, PortfolioPerformance


class PortfolioDatabaseService:
    """Service for portfolio database operations."""

    def __init__(self, db: Session):
        self.db = db

    def create_portfolio(self, portfolio_data: Dict[str, Any]) -> Portfolio:
        """Create a new portfolio."""
        portfolio = Portfolio.from_dict(portfolio_data)
        self.db.add(portfolio)
        self.db.commit()
        self.db.refresh(portfolio)
        return portfolio

    def get_portfolio(
        self, portfolio_id: str, user_id: str = "current_user"
    ) -> Optional[Portfolio]:
        """Get a portfolio by ID."""
        return (
            self.db.query(Portfolio)
            .filter(and_(Portfolio.id == portfolio_id, Portfolio.user_id == user_id))
            .first()
        )

    def get_portfolios(
        self, user_id: str = "current_user", limit: int = 100, offset: int = 0
    ) -> List[Portfolio]:
        """Get all portfolios for a user."""
        return (
            self.db.query(Portfolio)
            .filter(Portfolio.user_id == user_id)
            .order_by(desc(Portfolio.updated_at))
            .offset(offset)
            .limit(limit)
            .all()
        )

    def update_portfolio(
        self, portfolio_id: str, updates: Dict[str, Any], user_id: str = "current_user"
    ) -> Optional[Portfolio]:
        """Update a portfolio."""
        portfolio = self.get_portfolio(portfolio_id, user_id)
        if not portfolio:
            return None

        # Update fields
        for key, value in updates.items():
            if hasattr(portfolio, key):
                setattr(portfolio, key, value)

        portfolio.updated_at = datetime.utcnow()
        portfolio.last_updated = datetime.utcnow()

        self.db.commit()
        self.db.refresh(portfolio)
        return portfolio

    def delete_portfolio(
        self, portfolio_id: str, user_id: str = "current_user"
    ) -> bool:
        """Delete a portfolio."""
        portfolio = self.get_portfolio(portfolio_id, user_id)
        if not portfolio:
            return False

        # Delete related holdings and performance data
        self.db.query(PortfolioHolding).filter(
            PortfolioHolding.portfolio_id == portfolio_id
        ).delete()
        self.db.query(PortfolioPerformance).filter(
            PortfolioPerformance.portfolio_id == portfolio_id
        ).delete()

        # Delete portfolio
        self.db.delete(portfolio)
        self.db.commit()
        return True

    def create_portfolio_from_workflow(
        self,
        workflow_id: str,
        execution_id: str,
        context: Dict[str, Any],
        user_id: str = "current_user",
    ) -> Portfolio:
        """Create a portfolio from workflow execution results."""
        # Extract portfolio info from context
        name = context.get("portfolio_name", f"Portfolio from {workflow_id}")
        description = context.get("portfolio_description", "Created via workflow")

        # Determine allocation based on workflow type and context
        allocation = self._determine_allocation(workflow_id, context)

        # Determine risk level
        risk_level = self._determine_risk_level(workflow_id, context)

        portfolio_data = {
            "user_id": user_id,
            "name": name,
            "description": description,
            "value": 100000.00,  # Starting value
            "change": 0.00,
            "change_percent": 0.00,
            "allocation": allocation,
            "risk_level": risk_level,
            "status": "Draft",
            "workflow_id": workflow_id,
            "execution_id": execution_id,
            "last_updated": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        return self.create_portfolio(portfolio_data)

    def _determine_allocation(
        self, workflow_id: str, context: Dict[str, Any]
    ) -> Dict[str, float]:
        """Determine portfolio allocation based on workflow and context."""
        if workflow_id == "comprehensive_portfolio_creation":
            template = context.get("template", {})
            if template and "allocation" in template:
                # Convert template allocation to proper format
                allocation = {}
                for asset, weight in template["allocation"].items():
                    allocation[asset] = (
                        float(weight) / 100.0
                    )  # Convert percentage to decimal
                return allocation
            else:
                return {"Stocks": 0.6, "Bonds": 0.3, "Cash": 0.1}
        elif workflow_id == "advanced_allocation_framework":
            return {"Stocks": 0.7, "Bonds": 0.2, "Alternatives": 0.1}
        else:
            return {"Stocks": 0.5, "Bonds": 0.4, "Cash": 0.1}

    def _determine_risk_level(self, workflow_id: str, context: Dict[str, Any]) -> str:
        """Determine portfolio risk level based on workflow and context."""
        if workflow_id == "comprehensive_portfolio_creation":
            template = context.get("template", {})
            if template and "riskLevel" in template:
                return template["riskLevel"]
            # Determine from allocation
            allocation = self._determine_allocation(workflow_id, context)
            stock_weight = allocation.get("Stocks", 0.0)
            if stock_weight >= 0.7:
                return "High"
            elif stock_weight >= 0.4:
                return "Medium"
            else:
                return "Low"
        elif workflow_id == "advanced_allocation_framework":
            return "High"  # Advanced frameworks are typically higher risk
        else:
            return "Medium"

    def add_holding(
        self, portfolio_id: str, holding_data: Dict[str, Any]
    ) -> PortfolioHolding:
        """Add a holding to a portfolio."""
        holding = PortfolioHolding()
        holding.portfolio_id = portfolio_id
        holding.symbol = holding_data.get("symbol", "")
        holding.name = holding_data.get("name", "")
        holding.asset_type = holding_data.get("asset_type", "Stock")
        holding.quantity = holding_data.get("quantity", 0.0)
        holding.average_price = holding_data.get("average_price", 0.0)
        holding.current_price = holding_data.get("current_price", 0.0)
        holding.market_value = holding_data.get("market_value", 0.0)
        holding.target_weight = holding_data.get("target_weight", 0.0)
        holding.actual_weight = holding_data.get("actual_weight", 0.0)

        self.db.add(holding)
        self.db.commit()
        self.db.refresh(holding)
        return holding

    def get_holdings(self, portfolio_id: str) -> List[PortfolioHolding]:
        """Get all holdings for a portfolio."""
        return (
            self.db.query(PortfolioHolding)
            .filter(PortfolioHolding.portfolio_id == portfolio_id)
            .all()
        )

    def add_performance_record(
        self, portfolio_id: str, performance_data: Dict[str, Any]
    ) -> PortfolioPerformance:
        """Add a performance record for a portfolio."""
        performance = PortfolioPerformance()
        performance.portfolio_id = portfolio_id
        performance.date = performance_data.get("date", datetime.utcnow())
        performance.total_value = performance_data.get("total_value", 0.0)
        performance.daily_return = performance_data.get("daily_return", 0.0)
        performance.cumulative_return = performance_data.get("cumulative_return", 0.0)
        performance.volatility = performance_data.get("volatility", 0.0)
        performance.sharpe_ratio = performance_data.get("sharpe_ratio", 0.0)
        performance.max_drawdown = performance_data.get("max_drawdown", 0.0)
        performance.benchmark_return = performance_data.get("benchmark_return", 0.0)
        performance.alpha = performance_data.get("alpha", 0.0)
        performance.beta = performance_data.get("beta", 0.0)

        self.db.add(performance)
        self.db.commit()
        self.db.refresh(performance)
        return performance

    def get_performance_history(
        self, portfolio_id: str, days: int = 365
    ) -> List[PortfolioPerformance]:
        """Get performance history for a portfolio."""
        cutoff_date = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)

        return (
            self.db.query(PortfolioPerformance)
            .filter(
                and_(
                    PortfolioPerformance.portfolio_id == portfolio_id,
                    PortfolioPerformance.date >= cutoff_date,
                )
            )
            .order_by(PortfolioPerformance.date)
            .all()
        )

    def update_portfolio_value(
        self, portfolio_id: str, new_value: float
    ) -> Optional[Portfolio]:
        """Update portfolio value and calculate change."""
        portfolio = self.get_portfolio(portfolio_id)
        if not portfolio:
            return None

        old_value = portfolio.value
        portfolio.value = new_value
        portfolio.change = new_value - old_value
        portfolio.change_percent = (
            (portfolio.change / old_value * 100) if old_value > 0 else 0.0
        )
        portfolio.last_updated = datetime.utcnow()
        portfolio.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(portfolio)
        return portfolio
