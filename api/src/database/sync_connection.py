#!/usr/bin/env python3
"""
Sync Database Connection Module
InvestByYourself Financial Platform

Sync database connection for workflow endpoints that need synchronous access.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ..core.config import settings

# Create sync engine
database_url = settings.DATABASE_URL
if database_url.startswith("postgresql+asyncpg://"):
    database_url = database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
elif database_url.startswith("sqlite+aiosqlite://"):
    database_url = database_url.replace("sqlite+aiosqlite://", "sqlite://", 1)

engine = create_engine(
    database_url,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Get database session dependency for sync operations."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
