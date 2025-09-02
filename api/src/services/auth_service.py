#!/usr/bin/env python3
"""
InvestByYourself Authentication Service
Tech-028: API Implementation

Authentication service for user management and JWT token handling.
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

from src.core.config import settings
from src.core.exceptions import AuthenticationError, ValidationError
from src.core.logging import get_logger

logger = get_logger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCreate(BaseModel):
    """User creation model."""

    email: EmailStr
    password: str
    first_name: str
    last_name: str


class UserInDB(BaseModel):
    """User in database model."""

    id: str
    email: str
    hashed_password: str
    first_name: str
    last_name: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class TokenData(BaseModel):
    """Token data model."""

    user_id: Optional[str] = None
    email: Optional[str] = None


class AuthService:
    """Authentication service for user management and JWT handling."""

    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_minutes = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire, "type": "access"})

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str, token_type: str = "access") -> TokenData:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Check token type
            if payload.get("type") != token_type:
                raise AuthenticationError("Invalid token type")

            user_id: str = payload.get("sub")
            email: str = payload.get("email")

            if user_id is None or email is None:
                raise AuthenticationError("Invalid token payload")

            return TokenData(user_id=user_id, email=email)

        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            raise AuthenticationError("Invalid token")

    def generate_password_reset_token(self, email: str) -> str:
        """Generate password reset token."""
        data = {
            "email": email,
            "type": "password_reset",
            "exp": datetime.utcnow() + timedelta(hours=1),  # 1 hour expiry
        }
        return jwt.encode(data, self.secret_key, algorithm=self.algorithm)

    def verify_password_reset_token(self, token: str) -> str:
        """Verify password reset token and return email."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            if payload.get("type") != "password_reset":
                raise AuthenticationError("Invalid token type")

            email: str = payload.get("email")
            if email is None:
                raise AuthenticationError("Invalid token payload")

            return email

        except JWTError as e:
            logger.warning(f"Password reset token verification failed: {e}")
            raise AuthenticationError("Invalid or expired token")

    def validate_password_strength(self, password: str) -> bool:
        """Validate password strength."""
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long")

        if not any(c.isupper() for c in password):
            raise ValidationError("Password must contain at least one uppercase letter")

        if not any(c.islower() for c in password):
            raise ValidationError("Password must contain at least one lowercase letter")

        if not any(c.isdigit() for c in password):
            raise ValidationError("Password must contain at least one digit")

        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            raise ValidationError(
                "Password must contain at least one special character"
            )

        return True

    def generate_user_id(self) -> str:
        """Generate a unique user ID."""
        return f"user_{secrets.token_urlsafe(16)}"

    def create_user(self, user_data: UserCreate) -> UserInDB:
        """Create a new user."""
        # Validate password strength
        self.validate_password_strength(user_data.password)

        # Hash password
        hashed_password = self.get_password_hash(user_data.password)

        # Generate user ID
        user_id = self.generate_user_id()

        # Create user object
        user = UserInDB(
            id=user_id,
            email=user_data.email,
            hashed_password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            is_active=True,
            is_verified=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        logger.info(f"User created: {user.email}")
        return user

    def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        """Authenticate a user with email and password."""
        # TODO: Replace with actual database lookup
        # For now, return None to indicate authentication failed
        logger.warning(f"Authentication attempt for {email} - database not implemented")
        return None

    def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email."""
        # TODO: Replace with actual database lookup
        logger.warning(f"User lookup for {email} - database not implemented")
        return None

    def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Get user by ID."""
        # TODO: Replace with actual database lookup
        logger.warning(f"User lookup for ID {user_id} - database not implemented")
        return None

    def update_user(
        self, user_id: str, update_data: Dict[str, Any]
    ) -> Optional[UserInDB]:
        """Update user information."""
        # TODO: Replace with actual database update
        logger.warning(f"User update for ID {user_id} - database not implemented")
        return None

    def change_password(
        self, user_id: str, old_password: str, new_password: str
    ) -> bool:
        """Change user password."""
        # TODO: Implement password change logic
        # 1. Get user from database
        # 2. Verify old password
        # 3. Validate new password strength
        # 4. Hash new password
        # 5. Update in database
        logger.warning(f"Password change for user {user_id} - database not implemented")
        return False

    def reset_password(self, email: str, new_password: str) -> bool:
        """Reset user password."""
        # TODO: Implement password reset logic
        # 1. Get user by email
        # 2. Validate new password strength
        # 3. Hash new password
        # 4. Update in database
        logger.warning(f"Password reset for {email} - database not implemented")
        return False


# Create global auth service instance
auth_service = AuthService()
