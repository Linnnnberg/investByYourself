#!/usr/bin/env python3
"""
InvestByYourself Database Initialization
Tech-028: API Implementation

Database initialization and migration utilities.
"""

import logging
from typing import Optional

from src.core.config import settings
from src.core.logging import get_logger
from src.database.connection import db_manager
from src.services.database import db_service

logger = get_logger(__name__)


async def init_database() -> None:
    """Initialize database tables and connections."""
    try:
        logger.info("Initializing database...")

        # Create all tables (existing user tables)
        db_service.create_tables()

        # Create company analysis tables
        await db_manager.initialize()
        await db_manager.create_tables()

        logger.info("Database initialized successfully")

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def close_database() -> None:
    """Close database connections."""
    try:
        logger.info("Closing database connections...")
        # Close company analysis database connections
        await db_manager.close()
        logger.info("Database connections closed")

    except Exception as e:
        logger.error(f"Error closing database: {e}")


def create_admin_user() -> Optional[str]:
    """Create an admin user for testing purposes."""
    try:
        from src.services.auth_service import auth_service
        from src.services.database import get_database_session

        # Get database session
        db_gen = get_database_session()
        db = next(db_gen)

        try:
            # Check if admin user already exists
            admin_email = "admin@investbyyourself.com"
            existing_user = db_service.get_user_by_email(db, admin_email)
            if existing_user:
                logger.info("Admin user already exists")
                return existing_user.id

            # Create admin user
            from src.services.auth_service import UserCreate

            admin_data = UserCreate(
                email=admin_email,
                password="${ADMIN_PASSWORD:-AdminPass123!}",
                first_name="Admin",
                last_name="User",
            )

            user = auth_service.create_user(admin_data)

            # Save to database
            user_dict = user.dict()
            user_dict["hashed_password"] = user.hashed_password
            del user_dict["id"]  # Let database generate ID

            db_user = db_service.create_user(db, user_dict)

            logger.info(f"Admin user created: {db_user.email}")
            return db_user.id

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Failed to create admin user: {e}")
        return None


if __name__ == "__main__":
    """Run database initialization directly."""
    import asyncio

    async def main():
        await init_database()

        # Create admin user in development
        if settings.ENVIRONMENT == "development":
            admin_id = create_admin_user()
            if admin_id:
                print(f"Admin user created with ID: {admin_id}")

    asyncio.run(main())
