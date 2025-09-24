#!/usr/bin/env python3
"""
Simplified Database Service for InvestByYourself
Tech-036: Authentication System Implementation

Simplified database service that only handles table creation.
"""

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.core.config import get_database_url, settings
from src.core.exceptions import DatabaseError
from src.core.logging import get_logger

# Import all models to ensure they are registered with Base
from src.models import auth, database
from src.models.database import Base

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


class DatabaseService:
    """Simplified database service for table creation."""

    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal

    def create_tables(self):
        """Create all database tables."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Failed to create database tables: {e}")
            raise DatabaseError("Failed to create database tables")


# Create global database service instance
db_service = DatabaseService()


def get_database_session():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
