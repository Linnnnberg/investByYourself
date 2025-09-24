#!/usr/bin/env python3
"""
Authentication Models for InvestByYourself
Tech-036: Authentication System Implementation

SQLAlchemy models for user authentication and authorization.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    """User database model for authentication."""

    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)

    # User preferences
    timezone = Column(String(50), default="UTC")
    language = Column(String(10), default="en")
    theme = Column(String(20), default="light")

    # Relationships
    portfolios = relationship("Portfolio", back_populates="user")
    watchlists = relationship("Watchlist", back_populates="user")
    # workflows = relationship("WorkflowExecution", back_populates="user")  # Commented out until WorkflowExecution is defined


class UserSession(Base):
    """User session model for JWT token management."""

    __tablename__ = "user_sessions"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    token_hash = Column(String(255), nullable=False, unique=True, index=True)
    refresh_token_hash = Column(String(255), nullable=False, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    last_used = Column(DateTime, default=datetime.utcnow)
    user_agent = Column(Text)
    ip_address = Column(String(45))


class UserProfile(Base):
    """Extended user profile model for investment preferences."""

    __tablename__ = "user_profiles"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, unique=True, index=True)

    # Investment preferences
    risk_tolerance = Column(String(20))  # conservative, moderate, aggressive
    investment_goals = Column(Text)  # JSON string of goals
    time_horizon = Column(String(20))  # short, medium, long
    investment_experience = Column(String(20))  # beginner, intermediate, advanced

    # Personal information
    age = Column(Integer)
    annual_income = Column(String(20))  # income range
    net_worth = Column(String(20))  # net worth range
    employment_status = Column(String(20))

    # Notification preferences
    email_notifications = Column(Boolean, default=True)
    price_alerts = Column(Boolean, default=True)
    market_updates = Column(Boolean, default=True)
    newsletter = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PasswordReset(Base):
    """Password reset token model."""

    __tablename__ = "password_resets"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    token_hash = Column(String(255), nullable=False, unique=True, index=True)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime)


class EmailVerification(Base):
    """Email verification token model."""

    __tablename__ = "email_verifications"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    token_hash = Column(String(255), nullable=False, unique=True, index=True)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime)
