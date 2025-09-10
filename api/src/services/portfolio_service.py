#!/usr/bin/env python3
"""
InvestByYourself API Portfolio Service
Tech-028: API Implementation

Business logic for portfolio management.
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.models.portfolio import (Holding, HoldingCreate, HoldingUpdate,
                                  Portfolio, PortfolioCreate, PortfolioDetail,
                                  PortfolioSummary, PortfolioUpdate,
                                  Transaction, TransactionCreate)

logger = logging.getLogger(__name__)


class PortfolioService:
    """Service for portfolio management operations."""

    def __init__(self, db: Session):
        self.db = db

    def create_portfolio(
        self, portfolio_data: PortfolioCreate, user_id: int
    ) -> Portfolio:
        """Create a new portfolio for a user."""
        try:
            portfolio = Portfolio(
                **portfolio_data.dict(),
                user_id=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            self.db.add(portfolio)
            self.db.commit()
            self.db.refresh(portfolio)
            logger.info(f"Created portfolio {portfolio.id} for user {user_id}")
            return portfolio
        except Exception as e:
            logger.error(f"Error creating portfolio: {e}")
            self.db.rollback()
            raise

    def get_user_portfolios(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[PortfolioSummary]:
        """Get all portfolios for a user with summary information."""
        try:
            portfolios = (
                self.db.query(Portfolio)
                .filter(Portfolio.user_id == user_id, Portfolio.is_active == True)
                .offset(skip)
                .limit(limit)
                .all()
            )

            portfolio_summaries = []
            for portfolio in portfolios:
                # Calculate summary metrics
                holdings_count = (
                    self.db.query(Holding)
                    .filter(Holding.portfolio_id == portfolio.id)
                    .count()
                )

                # Get latest transaction date
                latest_transaction = (
                    self.db.query(Transaction)
                    .filter(Transaction.portfolio_id == portfolio.id)
                    .order_by(Transaction.transaction_date.desc())
                    .first()
                )

                last_updated = (
                    latest_transaction.transaction_date
                    if latest_transaction
                    else portfolio.updated_at
                )

                summary = PortfolioSummary(
                    id=portfolio.id,
                    name=portfolio.name,
                    total_value=portfolio.total_value,
                    total_cost=portfolio.total_cost,
                    total_gain_loss=portfolio.total_gain_loss,
                    total_gain_loss_pct=portfolio.total_gain_loss_pct,
                    holdings_count=holdings_count,
                    last_updated=last_updated,
                    risk_profile=portfolio.risk_profile,
                )
                portfolio_summaries.append(summary)

            return portfolio_summaries
        except Exception as e:
            logger.error(f"Error getting user portfolios: {e}")
            raise

    def get_portfolio(
        self, portfolio_id: int, user_id: int
    ) -> Optional[PortfolioDetail]:
        """Get a specific portfolio with holdings and transactions."""
        try:
            portfolio = (
                self.db.query(Portfolio)
                .filter(Portfolio.id == portfolio_id, Portfolio.user_id == user_id)
                .first()
            )

            if not portfolio:
                return None

            # Get holdings
            holdings = (
                self.db.query(Holding)
                .filter(Holding.portfolio_id == portfolio_id)
                .all()
            )

            # Get transactions
            transactions = (
                self.db.query(Transaction)
                .filter(Transaction.portfolio_id == portfolio_id)
                .order_by(Transaction.transaction_date.desc())
                .all()
            )

            # Create portfolio detail
            portfolio_detail = PortfolioDetail(
                **portfolio.__dict__, holdings=holdings, transactions=transactions
            )

            return portfolio_detail
        except Exception as e:
            logger.error(f"Error getting portfolio {portfolio_id}: {e}")
            raise

    def update_portfolio(
        self, portfolio_id: int, user_id: int, portfolio_data: PortfolioUpdate
    ) -> Optional[Portfolio]:
        """Update a portfolio."""
        try:
            portfolio = (
                self.db.query(Portfolio)
                .filter(Portfolio.id == portfolio_id, Portfolio.user_id == user_id)
                .first()
            )

            if not portfolio:
                return None

            # Update fields
            update_data = portfolio_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(portfolio, field, value)

            portfolio.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(portfolio)

            logger.info(f"Updated portfolio {portfolio_id}")
            return portfolio
        except Exception as e:
            logger.error(f"Error updating portfolio {portfolio_id}: {e}")
            self.db.rollback()
            raise

    def delete_portfolio(self, portfolio_id: int, user_id: int) -> bool:
        """Delete a portfolio (soft delete by setting is_active to False)."""
        try:
            portfolio = (
                self.db.query(Portfolio)
                .filter(Portfolio.id == portfolio_id, Portfolio.user_id == user_id)
                .first()
            )

            if not portfolio:
                return False

            portfolio.is_active = False
            portfolio.updated_at = datetime.utcnow()
            self.db.commit()

            logger.info(f"Deleted portfolio {portfolio_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting portfolio {portfolio_id}: {e}")
            self.db.rollback()
            raise

    def add_holding(
        self, portfolio_id: int, user_id: int, holding_data: HoldingCreate
    ) -> Optional[Holding]:
        """Add a holding to a portfolio."""
        try:
            # Verify portfolio ownership
            portfolio = (
                self.db.query(Portfolio)
                .filter(Portfolio.id == portfolio_id, Portfolio.user_id == user_id)
                .first()
            )

            if not portfolio:
                return None

            # Create holding
            holding = Holding(
                **holding_data.dict(),
                portfolio_id=portfolio_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            self.db.add(holding)
            self.db.commit()
            self.db.refresh(holding)

            # Update portfolio totals
            self._update_portfolio_totals(portfolio_id)

            logger.info(f"Added holding {holding.symbol} to portfolio {portfolio_id}")
            return holding
        except Exception as e:
            logger.error(f"Error adding holding: {e}")
            self.db.rollback()
            raise

    def update_holding(
        self,
        holding_id: int,
        portfolio_id: int,
        user_id: int,
        holding_data: HoldingUpdate,
    ) -> Optional[Holding]:
        """Update a holding in a portfolio."""
        try:
            # Verify portfolio ownership
            portfolio = (
                self.db.query(Portfolio)
                .filter(Portfolio.id == portfolio_id, Portfolio.user_id == user_id)
                .first()
            )

            if not portfolio:
                return None

            # Get holding
            holding = (
                self.db.query(Holding)
                .filter(Holding.id == holding_id, Holding.portfolio_id == portfolio_id)
                .first()
            )

            if not holding:
                return None

            # Update fields
            update_data = holding_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(holding, field, value)

            holding.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(holding)

            # Update portfolio totals
            self._update_portfolio_totals(portfolio_id)

            logger.info(f"Updated holding {holding_id}")
            return holding
        except Exception as e:
            logger.error(f"Error updating holding {holding_id}: {e}")
            self.db.rollback()
            raise

    def remove_holding(self, holding_id: int, portfolio_id: int, user_id: int) -> bool:
        """Remove a holding from a portfolio."""
        try:
            # Verify portfolio ownership
            portfolio = (
                self.db.query(Portfolio)
                .filter(Portfolio.id == portfolio_id, Portfolio.user_id == user_id)
                .first()
            )

            if not portfolio:
                return False

            # Get holding
            holding = (
                self.db.query(Holding)
                .filter(Holding.id == holding_id, Holding.portfolio_id == portfolio_id)
                .first()
            )

            if not holding:
                return False

            self.db.delete(holding)
            self.db.commit()

            # Update portfolio totals
            self._update_portfolio_totals(portfolio_id)

            logger.info(f"Removed holding {holding_id}")
            return True
        except Exception as e:
            logger.error(f"Error removing holding {holding_id}: {e}")
            self.db.rollback()
            raise

    def add_transaction(
        self, portfolio_id: int, user_id: int, transaction_data: TransactionCreate
    ) -> Optional[Transaction]:
        """Add a transaction to a portfolio."""
        try:
            # Verify portfolio ownership
            portfolio = (
                self.db.query(Portfolio)
                .filter(Portfolio.id == portfolio_id, Portfolio.user_id == user_id)
                .first()
            )

            if not portfolio:
                return None

            # Create transaction
            transaction = Transaction(
                **transaction_data.dict(),
                portfolio_id=portfolio_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            self.db.add(transaction)
            self.db.commit()
            self.db.refresh(transaction)

            # Update portfolio totals
            self._update_portfolio_totals(portfolio_id)

            logger.info(
                f"Added transaction {transaction.id} to portfolio {portfolio_id}"
            )
            return transaction
        except Exception as e:
            logger.error(f"Error adding transaction: {e}")
            self.db.rollback()
            raise

    def get_portfolio_holdings(self, portfolio_id: int, user_id: int) -> List[Holding]:
        """Get all holdings for a portfolio."""
        try:
            # Verify portfolio ownership
            portfolio = (
                self.db.query(Portfolio)
                .filter(Portfolio.id == portfolio_id, Portfolio.user_id == user_id)
                .first()
            )

            if not portfolio:
                return []

            holdings = (
                self.db.query(Holding)
                .filter(Holding.portfolio_id == portfolio_id)
                .all()
            )

            return holdings
        except Exception as e:
            logger.error(f"Error getting portfolio holdings: {e}")
            raise

    def get_portfolio_transactions(
        self, portfolio_id: int, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Transaction]:
        """Get transactions for a portfolio."""
        try:
            # Verify portfolio ownership
            portfolio = (
                self.db.query(Portfolio)
                .filter(Portfolio.id == portfolio_id, Portfolio.user_id == user_id)
                .first()
            )

            if not portfolio:
                return []

            transactions = (
                self.db.query(Transaction)
                .filter(Transaction.portfolio_id == portfolio_id)
                .order_by(Transaction.transaction_date.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )

            return transactions
        except Exception as e:
            logger.error(f"Error getting portfolio transactions: {e}")
            raise

    def _update_portfolio_totals(self, portfolio_id: int):
        """Update portfolio totals based on current holdings."""
        try:
            # Calculate totals from holdings
            holdings = (
                self.db.query(Holding)
                .filter(Holding.portfolio_id == portfolio_id)
                .all()
            )

            total_value = Decimal("0.00")
            total_cost = Decimal("0.00")

            for holding in holdings:
                if holding.current_price:
                    total_value += holding.quantity * holding.current_price
                total_cost += holding.quantity * holding.cost_basis

            total_gain_loss = total_value - total_cost
            total_gain_loss_pct = (
                (total_gain_loss / total_cost * 100)
                if total_cost > 0
                else Decimal("0.00")
            )

            # Update portfolio
            portfolio = (
                self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            )

            if portfolio:
                portfolio.total_value = total_value
                portfolio.total_cost = total_cost
                portfolio.total_gain_loss = total_gain_loss
                portfolio.total_gain_loss_pct = total_gain_loss_pct
                portfolio.updated_at = datetime.utcnow()

                self.db.commit()

        except Exception as e:
            logger.error(f"Error updating portfolio totals: {e}")
            self.db.rollback()
            raise

    def get_portfolio_analytics(
        self, portfolio_id: int, user_id: int
    ) -> Dict[str, Any]:
        """Get portfolio analytics and performance metrics."""
        try:
            # Verify portfolio ownership
            portfolio = (
                self.db.query(Portfolio)
                .filter(Portfolio.id == portfolio_id, Portfolio.user_id == user_id)
                .first()
            )

            if not portfolio:
                return {}

            # Get holdings for analysis
            holdings = (
                self.db.query(Holding)
                .filter(Holding.portfolio_id == portfolio_id)
                .all()
            )

            # Calculate analytics
            analytics = {
                "total_holdings": len(holdings),
                "asset_allocation": self._calculate_asset_allocation(holdings),
                "sector_allocation": self._calculate_sector_allocation(holdings),
                "top_holdings": self._get_top_holdings(holdings),
                "performance_metrics": {
                    "total_return": float(portfolio.total_gain_loss_pct),
                    "total_value": float(portfolio.total_value),
                    "total_cost": float(portfolio.total_cost),
                    "unrealized_gain_loss": float(portfolio.total_gain_loss),
                },
            }

            return analytics
        except Exception as e:
            logger.error(f"Error getting portfolio analytics: {e}")
            raise

    def _calculate_asset_allocation(self, holdings: List[Holding]) -> Dict[str, float]:
        """Calculate asset allocation percentages."""
        if not holdings:
            return {}

        total_value = sum(
            h.quantity * (h.current_price or h.cost_basis) for h in holdings
        )
        if total_value == 0:
            return {}

        allocation = {}
        for holding in holdings:
            value = holding.quantity * (holding.current_price or holding.cost_basis)
            percentage = (value / total_value) * 100
            asset_type = holding.asset_type.value

            if asset_type in allocation:
                allocation[asset_type] += percentage
            else:
                allocation[asset_type] = percentage

        return {k: round(v, 2) for k, v in allocation.items()}

    def _calculate_sector_allocation(self, holdings: List[Holding]) -> Dict[str, float]:
        """Calculate sector allocation (placeholder - would need sector data from market data service)."""
        # This would require integration with market data service to get sector information
        # For now, return empty dict
        return {}

    def _get_top_holdings(
        self, holdings: List[Holding], limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get top holdings by value."""
        if not holdings:
            return []

        # Calculate values and sort
        holdings_with_values = []
        for holding in holdings:
            value = holding.quantity * (holding.current_price or holding.cost_basis)
            holdings_with_values.append(
                {
                    "symbol": holding.symbol,
                    "quantity": float(holding.quantity),
                    "value": float(value),
                    "percentage": 0,  # Will calculate below
                }
            )

        # Sort by value descending
        holdings_with_values.sort(key=lambda x: x["value"], reverse=True)

        # Calculate percentages
        total_value = sum(h["value"] for h in holdings_with_values)
        if total_value > 0:
            for holding in holdings_with_values:
                holding["percentage"] = round((holding["value"] / total_value) * 100, 2)

        return holdings_with_values[:limit]
