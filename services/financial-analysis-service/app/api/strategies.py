"""
Strategies API Router
====================

API endpoints for investment strategy management.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

# Create router
router = APIRouter()


# Pydantic models for request/response
class StrategyBase(BaseModel):
    name: str
    description: Optional[str] = None
    strategy_type: str
    parameters: dict
    is_active: bool = True


class StrategyCreate(StrategyBase):
    user_id: int


class StrategyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[dict] = None
    is_active: Optional[bool] = None


class StrategyResponse(StrategyBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# In-memory storage for development (will be replaced with database)
strategies_db = {}
strategy_counter = 1


@router.post(
    "/strategies", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED
)
async def create_strategy(strategy: StrategyCreate):
    """Create a new investment strategy."""
    global strategy_counter

    # Validate strategy type
    valid_types = ["sector_rotation", "momentum", "hedge", "custom"]
    if strategy.strategy_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid strategy type. Must be one of: {valid_types}",
        )

    # Create strategy
    strategy_id = strategy_counter
    strategy_counter += 1

    now = datetime.utcnow()
    strategy_data = {
        "id": strategy_id,
        "user_id": strategy.user_id,
        "name": strategy.name,
        "description": strategy.description,
        "strategy_type": strategy.strategy_type,
        "parameters": strategy.parameters,
        "is_active": strategy.is_active,
        "created_at": now,
        "updated_at": now,
    }

    strategies_db[strategy_id] = strategy_data

    return StrategyResponse(**strategy_data)


@router.get("/strategies", response_model=List[StrategyResponse])
async def list_strategies(
    user_id: Optional[int] = None,
    strategy_type: Optional[str] = None,
    is_active: Optional[bool] = None,
):
    """List strategies with optional filtering."""
    strategies = list(strategies_db.values())

    # Apply filters
    if user_id is not None:
        strategies = [s for s in strategies if s["user_id"] == user_id]

    if strategy_type is not None:
        strategies = [s for s in strategies if s["strategy_type"] == strategy_type]

    if is_active is not None:
        strategies = [s for s in strategies if s["is_active"] == is_active]

    return [StrategyResponse(**s) for s in strategies]


@router.get("/strategies/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(strategy_id: int):
    """Get a specific strategy by ID."""
    if strategy_id not in strategies_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Strategy not found"
        )

    return StrategyResponse(**strategies_db[strategy_id])


@router.put("/strategies/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(strategy_id: int, strategy_update: StrategyUpdate):
    """Update an existing strategy."""
    if strategy_id not in strategies_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Strategy not found"
        )

    # Update fields
    current_strategy = strategies_db[strategy_id]
    update_data = strategy_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        current_strategy[field] = value

    current_strategy["updated_at"] = datetime.utcnow()

    return StrategyResponse(**current_strategy)


@router.delete("/strategies/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_strategy(strategy_id: int):
    """Delete a strategy."""
    if strategy_id not in strategies_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Strategy not found"
        )

    del strategies_db[strategy_id]
    return None


@router.get("/strategies/{strategy_id}/validate")
async def validate_strategy(strategy_id: int):
    """Validate a strategy's configuration."""
    if strategy_id not in strategies_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Strategy not found"
        )

    strategy = strategies_db[strategy_id]

    # Basic validation logic (will be enhanced)
    validation_result = {
        "strategy_id": strategy_id,
        "is_valid": True,
        "errors": [],
        "warnings": [],
        "validation_timestamp": datetime.utcnow().isoformat(),
    }

    # Check required parameters based on strategy type
    if strategy["strategy_type"] == "sector_rotation":
        required_params = ["rebalancing_frequency", "sectors"]
        for param in required_params:
            if param not in strategy["parameters"]:
                validation_result["is_valid"] = False
                validation_result["errors"].append(
                    f"Missing required parameter: {param}"
                )

    elif strategy["strategy_type"] == "momentum":
        required_params = ["lookback_period", "rebalancing_frequency"]
        for param in required_params:
            if param not in strategy["parameters"]:
                validation_result["is_valid"] = False
                validation_result["errors"].append(
                    f"Missing required parameter: {param}"
                )

    elif strategy["strategy_type"] == "hedge":
        required_params = ["trend_period", "volatility_lookback"]
        for param in required_params:
            if param not in strategy["parameters"]:
                validation_result["is_valid"] = False
                validation_result["errors"].append(
                    f"Missing required parameter: {param}"
                )

    return validation_result
