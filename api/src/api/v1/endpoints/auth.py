#!/usr/bin/env python3
"""
InvestByYourself API Authentication Endpoints
Tech-028: API Implementation

Authentication and authorization endpoints for user management.
"""

from datetime import datetime, timedelta
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.exceptions import AuthenticationError, ValidationError
from src.core.logging import get_logger
from src.services.auth_service import UserCreate, auth_service
from src.services.database import db_service, get_database_session

logger = get_logger(__name__)

# Create router
router = APIRouter()

# Security scheme
security = HTTPBearer()


# Pydantic models
class UserRegister(BaseModel):
    """User registration model."""

    email: EmailStr
    password: str
    first_name: str
    last_name: str


class UserLogin(BaseModel):
    """User login model."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response model."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserProfile(BaseModel):
    """User profile model."""

    id: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PasswordReset(BaseModel):
    """Password reset model."""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation model."""

    token: str
    new_password: str


# Authentication endpoints
@router.post("/register", response_model=TokenResponse)
async def register_user(
    user_data: UserRegister, db: Session = Depends(get_database_session)
) -> Dict[str, Any]:
    """
    Register a new user.

    Creates a new user account and returns authentication tokens.
    """
    try:
        logger.info(f"User registration attempt: {user_data.email}")

        # Check if email already exists
        if db_service.check_email_exists(db, user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Create user
        user_create = UserCreate(
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
        )

        user = auth_service.create_user(user_create)

        # Save user to database
        user_dict = user.dict()
        user_dict["hashed_password"] = user.hashed_password
        del user_dict["id"]  # Let database generate ID

        db_user = db_service.create_user(db, user_dict)

        # Generate JWT tokens
        token_data = {"sub": db_user.id, "email": db_user.email}
        access_token = auth_service.create_access_token(token_data)
        refresh_token = auth_service.create_refresh_token(token_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    except ValidationError as e:
        logger.warning(f"Registration validation error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed",
        )


@router.post("/login", response_model=TokenResponse)
async def login_user(
    credentials: UserLogin, db: Session = Depends(get_database_session)
) -> Dict[str, Any]:
    """
    Authenticate user and return tokens.

    Validates user credentials and returns JWT access and refresh tokens.
    """
    try:
        logger.info(f"User login attempt: {credentials.email}")

        # Get user from database
        db_user = db_service.get_user_by_email(db, credentials.email)
        if not db_user:
            raise AuthenticationError("Invalid email or password")

        # Check if user is active
        if not db_user.is_active:
            raise AuthenticationError("Account is deactivated")

        # Verify password
        if not auth_service.verify_password(
            credentials.password, db_user.hashed_password
        ):
            raise AuthenticationError("Invalid email or password")

        # Generate JWT tokens
        token_data = {"sub": db_user.id, "email": db_user.email}
        access_token = auth_service.create_access_token(token_data)
        refresh_token = auth_service.create_refresh_token(token_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    except AuthenticationError as e:
        logger.warning(f"Authentication failed: {e.message}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message)
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_database_session),
) -> Dict[str, Any]:
    """
    Refresh access token using refresh token.

    Validates refresh token and returns new access token.
    """
    try:
        refresh_token = credentials.credentials
        logger.info("Token refresh attempt")

        # Verify refresh token
        token_data = auth_service.verify_token(refresh_token, "refresh")

        # Get user from database
        db_user = db_service.get_user_by_id(db, token_data.user_id)
        if not db_user or not db_user.is_active:
            raise AuthenticationError("Invalid refresh token")

        # Generate new tokens
        new_token_data = {"sub": db_user.id, "email": db_user.email}
        new_access_token = auth_service.create_access_token(new_token_data)
        new_refresh_token = auth_service.create_refresh_token(new_token_data)

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    except AuthenticationError as e:
        logger.warning(f"Token refresh failed: {e.message}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message)
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed",
        )


@router.post("/logout")
async def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, str]:
    """
    Logout user and invalidate tokens.

    Invalidates the user's access and refresh tokens.
    """
    try:
        access_token = credentials.credentials
        logger.info("User logout")

        # TODO: Implement logout logic
        # - Add token to blacklist
        # - Clear user session

        return {"message": "Successfully logged out"}

    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Logout failed"
        )


@router.get("/profile", response_model=UserProfile)
async def get_user_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_database_session),
) -> Dict[str, Any]:
    """
    Get current user profile.

    Returns the authenticated user's profile information.
    """
    try:
        access_token = credentials.credentials
        logger.info("Get user profile")

        # Verify access token
        token_data = auth_service.verify_token(access_token, "access")

        # Get user from database
        db_user = db_service.get_user_by_id(db, token_data.user_id)
        if not db_user:
            raise AuthenticationError("User not found")

        return {
            "id": db_user.id,
            "email": db_user.email,
            "first_name": db_user.first_name,
            "last_name": db_user.last_name,
            "is_active": db_user.is_active,
            "created_at": db_user.created_at,
            "updated_at": db_user.updated_at,
        }

    except AuthenticationError as e:
        logger.warning(f"Profile access failed: {e.message}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message)
    except Exception as e:
        logger.error(f"Profile retrieval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile retrieval failed",
        )


@router.put("/profile", response_model=UserProfile)
async def update_user_profile(
    profile_data: Dict[str, Any],
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_database_session),
) -> Dict[str, Any]:
    """
    Update current user profile.

    Updates the authenticated user's profile information.
    """
    try:
        access_token = credentials.credentials
        logger.info("Update user profile")

        # Verify access token
        token_data = auth_service.verify_token(access_token, "access")

        # Get user from database
        db_user = db_service.get_user_by_id(db, token_data.user_id)
        if not db_user:
            raise AuthenticationError("User not found")

        # Prepare update data (exclude sensitive fields)
        update_data = {}
        allowed_fields = ["first_name", "last_name"]

        for field in allowed_fields:
            if field in profile_data:
                update_data[field] = profile_data[field]

        # Update user in database
        updated_user = db_service.update_user(db, token_data.user_id, update_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update profile",
            )

        return {
            "id": updated_user.id,
            "email": updated_user.email,
            "first_name": updated_user.first_name,
            "last_name": updated_user.last_name,
            "is_active": updated_user.is_active,
            "created_at": updated_user.created_at,
            "updated_at": updated_user.updated_at,
        }

    except AuthenticationError as e:
        logger.warning(f"Profile update failed: {e.message}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message)
    except ValidationError as e:
        logger.warning(f"Profile validation failed: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message
        )
    except Exception as e:
        logger.error(f"Profile update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed",
        )


@router.post("/forgot-password")
async def forgot_password(
    reset_data: PasswordReset, db: Session = Depends(get_database_session)
) -> Dict[str, str]:
    """
    Request password reset.

    Sends password reset email to the user.
    """
    try:
        logger.info(f"Password reset request: {reset_data.email}")

        # Check if user exists
        db_user = db_service.get_user_by_email(db, reset_data.email)
        if not db_user:
            # Don't reveal if email exists or not for security
            return {
                "message": "If the email exists, a password reset link has been sent"
            }

        # Generate reset token
        reset_token = auth_service.generate_password_reset_token(reset_data.email)

        # Store reset token in database
        from datetime import datetime, timedelta

        expires_at = datetime.utcnow() + timedelta(hours=1)
        db_service.create_password_reset_token(db, db_user.id, reset_token, expires_at)

        # TODO: Send reset email with token
        # For now, just log the token (in production, send via email)
        logger.info(f"Password reset token for {reset_data.email}: {reset_token}")

        return {"message": "If the email exists, a password reset link has been sent"}

    except Exception as e:
        logger.error(f"Password reset error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed",
        )


@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordResetConfirm, db: Session = Depends(get_database_session)
) -> Dict[str, str]:
    """
    Reset password with token.

    Resets user password using the provided reset token.
    """
    try:
        logger.info("Password reset confirmation")

        # Verify reset token
        email = auth_service.verify_password_reset_token(reset_data.token)

        # Get reset token from database
        reset_token_record = db_service.get_password_reset_token(db, reset_data.token)
        if not reset_token_record:
            raise AuthenticationError("Invalid or expired reset token")

        # Get user
        db_user = db_service.get_user_by_id(db, reset_token_record.user_id)
        if not db_user:
            raise AuthenticationError("User not found")

        # Validate new password strength
        auth_service.validate_password_strength(reset_data.new_password)

        # Hash new password
        new_hashed_password = auth_service.get_password_hash(reset_data.new_password)

        # Update user password
        update_data = {"hashed_password": new_hashed_password}
        updated_user = db_service.update_user(db, db_user.id, update_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update password",
            )

        # Mark reset token as used
        db_service.mark_password_reset_token_used(db, reset_data.token)

        logger.info(f"Password reset successful for user: {email}")
        return {"message": "Password reset successfully"}

    except AuthenticationError as e:
        logger.warning(f"Password reset failed: {e.message}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message)
    except ValidationError as e:
        logger.warning(f"Password validation failed: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message
        )
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed",
        )
