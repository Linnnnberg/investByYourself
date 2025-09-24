"""
Strategy Data Model - Financial Analysis Service
===============================================

SQLAlchemy model for investment strategies.
"""

from datetime import datetime

from app.core.database import Base
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Strategy(Base):
    """Strategy model for storing investment strategy configurations."""

    __tablename__ = "strategies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    strategy_type = Column(String(100), nullable=False, index=True)
    parameters = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="strategies")
    backtests = relationship("Backtest", back_populates="strategy")

    def __repr__(self):
        return (
            f"<Strategy(id={self.id}, name='{self.name}', type='{self.strategy_type}')>"
        )

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "strategy_type": self.strategy_type,
            "parameters": self.parameters,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Create model from dictionary."""
        return cls(
            user_id=data.get("user_id"),
            name=data.get("name"),
            description=data.get("description"),
            strategy_type=data.get("strategy_type"),
            parameters=data.get("parameters", {}),
            is_active=data.get("is_active", True),
        )
