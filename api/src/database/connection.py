#!/usr/bin/env python3
"""
Database Connection Module
Story-005: Enhanced Company Profile & Fundamentals Analysis (MVP)

Database connection and session management for company analysis.
"""

import asyncio
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from ..core.config import settings
from ..models.database import Base


class DatabaseManager:
    """Database connection manager."""

    def __init__(self):
        """Initialize database manager."""
        self.engine = None
        self.session_factory = None
        self._initialized = False

    async def initialize(self):
        """Initialize database connection."""
        if self._initialized:
            return

        # Create async engine
        database_url = settings.DATABASE_URL
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace(
                "postgresql://", "postgresql+asyncpg://", 1
            )
        elif database_url.startswith("sqlite://"):
            database_url = database_url.replace("sqlite://", "sqlite+aiosqlite://", 1)

        self.engine = create_async_engine(
            database_url,
            echo=settings.DEBUG,
            pool_pre_ping=True,
        )

        # Create session factory
        self.session_factory = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

        self._initialized = True

    async def create_tables(self):
        """Create all database tables."""
        if not self._initialized:
            await self.initialize()

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self):
        """Close database connections."""
        if self.engine:
            await self.engine.dispose()
            self._initialized = False

    def get_session(self) -> async_sessionmaker[AsyncSession]:
        """Get session factory."""
        if not self._initialized:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self.session_factory


# Global database manager instance
db_manager = DatabaseManager()


async def get_db_session() -> AsyncSession:
    """Get database session dependency."""
    if not db_manager._initialized:
        await db_manager.initialize()

    return db_manager.get_session()


async def init_database():
    """Initialize database on startup."""
    await db_manager.initialize()
    await db_manager.create_tables()


async def close_database():
    """Close database on shutdown."""
    await db_manager.close()
