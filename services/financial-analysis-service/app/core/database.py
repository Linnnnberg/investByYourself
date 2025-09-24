"""
Database Connection Management - Financial Analysis Service
========================================================

Database connection and session management for PostgreSQL.
"""

import logging
import os
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

from .config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create base class for models
Base = declarative_base()

# Database engine
engine = None
SessionLocal = None


def get_database_url() -> str:
    """Get database URL from environment or settings."""
    return os.getenv("DATABASE_URL", settings.database_url)


def create_database_engine():
    """Create database engine with connection pooling."""
    global engine, SessionLocal

    database_url = get_database_url()

    # Create engine with connection pooling
    engine = create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_pre_ping=True,
        pool_recycle=3600,  # Recycle connections every hour
        echo=settings.debug,  # Log SQL queries in debug mode
    )

    # Create session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    logger.info(f"Database engine created with pool size {settings.database_pool_size}")
    return engine


def get_database_engine():
    """Get database engine, creating it if necessary."""
    global engine
    if engine is None:
        engine = create_database_engine()
    return engine


def get_db_session() -> Session:
    """Get database session."""
    if SessionLocal is None:
        create_database_engine()

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_database_connection() -> bool:
    """Test database connection."""
    try:
        engine = get_database_engine()
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
            logger.info("Database connection test successful")
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


def get_database_status() -> dict:
    """Get database status information."""
    try:
        engine = get_database_engine()
        with engine.connect() as connection:
            # Get basic database info
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]

            # Get connection pool info
            pool = engine.pool
            pool_status = {
                "size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "invalid": pool.invalid(),
            }

            return {
                "status": "connected",
                "version": version,
                "pool_status": pool_status,
                "url": (
                    get_database_url().replace(
                        get_database_url().split("@")[0].split("//")[1], "***:***"
                    )
                    if "@" in get_database_url()
                    else get_database_url()
                ),
            }
    except Exception as e:
        return {"status": "error", "error": str(e), "url": get_database_url()}


# Initialize database on module import
try:
    if test_database_connection():
        logger.info("Database initialized successfully")
    else:
        logger.warning(
            "Database connection failed - service will use in-memory storage"
        )
except Exception as e:
    logger.warning(
        f"Database initialization failed: {e} - service will use in-memory storage"
    )
