#!/usr/bin/env python3
"""
Database Models for Company Analysis
Story-005: Enhanced Company Profile & Fundamentals Analysis (MVP)

SQLAlchemy models for company and financial data.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    DECIMAL,
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
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
