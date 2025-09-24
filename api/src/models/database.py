#!/usr/bin/env python3
"""
Database Models for Company Analysis
Story-005: Enhanced Company Profile & Fundamentals Analysis (MVP)

SQLAlchemy models for company and financial data.
"""

import json
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    DECIMAL,
    JSON,
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Company(Base):
    """Company database model."""

    __tablename__ = "companies"

    id = Column(String, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    sector = Column(String(100), index=True)
    industry = Column(String(100), index=True)
    exchange = Column(String(20))
    currency = Column(String(3), default="USD")
    country = Column(String(100))
    website = Column(String(255))
    description = Column(Text)
    employee_count = Column(Integer)
    market_cap = Column(DECIMAL(20, 2))
    enterprise_value = Column(DECIMAL(20, 2))
    ceo = Column(String(255))
    headquarters = Column(String(255))
    founded_year = Column(Integer)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    financial_ratios = relationship("FinancialRatio", back_populates="company")
    market_data = relationship("MarketData", back_populates="company")
    historical_prices = relationship("HistoricalPrice", back_populates="company")
    technical_indicators = relationship("TechnicalIndicator", back_populates="company")
    data_quality_metrics = relationship("DataQualityMetrics", back_populates="company")


class FinancialRatio(Base):
    """Financial ratios database model."""

    __tablename__ = "financial_ratios"

    id = Column(String, primary_key=True, index=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False, index=True)
    ratio_date = Column(DateTime, nullable=False, index=True)
    ratio_type = Column(String(50), nullable=False, index=True)
    ratio_value = Column(DECIMAL(15, 6))
    ratio_unit = Column(String(20))
    source = Column(String(50), default="yfinance")
    confidence_score = Column(DECIMAL(3, 2), default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="financial_ratios")


class MarketData(Base):
    """Market data database model."""

    __tablename__ = "market_data"

    id = Column(String, primary_key=True, index=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False, index=True)
    data_date = Column(DateTime, nullable=False, index=True)
    open_price = Column(DECIMAL(10, 4))
    high_price = Column(DECIMAL(10, 4))
    low_price = Column(DECIMAL(10, 4))
    close_price = Column(DECIMAL(10, 4))
    adjusted_close = Column(DECIMAL(10, 4))
    volume = Column(BigInteger)
    market_cap = Column(DECIMAL(20, 2))
    enterprise_value = Column(DECIMAL(20, 2))
    pe_ratio = Column(DECIMAL(10, 4))
    pb_ratio = Column(DECIMAL(10, 4))
    ps_ratio = Column(DECIMAL(10, 4))
    dividend_yield = Column(DECIMAL(5, 4))
    beta = Column(DECIMAL(5, 4))
    source = Column(String(50), default="yfinance")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="market_data")


class EconomicIndicator(Base):
    """Economic indicators database model."""

    __tablename__ = "economic_indicators"

    id = Column(String, primary_key=True, index=True)
    indicator_date = Column(DateTime, nullable=False, index=True)
    indicator_type = Column(String(50), nullable=False, index=True)
    indicator_value = Column(DECIMAL(15, 6))
    indicator_unit = Column(String(20))
    period_type = Column(String(20), default="monthly")
    source = Column(String(50), default="FRED")
    created_at = Column(DateTime, default=datetime.utcnow)


class DataQuality(Base):
    """Data quality tracking database model."""

    __tablename__ = "data_quality"

    id = Column(String, primary_key=True, index=True)
    data_source = Column(String(50), nullable=False, index=True)
    data_type = Column(String(50), nullable=False, index=True)
    quality_date = Column(DateTime, nullable=False, index=True)
    record_count = Column(Integer)
    completeness_score = Column(DECIMAL(3, 2))
    accuracy_score = Column(DECIMAL(3, 2))
    freshness_score = Column(DECIMAL(3, 2))
    overall_score = Column(DECIMAL(3, 2))
    issues_found = Column(Text)  # JSON array of issues
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


class DataCollectionLog(Base):
    """Data collection logs database model."""

    __tablename__ = "data_collection_logs"

    id = Column(String, primary_key=True, index=True)
    collection_date = Column(DateTime, nullable=False, index=True)
    data_source = Column(String(50), nullable=False, index=True)
    data_type = Column(String(50), nullable=False, index=True)
    status = Column(String(20), nullable=False)  # 'success', 'partial', 'failed'
    records_collected = Column(Integer)
    records_processed = Column(Integer)
    errors = Column(Text)  # JSON array of errors
    duration_seconds = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


# Workflow Database Models


class DBWorkflowDefinition(Base):
    """Workflow definition database model."""

    __tablename__ = "workflow_definitions"

    id = Column(String, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    steps = Column(JSON, nullable=False)  # List of workflow steps
    entry_points = Column(JSON, nullable=False)  # List of entry point step IDs
    exit_points = Column(JSON, nullable=False)  # List of exit point step IDs
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    executions = relationship(
        "DBWorkflowExecution", back_populates="workflow_definition"
    )


class DBWorkflowExecution(Base):
    """Workflow execution database model."""

    __tablename__ = "workflow_executions"

    id = Column(String, primary_key=True, index=True)
    workflow_id = Column(
        String, ForeignKey("workflow_definitions.id"), nullable=False, index=True
    )
    user_id = Column(String, nullable=False, index=True)
    session_id = Column(String, nullable=False, index=True)
    status = Column(
        String(20), nullable=False, index=True
    )  # pending, running, completed, failed, paused, cancelled
    current_step = Column(String(100), index=True)
    progress = Column(Float, default=0.0)
    context_data = Column(JSON, default=dict)  # Workflow context data
    step_results = Column(JSON, default=dict)  # Results from each step
    error_message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workflow_definition = relationship(
        "DBWorkflowDefinition", back_populates="executions"
    )
    step_executions = relationship(
        "DBStepExecution", back_populates="workflow_execution"
    )


class DBStepExecution(Base):
    """Step execution database model."""

    __tablename__ = "step_executions"

    id = Column(String, primary_key=True, index=True)
    workflow_execution_id = Column(
        String, ForeignKey("workflow_executions.id"), nullable=False, index=True
    )
    step_id = Column(String, nullable=False, index=True)
    step_name = Column(String(255), nullable=False)
    step_type = Column(String(50), nullable=False, index=True)
    status = Column(
        String(20), nullable=False, index=True
    )  # pending, running, completed, failed, skipped
    input_data = Column(JSON, default=dict)
    output_data = Column(JSON, default=dict)
    error_message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    workflow_execution = relationship(
        "DBWorkflowExecution", back_populates="step_executions"
    )


class HistoricalPrice(Base):
    """Historical price data database model."""

    __tablename__ = "historical_prices"

    id = Column(String, primary_key=True, index=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    open = Column(DECIMAL(10, 4), nullable=False)
    high = Column(DECIMAL(10, 4), nullable=False)
    low = Column(DECIMAL(10, 4), nullable=False)
    close = Column(DECIMAL(10, 4), nullable=False)
    volume = Column(BigInteger, nullable=False)
    adjusted_close = Column(DECIMAL(10, 4))
    dividend_amount = Column(DECIMAL(10, 4), default=0)
    split_coefficient = Column(DECIMAL(10, 4), default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="historical_prices")

    # Indexes
    __table_args__ = (
        Index("idx_historical_prices_company_date", "company_id", "date"),
        Index("idx_historical_prices_date", "date"),
    )


class TechnicalIndicator(Base):
    """Technical indicators database model."""

    __tablename__ = "technical_indicators"

    id = Column(String, primary_key=True, index=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    indicator_type = Column(String(50), nullable=False, index=True)
    indicator_name = Column(String(100), nullable=False)
    value = Column(DECIMAL(15, 6))
    period = Column(Integer)
    indicator_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="technical_indicators")

    # Indexes
    __table_args__ = (
        Index("idx_technical_indicators_company_date", "company_id", "date"),
        Index("idx_technical_indicators_type", "indicator_type"),
    )


class DataQualityMetrics(Base):
    """Data quality and validation metrics database model."""

    __tablename__ = "data_quality_metrics"

    id = Column(String, primary_key=True, index=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False, index=True)
    data_type = Column(String(50), nullable=False)  # 'price' or 'indicator'
    date_range_start = Column(Date, nullable=False)
    date_range_end = Column(Date, nullable=False)
    total_records = Column(Integer, nullable=False)
    missing_records = Column(Integer, default=0)
    quality_score = Column(DECIMAL(3, 2))  # 0.00 to 1.00
    last_updated = Column(DateTime, default=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="data_quality_metrics")


class Portfolio(Base):
    """Portfolio database model."""

    __tablename__ = "portfolios"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    risk_profile = Column(
        String(20), default="moderate"
    )  # conservative, moderate, aggressive
    target_allocation = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    total_value = Column(DECIMAL(20, 2), default=0.00)
    total_cost = Column(DECIMAL(20, 2), default=0.00)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="portfolios")
    holdings = relationship("PortfolioHolding", back_populates="portfolio")


class PortfolioHolding(Base):
    """Portfolio holding database model."""

    __tablename__ = "portfolio_holdings"

    id = Column(String, primary_key=True, index=True)
    portfolio_id = Column(
        String, ForeignKey("portfolios.id"), nullable=False, index=True
    )
    company_id = Column(String, ForeignKey("companies.id"), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    quantity = Column(DECIMAL(20, 8), nullable=False)
    average_cost = Column(DECIMAL(20, 2), nullable=False)
    current_price = Column(DECIMAL(20, 2))
    market_value = Column(DECIMAL(20, 2))
    gain_loss = Column(DECIMAL(20, 2))
    gain_loss_pct = Column(DECIMAL(5, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    portfolio = relationship("Portfolio", back_populates="holdings")
    company = relationship("Company")


class Watchlist(Base):
    """Watchlist database model."""

    __tablename__ = "watchlists"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    company_id = Column(String, ForeignKey("companies.id"), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    added_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    target_price = Column(DECIMAL(20, 2))
    alert_price = Column(DECIMAL(20, 2))
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="watchlists")
    company = relationship("Company")
