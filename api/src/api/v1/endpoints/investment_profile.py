"""
Investment Profile API Endpoints
Tech-028: API Implementation
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from ....models.investment_profile import (
    InvestmentProfile,
    InvestmentProfileCreate,
    InvestmentProfileSummary,
    InvestmentProfileUpdate,
    ProfileAssessment,
)
from ....services.investment_profile import investment_profile_service

router = APIRouter()


@router.get("/health", summary="Investment Profile Health Check")
async def health_check():
    """Health check endpoint for investment profile service."""
    return {
        "status": "healthy",
        "service": "Investment Profile API",
        "version": "1.0.0",
        "endpoints": [
            "GET /assessment - Get assessment questions",
            "POST /profiles - Create investment profile",
            "GET /profiles - List user profiles",
            "GET /profiles/{id} - Get profile by ID",
            "PUT /profiles/{id} - Update profile",
            "DELETE /profiles/{id} - Delete profile",
        ],
    }


@router.get(
    "/assessment", response_model=ProfileAssessment, summary="Get Assessment Questions"
)
async def get_assessment_questions():
    """Get investment profile assessment questions."""
    try:
        questions = investment_profile_service.get_assessment_questions()
        return ProfileAssessment(
            questions=questions,
            total_questions=len(questions),
            estimated_time="5-10 minutes",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get assessment questions: {str(e)}"
        )


@router.post(
    "/profiles", response_model=InvestmentProfile, summary="Create Investment Profile"
)
async def create_investment_profile(profile_data: InvestmentProfileCreate):
    """Create a new investment profile."""
    try:
        profile = investment_profile_service.create_profile(profile_data)
        return profile
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create profile: {str(e)}"
        )


@router.get(
    "/profiles",
    response_model=List[InvestmentProfileSummary],
    summary="List User Profiles",
)
async def list_user_profiles(
    user_id: str = Query(..., description="User ID"),
    skip: int = Query(0, ge=0, description="Number of profiles to skip"),
    limit: int = Query(
        100, ge=1, le=1000, description="Maximum number of profiles to return"
    ),
):
    """List investment profiles for a user."""
    try:
        profiles = investment_profile_service.get_user_profiles(user_id)
        return profiles[skip : skip + limit]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list profiles: {str(e)}"
        )


@router.get(
    "/profiles/{profile_id}",
    response_model=InvestmentProfile,
    summary="Get Profile by ID",
)
async def get_investment_profile(profile_id: str):
    """Get investment profile by ID."""
    try:
        profile = investment_profile_service.get_profile(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        return profile
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get profile: {str(e)}")


@router.put(
    "/profiles/{profile_id}", response_model=InvestmentProfile, summary="Update Profile"
)
async def update_investment_profile(
    profile_id: str, update_data: InvestmentProfileUpdate
):
    """Update an investment profile."""
    try:
        profile = investment_profile_service.update_profile(profile_id, update_data)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        return profile
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update profile: {str(e)}"
        )


@router.delete("/profiles/{profile_id}", summary="Delete Profile")
async def delete_investment_profile(profile_id: str):
    """Delete an investment profile."""
    try:
        success = investment_profile_service.delete_profile(profile_id)
        if not success:
            raise HTTPException(status_code=404, detail="Profile not found")
        return {"message": "Profile deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete profile: {str(e)}"
        )


@router.post(
    "/profiles/{profile_id}/recalculate",
    response_model=InvestmentProfile,
    summary="Recalculate Profile",
)
async def recalculate_profile(profile_id: str):
    """Recalculate risk score and recommendations for a profile."""
    try:
        profile = investment_profile_service.get_profile(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        # Create update data from current profile
        update_data = InvestmentProfileUpdate(
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

        # Update profile (this will recalculate everything)
        updated_profile = investment_profile_service.update_profile(
            profile_id, update_data
        )
        return updated_profile
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to recalculate profile: {str(e)}"
        )


@router.get(
    "/profiles/{profile_id}/recommendations", summary="Get Profile Recommendations"
)
async def get_profile_recommendations(profile_id: str):
    """Get investment recommendations for a profile."""
    try:
        profile = investment_profile_service.get_profile(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        return {
            "profile_id": profile.id,
            "risk_score": profile.risk_score,
            "recommendations": profile.recommendations,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get recommendations: {str(e)}"
        )


@router.get("/profiles/{profile_id}/risk-analysis", summary="Get Risk Analysis")
async def get_risk_analysis(profile_id: str):
    """Get detailed risk analysis for a profile."""
    try:
        profile = investment_profile_service.get_profile(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")

        risk_score = profile.risk_score

        # Generate risk analysis
        risk_analysis = {
            "profile_id": profile.id,
            "risk_score": risk_score,
            "risk_interpretation": {
                "level": risk_score.risk_level,
                "description": _get_risk_description(risk_score.risk_level),
                "suitable_for": _get_suitable_investors(risk_score.risk_level),
                "typical_returns": _get_typical_returns(risk_score.risk_level),
                "typical_volatility": _get_typical_volatility(risk_score.risk_level),
            },
            "component_analysis": _analyze_components(risk_score.component_scores),
            "recommendations": profile.recommendations,
        }

        return risk_analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get risk analysis: {str(e)}"
        )


def _get_risk_description(risk_level: str) -> str:
    """Get risk level description."""
    descriptions = {
        "Conservative": "Low risk tolerance with focus on capital preservation and steady income.",
        "Moderate": "Balanced risk tolerance with mix of growth and income investments.",
        "Aggressive": "High risk tolerance with focus on maximum growth potential.",
    }
    return descriptions.get(risk_level, "Unknown risk level")


def _get_suitable_investors(risk_level: str) -> List[str]:
    """Get suitable investor types for risk level."""
    suitable = {
        "Conservative": [
            "Retirees seeking income",
            "Risk-averse investors",
            "Short-term goal savers",
            "Capital preservation focused",
        ],
        "Moderate": [
            "Balanced growth seekers",
            "Medium-term investors",
            "Income and growth focused",
            "Moderate risk tolerance",
        ],
        "Aggressive": [
            "Long-term growth investors",
            "High risk tolerance",
            "Maximum return seekers",
            "Experienced investors",
        ],
    }
    return suitable.get(risk_level, [])


def _get_typical_returns(risk_level: str) -> dict:
    """Get typical returns for risk level."""
    returns = {
        "Conservative": {"min": 3.0, "max": 6.0, "average": 4.5},
        "Moderate": {"min": 5.0, "max": 9.0, "average": 7.0},
        "Aggressive": {"min": 7.0, "max": 12.0, "average": 9.5},
    }
    return returns.get(risk_level, {})


def _get_typical_volatility(risk_level: str) -> dict:
    """Get typical volatility for risk level."""
    volatility = {
        "Conservative": {"min": 5.0, "max": 10.0, "average": 8.0},
        "Moderate": {"min": 10.0, "max": 15.0, "average": 12.0},
        "Aggressive": {"min": 15.0, "max": 25.0, "average": 20.0},
    }
    return volatility.get(risk_level, {})


def _analyze_components(component_scores: dict) -> dict:
    """Analyze individual component scores."""
    analysis = {}
    for component, score in component_scores.items():
        if score == 1:
            level = "Low"
            description = "Conservative approach"
        elif score == 2:
            level = "Medium"
            description = "Balanced approach"
        else:
            level = "High"
            description = "Aggressive approach"

        analysis[component] = {
            "score": score,
            "level": level,
            "description": description,
        }

    return analysis
