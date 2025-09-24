"""
Investment Profile Models
Tech-028: API Implementation
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class RiskTolerance(str, Enum):
    """Risk tolerance levels."""

    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class TimeHorizon(str, Enum):
    """Investment time horizon."""

    SHORT = "short"  # 1-3 years
    MEDIUM = "medium"  # 3-10 years
    LONG = "long"  # 10+ years


class InvestmentExperience(str, Enum):
    """Investment experience levels."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class FinancialGoals(str, Enum):
    """Financial goals."""

    PRESERVATION = "preservation"
    GROWTH = "growth"
    AGGRESSIVE_GROWTH = "aggressive_growth"


class LiquidityNeeds(str, Enum):
    """Liquidity needs."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IncomeNeeds(str, Enum):
    """Income needs."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class MarketVolatility(str, Enum):
    """Market volatility tolerance."""

    AVOID = "avoid"
    TOLERATE = "tolerate"
    EMBRACE = "embrace"


class Diversification(str, Enum):
    """Diversification preference."""

    CONCENTRATED = "concentrated"
    BALANCED = "balanced"
    DIVERSIFIED = "diversified"


class Rebalancing(str, Enum):
    """Portfolio rebalancing preference."""

    PASSIVE = "passive"
    MODERATE = "moderate"
    ACTIVE = "active"


class InvestmentProfileCreate(BaseModel):
    """Investment profile creation model."""

    user_id: str = Field(..., description="User ID")
    risk_tolerance: RiskTolerance = Field(..., description="Risk tolerance level")
    time_horizon: TimeHorizon = Field(..., description="Investment time horizon")
    investment_experience: InvestmentExperience = Field(
        ..., description="Investment experience level"
    )
    financial_goals: FinancialGoals = Field(..., description="Primary financial goal")
    liquidity_needs: LiquidityNeeds = Field(..., description="Liquidity needs")
    income_needs: IncomeNeeds = Field(..., description="Income needs")
    market_volatility: MarketVolatility = Field(
        ..., description="Market volatility tolerance"
    )
    diversification: Diversification = Field(
        ..., description="Diversification preference"
    )
    rebalancing: Rebalancing = Field(
        ..., description="Portfolio rebalancing preference"
    )


class InvestmentProfileUpdate(BaseModel):
    """Investment profile update model."""

    risk_tolerance: Optional[RiskTolerance] = None
    time_horizon: Optional[TimeHorizon] = None
    investment_experience: Optional[InvestmentExperience] = None
    financial_goals: Optional[FinancialGoals] = None
    liquidity_needs: Optional[LiquidityNeeds] = None
    income_needs: Optional[IncomeNeeds] = None
    market_volatility: Optional[MarketVolatility] = None
    diversification: Optional[Diversification] = None
    rebalancing: Optional[Rebalancing] = None


class RiskScore(BaseModel):
    """Risk score calculation result."""

    total_score: int = Field(..., description="Total risk score (9-27)")
    risk_level: str = Field(
        ..., description="Risk level (Conservative/Moderate/Aggressive)"
    )
    risk_percentage: float = Field(..., description="Risk percentage (0-100)")
    component_scores: Dict[str, int] = Field(
        ..., description="Individual component scores"
    )


class InvestmentRecommendation(BaseModel):
    """Investment recommendation based on profile."""

    strategy_name: str = Field(..., description="Recommended strategy name")
    description: str = Field(..., description="Strategy description")
    asset_allocation: Dict[str, float] = Field(
        ..., description="Recommended asset allocation"
    )
    expected_return: float = Field(..., description="Expected annual return (%)")
    expected_volatility: float = Field(..., description="Expected volatility (%)")
    suitability_score: float = Field(..., description="Suitability score (0-100)")


class InvestmentProfile(BaseModel):
    """Investment profile model."""

    id: UUID = Field(default_factory=uuid4, description="Profile ID")
    user_id: str = Field(..., description="User ID")
    risk_tolerance: RiskTolerance = Field(..., description="Risk tolerance level")
    time_horizon: TimeHorizon = Field(..., description="Investment time horizon")
    investment_experience: InvestmentExperience = Field(
        ..., description="Investment experience level"
    )
    financial_goals: FinancialGoals = Field(..., description="Primary financial goal")
    liquidity_needs: LiquidityNeeds = Field(..., description="Liquidity needs")
    income_needs: IncomeNeeds = Field(..., description="Income needs")
    market_volatility: MarketVolatility = Field(
        ..., description="Market volatility tolerance"
    )
    diversification: Diversification = Field(
        ..., description="Diversification preference"
    )
    rebalancing: Rebalancing = Field(
        ..., description="Portfolio rebalancing preference"
    )
    risk_score: RiskScore = Field(..., description="Calculated risk score")
    recommendations: List[InvestmentRecommendation] = Field(
        ..., description="Investment recommendations"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )


class InvestmentProfileSummary(BaseModel):
    """Investment profile summary for listing."""

    id: UUID = Field(..., description="Profile ID")
    user_id: str = Field(..., description="User ID")
    risk_level: str = Field(..., description="Risk level")
    risk_score: int = Field(..., description="Total risk score")
    primary_strategy: str = Field(..., description="Primary recommended strategy")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class ProfileQuestion(BaseModel):
    """Investment profile question model."""

    id: str = Field(..., description="Question ID")
    title: str = Field(..., description="Question title")
    description: str = Field(..., description="Question description")
    options: List[Dict[str, Any]] = Field(..., description="Answer options")


class ProfileAssessment(BaseModel):
    """Profile assessment model."""

    questions: List[ProfileQuestion] = Field(..., description="Assessment questions")
    total_questions: int = Field(..., description="Total number of questions")
    estimated_time: str = Field(..., description="Estimated completion time")
