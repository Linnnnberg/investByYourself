"""
Investment Profile Service
Tech-028: API Implementation
"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from ..models.investment_profile import (
    Diversification,
    FinancialGoals,
    IncomeNeeds,
    InvestmentExperience,
    InvestmentProfile,
    InvestmentProfileCreate,
    InvestmentProfileSummary,
    InvestmentProfileUpdate,
    InvestmentRecommendation,
    LiquidityNeeds,
    MarketVolatility,
    Rebalancing,
    RiskScore,
    RiskTolerance,
    TimeHorizon,
)


class InvestmentProfileService:
    """Investment profile service for risk assessment and recommendations."""

    def __init__(self):
        """Initialize the investment profile service."""
        self.profiles: Dict[str, InvestmentProfile] = {}

    def calculate_risk_score(self, profile_data: InvestmentProfileCreate) -> RiskScore:
        """Calculate risk score based on profile data."""
        # Risk scoring weights (1-3 scale)
        scores = {
            "risk_tolerance": self._get_risk_tolerance_score(
                profile_data.risk_tolerance
            ),
            "time_horizon": self._get_time_horizon_score(profile_data.time_horizon),
            "investment_experience": self._get_experience_score(
                profile_data.investment_experience
            ),
            "financial_goals": self._get_goals_score(profile_data.financial_goals),
            "liquidity_needs": self._get_liquidity_score(profile_data.liquidity_needs),
            "income_needs": self._get_income_score(profile_data.income_needs),
            "market_volatility": self._get_volatility_score(
                profile_data.market_volatility
            ),
            "diversification": self._get_diversification_score(
                profile_data.diversification
            ),
            "rebalancing": self._get_rebalancing_score(profile_data.rebalancing),
        }

        total_score = sum(scores.values())
        risk_percentage = (total_score / 27) * 100

        # Determine risk level
        if total_score <= 12:
            risk_level = "Conservative"
        elif total_score <= 18:
            risk_level = "Moderate"
        else:
            risk_level = "Aggressive"

        return RiskScore(
            total_score=total_score,
            risk_level=risk_level,
            risk_percentage=risk_percentage,
            component_scores=scores,
        )

    def generate_recommendations(
        self, risk_score: RiskScore
    ) -> List[InvestmentRecommendation]:
        """Generate investment recommendations based on risk score."""
        recommendations = []

        if risk_score.total_score <= 12:
            # Conservative recommendations
            recommendations.extend(
                [
                    InvestmentRecommendation(
                        strategy_name="Conservative Portfolio",
                        description="Low-risk portfolio focused on capital preservation and steady income",
                        asset_allocation={
                            "Bonds": 60.0,
                            "Large-cap Stocks": 30.0,
                            "Cash": 10.0,
                        },
                        expected_return=4.5,
                        expected_volatility=8.0,
                        suitability_score=95.0,
                    ),
                    InvestmentRecommendation(
                        strategy_name="Income Focus",
                        description="Dividend-focused strategy for regular income generation",
                        asset_allocation={
                            "Dividend Stocks": 50.0,
                            "Bond Funds": 40.0,
                            "REITs": 10.0,
                        },
                        expected_return=5.2,
                        expected_volatility=10.0,
                        suitability_score=85.0,
                    ),
                ]
            )
        elif risk_score.total_score <= 18:
            # Moderate recommendations
            recommendations.extend(
                [
                    InvestmentRecommendation(
                        strategy_name="Balanced Portfolio",
                        description="Balanced approach with growth and income components",
                        asset_allocation={
                            "Stocks": 50.0,
                            "Bonds": 40.0,
                            "Alternatives": 10.0,
                        },
                        expected_return=7.0,
                        expected_volatility=12.0,
                        suitability_score=90.0,
                    ),
                    InvestmentRecommendation(
                        strategy_name="Growth & Income",
                        description="Mix of growth stocks and dividend payers for balanced returns",
                        asset_allocation={
                            "Growth Stocks": 40.0,
                            "Dividend Stocks": 30.0,
                            "Bonds": 20.0,
                            "International": 10.0,
                        },
                        expected_return=7.5,
                        expected_volatility=14.0,
                        suitability_score=80.0,
                    ),
                ]
            )
        else:
            # Aggressive recommendations
            recommendations.extend(
                [
                    InvestmentRecommendation(
                        strategy_name="Growth Portfolio",
                        description="High-growth strategy with higher risk tolerance",
                        asset_allocation={
                            "Stocks": 70.0,
                            "Alternatives": 20.0,
                            "Bonds": 10.0,
                        },
                        expected_return=9.5,
                        expected_volatility=18.0,
                        suitability_score=95.0,
                    ),
                    InvestmentRecommendation(
                        strategy_name="Aggressive Growth",
                        description="Maximum growth potential with small-cap and international exposure",
                        asset_allocation={
                            "Small-cap Stocks": 30.0,
                            "International Stocks": 25.0,
                            "Growth Stocks": 25.0,
                            "Alternatives": 15.0,
                            "Bonds": 5.0,
                        },
                        expected_return=11.0,
                        expected_volatility=22.0,
                        suitability_score=85.0,
                    ),
                ]
            )

        return recommendations

    def create_profile(
        self, profile_data: InvestmentProfileCreate
    ) -> InvestmentProfile:
        """Create a new investment profile."""
        # Calculate risk score
        risk_score = self.calculate_risk_score(profile_data)

        # Generate recommendations
        recommendations = self.generate_recommendations(risk_score)

        # Create profile
        profile = InvestmentProfile(
            user_id=profile_data.user_id,
            risk_tolerance=profile_data.risk_tolerance,
            time_horizon=profile_data.time_horizon,
            investment_experience=profile_data.investment_experience,
            financial_goals=profile_data.financial_goals,
            liquidity_needs=profile_data.liquidity_needs,
            income_needs=profile_data.income_needs,
            market_volatility=profile_data.market_volatility,
            diversification=profile_data.diversification,
            rebalancing=profile_data.rebalancing,
            risk_score=risk_score,
            recommendations=recommendations,
        )

        # Store profile
        self.profiles[str(profile.id)] = profile

        return profile

    def get_profile(self, profile_id: str) -> Optional[InvestmentProfile]:
        """Get investment profile by ID."""
        return self.profiles.get(profile_id)

    def get_user_profiles(self, user_id: str) -> List[InvestmentProfileSummary]:
        """Get all profiles for a user."""
        user_profiles = [
            profile for profile in self.profiles.values() if profile.user_id == user_id
        ]

        return [
            InvestmentProfileSummary(
                id=profile.id,
                user_id=profile.user_id,
                risk_level=profile.risk_score.risk_level,
                risk_score=profile.risk_score.total_score,
                primary_strategy=(
                    profile.recommendations[0].strategy_name
                    if profile.recommendations
                    else "No Strategy"
                ),
                created_at=profile.created_at,
                updated_at=profile.updated_at,
            )
            for profile in user_profiles
        ]

    def update_profile(
        self, profile_id: str, update_data: InvestmentProfileUpdate
    ) -> Optional[InvestmentProfile]:
        """Update an investment profile."""
        profile = self.profiles.get(profile_id)
        if not profile:
            return None

        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(profile, field, value)

        # Recalculate risk score and recommendations
        profile_data = InvestmentProfileCreate(
            user_id=profile.user_id,
            risk_tolerance=profile.risk_tolerance,
            time_horizon=profile.time_horizon,
            investment_experience=profile.investment_experience,
            financial_goals=profile.financial_goals,
            liquidity_needs=profile.liquidity_needs,
            income_needs=profile.income_needs,
            market_volatility=profile.market_volatility,
            diversification=profile.diversification,
            rebalancing=profile.rebalancing,
        )

        profile.risk_score = self.calculate_risk_score(profile_data)
        profile.recommendations = self.generate_recommendations(profile.risk_score)
        profile.updated_at = datetime.utcnow()

        return profile

    def delete_profile(self, profile_id: str) -> bool:
        """Delete an investment profile."""
        if profile_id in self.profiles:
            del self.profiles[profile_id]
            return True
        return False

    def get_assessment_questions(self) -> List[Dict]:
        """Get investment profile assessment questions."""
        return [
            {
                "id": "risk_tolerance",
                "title": "Risk Tolerance",
                "description": "How comfortable are you with investment risk?",
                "options": [
                    {
                        "value": "conservative",
                        "label": "Conservative",
                        "description": "I prefer stable, low-risk investments with predictable returns",
                        "score": 1,
                    },
                    {
                        "value": "moderate",
                        "label": "Moderate",
                        "description": "I can handle some risk for potentially higher returns",
                        "score": 2,
                    },
                    {
                        "value": "aggressive",
                        "label": "Aggressive",
                        "description": "I am comfortable with high risk for potentially high returns",
                        "score": 3,
                    },
                ],
            },
            {
                "id": "time_horizon",
                "title": "Investment Time Horizon",
                "description": "How long do you plan to invest?",
                "options": [
                    {
                        "value": "short",
                        "label": "Short-term (1-3 years)",
                        "description": "I need access to my money within the next few years",
                        "score": 1,
                    },
                    {
                        "value": "medium",
                        "label": "Medium-term (3-10 years)",
                        "description": "I can invest for several years before needing the money",
                        "score": 2,
                    },
                    {
                        "value": "long",
                        "label": "Long-term (10+ years)",
                        "description": "I am investing for retirement or long-term goals",
                        "score": 3,
                    },
                ],
            },
            {
                "id": "investment_experience",
                "title": "Investment Experience",
                "description": "How experienced are you with investing?",
                "options": [
                    {
                        "value": "beginner",
                        "label": "Beginner",
                        "description": "I am new to investing and prefer simple strategies",
                        "score": 1,
                    },
                    {
                        "value": "intermediate",
                        "label": "Intermediate",
                        "description": "I have some experience and understand basic concepts",
                        "score": 2,
                    },
                    {
                        "value": "advanced",
                        "label": "Advanced",
                        "description": "I am experienced and comfortable with complex strategies",
                        "score": 3,
                    },
                ],
            },
            {
                "id": "financial_goals",
                "title": "Financial Goals",
                "description": "What is your primary investment objective?",
                "options": [
                    {
                        "value": "preservation",
                        "label": "Capital Preservation",
                        "description": "I want to protect my money from inflation",
                        "score": 1,
                    },
                    {
                        "value": "growth",
                        "label": "Balanced Growth",
                        "description": "I want steady growth with some risk",
                        "score": 2,
                    },
                    {
                        "value": "aggressive_growth",
                        "label": "Aggressive Growth",
                        "description": "I want maximum growth potential",
                        "score": 3,
                    },
                ],
            },
            {
                "id": "liquidity_needs",
                "title": "Liquidity Needs",
                "description": "How quickly might you need access to your investments?",
                "options": [
                    {
                        "value": "high",
                        "label": "High Liquidity",
                        "description": "I might need quick access to my money",
                        "score": 1,
                    },
                    {
                        "value": "medium",
                        "label": "Medium Liquidity",
                        "description": "I can plan ahead for most cash needs",
                        "score": 2,
                    },
                    {
                        "value": "low",
                        "label": "Low Liquidity",
                        "description": "I rarely need quick access to invested funds",
                        "score": 3,
                    },
                ],
            },
            {
                "id": "income_needs",
                "title": "Income Needs",
                "description": "Do you need regular income from your investments?",
                "options": [
                    {
                        "value": "high",
                        "label": "High Income",
                        "description": "I need regular income to cover expenses",
                        "score": 1,
                    },
                    {
                        "value": "medium",
                        "label": "Some Income",
                        "description": "I would like some income but can reinvest",
                        "score": 2,
                    },
                    {
                        "value": "low",
                        "label": "Low Income",
                        "description": "I prefer growth over income",
                        "score": 3,
                    },
                ],
            },
            {
                "id": "market_volatility",
                "title": "Market Volatility",
                "description": "How do you react to market volatility?",
                "options": [
                    {
                        "value": "avoid",
                        "label": "Avoid Volatility",
                        "description": "I prefer stable, predictable investments",
                        "score": 1,
                    },
                    {
                        "value": "tolerate",
                        "label": "Tolerate Volatility",
                        "description": "I can handle some ups and downs",
                        "score": 2,
                    },
                    {
                        "value": "embrace",
                        "label": "Embrace Volatility",
                        "description": "I see volatility as opportunity",
                        "score": 3,
                    },
                ],
            },
            {
                "id": "diversification",
                "title": "Diversification Preference",
                "description": "How do you prefer to diversify your investments?",
                "options": [
                    {
                        "value": "concentrated",
                        "label": "Concentrated",
                        "description": "I prefer to focus on a few strong investments",
                        "score": 1,
                    },
                    {
                        "value": "balanced",
                        "label": "Balanced",
                        "description": "I want a mix of different types of investments",
                        "score": 2,
                    },
                    {
                        "value": "diversified",
                        "label": "Highly Diversified",
                        "description": "I want broad diversification across many assets",
                        "score": 3,
                    },
                ],
            },
            {
                "id": "rebalancing",
                "title": "Portfolio Rebalancing",
                "description": "How actively do you want to manage your portfolio?",
                "options": [
                    {
                        "value": "passive",
                        "label": "Passive",
                        "description": "I prefer set-and-forget strategies",
                        "score": 1,
                    },
                    {
                        "value": "moderate",
                        "label": "Moderate",
                        "description": "I want some control but not constant monitoring",
                        "score": 2,
                    },
                    {
                        "value": "active",
                        "label": "Active",
                        "description": "I want to actively manage and adjust my portfolio",
                        "score": 3,
                    },
                ],
            },
        ]

    # Private helper methods for scoring
    def _get_risk_tolerance_score(self, risk_tolerance: RiskTolerance) -> int:
        """Get risk tolerance score."""
        return {"conservative": 1, "moderate": 2, "aggressive": 3}[risk_tolerance.value]

    def _get_time_horizon_score(self, time_horizon: TimeHorizon) -> int:
        """Get time horizon score."""
        return {"short": 1, "medium": 2, "long": 3}[time_horizon.value]

    def _get_experience_score(self, experience: InvestmentExperience) -> int:
        """Get investment experience score."""
        return {"beginner": 1, "intermediate": 2, "advanced": 3}[experience.value]

    def _get_goals_score(self, goals: FinancialGoals) -> int:
        """Get financial goals score."""
        return {"preservation": 1, "growth": 2, "aggressive_growth": 3}[goals.value]

    def _get_liquidity_score(self, liquidity: LiquidityNeeds) -> int:
        """Get liquidity needs score."""
        return {"high": 1, "medium": 2, "low": 3}[liquidity.value]

    def _get_income_score(self, income: IncomeNeeds) -> int:
        """Get income needs score."""
        return {"high": 1, "medium": 2, "low": 3}[income.value]

    def _get_volatility_score(self, volatility: MarketVolatility) -> int:
        """Get market volatility score."""
        return {"avoid": 1, "tolerate": 2, "embrace": 3}[volatility.value]

    def _get_diversification_score(self, diversification: Diversification) -> int:
        """Get diversification score."""
        return {"concentrated": 1, "balanced": 2, "diversified": 3}[
            diversification.value
        ]

    def _get_rebalancing_score(self, rebalancing: Rebalancing) -> int:
        """Get rebalancing score."""
        return {"passive": 1, "moderate": 2, "active": 3}[rebalancing.value]


# Global service instance
investment_profile_service = InvestmentProfileService()
