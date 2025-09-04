#!/usr/bin/env python3
"""
InvestByYourself Database Service
Tech-028: API Implementation

Database service for user and application data management.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import Boolean, Column, DateTime, String, Text, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.core.config import get_database_url, settings
from src.core.exceptions import DatabaseError
from src.core.logging import get_logger

logger = get_logger(__name__)


# Database setup
def create_database_engine():
    """Create database engine with appropriate configuration."""
    database_url = get_database_url()

    if settings.DATABASE_TYPE.lower() == "sqlite":
        # SQLite configuration for development
        return create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=settings.DEBUG,  # Log SQL queries in debug mode
        )
    else:
        # PostgreSQL configuration for production
        return create_engine(
            database_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=settings.DEBUG,
        )


engine = create_database_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    """User database model."""

    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PasswordResetToken(Base):
    """Password reset token database model."""

    __tablename__ = "password_reset_tokens"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class DatabaseService:
    """Database service for data operations."""

    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal

    def get_db(self) -> Session:
        """Get database session."""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def create_tables(self):
        """Create all database tables."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Failed to create database tables: {e}")
            raise DatabaseError("Failed to create database tables")

    def create_user(self, db: Session, user_data: Dict[str, Any]) -> User:
        """Create a new user in the database."""
        try:
            db_user = User(**user_data)
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            logger.info(f"User created in database: {db_user.email}")
            return db_user
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Failed to create user: {e}")
            raise DatabaseError("Failed to create user")

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            return db.query(User).filter(User.email == email).first()
        except SQLAlchemyError as e:
            logger.error(f"Failed to get user by email: {e}")
            raise DatabaseError("Failed to get user")

    def get_user_by_id(self, db: Session, user_id: str) -> Optional[User]:
        """Get user by ID."""
        try:
            return db.query(User).filter(User.id == user_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Failed to get user by ID: {e}")
            raise DatabaseError("Failed to get user")

    def update_user(
        self, db: Session, user_id: str, update_data: Dict[str, Any]
    ) -> Optional[User]:
        """Update user information."""
        try:
            db_user = db.query(User).filter(User.id == user_id).first()
            if not db_user:
                return None

            for key, value in update_data.items():
                if hasattr(db_user, key):
                    setattr(db_user, key, value)

            db_user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_user)
            logger.info(f"User updated: {db_user.email}")
            return db_user
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Failed to update user: {e}")
            raise DatabaseError("Failed to update user")

    def delete_user(self, db: Session, user_id: str) -> bool:
        """Delete user."""
        try:
            db_user = db.query(User).filter(User.id == user_id).first()
            if not db_user:
                return False

            db.delete(db_user)
            db.commit()
            logger.info(f"User deleted: {db_user.email}")
            return True
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Failed to delete user: {e}")
            raise DatabaseError("Failed to delete user")

    def create_password_reset_token(
        self, db: Session, user_id: str, token: str, expires_at: datetime
    ) -> PasswordResetToken:
        """Create password reset token."""
        try:
            reset_token = PasswordResetToken(
                user_id=user_id, token=token, expires_at=expires_at
            )
            db.add(reset_token)
            db.commit()
            db.refresh(reset_token)
            logger.info(f"Password reset token created for user: {user_id}")
            return reset_token
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Failed to create password reset token: {e}")
            raise DatabaseError("Failed to create password reset token")

    def get_password_reset_token(
        self, db: Session, token: str
    ) -> Optional[PasswordResetToken]:
        """Get password reset token."""
        try:
            return (
                db.query(PasswordResetToken)
                .filter(
                    PasswordResetToken.token == token,
                    PasswordResetToken.used == False,
                    PasswordResetToken.expires_at > datetime.utcnow(),
                )
                .first()
            )
        except SQLAlchemyError as e:
            logger.error(f"Failed to get password reset token: {e}")
            raise DatabaseError("Failed to get password reset token")

    def mark_password_reset_token_used(self, db: Session, token: str) -> bool:
        """Mark password reset token as used."""
        try:
            reset_token = (
                db.query(PasswordResetToken)
                .filter(PasswordResetToken.token == token)
                .first()
            )
            if not reset_token:
                return False

            reset_token.used = True
            db.commit()
            logger.info(f"Password reset token marked as used: {token}")
            return True
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Failed to mark password reset token as used: {e}")
            raise DatabaseError("Failed to update password reset token")

    def get_all_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        try:
            return db.query(User).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Failed to get users: {e}")
            raise DatabaseError("Failed to get users")

    def check_email_exists(self, db: Session, email: str) -> bool:
        """Check if email already exists."""
        try:
            user = db.query(User).filter(User.email == email).first()
            return user is not None
        except SQLAlchemyError as e:
            logger.error(f"Failed to check email existence: {e}")
            raise DatabaseError("Failed to check email existence")


# Create global database service instance
db_service = DatabaseService()


def get_database_session() -> Session:
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
