from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import get_db_session
from src.models.database import Company, Watchlist

router = APIRouter()


# Pydantic models for API responses
class WatchlistItemResponse(BaseModel):
    id: int
    user_id: str
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float
    added_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WatchlistItemCreate(BaseModel):
    symbol: str


class WatchlistSummary(BaseModel):
    total_items: int
    gainers: int
    losers: int
    avg_change_percent: float


@router.get("/", response_model=List[WatchlistItemResponse])
async def get_watchlist(
    user_id: str = "default_user",  # TODO: Get from authentication
    db: AsyncSession = Depends(get_db_session),
):
    """Get user's watchlist"""
    try:
        # Query watchlist with company data
        query = select(Watchlist, Company).join(
            Company, Watchlist.symbol == Company.symbol
        )
        result = await db.execute(query)
        watchlist_items = result.all()

        if not watchlist_items:
            # Return empty list if no watchlist items
            return []

        # Convert to response format
        watchlist_responses = []
        for i, (watchlist_item, company) in enumerate(watchlist_items):
            # Generate mock price data for now (since we don't have real market data yet)
            base_price = 100.0 + hash(company.symbol) % 500
            change = (hash(company.symbol + "change") % 20) - 10
            change_percent = (change / base_price) * 100

            watchlist_responses.append(
                {
                    "id": i + 1,
                    "user_id": user_id,
                    "symbol": company.symbol,
                    "name": company.name,
                    "price": round(base_price, 2),
                    "change": round(change, 2),
                    "change_percent": round(change_percent, 2),
                    "added_date": watchlist_item.added_at,
                    "created_at": watchlist_item.added_at,
                    "updated_at": watchlist_item.added_at,
                }
            )

        return watchlist_responses
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch watchlist: {str(e)}"
        )


@router.get("/summary", response_model=WatchlistSummary)
async def get_watchlist_summary(
    user_id: str = "default_user",  # TODO: Get from authentication
    db: AsyncSession = Depends(get_db_session),
):
    """Get watchlist summary statistics"""
    try:
        # Mock summary data
        summary = {
            "total_items": 5,
            "gainers": 3,
            "losers": 2,
            "avg_change_percent": 0.25,
        }
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch watchlist summary: {str(e)}"
        )


@router.post("/", response_model=WatchlistItemResponse)
async def add_to_watchlist(
    item: WatchlistItemCreate,
    user_id: str = "default_user",  # TODO: Get from authentication
    db: AsyncSession = Depends(get_db_session),
):
    """Add a company to watchlist"""
    try:
        # Check if company exists
        company_query = select(Company).where(Company.symbol == item.symbol.upper())
        company_result = await db.execute(company_query)
        company = company_result.scalar_one_or_none()

        if not company:
            raise HTTPException(
                status_code=404, detail=f"Company with symbol {item.symbol} not found"
            )

        # Check if already in watchlist
        existing_query = select(Watchlist).where(
            Watchlist.user_id == user_id, Watchlist.symbol == item.symbol.upper()
        )
        existing_result = await db.execute(existing_query)
        existing_item = existing_result.scalar_one_or_none()

        if existing_item:
            raise HTTPException(
                status_code=400, detail=f"Company {item.symbol} already in watchlist"
            )

        # Add to watchlist
        new_watchlist_item = Watchlist(
            id=f"watchlist_{user_id}_{item.symbol.upper()}_{int(datetime.now().timestamp())}",
            user_id=user_id,
            company_id=company.id,
            symbol=item.symbol.upper(),
            added_at=datetime.now(),
        )

        db.add(new_watchlist_item)
        await db.commit()
        await db.refresh(new_watchlist_item)

        # Generate mock price data
        base_price = 100.0 + hash(company.symbol) % 500
        change = (hash(company.symbol + "change") % 20) - 10
        change_percent = (change / base_price) * 100

        return {
            "id": 1,  # Simple ID for now
            "user_id": user_id,
            "symbol": company.symbol,
            "name": company.name,
            "price": round(base_price, 2),
            "change": round(change, 2),
            "change_percent": round(change_percent, 2),
            "added_date": new_watchlist_item.added_at,
            "created_at": new_watchlist_item.added_at,
            "updated_at": new_watchlist_item.added_at,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to add to watchlist: {str(e)}"
        )


@router.delete("/{symbol}")
async def remove_from_watchlist(
    symbol: str,
    user_id: str = "default_user",  # TODO: Get from authentication
    db: AsyncSession = Depends(get_db_session),
):
    """Remove a company from watchlist"""
    try:
        # Find and delete watchlist item
        query = select(Watchlist).where(
            Watchlist.user_id == user_id, Watchlist.symbol == symbol.upper()
        )
        result = await db.execute(query)
        watchlist_item = result.scalar_one_or_none()

        if not watchlist_item:
            raise HTTPException(
                status_code=404, detail=f"Company {symbol} not found in watchlist"
            )

        await db.delete(watchlist_item)
        await db.commit()

        return {"message": f"{symbol.upper()} removed from watchlist successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to remove from watchlist: {str(e)}"
        )


@router.get("/{symbol}", response_model=WatchlistItemResponse)
async def get_watchlist_item(
    symbol: str,
    user_id: str = "default_user",  # TODO: Get from authentication
    db: AsyncSession = Depends(get_db_session),
):
    """Get a specific watchlist item"""
    try:
        # Mock response
        item = {
            "id": 1,
            "user_id": user_id,
            "symbol": symbol.upper(),
            "name": f"{symbol.upper()} Inc.",
            "price": 175.43,
            "change": 2.15,
            "change_percent": 1.24,
            "added_date": datetime.now(),
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        return item
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch watchlist item: {str(e)}"
        )
