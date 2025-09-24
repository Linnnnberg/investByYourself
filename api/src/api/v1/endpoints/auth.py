#!/usr/bin/env python3
"""
Authentication API Endpoints for InvestByYourself
Tech-036: Authentication System Implementation

FastAPI endpoints for user authentication, registration, and session management.
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.database.connection import get_db_session
from src.services.auth_service import AuthService

router = APIRouter()
security = HTTPBearer()


# Pydantic models for API requests/responses
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordReset(BaseModel):
    token: str
    new_password: str


class EmailVerificationRequest(BaseModel):
    token: str


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    theme: Optional[str] = None
    risk_tolerance: Optional[str] = None
    investment_goals: Optional[str] = None
    time_horizon: Optional[str] = None
    investment_experience: Optional[str] = None
    age: Optional[int] = None
    annual_income: Optional[str] = None
    net_worth: Optional[str] = None
    employment_status: Optional[str] = None
    email_notifications: Optional[bool] = None
    price_alerts: Optional[bool] = None
    market_updates: Optional[bool] = None
    newsletter: Optional[bool] = None


# Dependency to get current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_session),
):
    """Get current authenticated user from JWT token."""
    try:
        import jwt

        from src.core.config import settings

        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
            )

        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        auth_service = AuthService(db)
        user = await auth_service.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )

        return user

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_data: UserRegister, db: AsyncSession = Depends(get_db_session)
):
    """Register a new user."""
    auth_service = AuthService(db)

    try:
        user = await auth_service.create_user(
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            full_name=user_data.full_name,
        )

        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            last_login=user.last_login,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}",
        )


@router.post("/login", response_model=TokenResponse)
async def login_user(login_data: UserLogin, db: AsyncSession = Depends(get_db_session)):
    """Login user and return JWT tokens."""
    auth_service = AuthService(db)

    user = await auth_service.authenticate_user(
        email=login_data.email, password=login_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    # Create tokens
    access_token = auth_service.create_access_token(
        data={"sub": user.id, "email": user.email, "username": user.username}
    )
    refresh_token = auth_service.create_refresh_token(
        data={"sub": user.id, "email": user.email, "username": user.username}
    )

    # Create session
    await auth_service.create_user_session(
        user_id=user.id, access_token=access_token, refresh_token=refresh_token
    )

    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=30 * 60,  # 30 minutes
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db_session)):
    """Refresh access token using refresh token."""
    try:
        import jwt

        from src.core.config import settings

        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
            )

        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        auth_service = AuthService(db)
        user = await auth_service.get_user_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        # Create new access token
        access_token = auth_service.create_access_token(
            data={"sub": user.id, "email": user.email, "username": user.username}
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,  # Keep same refresh token
            token_type="bearer",
            expires_in=30 * 60,
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired"
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )


@router.post("/logout")
async def logout_user(
    current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db_session)
):
    """Logout user and invalidate all sessions."""
    auth_service = AuthService(db)
    await auth_service.invalidate_all_user_sessions(current_user.id)

    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user=Depends(get_current_user)):
    """Get current user information."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
    )


@router.post("/password-reset-request")
async def request_password_reset(
    request_data: PasswordResetRequest, db: AsyncSession = Depends(get_db_session)
):
    """Request password reset token."""
    auth_service = AuthService(db)

    user = await auth_service.get_user_by_email(request_data.email)
    if not user:
        # Don't reveal if email exists
        return {"message": "If the email exists, a password reset link has been sent"}

    token = await auth_service.create_password_reset_token(user.id)

    # TODO: Send email with reset token
    # For now, return token in response (remove in production)
    return {
        "message": "Password reset token created",
        "token": token,  # Remove this in production
    }


@router.post("/password-reset")
async def reset_password(
    reset_data: PasswordReset, db: AsyncSession = Depends(get_db_session)
):
    """Reset password using token."""
    auth_service = AuthService(db)

    success = await auth_service.reset_password(
        token=reset_data.token, new_password=reset_data.new_password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    return {"message": "Password successfully reset"}


@router.post("/verify-email")
async def verify_email(
    verification_data: EmailVerificationRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """Verify email using token."""
    auth_service = AuthService(db)

    success = await auth_service.verify_email(verification_data.token)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )

    return {"message": "Email successfully verified"}


@router.post("/resend-verification")
async def resend_verification(
    current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db_session)
):
    """Resend email verification token."""
    if current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already verified"
        )

    auth_service = AuthService(db)
    token = await auth_service.create_email_verification_token(current_user.id)

    # TODO: Send email with verification token
    # For now, return token in response (remove in production)
    return {
        "message": "Verification token created",
        "token": token,  # Remove this in production
    }


@router.get("/profile")
async def get_user_profile(
    current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db_session)
):
    """Get user profile."""
    auth_service = AuthService(db)
    profile = await auth_service.get_user_profile(current_user.id)

    if not profile:
        return {"message": "Profile not found"}

    return {
        "user_id": profile.user_id,
        "risk_tolerance": profile.risk_tolerance,
        "investment_goals": profile.investment_goals,
        "time_horizon": profile.time_horizon,
        "investment_experience": profile.investment_experience,
        "age": profile.age,
        "annual_income": profile.annual_income,
        "net_worth": profile.net_worth,
        "employment_status": profile.employment_status,
        "email_notifications": profile.email_notifications,
        "price_alerts": profile.price_alerts,
        "market_updates": profile.market_updates,
        "newsletter": profile.newsletter,
        "created_at": profile.created_at,
        "updated_at": profile.updated_at,
    }


@router.put("/profile")
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Update user profile."""
    auth_service = AuthService(db)

    # Convert to dict and remove None values
    update_data = {k: v for k, v in profile_data.dict().items() if v is not None}

    profile = await auth_service.update_user_profile(current_user.id, update_data)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
        )

    return {"message": "Profile updated successfully"}
