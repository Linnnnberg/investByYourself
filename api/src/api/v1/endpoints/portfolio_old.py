#!/usr/bin/env python3
"""
InvestByYourself API Portfolio Management Endpoints
Tech-028: API Implementation

Portfolio management endpoints for CRUD operations.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Path, Query

from src.models.portfolio import (
    AssetType,
    Holding,
    HoldingCreate,
    HoldingUpdate,
    Portfolio,
    PortfolioCreate,
    PortfolioDetail,
    PortfolioSummary,
    PortfolioUpdate,
    RiskProfile,
    Transaction,
    TransactionCreate,
    TransactionType,
)

router = APIRouter()


# Health Check for Portfolio Service
@router.get("/health", summary="Portfolio Service Health")
async def portfolio_health():
    """Health check for portfolio service."""
    return {
        "status": "healthy",
        "service": "portfolio",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# Mock data for testing
mock_portfolios = [
    {
        "id": 1,
        "name": "Growth Portfolio",
        "description": "Aggressive growth focused portfolio",
        "risk_profile": RiskProfile.AGGRESSIVE,
        "user_id": 1,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "total_value": Decimal("50000.00"),
        "total_cost": Decimal("45000.00"),
        "total_gain_loss": Decimal("5000.00"),
        "total_gain_loss_pct": Decimal("11.11"),
        "is_active": True,
    },
    {
        "id": 2,
        "name": "Conservative Portfolio",
        "description": "Low-risk income focused portfolio",
        "risk_profile": RiskProfile.CONSERVATIVE,
        "user_id": 1,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "total_value": Decimal("75000.00"),
        "total_cost": Decimal("70000.00"),
        "total_gain_loss": Decimal("5000.00"),
        "total_gain_loss_pct": Decimal("7.14"),
        "is_active": True,
    },
]

mock_holdings = [
    {
        "id": 1,
        "portfolio_id": 1,
        "symbol": "AAPL",
        "asset_type": AssetType.STOCK,
        "quantity": Decimal("100"),
        "cost_basis": Decimal("150.00"),
        "current_price": Decimal("155.00"),
        "notes": "Tech growth stock",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "market_value": Decimal("15500.00"),
        "gain_loss": Decimal("500.00"),
        "gain_loss_pct": Decimal("3.33"),
    },
    {
        "id": 2,
        "portfolio_id": 1,
        "symbol": "TSLA",
        "asset_type": AssetType.STOCK,
        "quantity": Decimal("50"),
        "cost_basis": Decimal("200.00"),
        "current_price": Decimal("220.00"),
        "notes": "EV leader",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "market_value": Decimal("11000.00"),
        "gain_loss": Decimal("1000.00"),
        "gain_loss_pct": Decimal("10.00"),
    },
]


@router.post("/", response_model=Portfolio, summary="Create Portfolio")
async def create_portfolio(portfolio_data: PortfolioCreate):
    """Create a new portfolio for the current user."""
    try:
        # Mock portfolio creation
        new_portfolio = {
            "id": len(mock_portfolios) + 1,
            **portfolio_data.model_dump(),
            "user_id": 1,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "total_value": Decimal("0.00"),
            "total_cost": Decimal("0.00"),
            "total_gain_loss": Decimal("0.00"),
            "total_gain_loss_pct": Decimal("0.00"),
            "is_active": True,
        }

        mock_portfolios.append(new_portfolio)
        return Portfolio(**new_portfolio)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create portfolio: {str(e)}"
        )


@router.get("/", response_model=List[PortfolioSummary], summary="List User Portfolios")
async def list_user_portfolios(
    skip: int = Query(0, ge=0, description="Number of portfolios to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of portfolios to return"
    ),
):
    """Get all portfolios for the current user."""
    try:
        portfolios = mock_portfolios[skip : skip + limit]

        portfolio_summaries = []
        for portfolio in portfolios:
            # Count holdings for this portfolio
            holdings_count = len(
                [h for h in mock_holdings if h["portfolio_id"] == portfolio["id"]]
            )

            summary = PortfolioSummary(
                id=portfolio["id"],
                name=portfolio["name"],
                total_value=portfolio["total_value"],
                total_cost=portfolio["total_cost"],
                total_gain_loss=portfolio["total_gain_loss"],
                total_gain_loss_pct=portfolio["total_gain_loss_pct"],
                holdings_count=holdings_count,
                last_updated=portfolio["updated_at"],
                risk_profile=portfolio["risk_profile"],
            )
            portfolio_summaries.append(summary)

        return portfolio_summaries
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get portfolios: {str(e)}"
        )


@router.get(
    "/{portfolio_id}", response_model=PortfolioDetail, summary="Get Portfolio Details"
)
async def get_portfolio(portfolio_id: int = Path(..., description="Portfolio ID")):
    """Get a specific portfolio with holdings and transactions."""
    try:
        portfolio = next((p for p in mock_portfolios if p["id"] == portfolio_id), None)

        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        # Get holdings for this portfolio
        holdings = [h for h in mock_holdings if h["portfolio_id"] == portfolio_id]

        # Create portfolio detail
        portfolio_detail = PortfolioDetail(
            **portfolio, holdings=holdings, transactions=[]  # No transactions for now
        )

        return portfolio_detail
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get portfolio: {str(e)}"
        )


@router.put("/{portfolio_id}", response_model=Portfolio, summary="Update Portfolio")
async def update_portfolio(
    portfolio_id: int = Path(..., description="Portfolio ID"),
    portfolio_data: PortfolioUpdate = None,
):
    """Update a portfolio."""
    try:
        portfolio = next((p for p in mock_portfolios if p["id"] == portfolio_id), None)

        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        # Update fields
        if portfolio_data:
            update_data = portfolio_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                portfolio[field] = value

        portfolio["updated_at"] = datetime.now(timezone.utc)

        return Portfolio(**portfolio)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update portfolio: {str(e)}"
        )


@router.delete("/{portfolio_id}", summary="Delete Portfolio")
async def delete_portfolio(portfolio_id: int = Path(..., description="Portfolio ID")):
    """Delete a portfolio (soft delete)."""
    try:
        portfolio = next((p for p in mock_portfolios if p["id"] == portfolio_id), None)

        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        portfolio["is_active"] = False
        portfolio["updated_at"] = datetime.now(timezone.utc)

        return {"message": "Portfolio deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete portfolio: {str(e)}"
        )


# Holdings Management Endpoints


@router.post("/{portfolio_id}/holdings", response_model=Holding, summary="Add Holding")
async def add_holding(
    portfolio_id: int = Path(..., description="Portfolio ID"),
    holding_data: HoldingCreate = None,
):
    """Add a holding to a portfolio."""
    try:
        portfolio = next((p for p in mock_portfolios if p["id"] == portfolio_id), None)

        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        if not holding_data:
            raise HTTPException(status_code=400, detail="Holding data is required")

        # Mock holding creation
        new_holding = {
            "id": len(mock_holdings) + 1,
            **holding_data.model_dump(),
            "portfolio_id": portfolio_id,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "market_value": holding_data.quantity
            * (holding_data.current_price or holding_data.cost_basis),
            "gain_loss": Decimal("0.00"),
            "gain_loss_pct": Decimal("0.00"),
        }

        mock_holdings.append(new_holding)
        return Holding(**new_holding)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add holding: {str(e)}")


@router.get(
    "/{portfolio_id}/holdings",
    response_model=List[Holding],
    summary="Get Portfolio Holdings",
)
async def get_portfolio_holdings(
    portfolio_id: int = Path(..., description="Portfolio ID")
):
    """Get all holdings for a portfolio."""
    try:
        portfolio = next((p for p in mock_portfolios if p["id"] == portfolio_id), None)

        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        holdings = [h for h in mock_holdings if h["portfolio_id"] == portfolio_id]
        return holdings
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get holdings: {str(e)}")


@router.put(
    "/{portfolio_id}/holdings/{holding_id}",
    response_model=Holding,
    summary="Update Holding",
)
async def update_holding(
    portfolio_id: int = Path(..., description="Portfolio ID"),
    holding_id: int = Path(..., description="Holding ID"),
    holding_data: HoldingUpdate = None,
):
    """Update a holding in a portfolio."""
    try:
        portfolio = next((p for p in mock_portfolios if p["id"] == portfolio_id), None)

        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        holding = next(
            (
                h
                for h in mock_holdings
                if h["id"] == holding_id and h["portfolio_id"] == portfolio_id
            ),
            None,
        )

        if not holding:
            raise HTTPException(status_code=404, detail="Holding not found")

        # Update fields
        if holding_data:
            update_data = holding_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                holding[field] = value

        holding["updated_at"] = datetime.now(timezone.utc)

        return Holding(**holding)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update holding: {str(e)}"
        )


@router.delete("/{portfolio_id}/holdings/{holding_id}", summary="Remove Holding")
async def remove_holding(
    portfolio_id: int = Path(..., description="Portfolio ID"),
    holding_id: int = Path(..., description="Holding ID"),
):
    """Remove a holding from a portfolio."""
    try:
        portfolio = next((p for p in mock_portfolios if p["id"] == portfolio_id), None)

        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        holding = next(
            (
                h
                for h in mock_holdings
                if h["id"] == holding_id and h["portfolio_id"] == portfolio_id
            ),
            None,
        )

        if not holding:
            raise HTTPException(status_code=404, detail="Holding not found")

        # Remove holding (in real implementation, this would be soft delete)
        mock_holdings.remove(holding)

        return {"message": "Holding removed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to remove holding: {str(e)}"
        )


# Analytics Endpoints


@router.get("/{portfolio_id}/analytics", summary="Get Portfolio Analytics")
async def get_portfolio_analytics(
    portfolio_id: int = Path(..., description="Portfolio ID")
):
    """Get portfolio analytics and performance metrics."""
    try:
        portfolio = next((p for p in mock_portfolios if p["id"] == portfolio_id), None)

        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        holdings = [h for h in mock_holdings if h["portfolio_id"] == portfolio_id]

        # Calculate analytics
        analytics = {
            "total_holdings": len(holdings),
            "asset_allocation": _calculate_asset_allocation(holdings),
            "sector_allocation": {},  # Placeholder
            "top_holdings": _get_top_holdings(holdings),
            "performance_metrics": {
                "total_return": float(portfolio["total_gain_loss_pct"]),
                "total_value": float(portfolio["total_value"]),
                "total_cost": float(portfolio["total_cost"]),
                "unrealized_gain_loss": float(portfolio["total_gain_loss"]),
            },
        }

        return analytics
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get analytics: {str(e)}"
        )


# Helper functions
def _calculate_asset_allocation(holdings: List[dict]) -> dict:
    """Calculate asset allocation percentages."""
    if not holdings:
        return {}

    total_value = sum(h["market_value"] for h in holdings)
    if total_value == 0:
        return {}

    allocation = {}
    for holding in holdings:
        percentage = (holding["market_value"] / total_value) * 100
        asset_type = holding["asset_type"].value

        if asset_type in allocation:
            allocation[asset_type] += percentage
        else:
            allocation[asset_type] = percentage

    return {k: round(v, 2) for k, v in allocation.items()}


def _get_top_holdings(holdings: List[dict], limit: int = 5) -> List[dict]:
    """Get top holdings by value."""
    if not holdings:
        return []

    # Sort by market value descending
    sorted_holdings = sorted(holdings, key=lambda x: x["market_value"], reverse=True)

    # Calculate percentages
    total_value = sum(h["market_value"] for h in sorted_holdings)
    top_holdings = []

    for holding in sorted_holdings[:limit]:
        percentage = (
            (holding["market_value"] / total_value) * 100 if total_value > 0 else 0
        )
        top_holdings.append(
            {
                "symbol": holding["symbol"],
                "quantity": float(holding["quantity"]),
                "value": float(holding["market_value"]),
                "percentage": round(percentage, 2),
            }
        )

    return top_holdings


# Health Check for Portfolio Service
@router.get("/health", summary="Portfolio Service Health")
async def portfolio_health():
    """Health check for portfolio service."""
    return {
        "status": "healthy",
        "service": "Portfolio Management",
        "endpoints": [
            "POST / - Create portfolio",
            "GET / - List portfolios",
            "GET /{id} - Get portfolio details",
            "PUT /{id} - Update portfolio",
            "DELETE /{id} - Delete portfolio",
            "POST /{id}/holdings - Add holding",
            "GET /{id}/holdings - Get holdings",
            "PUT /{id}/holdings/{holding_id} - Update holding",
            "DELETE /{id}/holdings/{holding_id} - Remove holding",
            "GET /{id}/analytics - Get analytics",
        ],
    }
