from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import get_db_session

router = APIRouter()


# Pydantic models for API responses
class PortfolioResponse(BaseModel):
    id: str
    name: str
    description: str
    total_value: str
    total_gain_loss: str
    total_gain_loss_pct: str
    holdings_count: int
    risk_profile: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PortfolioCreate(BaseModel):
    name: str
    description: str
    risk_profile: str = "Medium"


class PortfolioUpdate(BaseModel):
    name: str = None
    description: str = None
    risk_profile: str = None


@router.get("/", response_model=List[PortfolioResponse])
async def get_portfolios(db: AsyncSession = Depends(get_db_session)):
    """Get all portfolios for the current user"""
    try:
        # For now, return mock data until we implement user authentication
        mock_portfolios = [
            {
                "id": "1",
                "name": "Growth Portfolio",
                "description": "Aggressive growth strategy focused on tech stocks",
                "total_value": "$125,000",
                "total_gain_loss": "+$12,500",
                "total_gain_loss_pct": "+11.1%",
                "holdings_count": 8,
                "risk_profile": "High",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
            {
                "id": "2",
                "name": "Conservative Portfolio",
                "description": "Stable income focus with dividend stocks",
                "total_value": "$85,000",
                "total_gain_loss": "+$2,100",
                "total_gain_loss_pct": "+2.5%",
                "holdings_count": 12,
                "risk_profile": "Low",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
            {
                "id": "3",
                "name": "Balanced Portfolio",
                "description": "Mix of growth and value stocks",
                "total_value": "$95,000",
                "total_gain_loss": "+$4,200",
                "total_gain_loss_pct": "+4.6%",
                "holdings_count": 15,
                "risk_profile": "Medium",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
        ]
        return mock_portfolios
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch portfolios: {str(e)}"
        )


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(portfolio_id: str, db: AsyncSession = Depends(get_db_session)):
    """Get a specific portfolio by ID"""
    try:
        # For now, return mock data
        mock_portfolio = {
            "id": portfolio_id,
            "name": f"Portfolio {portfolio_id}",
            "description": f"Description for portfolio {portfolio_id}",
            "total_value": "$100,000",
            "total_gain_loss": "+$5,000",
            "total_gain_loss_pct": "+5.0%",
            "holdings_count": 10,
            "risk_profile": "Medium",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        return mock_portfolio
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch portfolio: {str(e)}"
        )


@router.post("/", response_model=PortfolioResponse)
async def create_portfolio(
    portfolio: PortfolioCreate, db: AsyncSession = Depends(get_db_session)
):
    """Create a new portfolio"""
    try:
        # For now, return mock data
        new_portfolio = {
            "id": "new_portfolio_id",
            "name": portfolio.name,
            "description": portfolio.description,
            "total_value": "$0",
            "total_gain_loss": "$0",
            "total_gain_loss_pct": "0%",
            "holdings_count": 0,
            "risk_profile": portfolio.risk_profile,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        return new_portfolio
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create portfolio: {str(e)}"
        )


@router.put("/{portfolio_id}", response_model=PortfolioResponse)
async def update_portfolio(
    portfolio_id: str,
    portfolio: PortfolioUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    """Update an existing portfolio"""
    try:
        # For now, return mock data
        updated_portfolio = {
            "id": portfolio_id,
            "name": portfolio.name or f"Updated Portfolio {portfolio_id}",
            "description": portfolio.description
            or f"Updated description for portfolio {portfolio_id}",
            "total_value": "$100,000",
            "total_gain_loss": "+$5,000",
            "total_gain_loss_pct": "+5.0%",
            "holdings_count": 10,
            "risk_profile": portfolio.risk_profile or "Medium",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        return updated_portfolio
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update portfolio: {str(e)}"
        )


@router.delete("/{portfolio_id}")
async def delete_portfolio(
    portfolio_id: str, db: AsyncSession = Depends(get_db_session)
):
    """Delete a portfolio"""
    try:
        # For now, return success
        return {"message": f"Portfolio {portfolio_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete portfolio: {str(e)}"
        )
