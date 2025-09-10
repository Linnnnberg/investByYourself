#!/usr/bin/env python3
"""
Database Service for InvestByYourself API
Tech-028: API Implementation

Database service layer that integrates with existing PostgreSQL infrastructure.
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, Optional

import asyncpg
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseService:
    """Database service for FastAPI application."""

    def __init__(self):
        self.engine = None
        self.async_engine = None
        self.session_factory = None
        self.async_session_factory = None
        self._connection_pool = None

    def get_database_url(self) -> str:
        """Get database URL from environment variables."""
        # Use development database for API
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        database = os.getenv("POSTGRES_DATABASE", "investbyyourself_dev")
        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "")

        if not password:
            logger.warning("POSTGRES_PASSWORD not set, using empty password")

        return f"postgresql://{user}:{password}@{host}:{port}/{database}"

    def get_async_database_url(self) -> str:
        """Get async database URL from environment variables."""
        # Use development database for API
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        database = os.getenv("POSTGRES_DATABASE", "investbyyourself_dev")
        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "")

        if not password:
            logger.warning("POSTGRES_PASSWORD not set, using empty password")

        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"

    def initialize(self) -> None:
        """Initialize database connections."""
        try:
            # Sync engine for basic operations
            database_url = self.get_database_url()
            self.engine = create_engine(
                database_url,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False,  # Set to True for SQL query logging
            )

            # Async engine for async operations
            async_database_url = self.get_async_database_url()
            self.async_engine = create_async_engine(
                async_database_url,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False,
            )

            # Session factories
            self.session_factory = sessionmaker(
                bind=self.engine, autocommit=False, autoflush=False
            )

            self.async_session_factory = async_sessionmaker(
                bind=self.async_engine,
                class_=AsyncSession,
                autocommit=False,
                autoflush=False,
            )

            logger.info("Database service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize database service: {e}")
            raise

    def test_connection(self) -> Dict[str, Any]:
        """Test database connection."""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 1 as test"))
                test_value = result.fetchone()[0]

                if test_value == 1:
                    logger.info("Database connection test: PASSED")
                    return {
                        "status": "connected",
                        "database": os.getenv(
                            "POSTGRES_DATABASE", "investbyyourself_dev"
                        ),
                        "host": os.getenv("POSTGRES_HOST", "localhost"),
                        "port": os.getenv("POSTGRES_PORT", "5432"),
                    }
                else:
                    logger.error("Database connection test: FAILED - Unexpected result")
                    return {"status": "failed", "error": "Unexpected test result"}

        except Exception as e:
            logger.warning(f"Database connection test: FAILED - {e}")
            logger.info("Falling back to mock data mode")
            return {
                "status": "mock_mode",
                "database": "mock_data",
                "host": "localhost",
                "port": "5432",
                "error": str(e),
            }

    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session."""
        if not self.async_session_factory:
            raise RuntimeError("Database service not initialized")

        async with self.async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    def get_sync_session(self) -> Session:
        """Get sync database session."""
        if not self.session_factory:
            raise RuntimeError("Database service not initialized")

        return self.session_factory()

    async def execute_query(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Execute a raw SQL query."""
        async with self.get_async_session() as session:
            result = await session.execute(text(query), params or {})
            return result.fetchall()

    async def get_portfolio_tables(self) -> list:
        """Get list of portfolio-related tables."""
        # Check if we're in mock mode
        connection_test = self.test_connection()
        if connection_test["status"] == "mock_mode":
            logger.info("Using mock portfolio tables")
            return [
                "portfolios",
                "holdings",
                "transactions",
                "users",
                "portfolio_analytics",
            ]

        query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name LIKE '%portfolio%'
        OR table_name LIKE '%holding%'
        OR table_name LIKE '%transaction%'
        OR table_name LIKE '%user%'
        ORDER BY table_name;
        """

        try:
            result = await self.execute_query(query)
            tables = [row[0] for row in result]
            logger.info(f"Found portfolio tables: {tables}")
            return tables
        except Exception as e:
            logger.error(f"Failed to get portfolio tables: {e}")
            return []

    async def get_table_schema(self, table_name: str) -> list:
        """Get table schema information."""
        # Check if we're in mock mode
        connection_test = self.test_connection()
        if connection_test["status"] == "mock_mode":
            logger.info(f"Using mock schema for table: {table_name}")
            # Return mock schema based on table name
            mock_schemas = {
                "portfolios": [
                    {
                        "column_name": "id",
                        "data_type": "integer",
                        "is_nullable": "NO",
                        "column_default": "nextval('portfolios_id_seq'::regclass)",
                    },
                    {
                        "column_name": "name",
                        "data_type": "character varying",
                        "is_nullable": "NO",
                        "column_default": None,
                    },
                    {
                        "column_name": "description",
                        "data_type": "text",
                        "is_nullable": "YES",
                        "column_default": None,
                    },
                    {
                        "column_name": "created_at",
                        "data_type": "timestamp",
                        "is_nullable": "NO",
                        "column_default": "CURRENT_TIMESTAMP",
                    },
                ],
                "holdings": [
                    {
                        "column_name": "id",
                        "data_type": "integer",
                        "is_nullable": "NO",
                        "column_default": "nextval('holdings_id_seq'::regclass)",
                    },
                    {
                        "column_name": "portfolio_id",
                        "data_type": "integer",
                        "is_nullable": "NO",
                        "column_default": None,
                    },
                    {
                        "column_name": "symbol",
                        "data_type": "character varying",
                        "is_nullable": "NO",
                        "column_default": None,
                    },
                    {
                        "column_name": "quantity",
                        "data_type": "numeric",
                        "is_nullable": "NO",
                        "column_default": None,
                    },
                    {
                        "column_name": "purchase_price",
                        "data_type": "numeric",
                        "is_nullable": "NO",
                        "column_default": None,
                    },
                ],
            }
            return mock_schemas.get(table_name, [])

        query = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = :table_name
        AND table_schema = 'public'
        ORDER BY ordinal_position;
        """

        try:
            result = await self.execute_query(query, {"table_name": table_name})
            schema = [
                {
                    "column_name": row[0],
                    "data_type": row[1],
                    "is_nullable": row[2],
                    "column_default": row[3],
                }
                for row in result
            ]
            return schema
        except Exception as e:
            logger.error(f"Failed to get schema for table {table_name}: {e}")
            return []

    def close(self) -> None:
        """Close database connections."""
        if self.engine:
            self.engine.dispose()
        if self.async_engine:
            asyncio.create_task(self.async_engine.dispose())
        logger.info("Database connections closed")


# Global database service instance
db_service = DatabaseService()


def get_database_service() -> DatabaseService:
    """Get the global database service instance."""
    return db_service


# Dependency for FastAPI
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions."""
    async with db_service.get_async_session() as session:
        yield session
