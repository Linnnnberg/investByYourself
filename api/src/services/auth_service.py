#!/usr/bin/env python3
"""
Authentication Service for InvestByYourself
Tech-036: Authentication System Implementation

Service layer for user authentication, JWT token management, and user operations.
"""

import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple

import jwt
from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..core.config import settings
from ..models.auth import (
    EmailVerification,
    PasswordReset,
    User,
    UserProfile,
    UserSession,
)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


class AuthService:
    """Authentication service for user management and JWT tokens."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # Password utilities
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    # User management
    async def create_user(
        self,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None,
    ) -> User:
        """Create a new user."""
        # Check if user already exists
        existing_user = await self.get_user_by_email(email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        existing_username = await self.get_user_by_username(username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken"
            )

        # Create user
        user_id = str(uuid.uuid4())
        hashed_password = self.get_password_hash(password)

        user = User(
            id=user_id,
            email=email,
            username=username,
            hashed_password=hashed_password,
            full_name=full_name,
            is_active=True,
            is_verified=False,
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        # Create user profile
        profile = UserProfile(
            id=str(uuid.uuid4()),
            user_id=user_id,
        )
        self.db.add(profile)
        await self.db.commit()

        return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user

    # JWT token management
    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, data: dict) -> str:
        """Create JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    async def create_user_session(
        self,
        user_id: str,
        access_token: str,
        refresh_token: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> UserSession:
        """Create a new user session."""
        session_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        # Hash tokens for storage
        access_token_hash = self.get_password_hash(access_token)
        refresh_token_hash = self.get_password_hash(refresh_token)

        session = UserSession(
            id=session_id,
            user_id=user_id,
            token_hash=access_token_hash,
            refresh_token_hash=refresh_token_hash,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
        )

        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get_user_session(self, session_id: str) -> Optional[UserSession]:
        """Get user session by ID."""
        result = await self.db.execute(
            select(UserSession).where(
                and_(
                    UserSession.id == session_id,
                    UserSession.is_active == True,
                    UserSession.expires_at > datetime.utcnow(),
                )
            )
        )
        return result.scalar_one_or_none()

    async def invalidate_session(self, session_id: str) -> bool:
        """Invalidate a user session."""
        session = await self.get_user_session(session_id)
        if not session:
            return False

        session.is_active = False
        await self.db.commit()
        return True

    async def invalidate_all_user_sessions(self, user_id: str) -> int:
        """Invalidate all sessions for a user."""
        result = await self.db.execute(
            select(UserSession).where(
                and_(UserSession.user_id == user_id, UserSession.is_active == True)
            )
        )
        sessions = result.scalars().all()

        for session in sessions:
            session.is_active = False

        await self.db.commit()
        return len(sessions)

    # Password reset
    async def create_password_reset_token(self, user_id: str) -> str:
        """Create password reset token."""
        token = secrets.token_urlsafe(32)
        token_hash = self.get_password_hash(token)
        expires_at = datetime.utcnow() + timedelta(hours=1)

        # Invalidate existing reset tokens for user
        await self.db.execute(
            select(PasswordReset).where(PasswordReset.user_id == user_id)
        )
        existing_tokens = await self.db.execute(
            select(PasswordReset).where(PasswordReset.user_id == user_id)
        )
        for token_obj in existing_tokens.scalars().all():
            token_obj.is_used = True

        # Create new reset token
        reset_token = PasswordReset(
            id=str(uuid.uuid4()),
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        self.db.add(reset_token)
        await self.db.commit()
        return token

    async def verify_password_reset_token(self, token: str) -> Optional[User]:
        """Verify password reset token and return user."""
        result = await self.db.execute(
            select(PasswordReset).where(
                and_(
                    PasswordReset.token_hash == self.get_password_hash(token),
                    PasswordReset.is_used == False,
                    PasswordReset.expires_at > datetime.utcnow(),
                )
            )
        )
        reset_token = result.scalar_one_or_none()

        if not reset_token:
            return None

        return await self.get_user_by_id(reset_token.user_id)

    async def reset_password(self, token: str, new_password: str) -> bool:
        """Reset user password using token."""
        user = await self.verify_password_reset_token(token)
        if not user:
            return False

        # Update password
        user.hashed_password = self.get_password_hash(new_password)

        # Mark token as used
        result = await self.db.execute(
            select(PasswordReset).where(
                PasswordReset.token_hash == self.get_password_hash(token)
            )
        )
        reset_token = result.scalar_one_or_none()
        if reset_token:
            reset_token.is_used = True
            reset_token.used_at = datetime.utcnow()

        # Invalidate all user sessions
        await self.invalidate_all_user_sessions(user.id)

        await self.db.commit()
        return True

    # Email verification
    async def create_email_verification_token(self, user_id: str) -> str:
        """Create email verification token."""
        token = secrets.token_urlsafe(32)
        token_hash = self.get_password_hash(token)
        expires_at = datetime.utcnow() + timedelta(days=1)

        # Create verification token
        verification_token = EmailVerification(
            id=str(uuid.uuid4()),
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        self.db.add(verification_token)
        await self.db.commit()
        return token

    async def verify_email(self, token: str) -> bool:
        """Verify email using token."""
        result = await self.db.execute(
            select(EmailVerification).where(
                and_(
                    EmailVerification.token_hash == self.get_password_hash(token),
                    EmailVerification.is_used == False,
                    EmailVerification.expires_at > datetime.utcnow(),
                )
            )
        )
        verification_token = result.scalar_one_or_none()

        if not verification_token:
            return False

        # Mark user as verified
        user = await self.get_user_by_id(verification_token.user_id)
        if user:
            user.is_verified = True
            verification_token.is_used = True
            verification_token.used_at = datetime.utcnow()
            await self.db.commit()
            return True

        return False

    # User profile management
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile."""
        result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def update_user_profile(
        self, user_id: str, profile_data: dict
    ) -> Optional[UserProfile]:
        """Update user profile."""
        profile = await self.get_user_profile(user_id)
        if not profile:
            return None

        for key, value in profile_data.items():
            if hasattr(profile, key):
                setattr(profile, key, value)

        profile.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(profile)
        return profile
