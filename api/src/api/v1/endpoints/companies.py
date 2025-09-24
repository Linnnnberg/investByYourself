from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import get_db_session
from src.models.database import Company

router = APIRouter()


# Pydantic models for API responses
class CompanyResponse(BaseModel):
    id: int
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float
    sector: str
    market_cap: str
    pe_ratio: float
    volume: str
    description: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CompanyCreate(BaseModel):
    symbol: str
    name: str
    sector: str
    description: str = ""


class CompanyUpdate(BaseModel):
    name: str = None
    sector: str = None
    description: str = None


@router.get("/", response_model=List[CompanyResponse])
async def get_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    sector: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    country: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db_session),
):
    """Get all companies with optional filtering"""
    try:
        # Build query
        query = select(Company)

        # Apply filters
        conditions = []

        if sector and sector != "All":
            conditions.append(Company.sector == sector)

        if country:
            conditions.append(Company.country == country)

        if search:
            search_lower = f"%{search.lower()}%"
            conditions.append(
                or_(
                    Company.name.ilike(search_lower), Company.symbol.ilike(search_lower)
                )
            )

        if conditions:
            query = query.where(and_(*conditions))

        # Apply pagination
        query = query.offset(skip).limit(limit)

        # Execute query
        result = await db.execute(query)
        companies = result.scalars().all()

        # Convert to response format
        company_responses = []
        for i, company in enumerate(companies):
            # Generate mock price data for now (since we don't have real market data yet)
            base_price = 100.0 + hash(company.symbol) % 500  # Simple hash-based price
            change = (
                hash(company.symbol + "change") % 20
            ) - 10  # Random change between -10 and +10
            change_percent = (change / base_price) * 100

            company_responses.append(
                {
                    "id": i + 1,  # Simple sequential ID
                    "symbol": company.symbol,
                    "name": company.name,
                    "price": round(base_price, 2),
                    "change": round(change, 2),
                    "change_percent": round(change_percent, 2),
                    "sector": company.sector or "Unknown",
                    "market_cap": f"{company.market_cap / 1_000_000_000:.1f}B"
                    if company.market_cap
                    else "N/A",
                    "pe_ratio": 25.0,  # Mock PE ratio
                    "volume": f"{hash(company.symbol + 'vol') % 100}M",  # Mock volume
                    "description": company.description
                    or f"Information about {company.name}",
                    "created_at": company.created_at,
                    "updated_at": company.updated_at,
                }
            )

        return company_responses
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch companies: {str(e)}"
        )


@router.get("/{symbol}", response_model=CompanyResponse)
async def get_company(symbol: str, db: AsyncSession = Depends(get_db_session)):
    """Get a specific company by symbol"""
    try:
        # Mock company data
        mock_company = {
            "id": 1,
            "symbol": symbol.upper(),
            "name": f"{symbol.upper()} Inc.",
            "price": 175.43,
            "change": 2.15,
            "change_percent": 1.24,
            "sector": "Technology",
            "market_cap": "2.8T",
            "pe_ratio": 28.5,
            "volume": "45.2M",
            "description": f"Detailed information about {symbol.upper()} company.",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        return mock_company
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch company: {str(e)}"
        )


@router.get("/sectors/", response_model=List[str])
async def get_sectors(db: AsyncSession = Depends(get_db_session)):
    """Get all available sectors"""
    try:
        sectors = [
            "Technology",
            "Automotive",
            "Consumer Discretionary",
            "Healthcare",
            "Financial",
            "Energy",
            "Industrial",
            "Consumer Staples",
            "Utilities",
            "Real Estate",
        ]
        return sectors
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch sectors: {str(e)}"
        )


@router.post("/", response_model=CompanyResponse)
async def create_company(
    company: CompanyCreate, db: AsyncSession = Depends(get_db_session)
):
    """Create a new company"""
    try:
        # For now, return mock data
        new_company = {
            "id": 999,
            "symbol": company.symbol.upper(),
            "name": company.name,
            "price": 0.0,
            "change": 0.0,
            "change_percent": 0.0,
            "sector": company.sector,
            "market_cap": "N/A",
            "pe_ratio": 0.0,
            "volume": "0",
            "description": company.description,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        return new_company
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create company: {str(e)}"
        )


@router.put("/{symbol}", response_model=CompanyResponse)
async def update_company(
    symbol: str, company: CompanyUpdate, db: AsyncSession = Depends(get_db_session)
):
    """Update an existing company"""
    try:
        # For now, return mock data
        updated_company = {
            "id": 1,
            "symbol": symbol.upper(),
            "name": company.name or f"Updated {symbol.upper()}",
            "price": 175.43,
            "change": 2.15,
            "change_percent": 1.24,
            "sector": company.sector or "Technology",
            "market_cap": "2.8T",
            "pe_ratio": 28.5,
            "volume": "45.2M",
            "description": company.description
            or f"Updated description for {symbol.upper()}",
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        return updated_company
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update company: {str(e)}"
        )


@router.delete("/{symbol}")
async def delete_company(symbol: str, db: AsyncSession = Depends(get_db_session)):
    """Delete a company"""
    try:
        return {"message": f"Company {symbol.upper()} deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete company: {str(e)}"
        )
