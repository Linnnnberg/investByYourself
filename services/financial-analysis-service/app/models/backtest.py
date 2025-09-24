"""
Backtest Data Model - Financial Analysis Service
===============================================

SQLAlchemy model for backtest executions.
"""

from datetime import datetime

from app.core.database import Base
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Backtest(Base):
    """Backtest model for storing backtest executions."""

    __tablename__ = "backtests"

    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    initial_investment = Column(Numeric(15, 2), nullable=False)
    parameters = Column(JSON, nullable=True)
    status = Column(String(50), default="queued", index=True)
    progress = Column(Numeric(5, 2), default=0.0)
    current_step = Column(String(255), nullable=True)
    results = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)

    # Relationships
    strategy = relationship("Strategy", back_populates="backtests")
    user = relationship("User", back_populates="backtests")

    def __repr__(self):
        return f"<Backtest(id={self.id}, strategy_id={self.strategy_id}, status='{self.status}')>"

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "strategy_id": self.strategy_id,
            "user_id": self.user_id,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "initial_investment": (
                float(self.initial_investment) if self.initial_investment else None
            ),
            "parameters": self.parameters,
            "status": self.status,
            "progress": float(self.progress) if self.progress else None,
            "current_step": self.current_step,
            "results": self.results,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "error_message": self.error_message,
        }
