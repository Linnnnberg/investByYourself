#!/usr/bin/env python3
"""
InvestByYourself API Portfolio Models
Tech-028: API Implementation

Data models for portfolio management.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class AssetType(str, Enum):
    """Asset type enumeration."""

    STOCK = "stock"
    BOND = "bond"
    ETF = "etf"
    MUTUAL_FUND = "mutual_fund"
    CRYPTO = "crypto"
    COMMODITY = "commodity"
    CASH = "cash"
    OTHER = "other"


class TransactionType(str, Enum):
    """Transaction type enumeration."""

    BUY = "buy"
    SELL = "sell"
    DIVIDEND = "dividend"
    SPLIT = "split"
    MERGE = "merge"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"


class RiskProfile(str, Enum):
    """Risk profile enumeration."""

    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class PortfolioBase(BaseModel):
    """Base portfolio model."""

    name: str = Field(..., min_length=1, max_length=100, description="Portfolio name")
    description: Optional[str] = Field(
        None, max_length=500, description="Portfolio description"
    )
    risk_profile: RiskProfile = Field(
        default=RiskProfile.MODERATE, description="Risk tolerance level"
    )
    target_allocation: Optional[dict] = Field(
        None, description="Target asset allocation percentages"
    )
    is_active: bool = Field(default=True, description="Whether portfolio is active")


class PortfolioCreate(PortfolioBase):
    """Portfolio creation model."""

    pass


class PortfolioUpdate(BaseModel):
    """Portfolio update model."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    risk_profile: Optional[RiskProfile] = None
    target_allocation: Optional[dict] = None
    is_active: Optional[bool] = None


class Portfolio(PortfolioBase):
    """Portfolio model with ID and timestamps."""

    id: int = Field(..., description="Unique portfolio ID")
    user_id: int = Field(..., description="Owner user ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    total_value: Decimal = Field(
        default=Decimal("0.00"), description="Total portfolio value"
    )
    total_cost: Decimal = Field(default=Decimal("0.00"), description="Total cost basis")
    total_gain_loss: Decimal = Field(
        default=Decimal("0.00"), description="Total unrealized gain/loss"
    )
    total_gain_loss_pct: Decimal = Field(
        default=Decimal("0.00"), description="Total gain/loss percentage"
    )

    class Config:
        from_attributes = True


class HoldingBase(BaseModel):
    """Base holding model."""

    symbol: str = Field(
        ..., min_length=1, max_length=20, description="Stock/ETF symbol"
    )
    asset_type: AssetType = Field(..., description="Type of asset")
    quantity: Decimal = Field(..., gt=0, description="Number of shares/units")
    cost_basis: Decimal = Field(..., ge=0, description="Average cost per share")
    current_price: Optional[Decimal] = Field(
        None, ge=0, description="Current market price"
    )
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")


class HoldingCreate(HoldingBase):
    """Holding creation model."""

    pass


class HoldingUpdate(BaseModel):
    """Holding update model."""

    quantity: Optional[Decimal] = Field(None, gt=0)
    cost_basis: Optional[Decimal] = Field(None, ge=0)
    current_price: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=500)


class Holding(HoldingBase):
    """Holding model with calculated fields."""

    id: int = Field(..., description="Unique holding ID")
    portfolio_id: int = Field(..., description="Portfolio ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    market_value: Decimal = Field(..., description="Current market value")
    gain_loss: Decimal = Field(..., description="Unrealized gain/loss")
    gain_loss_pct: Decimal = Field(..., description="Gain/loss percentage")

    @validator("market_value", "gain_loss", "gain_loss_pct", pre=True, always=True)
    def calculate_derived_fields(cls, v, values):
        """Calculate derived fields if not provided."""
        if (
            "quantity" in values
            and "current_price" in values
            and values["current_price"]
        ):
            quantity = values["quantity"]
            current_price = values["current_price"]
            cost_basis = values.get("cost_basis", 0)

            market_value = quantity * current_price
            gain_loss = market_value - (quantity * cost_basis)
            gain_loss_pct = (
                (gain_loss / (quantity * cost_basis)) * 100 if cost_basis > 0 else 0
            )

            return {
                "market_value": market_value,
                "gain_loss": gain_loss,
                "gain_loss_pct": gain_loss_pct,
            }
        return v

    class Config:
        from_attributes = True


class TransactionBase(BaseModel):
    """Base transaction model."""

    transaction_type: TransactionType = Field(..., description="Type of transaction")
    symbol: str = Field(
        ..., min_length=1, max_length=20, description="Stock/ETF symbol"
    )
    quantity: Decimal = Field(..., description="Number of shares/units")
    price: Decimal = Field(..., ge=0, description="Transaction price per share")
    fees: Decimal = Field(default=Decimal("0.00"), ge=0, description="Transaction fees")
    notes: Optional[str] = Field(None, max_length=500, description="Transaction notes")
    transaction_date: datetime = Field(
        default_factory=datetime.utcnow, description="Transaction date"
    )


class TransactionCreate(TransactionBase):
    """Transaction creation model."""

    pass


class Transaction(TransactionBase):
    """Transaction model with ID and timestamps."""

    id: int = Field(..., description="Unique transaction ID")
    portfolio_id: int = Field(..., description="Portfolio ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    total_amount: Decimal = Field(..., description="Total transaction amount")

    @validator("total_amount", pre=True, always=True)
    def calculate_total_amount(cls, v, values):
        """Calculate total transaction amount."""
        if "quantity" in values and "price" in values:
            quantity = values["quantity"]
            price = values["price"]
            fees = values.get("fees", 0)
            return (quantity * price) + fees
        return v

    class Config:
        from_attributes = True


class PortfolioSummary(BaseModel):
    """Portfolio summary with key metrics."""

    id: int
    name: str
    total_value: Decimal
    total_cost: Decimal
    total_gain_loss: Decimal
    total_gain_loss_pct: Decimal
    holdings_count: int
    last_updated: datetime
    risk_profile: RiskProfile


class PortfolioDetail(Portfolio):
    """Portfolio with holdings and transactions."""

    holdings: List[Holding] = Field(default_factory=list)
    transactions: List[Transaction] = Field(default_factory=list)
