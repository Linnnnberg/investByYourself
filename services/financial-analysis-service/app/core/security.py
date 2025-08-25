"""
Security Module - Financial Analysis Service
===========================================

Authentication and authorization functionality.
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token handling
security = HTTPBearer()

# Mock user database for development (will be replaced with actual database)
users_db = {
    1: {
        "id": 1,
        "username": "admin",
        "email": "admin@investbyyourself.com",
        "hashed_password": pwd_context.hash("admin123"),
        "is_active": True,
        "role": "admin",
    },
    2: {
        "id": 2,
        "username": "user",
        "email": "user@investbyyourself.com",
        "hashed_password": pwd_context.hash("user123"),
        "is_active": True,
        "role": "user",
    },
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate a user with username and password."""
    for user in users_db.values():
        if user["username"] == username and verify_password(
            password, user["hashed_password"]
        ):
            return user
    return None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire})

    try:
        encoded_jwt = jwt.encode(
            to_encode, settings.secret_key, algorithm=settings.algorithm
        )
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating access token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create access token",
        )


def verify_token(token: str) -> Optional[dict]:
    """Verify a JWT token and return the payload."""
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return payload
    except JWTError as e:
        logger.warning(f"JWT token verification failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {e}")
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Get the current authenticated user from the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = verify_token(token)

        if payload is None:
            raise credentials_exception

        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        # Get user from database (using mock for now)
        user = users_db.get(user_id)
        if user is None:
            raise credentials_exception

        return user

    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise credentials_exception


async def get_current_active_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Get the current active user."""
    if not current_user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


def require_role(required_role: str):
    """Decorator to require a specific role."""

    def role_checker(current_user: dict = Depends(get_current_active_user)):
        if current_user.get("role") != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required",
            )
        return current_user

    return role_checker


def require_admin(current_user: dict = Depends(get_current_active_user)) -> dict:
    """Require admin role."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required"
        )
    return current_user


# Mock authentication endpoints for development
async def login(username: str, password: str) -> Optional[dict]:
    """Mock login function."""
    user = authenticate_user(username, password)
    if not user:
        return None

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user["id"])}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
        },
    }


def get_user_by_id(user_id: int) -> Optional[dict]:
    """Get user by ID from mock database."""
    return users_db.get(user_id)


def get_user_by_username(username: str) -> Optional[dict]:
    """Get user by username from mock database."""
    for user in users_db.values():
        if user["username"] == username:
            return user
    return None


# Security utilities
def is_authenticated(user: dict) -> bool:
    """Check if user is authenticated."""
    return user is not None and user.get("is_active", False)


def has_permission(user: dict, permission: str) -> bool:
    """Check if user has a specific permission."""
    if not is_authenticated(user):
        return False

    # Simple permission system based on role
    role_permissions = {
        "admin": ["read", "write", "delete", "admin"],
        "user": ["read", "write"],
        "viewer": ["read"],
    }

    user_role = user.get("role", "viewer")
    return permission in role_permissions.get(user_role, [])


def log_security_event(event_type: str, user_id: Optional[int], details: str):
    """Log security-related events."""
    logger.info(f"SECURITY: {event_type} - User: {user_id} - {details}")


# Initialize security module
logger.info("Security module initialized")
